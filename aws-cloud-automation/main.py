''' 
    Performs deployment of a simple crud operation by creating 
    an API Gateway, a Lambda Function and a DynamoDB for storage.
'''
import boto3
from src.api_gateway import create_api_gatway, create_crud_api_resource
from src.lambda_api import create_lambda_function, zip_lambda_function_file, add_lambda_permission
from utils_helper_apis.aws_helper import add_aws_iam_role_and_policy



lambda_iam_role = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}

lambda_policy_role = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::<bucket-name>",
                "arn:aws:s3:::<bucket-name>/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:GetItem"
            ],
            "Resource": "arn:aws:dynamodb:<aws-region>:<aws-account-id>:table/<table-name>"
        }
    ]
}

def main():
    ''' 
        Starts preparing services for performing crud operations, such
        as API Gateway, a Lambda Function and a DynamoDB for storage.
        1. Add role for using lambda function and policy to use DynamoDB.
        2. Create the by using the zip file of the file containing 
           the function.
        3. Create the api-gateway for providing the http end points.
        4. Add the permission for api-gateway to invoke the lambda func.
    '''
    print("This is an example of AWS Cloud Automation")

    region = 'us-east-1'
    api_gw_name = 'api-gateway-crud'               # Name of api-gateway appears on AWS console.
    lambda_function_name = 'DynamoDbCrudHandler'   # Name of lambda func. appears on AWS console.
    

    # 1. Add the lambda function role
    lambda_role_arn = add_aws_iam_role_and_policy(lambda_iam_role, 
                                                  lambda_policy_role, 
                                                  'lambda_iam_role', 
                                                  'lambda_iam_role_policy')
    if lambda_role_arn is not None:
        
        client = boto3.client('lambda', region_name='us-east-1')
        zip_file = zip_lambda_function_file("rest_api_proxy.py",
                                            "lambda_function.zip")

        # 2. creat the lambda function
        create_lambda_function(lambda_client=client,
                               lambda_role_arn=lambda_role_arn,
                               func_name=lambda_function_name,
                               file_path=zip_file,
                               func_file='lambda_function')

        # 3. create the api-gateway
        apigateway_client = boto3.client('apigateway')
        api_id = create_api_gatway(apigateway_client=apigateway_client,
                                   api_name=api_gw_name,
                                   region=region)

        #4. Add permissions for API-Gateway to be able to call lambda func.
        account_id = boto3.client('sts').get_caller_identity()['Account']
        api_gateway_arn = f"arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*/*"
        add_lambda_permission(function_name=lambda_function_name,
                              service_arn=api_gateway_arn,
                              statement_id='apigateway-access',
                              lambda_client=client,
                              principal_serivce="apigateway.amazonaws.com")
        
        create_crud_api_resource(apigateway_client, api_id, 'prod', region)

    
    #4. add api permissions
    #5. deploy to AWS


if __name__ == '__main__':
    main()