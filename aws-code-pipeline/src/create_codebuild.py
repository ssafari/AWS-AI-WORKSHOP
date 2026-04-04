import boto3
import json

client = boto3.client('codebuild', region_name='us-east-1')

# You would need an IAM role ARN with CodeBuild permissions
codebuild_service_role_arn = 'arn:aws:iam::123456789012:role/CodeBuildServiceRole'


response = client.create_project(
    name='MyBoto3BuildProject',
    description='A build project created with Boto3',
    serviceRole=codebuild_service_role_arn,
    source={
        'type': 'CODECOMMIT',
        'location': 'https://git-codecommit.your_region://', # Use the clone URL from CodeCommit
        'buildspec': 'buildspec.yaml' # The buildspec file should be in your repo
        # 'type': 'S3', # or 'GITHUB', 'CODECOMMIT', etc.
        # 'location': 'my-source-bucket/source.zip', 
        # When used within CodePipeline, the location is ignored and handled by the pipeline source action.
    },
    artifacts={
        'type': 'S3',
        'location': 'my-artifact-bucket',
        'packaging': 'ZIP'
    },
    environment={
        'type': 'LINUX_CONTAINER',
        'image': 'aws/codebuild/standard:5.0', # Use an appropriate image
        'computeType': 'BUILD_GENERAL1_SMALL',
    }
)
print(f"Project created: {response['project']['name']}")

response = client.start_build(
    projectName='MyBoto3BuildProject',
    # You can override source version, environment variables, etc. here.
)
print(f"Build started with ID: {response['build']['id']}")

build_id = response['build']['id']
build_details = client.batch_get_builds(ids=[build_id])
print(f"Build status: {build_details['builds'][0]['buildStatus']}")
