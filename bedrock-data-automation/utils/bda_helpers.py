import os
import time
import boto3
from urllib.parse import urlparse
import requests
import base64
import io
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from botocore.exceptions import ClientError
from IPython.display import HTML
from IPython.display import display
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
import json
import ipywidgets as widgets
import pandas as pd


def invoke_blueprint_recommendation_async(bda_client, payload):
    credentials = boto3.Session().get_credentials().get_frozen_credentials()
    region_name = boto3.Session().region_name
    url = f"{bda_client.meta.endpoint_url}/invokeBlueprintRecommendationAsync"
    print(f'Sending request to {url}')
    result = send_request(
        region = region_name,
        url = url,
        method = "POST", 
        credentials = credentials,
        payload=payload
    )
    return result


def get_blueprint_recommendation(bda_client, job_id):
    credentials = boto3.Session().get_credentials().get_frozen_credentials()
    region_name = boto3.Session().region_name
    url = f"{bda_client.meta.endpoint_url}/getBlueprintRecommendation/{job_id}/"
    result = send_request(
        region = region_name,
        url = url,
        method = "POST",
        credentials = credentials        
    )
    return result

def create_or_update_blueprint(bda_client, blueprint_name, blueprint_description, blueprint_type, blueprint_stage, blueprint_schema):
    list_blueprints_response = bda_client.list_blueprints(
        blueprintStageFilter='ALL'
    )
    blueprint = next((blueprint for blueprint in
                      list_blueprints_response['blueprints']
                      if 'blueprintName' in blueprint and
                      blueprint['blueprintName'] == blueprint_name), None)

    if not blueprint:
        print(f'No existing blueprint found with name={blueprint_name}, creating custom blueprint')
        response = bda_client.create_blueprint(
            blueprintName=blueprint_name,
            type=blueprint_type,
            blueprintStage=blueprint_stage,
            schema=json.dumps(blueprint_schema)
        )
    else:
        print(f'Found existing blueprint with name={blueprint_name}, updating Stage and Schema')
        response = bda_client.update_blueprint(
            blueprintArn=blueprint['blueprintArn'],
            blueprintStage=blueprint_stage,
            schema=json.dumps(blueprint_schema)
        )

    return response['blueprint']['blueprintArn']
  