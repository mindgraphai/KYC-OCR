import base64
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() 

# Global API key and client setup
api_key = os.getenv("OPENAI_API_KEY")  # Read the API key from the environment variable
client = OpenAI(api_key=api_key)  # Set OpenAI's API key globally



def encode_image(image_path):
    """
    Function to encode an image to base64 format.
    
    :param image_path: Path to the image to be encoded
    :return: Base64 encoded string of the image
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_response(response):
    """
    Process the response from GPT-4 Vision and save the result as a JSON file.
    
    :param response: The response from GPT-4 Vision API
    :param image_local: Path to the local image to use in naming the JSON file
    :return: Parsed JSON data
    """
    try:
        # Accessing the response using dot notation
        json_string = response.choices[0].message.content
        json_string = json_string.replace("```json\n", "").replace("\n```", "")
        json_data = json.loads(json_string)

        # Create a filename based on the local image file name (without extension)
        #filename_without_extension = os.path.splitext(os.path.basename(image_local))[0]
        #json_filename = f"{filename_without_extension}.json"

        # Save the JSON data to a file
        #json_filepath = os.path.join("./Data", json_filename)
        #with open(json_filepath, 'w') as file:
            #json.dump(json_data, file, indent=4)

        #print(f"JSON data saved to {json_filepath}")

        # Return the processed JSON data, which is a dictionary
        return json_data
    except Exception as e:
        return {"error": f"Failed to process response: {str(e)}"}

def get_image_analysis(encoded_image):
    """
    Function to send the image to OpenAI's GPT-4 Vision for analysis.
    
    :param encoded_image: Base64 encoded image string
    :param image_local: Path to the local image (used for naming output JSON file)
    :return: JSON response containing the relevant fields
    """
    # Ensure the image data is prefixed correctly
    base64_image_data = f"data:image/jpg;base64,{encoded_image}"

    try:
        response = client.chat.completions.create(
            model='gpt-4o',  # Ensure you are using the correct model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Return JSON document with data. Only return JSON not other text"},
                        {
                            "type": "image_url",
                            "image_url": {"url": base64_image_data}  # Passing the base64 image directly
                        }
                    ],
                }
            ],
            max_tokens=500,
        )

        # Process the response and save to a JSON file
        return response
    except Exception as e:
        return {"error": f"Error during analysis: {str(e)}"}
    