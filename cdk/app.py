#!/usr/bin/env python3
import aws_cdk as cdk
from lambda_s3_local.lambda_s3_local_stack import LambdaS3Stack

app = cdk.App()

LambdaS3Stack(app, "LambdaS3Stack",
    env=cdk.Environment(account="000000000000", region="us-east-1")
)

app.synth()