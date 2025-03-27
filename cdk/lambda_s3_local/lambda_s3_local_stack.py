from aws_cdk import Stack, RemovalPolicy
from constructs import Construct
import aws_cdk.aws_lambda as _lambda
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_iam as iam

class LambdaS3Stack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Crear el bucket de logs en S3
        logs_bucket = s3.Bucket(self, "LogsBucket",
                                bucket_name="logs-bucket",
                                removal_policy=RemovalPolicy.DESTROY)

        # Crear la función Lambda
        lambda_function = _lambda.Function(self, "LogIngestLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda_s3_local/lambda_code"),
            environment={
                "S3_BUCKET": logs_bucket.bucket_name
            }
        )

        # Permitir que Lambda escriba en S3
        logs_bucket.grant_write(lambda_function)

        # Agregar permisos explícitos a Lambda
        lambda_function.add_to_role_policy(iam.PolicyStatement(
            actions=["s3:PutObject"],
            resources=[logs_bucket.arn_for_objects("logs/*")]
        ))