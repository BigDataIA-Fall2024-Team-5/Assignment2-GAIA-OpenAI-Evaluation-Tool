# pipeline_endpoints.py
from fastapi import APIRouter, HTTPException
from scripts.main import process_dataset

# Create the router for pipeline-related operations
pipeline_router = APIRouter()

@pipeline_router.post("/process-dataset")
async def process_dataset_pipeline():
    """
    Endpoint to trigger the dataset processing pipeline.
    """
    try:
        result = process_dataset()
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
