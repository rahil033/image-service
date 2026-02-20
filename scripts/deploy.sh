#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-test}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-test}"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
export USE_LOCALSTACK="${USE_LOCALSTACK:-1}"

BUCKET_NAME="${BUCKET_NAME:-image-service-bucket}"
TABLE_NAME="${TABLE_NAME:-image-metadata}"
FUNCTION_NAME="${FUNCTION_NAME:-imageService}"
API_NAME="${API_NAME:-image-api}"
STAGE_NAME="${STAGE_NAME:-dev}"
HANDLER_NAME="${HANDLER_NAME:-src.handlers.image_handler.lambda_handler}"
LAMBDA_RUNTIME="${LAMBDA_RUNTIME:-python3.12}"
FUNCTION_ZIP="${FUNCTION_ZIP:-${ROOT_DIR}/function.zip}"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

ensure_bucket() {
  echo "Ensuring S3 bucket exists: ${BUCKET_NAME}"
  if ! awslocal s3api head-bucket --bucket "${BUCKET_NAME}" >/dev/null 2>&1; then
    awslocal s3api create-bucket --bucket "${BUCKET_NAME}" >/dev/null
  fi
}

ensure_table() {
  echo "Ensuring DynamoDB table exists: ${TABLE_NAME}"
  if ! awslocal dynamodb describe-table --table-name "${TABLE_NAME}" >/dev/null 2>&1; then
    awslocal dynamodb create-table \
      --table-name "${TABLE_NAME}" \
      --attribute-definitions AttributeName=image_id,AttributeType=S \
      --key-schema AttributeName=image_id,KeyType=HASH \
      --billing-mode PAY_PER_REQUEST >/dev/null
  fi
}

package_lambda() {
  echo "Packaging Lambda artifact"
  rm -f "${FUNCTION_ZIP}"
  (
    cd "${ROOT_DIR}"
    zip -r "${FUNCTION_ZIP}" . \
      -x "*.git*" \
      -x "venv/*" \
      -x ".venv/*" \
      -x "__pycache__/*" \
      -x "tests/*" \
      -x "localstack/*" >/dev/null
  )
}

ensure_lambda() {
  echo "Ensuring Lambda function exists: ${FUNCTION_NAME}"
  if awslocal lambda get-function --function-name "${FUNCTION_NAME}" >/dev/null 2>&1; then
    awslocal lambda update-function-code \
      --function-name "${FUNCTION_NAME}" \
      --zip-file "fileb://${FUNCTION_ZIP}" >/dev/null

    awslocal lambda update-function-configuration \
      --function-name "${FUNCTION_NAME}" \
      --runtime "${LAMBDA_RUNTIME}" \
      --handler "${HANDLER_NAME}" \
      --environment "Variables={BUCKET_NAME=${BUCKET_NAME},TABLE_NAME=${TABLE_NAME},AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION},USE_LOCALSTACK=1}" >/dev/null
  else
    awslocal lambda create-function \
      --function-name "${FUNCTION_NAME}" \
      --runtime "${LAMBDA_RUNTIME}" \
      --handler "${HANDLER_NAME}" \
      --role arn:aws:iam::000000000000:role/lambda-role \
      --zip-file "fileb://${FUNCTION_ZIP}" \
      --environment "Variables={BUCKET_NAME=${BUCKET_NAME},TABLE_NAME=${TABLE_NAME},AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION},USE_LOCALSTACK=1}" >/dev/null
  fi
}

ensure_api() {
  echo "Ensuring API Gateway exists: ${API_NAME}"
  local api_id
  local root_id
  local resource_id
  local lambda_arn

  api_id="$(awslocal apigateway get-rest-apis --query "items[?name=='${API_NAME}'].id | [0]" --output text)"
  if [[ -z "${api_id}" || "${api_id}" == "None" ]]; then
    api_id="$(awslocal apigateway create-rest-api --name "${API_NAME}" --query 'id' --output text)"
  fi

  root_id="$(awslocal apigateway get-resources --rest-api-id "${api_id}" --query 'items[?path==`/`].id | [0]' --output text)"
  resource_id="$(awslocal apigateway get-resources --rest-api-id "${api_id}" --query "items[?pathPart=='images'].id | [0]" --output text)"

  if [[ -z "${resource_id}" || "${resource_id}" == "None" ]]; then
    resource_id="$(awslocal apigateway create-resource --rest-api-id "${api_id}" --parent-id "${root_id}" --path-part images --query 'id' --output text)"
  fi

  awslocal apigateway put-method \
    --rest-api-id "${api_id}" \
    --resource-id "${resource_id}" \
    --http-method ANY \
    --authorization-type NONE >/dev/null

  lambda_arn="arn:aws:lambda:${AWS_DEFAULT_REGION}:000000000000:function:${FUNCTION_NAME}"

  awslocal apigateway put-integration \
    --rest-api-id "${api_id}" \
    --resource-id "${resource_id}" \
    --http-method ANY \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:${AWS_DEFAULT_REGION}:lambda:path/2015-03-31/functions/${lambda_arn}/invocations" >/dev/null

  awslocal lambda add-permission \
    --function-name "${FUNCTION_NAME}" \
    --statement-id "apigateway-invoke-${api_id}" \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${AWS_DEFAULT_REGION}:000000000000:${api_id}/*/*/images" >/dev/null 2>&1 || true

  awslocal apigateway create-deployment \
    --rest-api-id "${api_id}" \
    --stage-name "${STAGE_NAME}" >/dev/null

  echo
  echo "Deployment complete"
  echo "API ID: ${api_id}"
  echo "Endpoint: http://localhost:4566/restapis/${api_id}/${STAGE_NAME}/_user_request_/images"
}

main() {
  require_cmd awslocal
  require_cmd zip

  ensure_bucket
  ensure_table
  package_lambda
  ensure_lambda
  ensure_api
}

main "$@"