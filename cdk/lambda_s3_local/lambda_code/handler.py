import boto3
import request
import os
import json
import traceback
import FastAPI, Request
import datetime
import BotoCoreError, ClientError
import Mangum  # Permite correr FastAPI en AWS Lambda


def main(event, context):
    try:
        app = FastAPI()
        # Configuración de S3 en LocalStack o AWS
        endpoint_url = os.getenv("LOCALSTACK_ENDPOINT", "http://localhost:4566")
        s3_client = boto3.client('s3', endpoint_url=endpoint_url)
        bucket_name = os.getenv("BUCKET_NAME", "my-local-bucket")

        @app.post("/logs/{service_name}")
        async def ingest_logs(service_name: str, request: Request):
            try:
                log_data = await request.json()
                date_str = datetime.now().strftime('%Y/%m/%d')
                s3_key = f"{date_str}/{service_name}/log_{datetime.now().isoformat()}.json"

                s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=json.dumps(log_data))
                return {"message": "Log stored successfully", "s3_key": s3_key}
            except (BotoCoreError, ClientError) as e:
                return {"error": f"Failed to store log: {str(e)}"}

        @app.post("/upload")
        async def upload_file(request: Request):
            try:
                body = await request.json()
                filename = body.get("filename", "archivo.txt")
                content = body.get("content", "Contenido por defecto")

                tmp_path = f"/tmp/{filename}"
                with open(tmp_path, "w") as f:
                    f.write(content)

                s3_client.upload_file(tmp_path, bucket_name, filename)
                return {"message": f"{filename} subido correctamente a {bucket_name}"}

            except (BotoCoreError, ClientError) as e:
                return {"error": f"Error al subir a S3: {str(e)}"}

        # Definir el handler para Lambda
        handler = Mangum(app)

    except Exception as e:
        print("[ERROR]", str(e))
        traceback.print_exc()
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }


