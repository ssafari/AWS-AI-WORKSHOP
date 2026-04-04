import boto3
import json
from IPython.display import JSON, IFrame
import pandas as pd
from pathlib import Path
import os



session = sagemaker.Session()
default_bucket = session.default_bucket()
current_region = boto3.session.Session().region_name

sts_client = boto3.client('sts')
account_id = sts_client.get_caller_identity()['Account']

# Initialize Bedrock Data Automation client
bda_client = boto3.client('bedrock-data-automation')
bda_runtime_client = boto3.client('bedrock-data-automation-runtime')
s3_client = boto3.client('s3')

bda_s3_input_location = f's3://{default_bucket}/bda/input'
bda_s3_output_location = f's3://{default_bucket}/bda/output'

local_download_path = 'data/documents'
local_file_name = 'claims-pack.pdf'
local_file_path = os.path.join(local_download_path, local_file_name)
#(bucket, key) = utils.get_bucket_and_key(document_url)
#response = s3_client.download_file(bucket, key, local_file_path)

document_s3_uri = f'{bda_s3_input_location}/{local_file_name}'

target_s3_bucket, target_s3_key =  helper_functions.get_bucket_and_key(document_s3_uri)
s3_client.upload_file(local_file_path, target_s3_bucket, target_s3_key)

print(f"Downloaded file to: {local_file_path}")
print(f"Uploaded file to S3: {target_s3_key}")
print(f"document_s3_uri: {document_s3_uri}")

blueprints = [
    {
        "name": 'claim-form',
        "description": 'Blueprint for Medical Claim form CMS 1500',
        "type": 'DOCUMENT',
        "stage": 'LIVE',
        "schema_path": 'data/blueprints/claims_form.json'
    }
]
blueprint = blueprints[0]
with open(blueprint['schema_path']) as f:
    blueprint_schema = json.load(f)
    blueprint_arn = create_or_update_blueprint(
            bda_client, 
            blueprint['name'], 
            blueprint['description'], 
            blueprint['type'],
            blueprint['stage'],
            blueprint_schema
    )

bda_project_name = 'document-custom-output-multiple-blueprints'
bda_project_stage = 'LIVE'
standard_output_configuration = {
    'document': {
        'extraction': {
            'granularity': {'types': ['DOCUMENT', 'PAGE']},
            'boundingBox': {'state': 'ENABLED'}
        },
        'generativeField': {'state': 'ENABLED'},
        'outputFormat': {
            'textFormat': {'types': ['MARKDOWN']},
            'additionalFileFormat': {'state': 'ENABLED'}
        }
    }
}

custom_output_configuration = {
    "blueprints": [
        {
            'blueprintArn': f'arn:aws:bedrock:{current_region}:aws:blueprint/bedrock-data-automation-public-bank-statement',
            'blueprintStage': 'LIVE'
        },
        {
            'blueprintArn': f'arn:aws:bedrock:{current_region}:aws:blueprint/bedrock-data-automation-public-us-driver-license',
            'blueprintStage': 'LIVE'
        },
        {
            'blueprintArn': f'arn:aws:bedrock:{current_region}:aws:blueprint/bedrock-data-automation-public-invoice',
            'blueprintStage': 'LIVE'
        },
        {
            'blueprintArn': f'arn:aws:bedrock:{current_region}:aws:blueprint/bedrock-data-automation-public-prescription-label',
            'blueprintStage': 'LIVE'
        },
        {
            'blueprintArn': f'arn:aws:bedrock:{current_region}:aws:blueprint/bedrock-data-automation-public-us-medical-insurance-card',
            'blueprintStage': 'LIVE'
        }
    ]
}
custom_output_configuration['blueprints'] += [
    {
        'blueprintArn': blueprint_arn,
        'blueprintStage': 'LIVE'
    } for blueprint_arn in blueprint_arns
]

override_configuration={'document': {'splitter': {'state': 'ENABLED'}}}
JSON(custom_output_configuration["blueprints"], root="Blueprint list", expanded=True)