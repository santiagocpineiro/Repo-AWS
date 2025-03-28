import json
import boto3
import os
from datetime import datetime
import requests

s3_client = boto3.client("s3")
S3_BUCKET = os.getenv("S3_BUCKET", "logs-bucket")

def lambda_handler(event, context):
    try:
        # Extraer datos del evento (suponiendo que viene desde API Gateway)
        body = json.loads(event["body"])
        service_name = event["pathParameters"]["service_name"]

        # Formatear la fecha y construir la ruta en S3
        today = datetime.utcnow().strftime("%Y/%m/%d")
        file_path = f"logs/{service_name}/{today}/{datetime.utcnow().isoformat()}.json"

        # Guardar el log en S3
        s3_client.put_object(Bucket=S3_BUCKET, Key=file_path, Body=json.dumps(body))

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Log almacenado en S3", "file_path": file_path})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }