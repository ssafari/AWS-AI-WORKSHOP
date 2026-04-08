''' 
    Create a Lambda function and upload the 
    code that handles the CRUD operations.
'''
import os
import json
import decimal
import boto3


# books_table = os.getenv('BOOKS_TABLE', None)
# dynamodb = boto3.resource('dynamodb')
# ddb_table = dynamodb.Table(books_table)


# JSON serializer fix,
def decimal_default_json(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

# Define some functions to perform the CRUD operations
def create(payload):
    return {
        'statusCode': 200,
        'body': payload,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

def read(payload):
    return {
        'statusCode': 200,
        'body': payload,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

def update(payload):
    return {
        'statusCode': 200,
        'body': payload,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

def delete(payload):
    return {
        'statusCode': 200,
        'body': payload,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

methods = {
    'POST': create,
    'GET': read,
    'PUT': update,
    'DELETE': delete
}

def lambda_handler(event, context):
    ''' define the lanbda function '''
    method = event['httpMethod']
    queryParams = event['queryStringParameters']
    pathParams = event['pathParameters']
    resource = event['resource']
    payload = {}
    if event['body'] is not None:
        payload = event['body']
    payload['method'] = method
    payload['resource'] = resource
    if pathParams is not None:
        payload['pathParams'] = pathParams
    if queryParams is not None:
        payload['queryParams'] = queryParams
    if method in methods:
        return methods[method](payload)
    raise ValueError(f'Unrecognized operation "{method}"')
