import os
import json
import boto3
from urllib.parse import urlparse
from botocore.exceptions import ClientError


# AWS managed service cannot access user private data directly;
# it must assume a role with specific s3:GetObject and s3:PutObject
# permissions to read input data or save model outputs.
# The IAM role serves as the mechanism for aws service to authenticate 
# with S3 securely.
def add_s3_iam_role_policy(bucket_name, service_name, role):
    ''' Create IAM Role and Policy for service to access S3 bucket '''
    try:
        iam = boto3.client("iam")
        # Create IAM Role and Policy
        role_name = iam.create_role(
            RoleName=f"{role}-{bucket_name}",
            AssumeRolePolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {
                            "Service": f"{service_name}"
                        },
                        "Action": "sts:AssumeRole"
                    }
                ] 
            })
        )['Role']['RoleName']

        policy_arn = iam.create_policy(
            PolicyName=f"{role}-Policy",
            PolicyDocument=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "s3:GetObject",
                            "s3:PutObject",
                            "s3:ListBucket"
                        ],
                        "Resource": [
                            f"arn:aws:s3:::{bucket_name}",
                            f"arn:aws:s3:::{bucket_name}/*"
                        ]
                    }
                ]
            })
        )['Policy']['Arn']

        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )
        role = iam.get_role(RoleName=role_name)
        role_arn = role['Role']['Arn']
        print('Role ARN: '+role_arn)
        return role_arn
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"Role '{role_name}' already exists.")
        role = iam.get_role(RoleName=role_name)
        role_arn = role['Role']['Arn']
        print('Role ARN: '+role_arn)
        return role_arn
    except Exception as e:
        print(f"An error occurred: {e}")
    return None

def create_s3_bucket(s3_client, bucket_name, region):
    ''' Ensure the S3 client is created in the same region as the buck '''
    try:
        if region == "us-east-1":
            response = s3_client.create_bucket(Bucket=bucket_name)
            print(f'S3 bucket ARN: {response['BucketArn']}')
        else:
            # Specify the LocationConstraint in the CreateBucketConfiguration
            location = {'LocationConstraint': region}
            response = s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration=location
            )
        print(f"S3 bucket '{bucket_name}' created successfully in region '{region}'.")
    except ClientError as e:
        print(f"Error creating bucket: {e}")


def get_s3_to_dict(s3_url, s3_client):
    bucket_name = s3_url.split('/')[2]
    object_key = '/'.join(s3_url.split('/')[3:])
    # Download the JSON file from S3
    # s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    json_content = response['Body'].read().decode('utf-8')
    # Parse the JSON content
    json_obj = json.loads(json_content)
    return json_obj

def get_s3_bucket_and_key(s3_uri):
    parsed_uri = urlparse(s3_uri)
    bucket_name = parsed_uri.netloc
    object_key = parsed_uri.path.lstrip('/')
    return (bucket_name, object_key)

def s3_directory_exists(s3_client, bucket_name, directory_path):
    """
    Checks if an S3 "directory" contains any objects.
    """
    # Ensure the path ends with a slash for consistent prefix matching
    if not directory_path.endswith('/'):
        directory_path += '/'

    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=directory_path,
        MaxKeys=1
    )
    return 'Contents' in response

def create_s3_directory(s3_client, bucket_name, directory_name):
    """ Directory creation in an S3 bucket."""
    # S3 stores folders as zero-byte objects with a trailing slash in the key
    directory_key = directory_name.strip('/') + '/'
    try:
        if s3_directory_exists(s3_client, bucket_name, directory_key):
            print(f"Directory '{directory_key}' created successfully in bucket '{bucket_name}'")
            return True
        s3_client.put_object(Bucket=bucket_name, Key=directory_key, Body=b'')
        print(f"Directory '{directory_key}' created successfully in bucket '{bucket_name}'")
    except ClientError as e:
        print(f"Error creating directory: {e.response['Error']['Message']}")
        return False
    return True

def read_s3_object(s3_uri, s3_client):
    # Parse the S3 URI
    parsed_uri = urlparse(s3_uri)
    bucket_name = parsed_uri.netloc
    object_key = parsed_uri.path.lstrip('/')
    # Create an S3 client
    # s3_client = boto3.client('s3')
    try:
        # Get the object from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        # Read the content of the object
        content = response['Body'].read().decode('utf-8')
        return content
    except ClientError as e:
        print(f"Error reading S3 object: {e}")
        return None


def get_bucket_and_key(s3_uri):
    parsed_uri = urlparse(s3_uri)
    bucket_name = parsed_uri.netloc
    object_key = parsed_uri.path.lstrip('/')
    return (bucket_name, object_key)


def upload_file_to_s3(bucket: str, local_path, local_file):
    s3_client = boto3.client('s3')

    bda_s3_input_location = f's3://{bucket}/bda/input'
    bda_s3_output_location = f's3://{bucket}/bda/output'

    local_download_path = 'data/documents'
    local_file_name = 'claims-pack.pdf'
    local_file_path = os.path.join(local_path, local_file)
    #(bucket, key) = utils.get_bucket_and_key(document_url)
    #response = s3_client.download_file(bucket, key, local_file_path)

    document_s3_uri = f'{bda_s3_input_location}/{local_file}'

    target_s3_bucket, target_s3_key =  get_bucket_and_key(document_s3_uri)
    s3_client.upload_file(local_file_path, target_s3_bucket, target_s3_key)

    print(f"Downloaded file to: {local_file_path}")
    print(f"Uploaded file to S3: {target_s3_key}")
    print(f"document_s3_uri: {document_s3_uri}")
    
    
def s3_bucket_exists(s3_client, bucket_name):
    """
    Checks if an S3 bucket exists and is accessible.
    """
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        # The bucket does not exist or you have no access.
        error_code = int(e.response['Error']['Code'])
        if error_code == 403:
            print(f"Private Bucket: Access Forbidden for '{bucket_name}'")
            return False
        elif error_code == 404:
            print(f"Bucket Does Not Exist: '{bucket_name}'")
            return False
        else:
            print(f"An unexpected error occurred: {e}")
            return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
    return True