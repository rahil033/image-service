"""
Entrypoint for the Image Service API using Flask.
"""
from flask import Flask, request, jsonify
from src.services.image_service import ImageService

app = Flask(__name__)
service = ImageService()

@app.route("/images", methods=["POST"])
def upload_image():
    try:
        user_id = request.form["user_id"]
        filename = request.form["filename"]
        image_file = request.files["image_data"]
        tags = request.form.get("tags", "")
        description = request.form.get("description", "")
        image_bytes = image_file.read()
        metadata = {
            "user_id": user_id,
            "filename": filename,
            "tags": tags,
            "description": description
        }
        image_id = service.upload_image(image_bytes, metadata)
        return jsonify({"image_id": image_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/images", methods=["GET"])
def list_images():
    try:
        user_id = request.args.get("user_id")
        tags = request.args.get("tags")
        limit = int(request.args.get("limit", 20))
        images = service.list_images(user_id=user_id, tags=tags, limit=limit)
        return jsonify(images)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/images/<image_id>", methods=["GET"])
def view_image(image_id):
    try:
        download = request.args.get("download", "false").lower() == "true"
        expires_in = int(request.args.get("expires_in", 3600))
        url = service.get_presigned_url(image_id, download, expires_in)
        return jsonify({"url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route("/images/<image_id>", methods=["DELETE"])
def delete_image(image_id):
    try:
        service.delete_image(image_id)
        return jsonify({"message": "Image deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
