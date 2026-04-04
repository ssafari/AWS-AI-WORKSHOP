import boto3
import json

iam_client = boto3.client('iam')


# IAM policy that grants DynamoDB and CloudWatch access
policy_document = {
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
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Scan",
                "dynamodb:Query"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/*"
        }
    ]
}

# Create IAM role
try:
    lambda_role = iam_client.create_role(
        RoleName='LambdaDynamoDBRole',
        AssumeRolePolicyDocument=json.dumps({
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
        }),
        Description='Role for Lambda to access DynamoDB'
    )
    # Attach policy
    iam_client.put_role_policy(
        RoleName='LambdaDynamoDBRole',
        PolicyName='LambdaDynamoDBPolicy',
        PolicyDocument=json.dumps(policy_document)
    )
    lambda_role_arn = lambda_role['Role']['Arn']
except Exception as e:
    print(f"Role creation failed or already exists: {e}")
    # You would need logic to retrieve the existing role ARN here if it exists.
    lambda_role_arn = 'arn:aws:iam::your-account-id:role/LambdaDynamoDBRole'
