### VARIABLES ###
CDK=npx aws-cdk-local
STACK_NAME=LambdaS3Stack
ENDPOINT=http://localhost:4566
BUCKET_NAME=logs-bucket
LAMBDA_NAME=$(shell awslocal lambda list-functions --query "Functions[?contains(FunctionName, 'lambdafunction')].FunctionName" --output text)

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
	curl -s -X GET "http://localhost:8000/get-latest-log/$(service_name)" > log.json && \
	python -c "import json,sys; data=json.load(sys.stdin); print(json.dumps({'body': json.dumps(data), 'pathParameters': {'service_name': '$(service_name)'}}))" < log.json > request.json && \
	awslocal lambda invoke \
		--function-name $(LAMBDA_NAME) \
		--payload file://request.json \
		response.json && cat response.json

list-bucket:
	awslocal s3 ls s3://$(BUCKET_NAME)/

get-object:
	awslocal s3 ls s3://$(BUCKET_NAME)/logs/$(SERVICE)/$(DATE)/

clean:
	rm -f response.json

run-api:
	python3 api/api.py

run-glue:
	python3 simulate_glue.py