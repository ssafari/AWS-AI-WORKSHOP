''' 
    Create a Lambda function and upload the 
    code that handles the CRUD operations.
'''
import boto3


# Define some functions to perform the CRUD operations
def create(payload, dynamo):
    return dynamo.put_item(Item=payload['Item'])

def read(payload, dynamo):
    return dynamo.get_item(Key=payload['Key'])

def update(payload, dynamo):
    return dynamo.update_item(**{k: payload[k] for k in ['Key', 'UpdateExpression', 
    'ExpressionAttributeNames', 'ExpressionAttributeValues'] if k in payload})

def delete(payload, dynamo):
    return dynamo.delete_item(Key=payload['Key'])

operations = {
    'POST': create,
    'GET': read,
    'PUT': update,
    'DELETE': delete
}

def lambda_handler(event, context):
    ''' define the lanbda function '''
    dynamodb = boto3.resource('dynamodb')
    operation = event['operation']
    payload = event['payload']
    if operation in operations:
        return operations[operation](payload, dynamodb)
    raise ValueError(f'Unrecognized operation "{operation}"')
