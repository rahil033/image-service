import json
from decimal import Decimal
from ..services.image_service import ImageService
from ..common.errors import NotFoundError, StorageError, DatabaseError

service = ImageService()

def lambda_handler(event, context):
    try:
        method = event.get("httpMethod")
        path = event.get("path")
        query = event.get("queryStringParameters") or {}
        body = json.loads(event.get("body") or "{}")

        if method == "POST":
            result = service.upload_image(
                user_id=body.get("user_id"),
                filename=body.get("filename"),
                image_data=body.get("image_data"),
                tags=body.get("tags"),
                description=body.get("description"),
                width=body.get("width"),
                height=body.get("height")
            )
            return response(200, result)

        elif method == "GET":
            if "image_id" in query:
                result = service.get_image(query["image_id"])
            else:
                result = service.list_images(
                    user_id=query.get("user_id"),
                    tags=query.get("tags"),
                    limit=int(query.get("limit", 50)),
                    last_key=query.get("last_key")
                )
            return response(200, result)

        elif method == "DELETE":
            image_id = query.get("image_id")
            result = service.delete_image(image_id)
            return response(200, result)

        return response(400, {"message": "Unsupported method"})

    except NotFoundError as e:
        return response(404, {"error": str(e)})

    except (StorageError, DatabaseError) as e:
        return response(500, {"error": str(e)})

    except Exception as e:
        return response(500, {"error": str(e)})


def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=decimal_default)
    }

