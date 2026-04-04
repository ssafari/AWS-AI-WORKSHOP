# Use the native inference API to send a text message to Amazon Titan Text.
import boto3
import json
import datetime
from botocore.exceptions import ClientError

def bedrock_run():
    # Create a Bedrock Runtime client in the AWS Region of your choice.
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    # Set the model ID, e.g., Titan Text Premier.
    model_id = "amazon.titan-text-premier-v1:0"
    # Define the prompt for the model.
    prompt = "Describe the purpose of a 'hello world' program in one line."
    # Format the request payload using the model's native structure.
    native_request = {
        "inputText": prompt,
        "textGenerationConfig": {
        "maxTokenCount": 512,
        "temperature": 0.5,
        },
    }
    # Convert the native request to JSON.
    request = json.dumps(native_request)

    try:
        # Invoke the model with the request.
        response = client.invoke_model(modelId=model_id, body=request)
    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke '{model_id}'. Reason: {e}")
        exit(1)
    # Decode the response body.
    model_response = json.loads(response["body"].read())
    # Extract and print the response text.
    response_text = model_response["results"][0]["outputText"]
    print(response_text)


def bedrock_finetuning():
    bedrock = boto3.client(service_name='bedrock')
    account_id = boto3.client('sts').get_caller_identity()['Account']
    # Set parameters
    customModelName = "custom-tuned-model"
    baseModelIdentifier = "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-express-v1"
    # Create job
    datetime_string = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    response_ft = bedrock.create_model_customization_job(
        jobName=f"Finetune-Job-{datetime_string}",
        customizationType="FINE_TUNING",
        roleArn=f"arn:aws:iam::{account_id}:role/Bedrock-Finetuning-Role-{account_id}",
        hyperParameters = {
            "epochCount": "5",
            "batchSize": "1",
            "learningRate": ".0001",
            # "learningRateWarmupSteps": "5"
        },
        trainingDataConfig={"s3Uri": f"s3://bedrock-finetuning-{account_id}/train.jsonl"},
        outputDataConfig={"s3Uri": f"s3://bedrock-finetuning-{account_id}/finetuning-output"},
        validationDataConfig={'validators': [{'s3Uri': f's3://bedrock-finetuning-{account_id}/validation.jsonl'}]},
        customModelName=customModelName,
        baseModelIdentifier=baseModelIdentifier
    )
    jobArn = response_ft.get('jobArn')
    print(jobArn)


# The following is a workflow that sets up an S3 bucket and an Amazon 
# OpenSearch Serverless vector store managed by Amazon Bedrock
def bedrock_create_kb(name, role_arn, embedding_model_arn, s3_bucket_arn):
    """ 
      Creates an Amazon Bedrock Knowledge Base with an 
      auto-managed vector store. 
    """
    try:
        # Initialize clients
        bedrock_agent_client = boto3.client('bedrock-agent', region_name='us-east-1')
        response = bedrock_agent_client.create_knowledge_base(
            name=name,
            description="A knowledge base for demonstration purposes.",
            roleArn=role_arn,
            knowledgeBaseConfiguration={
                'type': 'VECTOR_CONTENT',
                'vectorKnowledgeBaseConfiguration': {
                    'embeddingModelArn': embedding_model_arn
                }
            },
            storageConfiguration={
                'type': 'OPENSEARCH_SERVERLESS',
                'opensearchServerlessConfiguration': {
                    # Let Bedrock create and manage the vector store for you
                    'collectionArn': '', # Can be empty if letting Bedrock manage
                    'vectorIndexName': 'bedrock-knowledge-base-index',
                    'fieldMapping': {
                        'vectorField': 'bedrock-vector',
                        'textField': 'bedrock-text',
                        'metadataField': 'bedrock-metadata'
                    }
                }
            }
        )
        kb_id = response['knowledgeBase']['knowledgeBaseId']
        print(f"Knowledge Base {name} created with ID: {kb_id}")
        return kb_id
    except Exception as e:
        print(f"Error creating knowledge base: {e}")
        return None


