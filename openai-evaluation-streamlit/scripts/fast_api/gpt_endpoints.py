from fastapi import APIRouter, HTTPException
from scripts.api_utils.chatgpt_utils import get_chatgpt_response

gpt_router = APIRouter()

@gpt_router.post("/ask")
async def ask_gpt(question: str, instructions: str = None, preprocessed_data: str = None):
    try:
        response = get_chatgpt_response(question, instructions, preprocessed_data)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
