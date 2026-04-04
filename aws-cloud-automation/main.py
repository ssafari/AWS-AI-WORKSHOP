import boto3
from src.lambda_api import create_lambda_function, zip_lambda_function_file, add_lambda_permission
from utils_helper_apis.aws_helper import add_aws_iam_role_and_policy
from src.api_gateway import create_api_gatway

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
    print("This is AWS Cloud Automation")

    region = 'us-east-1'
    api_name = 'DynamoCRUDAPI'
    apigateway_client = boto3.client('apigateway')

    #1. create the lambda function
    lambda_role_arn = add_aws_iam_role_and_policy(lambda_iam_role, 
                                                  lambda_policy_role, 
                                                  'lambda_iam_role', 
                                                  'lambda_iam_role_policy')
    if lambda_role_arn is not None:
        lambda_function_name = 'DynamodbCrudHandler'
        client = boto3.client('lambda', region_name='us-east-1')
        zip_file = zip_lambda_function_file("src/lambda_function.py",
                                            "lambda_function.zip")
        
        create_lambda_function(lambda_client=client,
                               lambda_role_arn=lambda_role_arn,
                               function_name="lambdaDynamodbCrud",
                               file_path=zip_file,
                               func_file='lambda_function')
        
        #3. create api-gateway
        api_id = create_api_gatway(apigateway_client=apigateway_client,
                                   api_name=api_name,
                                   region=region)
        
        #2. add lambda permissions for API-Gateway
        account_id = boto3.client('sts').get_caller_identity()['Account']
        api_gateway_arn = f"arn:aws:execute-api:{region}:{account_id}:{api_id}/*/*/*"
        add_lambda_permission(function_name=lambda_function_name, 
                              service_arn=api_gateway_arn,
                              statement_id='',
                              lambda_client=client,
                              principal_serivce="apigateway.amazonaws.com")

    
    #4. add api permissions
    #5. deploy to AWS


if __name__ == 'main':
    main()