import zipfile

def zip_lambda_function_file(file_to_zip, zip_archive_name):
    ''' Open the new ZIP file in write mode ('w') and use 
        'with' to ensure it closes automatically 
    '''
    with zipfile.ZipFile(zip_archive_name, mode="w") as archive:
        # Add the file to the archive
        archive.write(file_to_zip)
        return zip_archive_name

def create_lambda_function(lambda_client, lambda_role_arn, func_name, file_path, func_file):
    try:
        with open(file_path, 'rb') as zip_file:
            zip_file_content = zip_file.read()

        response = lambda_client.create_function(
            FunctionName=func_name,
            Runtime='python3.9', # Choose the latest supported Python runtime
            Role=lambda_role_arn,
            Handler=f'{func_file}.lambda_handler',
            Code={
                'ZipFile': zip_file_content
            },
            Description='BookShop Lambda Function',
            Timeout=30,
            MemorySize=256
            #Environment={'Variables': {'DYNAMODB_TABLE': table_name}}
        )
        function_arn = response['FunctionArn']
        print(f"Lambda function {func_name} created with ARN: {function_arn}")
        return function_arn
    except Exception as e:
        print(f"Lambda function creation failed or already exists: {e}")
        # Logic to retrieve function ARN if it exists
        #function_arn = 'arn:aws:lambda:your-region:your-account-id:function:DynamoCRUDHandler'
    return None


def add_lambda_permission(function_name,
                          service_arn,
                          statement_id,
                          lambda_client,
                          principal_serivce):
    try:
        response = lambda_client.add_permission(
            FunctionName=function_name,
            StatementId=statement_id,
            Action="lambda:InvokeFunction",
            Principal=principal_serivce,
            SourceArn=service_arn
        )
        print(f"Permission added successfully: {response['Statement']}")
    except Exception as e:
        print(f"Error adding permission: {e}")