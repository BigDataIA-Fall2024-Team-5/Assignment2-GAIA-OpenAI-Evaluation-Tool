import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from scripts.api_utils.chatgpt_utils import get_chatgpt_response, compare_and_update_status, init_openai


# Define the request body models
class AskRequest(BaseModel):
    question: str
    instructions: Optional[str] = None
    preprocessed_data: Optional[str] = None

class CompareRequest(BaseModel):
    row: dict  # Expecting a dict-like structure with the 'FinalAnswer', 'Question', etc.
    chatgpt_response: str
    instructions: Optional[str] = None

# Initialize the router
gpt_router = APIRouter()

# Updated ask_gpt endpoint with the AskRequest model
@gpt_router.post("/ask")
async def ask_gpt(request: AskRequest):
    try:
        # Extract data from the request model
        question = request.question
        instructions = request.instructions
        preprocessed_data = request.preprocessed_data

        # Pass the extracted data to the ChatGPT function
        response = get_chatgpt_response(question, instructions, preprocessed_data)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to compare GPT's response with an expected answer
@gpt_router.post("/compare")
async def compare_gpt(compare_request: CompareRequest):
    try:
        # Extract data from the request body
        row = compare_request.row
        chatgpt_response = compare_request.chatgpt_response
        instructions = compare_request.instructions

        # Call the function to compare the response
        comparison_result = compare_and_update_status(row, chatgpt_response, instructions)

        return {"comparison_result": comparison_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
