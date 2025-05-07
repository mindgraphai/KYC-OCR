from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
import os
from image_processing import encode_image, get_image_analysis, process_response  # Import the image processing functions

app = Flask(__name__)
api = Api(app)

# Swagger UI setup
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'  # Path to Swagger JSON file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "GPT-4 Vision Image Processing"
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

class ImageProcessor(Resource):
    def post(self):
        """
        API endpoint that receives an image, processes it, and returns the relevant fields.
        """
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files['image']
        
        # Save the image temporarily
        temp_path = 'temp_image.jpg'
        image_file.save(temp_path)
        
        try:
            # Encode the uploaded image to base64
            encoded_image = encode_image(temp_path)

            # Perform image analysis with the base64-encoded image
            openai_response = get_image_analysis(encoded_image)

            # Process the OpenAI response and get the result
            result = process_response(openai_response)

            os.remove(temp_path)  # Clean up the temporary file
            
            # Return the analysis as JSON
            return jsonify(result)

        except Exception as e:
            os.remove(temp_path)
            return jsonify({"error": str(e)}), 500

api.add_resource(ImageProcessor, '/process_image')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
