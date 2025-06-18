from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import os
import uuid
from image_processing import encode_image, get_image_analysis, process_response
from celery_app import celery_app
from auth import get_api_key

# Constants
TEMP_IMAGE_PATH = 'temp_image.jpg'

# Initialize FastAPI app
app = FastAPI(
    title="GPT-4 Vision Image Processing",
    description="API for processing images using GPT-4 Vision model",
    version="1.0.0"
)

@celery_app.task(name='image_processing.process_image_task', 
                bind=True,
                max_retries=3,
                default_retry_delay=60)
def process_image_task(self, image_data: bytes):
    """
    Celery task to process an image using GPT-4 Vision model.
    """
    try:
        # Save the image data temporarily
        with open(TEMP_IMAGE_PATH, "wb") as buffer:
            buffer.write(image_data)

        # Process the image
        encoded_image = encode_image(TEMP_IMAGE_PATH)
        openai_response = get_image_analysis(encoded_image)
        result = process_response(openai_response)
        
        # Clean up the result after processing
        self.backend.delete(self.request.id)
        
        return result

    except Exception as e:
        # If task fails, retry up to 3 times
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {"error": f"Image processing failed after 3 retries: {str(e)}"}

    finally:
        if os.path.exists(TEMP_IMAGE_PATH):
            os.remove(TEMP_IMAGE_PATH)

@app.post("/read_text")
async def process_image(
    image: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    """
    Queue an image for processing using GPT-4 Vision model.
    Returns a task ID for tracking the processing status.
    """
    try:
        # Read the image data
        content = await image.read()
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Queue the task
        task = process_image_task.apply_async(args=[content], task_id=task_id)
        
        return JSONResponse(
            status_code=202,
            content={"id": task_id}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue image: {str(e)}")

@app.get("/id")
async def get_task_status(
    task_id: str,
    api_key: str = Depends(get_api_key)
):
    """
    Get the status and result of a processing task.
    """
    try:
        task = celery_app.AsyncResult(task_id)
        
        # Check task state
        if task.state == 'PENDING':
            return JSONResponse(
                status_code=202,
                content={"status": "Processing"}
            )
        elif task.state == 'SUCCESS':
            return JSONResponse(
                status_code=200,
                content=task.result
            )
        elif task.state == 'FAILURE':
            return JSONResponse(
                status_code=400,
                content={"error": str(task.result)}
            )
        else:
            # If task state is not one of the above, it's likely an invalid task
            return JSONResponse(
                status_code=404,
                content={"error": "Task ID not found"}
            )
            
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": str(e)}
        )

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
