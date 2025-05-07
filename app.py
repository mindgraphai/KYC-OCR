from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
import os

from image_processing import encode_image, get_image_analysis, process_response

# Constants
TEMP_IMAGE_PATH = 'temp_image.jpg'
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

# Initialize Flask app
app = Flask(__name__)
api = Api(app)

# Swagger UI setup
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "GPT-4 Vision Image Processing"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

class ImageProcessor(Resource):
    """
    API endpoint that receives an image, processes it, and returns structured analysis.
    """
    def post(self):
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400

        image_file = request.files['image']
        image_file.save(TEMP_IMAGE_PATH)

        try:
            encoded_image = encode_image(TEMP_IMAGE_PATH)
            openai_response = get_image_analysis(encoded_image)
            result = process_response(openai_response)
            return jsonify(result)

        except Exception as e:
            return jsonify({"error": f"Image processing failed: {str(e)}"}), 500

        finally:
            if os.path.exists(TEMP_IMAGE_PATH):
                os.remove(TEMP_IMAGE_PATH)

# Register API endpoint
api.add_resource(ImageProcessor, '/process_image')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
