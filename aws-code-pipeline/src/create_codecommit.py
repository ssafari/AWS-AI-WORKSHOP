import boto3

codecommit = boto3.client('codecommit', region_name='your_region')

response = codecommit.create_repository(
    repositoryName='MyBoto3Repo',
    repositoryDescription='A repository created with Boto3'
)
print(f"Repository created: {response['repositoryMetadata']['repositoryCloneUrlHttp']}")

response = codecommit.batch_get_repositories(
    repositoryNames=['MyBoto3Repo']
)
print(f"Clone URL: {response['repositories'][0]['cloneUrlHttp']}")

