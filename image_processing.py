import base64
import cv2
import numpy as np
import json
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_object):
    """
    Encode an image_object (numpy array or bytes) to a base64 string.
    Args:
        image_object: Numpy array or bytes representing the image
    Returns:
        Base64-encoded string of the image
    """
    if isinstance(image_object, bytes):
        return base64.b64encode(image_object).decode('utf-8')
    return base64.b64encode(image_object.tobytes()).decode('utf-8')

def get_image_analysis(encoded_image):
    """
    Send a base64-encoded image to OpenAI's GPT-4 Vision model for analysis.
    Args:
        encoded_image: Base64-encoded image string
    Returns:
        OpenAI API response object or raises RuntimeError on error
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
    Args:
        response: OpenAI API response object
    Returns:
        Parsed dictionary if successful, or error dict if failed
    """
    try:
        raw_content = response.choices[0].message.content
        json_string = raw_content.strip().removeprefix("```json").removesuffix("```").strip()
        return json.loads(json_string)
    except Exception as e:
        return {"error": f"Failed to process response: {str(e)}"}
