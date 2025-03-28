from fastapi import FastAPI, HTTPException
import boto3
import json
import uvicorn

# Crear la API
api = FastAPI()

# Configurar AWS Lambda en LocalStack
LAMBDA_NAME = "LambdaS3Stack-lambdafunction45C982D3-1b295e1f"
LOCALSTACK_ENDPOINT = "http://localhost:4566"

lambda_client = boto3.client("lambda", region_name="us-east-1", endpoint_url=LOCALSTACK_ENDPOINT)

@api.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}

@api.post("/log/{service_name}")
async def log_event(service_name: str, log_data: dict):
    """ Invoca la Lambda con los logs """
    try:
        payload = {
            "body": json.dumps(log_data),
            "pathParameters": {"service_name": service_name}
        }

        response = lambda_client.invoke(
            FunctionName=LAMBDA_NAME,
            Payload=json.dumps(payload)
        )

        response_payload = json.loads(response["Payload"].read().decode("utf-8"))

        if response_payload.get("statusCode") != 200:
            raise HTTPException(status_code=500, detail=response_payload["body"])

        return json.loads(response_payload["body"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(api, host="localhost", port=8000)