def bedrock_kb_data_source(kb_id, bucket_name):
    """Creates a data source for the knowledge base."""
    try:
        bedrock_agent_client = boto3.client('bedrock-agent', region_name='us-east-1')
        response = bedrock_agent_client.create_data_source(
            knowledgeBaseId=kb_id,
            name="S3DataSource",
            dataSourceConfiguration={
                'type': 'S3',
                's3Configuration': {
                    'bucketArn': f'arn:aws:s3:::{bucket_name}'
                }
            },
            vectorIngestionConfiguration={
                'chunkingConfiguration': {
                    'chunkingStrategy': 'FIXED_SIZE', # Other options available
                    'fixedSizeChunkingConfiguration': {
                        'maxTokens': 512,
                        'overlapTokens': 0
                    }
                }
            }
        )
        ds_id = response['dataSource']['dataSourceId']
        print(f"Data source created with ID: {ds_id}")
        return ds_id
    except Exception as e:
        print(f"Error creating data source: {e}")
        return None


# Runs an ingestion job to process the documents
# in S3 bucket and populate the vector store.
def bedrock_start_kb_job(kb_id, ds_id):
    """ Starts an ingestion job for the data source. """
    try:
        # Initialize clients
        bedrock_agent_client = boto3.client('bedrock-agent', region_name='us-east-1')
        response = bedrock_agent_client.start_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=ds_id
        )
        job_id = response['ingestionJob']['ingestionJobId']
        print(f"Ingestion job {job_id} started. Status: {response['ingestionJob']['status']}")
        return job_id
    except Exception as e:
        print(f"Error starting ingestion job: {e}")
        return None


# implement RAG, handling the retrieval of relevant information from the
# data source and passing it to the Language Model (LLM) for a final answer.
def bedrock_generate_kb_response(kb_id, input_text, foundation_model):
    """
      Retrieves relevant information from the knowledge 
      base and generates a response.
    """
    bedrock_agent_runtime = boto3.client(
        service_name="bedrock-agent-runtime",
        region_name="us-east-1" # Use the region where your KB is created
    )
    response = bedrock_agent_runtime.retrieve_and_generate(
        input={
            'text': input_text
        },
        retrieveAndGenerateConfiguration={
            'type': 'KNOWLEDGE_BASE',
            'knowledgeBaseConfiguration': {
                'knowledgeBaseId': kb_id,
                'modelArn': f'arn:aws:bedrock:us-east-1::foundation-model/{foundation_model}'
            }
        }
    )
    # Extract the generated text response
    generated_text = response['output']['text']
    # You can also retrieve the sources/citations used
    citations = response['citations']
    return generated_text, citations



def bedrock_extract_kb_resp(sources):
    ''' '''
    if sources:
        print("Citations:")
        for citation in sources:
            # Check if retrievedReferences exists and has items
            if 'retrievedReferences' in citation:
                for reference in citation['retrievedReferences']:
                    if 'location' in reference and 's3Location' in reference['location']:
                        s3_uri = reference['location']['s3Location']['uri']
                        print(f"- Source location: {s3_uri}")
                    if 'content' in reference and 'text' in reference['content']:
                        print(f"  Content snippet: {reference['content']['text'][:200]}...") # Print first 200 chars
            else:
                print("- No detailed references available for this citation.")


# list all available, pre-built Amazon Bedrock foundation models 
# and filter for those that support the "EMBEDDING" use case
def bedrock_foundation_models():
    ''' Initialize the boto3 client for the bedrock service '''
    try:
        bedrock_client = boto3.client('bedrock', region_name='us-east-1')
        response = bedrock_client.list_foundation_models()

        embedding_models = []
        for model in response['modelSummaries']:
            if 'EMBEDDING' in model['inferenceTypes']:
                embedding_models.append({
                    'modelId': model['modelId'],
                    'modelArn': model['modelArn'],
                    'providerName': model['providerName']
                })

        print("Available Embedding Models:")
        for model in embedding_models:
            print(f"* Model ID: {model['modelId']}, ARN: {model['modelArn']}, Provider: {model['providerName']}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Using Amazon Nova foundation modle for 
# performing multimodal embeddings
def bedrock_multimodal_embeddings():
    



def main():
  bedrock_foundation_models()

if __name__ == "__main__":
    main()