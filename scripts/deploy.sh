#!/bin/bash

set -e

export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export LOCALSTACK=http://localhost:4566

echo "Creating S3 bucket..."
awslocal s3api create-bucket \
    --bucket image-service-bucket || true

echo "Creating DynamoDB table..."
awslocal dynamodb create-table \
    --table-name image-metadata \
    --attribute-definitions \
        AttributeName=image_id,AttributeType=S \
    --key-schema \
        AttributeName=image_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST || true


echo "Packaging Lambda..."
zip -r function.zip . -x "*.git*" -x "venv/*" -x "__pycache__/*"

echo "Creating Lambda function..."
awslocal lambda create-function \
  --function-name imageService \
  --runtime python3.9 \
  --handler src.handlers.image_handler.lambda_handler \
  --role arn:aws:iam::000000000000:role/lambda-role \
  --zip-file fileb://function.zip || true

echo "Creating API Gateway..."
API_ID=$(awslocal apigateway create-rest-api \
  --name image-api \
  --query 'id' --output text)

ROOT_ID=$(awslocal apigateway get-resources \
  --rest-api-id $API_ID \
  --query 'items[0].id' --output text)

RESOURCE_ID=$(awslocal apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part images \
  --query 'id' --output text)

awslocal apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method ANY \
  --authorization-type NONE

awslocal apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method ANY \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:000000000000:function:imageService/invocations

awslocal apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name dev

echo ""
echo "Deployment complete for API Gateway with ID: $API_ID"
echo ""
echo "Endpoint:"
echo "http://localhost:4566/restapis/$API_ID/dev/_user_request_/images"
