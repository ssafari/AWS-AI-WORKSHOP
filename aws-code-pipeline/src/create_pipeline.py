''' CodePipeline using a Boto3 client for the codepipeline service '''
import json
import boto3


def create_pipeline(client, codepipeline_service_role_arn, artifact_store_bucket, provider='CodeCommit'):
    # You would need an IAM role ARN for CodePipeline
    # codepipeline_service_role_arn = 'arn:aws:iam::123456789012:role/CodePipelineServiceRole'
    # And an S3 bucket for artifacts
    # artifact_store_bucket = 'your-codepipeline-artifact-bucket'


    pipeline_structure = {
        'name': 'YourNewPipelineName',
        'roleArn': codepipeline_service_role_arn,
        'artifactStore': {
            'type': 'S3',
            'location': artifact_store_bucket
        },
        'stages': [
            {
                'name': 'Source',
                'actions': [
                    {
                        'name': 'SourceAction',
                        'actionTypeId': {
                            'category': 'Source',
                            'owner': 'AWS',
                            'provider': provider,
                            'version': '1'
                        },
                        'configuration': {
                            'RepositoryName': 'MyBoto3Repo',
                            'BranchName': 'main'
                        },
                        'outputArtifacts': [
                            {
                                'name': 'SourceArtifact'
                            }
                        ],
                        'runOrder': 1
                    }
                    # {
                    #     'name': 'SourceAction',
                    #     'actionProvider': 'S3', # or 'GitHub', 'CodeCommit'
                    #     'configuration': {
                    #         'S3Bucket': 'my-source-bucket',
                    #         'S3ObjectKey': 'source.zip'
                    #         # Other specific configurations depending on provider
                    #     },
                    #     'outputArtifacts': [{'name': 'SourceArtifact'}],
                    #     'runOrder': 1,
                    #     'connectorProvider': 'S3', # This might be required for some providers
                    #     'version': '1',
                    # },
                ]
            },
            {
                'name': 'Build',
                'actions': [
                    {
                        'name': 'BuildAction',
                        'actionTypeId': {
                            'category': 'Build',
                            'owner': 'AWS',
                            'provider': 'CodeBuild',
                            'version': '1'
                        },
                        'configuration': {
                            'ProjectName': 'MyBoto3BuildProject'
                        },
                        'inputArtifacts': [{'name': 'SourceArtifact'}],
                        'outputArtifacts': [{'name': 'BuildArtifact'}],
                        'runOrder': 1
                    },
                    # {
                    #     'name': 'BuildAction',
                    #     'actionProvider': 'CodeBuild',
                    #     'configuration': {
                    #         'ProjectName': 'MyBoto3BuildProject' # Name of the CodeBuild project created above
                    #     },
                    #     'inputArtifacts': [{'name': 'SourceArtifact'}],
                    #     'outputArtifacts': [{'name': 'BuildArtifact'}],
                    #     'runOrder': 1,
                    #     'version': '1',
                    # },
                ]
            }
            # ... additional stages (e.g., Deploy)
        ],
        'version': 1
    }



    # Create a Boto3 session (optional, Boto3 uses default credentials/region automatically)
    # session = boto3.Session(region_name='us-east-1')

    # Create the CodePipeline client
    client = boto3.client('codepipeline', region_name='us-east-1')

    response = client.create_pipeline(
        pipeline=pipeline_structure
    )
    print(f"Pipeline created: {response['pipeline']['name']}")


    try:
        response = client.start_pipeline_execution(
            name='YourPipelineName'
        )
        print(f"Pipeline execution started with execution ID: {response['pipelineExecutionId']}")
    except client.exceptions.PipelineNotFoundException:
        print("Pipeline not found.")
    except Exception as e:
        print(f"An error occurred: {e}")