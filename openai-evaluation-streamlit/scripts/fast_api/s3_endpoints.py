from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from scripts.api_utils.amazon_s3_utils import read_pdf_summary_from_s3, get_s3_client
import logging

s3_router = APIRouter()

# Configure a logger
logger = logging.getLogger("uvicorn")

# Pydantic model for the request
class FetchPDFSummaryRequest(BaseModel):
    file_name: str
    extraction_method: str

# Fetch PDF summary from S3
@s3_router.post("/fetch_pdf_summary/")
def fetch_pdf_summary(request: FetchPDFSummaryRequest):
    try:
        # Use the S3 client from amazon_s3_utils
        s3_client_instance = get_s3_client()

        summary = read_pdf_summary_from_s3(
            file_name=request.file_name,
            extraction_method=request.extraction_method,
            bucket_name=s3_client_instance.bucket_name,
            s3_client=s3_client_instance.client
        )
        
        if summary:
            return {"summary": summary}
        else:
            raise HTTPException(status_code=404, detail="PDF summary not available.")
    except Exception as e:
        # Log the actual error message
        logger.error(f"Error fetching PDF summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
