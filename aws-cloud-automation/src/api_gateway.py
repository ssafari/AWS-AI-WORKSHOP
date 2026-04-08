import json
import os
import boto3


function_arn = 'arn:aws:lambda:<region>:<account-id>:function:DynamoDbCRUDHandler'

def create_api_gatway(apigateway_client, api_name, region):
    ''' Creates an api-gateway service and returns the rest-api-id '''
    try:
        # 1. Create a REST API
        # region = 'us-east-1'
        # api_name = 'DynamoDbCRUDAPI'
        # apigateway_client = boto3.client('apigateway')
        rest_api = apigateway_client.create_rest_api(
            name=api_name,
            description='CRUD API for DynamoDB via Lambda',
            version='1.0'
        )
        rest_api_id = rest_api['id']
        print(f"REST API {api_name} created with ID: {rest_api_id}")
        return rest_api_id
    except Exception as e:
        print(f"REST API creation failed or already exists: {e}")
    return None

def create_crud_api_resource(apigateway_client, rest_api_id, stage_name, region):
    ''' 
        Creates api-getway CRUD operation endpoint resources 
        for calling from https. Deployes api-gateway to AWS.
    '''
    try:
        # 2. Get the root resource ID
        root_resource_id = apigateway_client.get_resources(restApiId=rest_api_id)['items'][0]['id']

        # 3. Create a new resource, e.g., '/api/v1/books'
        api_resource = apigateway_client.create_resource(
            restApiId=rest_api_id,
            parentId=root_resource_id,
            pathPart='api/v1/books'
        )
        api_resource_id = api_resource['id']

        # 4. Create CRUD methods for the resource
        http_methods = ['GET', 'POST', 'PUT', 'DELETE']
        for idx, http_method in enumerate(http_methods):
            apigateway_client.put_method(
                restApiId=rest_api_id,
                resourceId=api_resource_id,
                httpMethod=http_method,
                authorizationType='NONE'
            )
            # 5. Set up the integration with the Lambda function
            apigateway_client.put_integration(
                restApiId=rest_api_id,
                resourceId=api_resource_id,
                httpMethod=http_method,
                type='AWS_PROXY',
                integrationHttpMethod='POST', # The backend Lambda function is invoked always POST
                uri=f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{function_arn}/invocations"
            )

        # 6. Create a deployment to a stage
        stage_name = 'prod'
        deployment = apigateway_client.create_deployment(
            restApiId=rest_api_id,
            stageName=stage_name
        )
        print(f"API deployed to stage {stage_name}. Invoke URL: {deployment['invokeUrl']}")
    except Exception as e:
        print(f"REST API creation failed or already exists: {e}")
        # Logic to retrieve API ID
        rest_api_id = rest_api_id

    

def invoke_api_gateway(client, api_id, stage, method, path):
    ''' 
        To invoke api-getway from local machine to test the
        setup of CRUD services operations.
    '''
    response = client.invoke_api(
        apiId=api_id,
        stageName=stage,
        httpMethod=method,
        path=path
    )
    print(response['body'].read().decode('utf-8'))
