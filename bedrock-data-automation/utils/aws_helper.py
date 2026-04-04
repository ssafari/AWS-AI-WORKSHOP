import os
import json
import boto3


def create_iam_user():
    # Replace with name for your IAM user
    username = "bedrock-api-user"
    # Add any AWS-managed or custom policies that you want to the user
    bedrock_policies = [
        "arn:aws:iam::aws:policy/AmazonBedrockLimitedAccess", # Limited access
        # "arn:aws:iam::aws:policy/AmazonBedrockMarketplaceAccess", # Optional: Access to Amazon Bedrock Marketplace actions
    ]
    # Set the key expiration time to a number of your choice
    expiration_time_in_days = 30
    iam_client = boto3.client("iam")
    # Create IAM user
    user = iam_client.create_iam_user(username)
    # Attach policies to user
    for policy_arn in bedrock_policies:
        iam_client.attach_managed_policy(username, policy_arn)
    # Create long-term Amazon Bedrock API key and return it
    service_credentials = iam_client.create_service_specific_credential(
        user_name=username,
        service_name="bedrock",
        credential_age_days=expiration_time_in_days
    )
    api_key = service_credentials["ServiceApiKeyValue"]
    os.environ['AWS_BEARER_TOKEN_BEDROCK'] = f"{api_key}"


def create_iam_role(role_policy, policy_doc, role_name, policy_name, role_desc):
    iam_client = boto3.client('iam')

    # role_name = "LambdaDynamoDBAPIGatewayAccess" 
    # role_description = "IAM role for Lambda function to access DynamoDB and API Gateway"
    # role_policy = {
    #     "Version": "2012-10-17",
    #     "Statement": [
    #         {
    #             "Effect": "Allow",
    #             "Principal": {
    #                 "Service": "lambda.amazonaws.com"
    #             },
    #             "Action": "sts:AssumeRole"
    #         }
    #     ]
    # }
    response = iam_client.create_role(
        RoleName=role_name,
        Description=role_desc,
        AssumeRolePolicyDocument=json.dumps(role_policy)
    )
    role_arn = response['Role']['Arn']

    # Attach the DynamoDB permission policy
    policy_arn_dynamodb = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
    response_attach_dynamodb = iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=policy_arn_dynamodb
    )
    # Create a policy to allow API Gateway to invoke Lambda functions
    policy_name_apigateway = "APIGatewayInvokeLambdaPolicy"
    policy_document_apigateway = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": "lambda:InvokeFunction",
                "Resource": "*"
            }
        ]
    }
    response_create_policy = iam_client.create_policy(
        PolicyName=policy_name_apigateway,
        PolicyDocument=json.dumps(policy_document_apigateway)
    )
    
    # Attach the API Gateway invoke policy to the role
    iam_client.attach_role_policy(
        RoleName=role_name,
        PolicyArn=response_create_policy['Policy']['Arn']
    )

    print("IAM role created and policies attached:")
    print("Role ARN:", role_arn)
    return role_arn, role_name


# AWS managed service cannot access user private data directly;
# it must assume a role with specific s3:GetObject and s3:PutObject
# permissions to read input data or save model outputs.
# The IAM role serves as the mechanism for aws service to authenticate 
# with S3 securely.
def add_aws_iam_role_policy(bucket_name, service_name, role):
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