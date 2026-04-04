'''
Docstring for bda_client
'''
import boto3
import json
import time


# Initialize BDA client
bda_client = boto3.client('bedrock-data-automation', region_name='your_region')

# Define input/output S3 URIs and Project ARN
input_s3_uri = 's3://your_input_bucket/your_input_file.pdf'
output_s3_uri = 's3://your_output_bucket/output_folder/' # BDA will write the JSON here
# Use your specific project ARN or the public default one
project_arn = 'arn:aws:bedrock:your_region:your_account_id:data-automation-project/your_project_id'

# Invoke the data automation
response = bda_client.invoke_data_automation_async(
    inputConfiguration={
        's3InputConfiguration': {
            's3Uri': input_s3_uri
        }
    },
    outputConfiguration={
        's3OutputConfiguration': {
            's3Uri': output_s3_uri
        }
    },
    dataAutomationProjectArn=project_arn
)

job_id = response['jobId']
print(f"BDA job started with ID: {job_id}")

s3_client = boto3.client('s3', region_name='your_region')
bucket_name = 'your_output_bucket'
output_key = f'output_folder/output_file.json' # The exact key might vary, check documentation for naming convention

# Function to check job status (simplified)
def check_job_status(job_id):
    while True:
        status_response = bda_client.get_data_automation_job(jobId=job_id)
        status = status_response['status']
        print(f"Job status: {status}")
        if status in ['SUCCEEDED', 'FAILED']:
            return status
        time.sleep(10) # Wait before checking again

# After checking the status and ensuring success
check_job_status(job_id)

# Retrieve the JSON output from S3
try:
    s3_object = s3_client.get_object(Bucket=bucket_name, Key=output_key)
    json_output_bytes = s3_object['Body'].read()
    json_output_string = json_output_bytes.decode('utf-8')
    # Parse the JSON string into a Python dictionary
    bda_data = json.loads(json_output_string)
    print("Successfully parsed BDA JSON output.")
except Exception as e:
    print(f"Error retrieving or parsing S3 object: {e}")

# Example using direct dictionary access based on your blueprint schema
# Assume your blueprint defines fields like 'hospital_name', 'visit_details', etc.
try:
    hospital_name = bda_data['hospital_name']
    visit_details = bda_data['visit_details']
    print(f"Extracted Hospital Name: {hospital_name}")
    print(f"Extracted Visit Details: {visit_details}")
except KeyError as e:
    print(f"KeyError {e}")


blueprint_schema = """
{
  "type": "object",
  "properties": {
    "HospitalName": {
      "type": "string",
      "description": "Name of the hospital"
    },
    "PatientDetails": {
      "type": "object",
      "properties": {
        "FirstName": {"type": "string"},
        "LastName": {"type": "string"}
      }
    }
  }
}
"""

try:
    response = bda_client.create_blueprint(
        blueprintName='YourCustomBlueprintName',
        type='DOCUMENT', # Or IMAGE, AUDIO, VIDEO
        blueprintStage='DEVELOPMENT',
        schema=blueprint_schema
    )
    print(f"Blueprint created: {response['blueprintArn']}")
except Exception as e:
    print(f"Error creating blueprint (maybe it already exists, consider update_blueprint): {e}")
