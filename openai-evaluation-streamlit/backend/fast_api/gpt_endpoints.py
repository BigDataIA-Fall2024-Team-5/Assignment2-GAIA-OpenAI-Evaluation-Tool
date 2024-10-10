from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError
from pydantic import BaseModel
from typing import Optional, Literal
import logging
from api_utils.chatgpt_utils import get_chatgpt_response, compare_and_update_status
from fast_api.jwt_handler import decode_token

# Set up a logger
logger = logging.getLogger("uvicorn")

# OAuth2PasswordBearer to retrieve the JWT token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Define the request body models
class AskRequest(BaseModel):
    question: str
    instructions: Optional[str] = None
    preprocessed_data: Optional[str] = None
    model_name: Literal["gpt-3.5-turbo", "gpt-4"] = "gpt-3.5-turbo"

class CompareRequest(BaseModel):
    row: dict
    chatgpt_response: str
    instructions: Optional[str] = None

# Initialize the router
gpt_router = APIRouter()

@gpt_router.post("/ask")
async def ask_gpt(request: AskRequest, token: str = Depends(oauth2_scheme)):
    try:
        # Decode and verify the JWT token
        payload = decode_token(token)

        # Extract data from the request model
        question = request.question
        instructions = request.instructions
        preprocessed_data = request.preprocessed_data
        model_name = request.model_name  # Extract the model name from the request

        # Pass the extracted data to the ChatGPT function
        response, used_model_name = get_chatgpt_response(
            question=question, 
            model_name=model_name, 
            instructions=instructions, 
            preprocessed_data=preprocessed_data
        )

        # Return the response and the model name used
        return {"response": response, "model_name": used_model_name}

    except ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired. Please log in again.")

    except JWTError:
        logger.error("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        logger.error(f"Unexpected error in ask_gpt: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@gpt_router.post("/compare")
async def compare_gpt(compare_request: CompareRequest, token: str = Depends(oauth2_scheme)):
    try:
        # Decode and verify the JWT token
        payload = decode_token(token)

        # Extract data from the request body
        row = compare_request.row
        chatgpt_response = compare_request.chatgpt_response
        instructions = compare_request.instructions

        # Call the function to compare the response
        comparison_result = compare_and_update_status(row, chatgpt_response, instructions)

        return {"comparison_result": comparison_result}

    except ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired. Please log in again.")

    except JWTError:
        logger.error("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        logger.error(f"Unexpected error in compare_gpt: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")