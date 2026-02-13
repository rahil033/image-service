# Image Service

A simple serverless image management service built with Python 3.12, AWS Lambda, S3, and DynamoDB.

## Features

- **Upload Images** - Upload images with metadata (tags, description, dimensions)
- **List Images** - Get images with filters (user_id, tags)
- **View/Download** - Get presigned URLs for viewing or downloading
- **Delete Images** - Remove images and metadata

## Architecture

```
API Gateway → Lambda → S3 + DynamoDB
```

**Components:**
- **Lambda Functions**: 4 handlers (upload, list, view, delete)
- **S3**: Image storage
- **DynamoDB**: Metadata storage

## Project Structure

```
image-service/
├── src/
│   ├── common/          # Config, logger, errors, utils
│   ├── models/          # ImageMetadata, APIResponse
│   ├── repositories/    # S3 and DynamoDB access
│   ├── services/        # Business logic
│   └── handlers/        # Lambda handlers
├── tests/               # Unit tests
│   ├── base_test.py
│   ├── test_upload_image.py
│   ├── test_list_images.py
│   ├── test_view_image.py
│   └── test_delete_image.py
├── requirements.txt
└── README.md
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_upload_image.py -v
```

**Test Results:** ✅ 14 tests passing

## API Endpoints

### Upload Image
```
POST /images
{
  "user_id": "user123",
  "filename": "photo.jpg",
  "image_data": "base64_encoded_data",
  "tags": "vacation,beach",
  "description": "Summer photo"
}
```

### List Images
```
GET /images?user_id=user123&tags=vacation&limit=20
```

### View/Download Image
```
GET /images/{image_id}?download=true&expires_in=3600
```

### Delete Image
```
DELETE /images/{image_id}
```

## Environment Variables

Set these when deploying to AWS:

```bash
BUCKET_NAME=your-s3-bucket-name
TABLE_NAME=your-dynamodb-table-name
AWS_DEFAULT_REGION=us-east-1
MAX_IMAGE_SIZE=10485760  # 10MB
```

## Deployment

1. Create S3 bucket and DynamoDB table in AWS
2. Package Lambda functions with dependencies
3. Deploy to AWS Lambda
4. Configure API Gateway routes
5. Set environment variables

## LocalStack Development Environment

This project uses [LocalStack](https://localstack.cloud/) for local AWS service emulation.

### Quick Start

1. **Start LocalStack**

   ```sh
   docker-compose up -d
   ```

   This will start LocalStack with S3 enabled. You can add more AWS services in `docker-compose.yml` as needed.

2. **(Optional) Configure AWS CLI for LocalStack**

   Install AWS CLI if you haven't:
   ```sh
   brew install awscli
   ```

   Configure AWS CLI to use LocalStack:
   ```sh
   aws configure --profile localstack
   # Use dummy values for AWS Access Key/Secret
   # Set region to us-east-1 or your preferred region
   ```

   Example S3 command:
   ```sh
   aws --endpoint-url=http://localhost:4566 --profile localstack s3 ls
   ```

## Local Deployment with LocalStack and Flask

To run the application locally with LocalStack:

1. **Start LocalStack**

```sh
docker-compose up -d
```

2. **Set environment variables**

```sh
export USE_LOCALSTACK=1
export AWS_DEFAULT_REGION=us-east-1
export BUCKET_NAME=your-s3-bucket-name
export TABLE_NAME=your-dynamodb-table-name
```

3. **Create S3 bucket and DynamoDB table in LocalStack (if not already created)**

```sh
aws --endpoint-url=http://localhost:4566 s3 mb s3://$BUCKET_NAME
aws --endpoint-url=http://localhost:4566 dynamodb create-table \
  --table-name $TABLE_NAME \
  --attribute-definitions AttributeName=image_id,AttributeType=S \
  --key-schema AttributeName=image_id,KeyType=HASH \
  --billing-mode PAYPER_REQUEST
```

4. **Install dependencies**

```sh
pip install -r requirements.txt
pip install flask
```

5. **Run the Flask app**

```sh
python main.py
```

The API will be available at: http://localhost:8000

You can use curl or Postman to test the endpoints:

```sh
curl -X POST "http://localhost:8000/images" -F "user_id=user123" -F "filename=photo.jpg" -F "image_data=@/path/to/photo.jpg" -F "tags=vacation,beach" -F "description=Summer photo"
curl "http://localhost:8000/images?user_id=user123"
```

### References
- [How to use LocalStack with Docker Compose](https://docs.localstack.cloud/references/docker-compose/)
- [How to use AWS CLI with LocalStack](https://docs.localstack.cloud/user-guide/aws-cli/)
- [What is LocalStack?](https://localstack.cloud/)

## Technology Stack

- **Python 3.12**
- **AWS Lambda** (serverless compute)
- **Amazon S3** (image storage)
- **DynamoDB** (metadata)
- **API Gateway** (REST API)
- **boto3** (AWS SDK)

## Code Structure

**Layered architecture:**
- `handlers/` - API entry points
- `services/` - Business logic
- `repositories/` - Data access (S3, DynamoDB)
- `models/` - Data structures
- `common/` - Shared utilities

**Simple, readable code:**
- No type hints
- Brief docstrings
- Clean functions
- Easy to understand
