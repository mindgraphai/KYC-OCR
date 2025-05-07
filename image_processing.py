import base64
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


def encode_image(image_path):
    """
    Encode an image file to a base64 string.
    
    :param image_path: Path to the image file
    :return: Base64-encoded image string
    """
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        raise RuntimeError(f"Failed to encode image: {str(e)}")


def get_image_analysis(encoded_image):
    """
    Send a base64-encoded image to OpenAI's GPT-4 Vision model for analysis.

    :param encoded_image: Base64-encoded image string
    :return: OpenAI API response object or error dict
    """
    base64_image_data = f"data:image/jpg;base64,{encoded_image}"

    try:
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Return JSON document with data. Only return JSON not other text"},
                        {"type": "image_url", "image_url": {"url": base64_image_data}},
                    ],
                }
            ],
            max_tokens=500,
        )
        return response
    except Exception as e:
        raise RuntimeError(f"Error during image analysis: {str(e)}")


def process_response(response):
    """
    Extract and parse the JSON content from the OpenAI API response.

    :param response: OpenAI API response object
    :return: Parsed dictionary or error dict
    """
    try:
        raw_content = response.choices[0].message.content
        json_string = raw_content.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(json_string)
    except Exception as e:
        return {"error": f"Failed to process response: {str(e)}"}
