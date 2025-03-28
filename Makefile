### VARIABLES ###
CDK=npx aws-cdk-local
STACK_NAME=LambdaS3Stack
ENDPOINT=http://localhost:4566
BUCKET_NAME=logs-bucket
LAMBDA_NAME=LambdaS3Stack-lambdafunction45C982D3-2074fa7a

### CDK ###
bootstrap:
	cd cdk && $(CDK) bootstrap --app "python3 app.py"

synth:
	cd cdk && $(CDK) synth --app "python3 app.py"

deploy:
	cd cdk && $(CDK) deploy $(STACK_NAME) --require-approval never --app "python3 app.py"

destroy:
	$(CDK) destroy $(STACK_NAME) --force

### LOCALSTACK ###t
start-localstack:
	docker compose up -d

stop-localstack:
	docker compose down

### LAMBDA ###
invoke:
	awslocal lambda invoke \
		--function-name $(LAMBDA_NAME) \
		--payload '{ "body": "{\"filename\": \"archivo.txt\", \"content\": \"Desde Makefile!\"}", "pathParameters": {"service_name": "service1"} }' \
		response.json && cat response.json

list-bucket:
	awslocal s3 ls s3://$(BUCKET_NAME)

get-object:
	awslocal s3 ls s3://$(BUCKET_NAME)/logs/service1/2025/03/27/

clean:
	rm -f response.json

run-api:
	python3 api/api.py