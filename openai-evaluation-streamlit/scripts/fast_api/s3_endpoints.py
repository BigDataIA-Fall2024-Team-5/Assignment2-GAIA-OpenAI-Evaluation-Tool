from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from scripts.api_utils.amazon_s3_utils import read_pdf_summary_from_s3, get_s3_client
import logging
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError
from scripts.fast_api.jwt_handler import decode_token

s3_router = APIRouter()

# Configure a logger
logger = logging.getLogger("uvicorn")

# Pydantic model for the request
class FetchPDFSummaryRequest(BaseModel):
    file_name: str
    extraction_method: str

# Dependency to retrieve the token from the request's Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Fetch PDF summary from S3 endpoint with JWT token authentication
@s3_router.post("/fetch_pdf_summary/")
async def fetch_pdf_summary(request: FetchPDFSummaryRequest, token: str = Depends(oauth2_scheme)):
    try:
        logger.info(f"Starting PDF fetch for file: {request.file_name}, method: {request.extraction_method}")
        
        # Decode and verify the JWT token
        payload = decode_token(token)
        
        # Use the S3 client from amazon_s3_utils
        s3_client_instance = get_s3_client()

        # Fetch the PDF summary from S3
        summary = read_pdf_summary_from_s3(
            file_name=request.file_name,
            extraction_method=request.extraction_method,
            bucket_name=s3_client_instance.bucket_name,
            s3_client=s3_client_instance.client
        )
        
        if summary:
            logger.info(f"PDF summary fetched successfully for file: {request.file_name}")
            return {"summary": summary}
        else:
            logger.warning(f"PDF summary not found for file: {request.file_name}")
            raise HTTPException(status_code=404, detail="PDF summary not available.")
    
    except (ExpiredSignatureError, JWTError) as token_error:
        # Handle expired or invalid token
        logger.error(f"Token error: {token_error}")
        raise HTTPException(status_code=401, detail=str(token_error))

    except Exception as e:
        # Log any other unexpected errors and return 500
        logger.error(f"Unexpected error while fetching PDF summary: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")