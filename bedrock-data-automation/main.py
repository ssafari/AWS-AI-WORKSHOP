import boto3
from utils import s3_helpers, bedrock_apis

def main():
    ''' BDA Practice'''
    print("Start Bedrock Data Automation")
    # 1. Upload files into S3 buckets
    region = 'us-east-1'
    bucket_name = 'bdfpro-dev'
    directory = 'health'
    aws_service = 'bedrock.amazonaws.com'
    iam_role='Bedrock-Finetuning-Role'
    s3_client = boto3.client('s3', region_name=region)
    if not s3_helpers.s3_bucket_exists(s3_client, bucket_name):
        s3_helpers.create_s3_bucket(s3_client, bucket_name, region)
    s3_helpers.create_s3_directory(s3_client, bucket_name, directory)

    role_arn = s3_helpers.add_s3_iam_role_policy(bucket_name, aws_service, iam_role)
    if role_arn is not None:
        bedrock_apis.bedrock_create_kb(name, role_arn, embedding_model_arn)

    # Initialize Bedrock Data Automation clients
    #bda_client = boto3.client('bedrock-data-automation')
    #bda_runtime_client = boto3.client('bedrock-data-automation-runtime')

    # 2. Create BDA project
    # 3. Create BDA project output blueprint
    #blueprint_schema = doc_helpers.read_json_file("hh")
    #blueprints = doc_helpers.read_json_file("")
    # response = bda_helpers.create_or_update_blueprint(
    #     bda_client,
    #     blueprint_name=blueprints[0]["name"],
    #     blueprint_description= blueprints[0]["description"],
    #     blueprint_type=blueprints[0]["type"],
    #     blueprint_stage=blueprints[0]["stage"],
    #     blueprint_schema=blueprint_schema)



if __name__ == "__main__":
    main()
