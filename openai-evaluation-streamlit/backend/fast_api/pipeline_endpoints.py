from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError
from backend.fast_api.jwt_handler import decode_token
from backend.main import process_dataset
import logging

# Create the router for pipeline-related operations
pipeline_router = APIRouter()

# Dependency to retrieve the token from the request's Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Logger configuration
logger = logging.getLogger("uvicorn")

@pipeline_router.post("/process-dataset")
async def process_dataset_pipeline(token: str = Depends(oauth2_scheme)):
    """
    Endpoint to trigger the dataset processing pipeline.
    This requires a valid JWT token.
    """
    try:
        # Decode and verify the JWT token
        payload = decode_token(token)
        
        # Trigger the dataset processing function
        result = process_dataset()

        # Return a successful result message
        return {"message": result}
    
    except (ExpiredSignatureError, JWTError) as token_error:
        # Handle expired or invalid token
        logger.error(f"Token error: {token_error}")
        raise HTTPException(status_code=401, detail=str(token_error))
    
    except Exception as e:
        # Handle any other exceptions during processing
        logger.error(f"An error occurred during dataset processing: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
