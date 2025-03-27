from aws_cdk import Stack, Environment, aws_lambda as _lambda, aws_s3 as s3
from aws_cdk import Duration
from constructs import Construct
import os

class LambdaS3LocalStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket = s3.Bucket(self, "LocalBucket", bucket_name="my-local-bucket")

        lambda_fn = _lambda.Function(
            self, "SaveToS3Function",
            runtime=_lambda.Runtime.PYTHON_3_9,
            function_name="SaveToS3Function",
            handler="handler.main",
            code=_lambda.Code.from_asset("lambda_s3_local/lambda_code"),
            timeout=Duration.seconds(10),
            environment={
                "BUCKET_NAME": bucket.bucket_name,
                "LOCALSTACK_ENDPOINT": "http://172.29.47.152:4566"
            }
        )

        bucket.grant_put(lambda_fn)