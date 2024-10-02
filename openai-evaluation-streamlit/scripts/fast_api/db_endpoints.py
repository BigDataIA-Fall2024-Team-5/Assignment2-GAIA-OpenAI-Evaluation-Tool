from fastapi import APIRouter, HTTPException, Query
from scripts.api_utils.azure_sql_utils import (
    fetch_all_users, 
    remove_user, 
    promote_to_admin, 
    fetch_user_results, 
    fetch_all_questions, 
    update_user_result_in_db
)
import logging
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Union

# Initialize logging
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

# Create a router for the database operations
db_router = APIRouter()

# Pydantic model for user response
class UserResponse(BaseModel):
    user_id: str
    username: str
    role: str

# Pydantic model for user result response
class UserResultResponse(BaseModel):
    user_id: str
    task_id: str
    user_result_status: Optional[str] = None
    chatgpt_response: Optional[str] = None

    class Config:
        from_attributes = True

# Pydantic model for questions response
class QuestionResponse(BaseModel):
    task_id: str
    Question: str  # Match with the database field 'Question'
    Level: int  # Match with the database field 'Level'
    FinalAnswer: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    Annotator_Metadata_Steps: Optional[str] = None
    Annotator_metadata_number_of_steps: Optional[Union[int, str]] = None  # Allow both int and str
    Annotator_Metadata_How_long_did_this_take: Optional[str] = None
    Annotator_Metadata_Tools: Optional[str] = None
    Annotator_Metadata_Number_of_tools: Optional[int] = None
    result_status: Optional[str] = None
    created_date: Optional[datetime] = None

    class Config:
        from_attributes = True

# Pydantic model for updating the user result
class UpdateResultModel(BaseModel):
    user_id: str
    task_id: str
    status: str
    chatgpt_response: str

# Fetch all users endpoint
@db_router.get("/users", response_model=List[UserResponse], tags=["Admin User Management"])
async def get_all_users():
    """
    Fetch all users from the database.
    """
    try:
        users = fetch_all_users()
        logger.info(f"Fetched {len(users)} users from the database.")
        return users
    except ValueError as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching users.")
    except Exception as e:
        logger.error(f"Unexpected error while fetching users: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching users.")

# Delete a user by user_id endpoint
@db_router.delete("/users/{user_id}", tags=["Admin User Management"])
async def delete_user(user_id: str, admin: str = Query(...)):
    """
    Delete a user from the database by their user_id.
    The admin user_id is passed to log who performed the action.
    """
    try:
        logger.info(f"Admin {admin} is attempting to delete user {user_id}.")
        success = remove_user(user_id)
        if success:
            logger.info(f"User '{user_id}' deleted successfully by admin {admin}.")
            return {"message": f"User '{user_id}' deleted successfully by admin {admin}."}
        else:
            raise HTTPException(status_code=404, detail="User not found.")
    except ValueError as e:
        logger.error(f"Error deleting user '{user_id}': {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Error deleting user '{user_id}': {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the user.")
    except Exception as e:
        logger.error(f"Unexpected error while deleting user '{user_id}': {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting the user.")

# Promote a user to admin by user_id endpoint
@db_router.put("/users/{user_id}/promote", tags=["Admin User Management"])
async def promote_user_to_admin(user_id: str, admin: str = Query(...)):
    """
    Promote a user to the admin role in the database.
    The admin user_id is passed to log who performed the action.
    """
    try:
        logger.info(f"Admin {admin} is attempting to promote user {user_id} to admin.")
        success = promote_to_admin(user_id)
        if success:
            logger.info(f"User '{user_id}' promoted to admin successfully by admin {admin}.")
            return {"message": f"User '{user_id}' promoted to admin successfully by admin {admin}."}
        else:
            raise HTTPException(status_code=404, detail="User not found for promotion.")
    except ValueError as e:
        logger.error(f"Error promoting user '{user_id}': {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Error promoting user '{user_id}': {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while promoting the user.")
    except Exception as e:
        logger.error(f"Unexpected error while promoting user '{user_id}': {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while promoting the user.")

@db_router.get("/questions", response_model=List[QuestionResponse], tags=["User call"])
async def get_all_questions():
    """
    Fetch all questions (GAIA dataset) from the database.
    """
    try:
        questions = fetch_all_questions()  # Fetch from database; ensure it returns a list of dictionaries
        return questions  # Pydantic will handle datetime conversion
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching questions.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching questions.")

# Fetch user-specific results endpoint
@db_router.get("/user_results/{user_id}", response_model=List[UserResultResponse], tags=["User call"])
async def get_user_results(user_id: str):
    """
    Fetch user-specific results from the database by user_id.
    """
    try:
        results = fetch_user_results(user_id) 
        if not results:
            logger.info(f"No results found for user '{user_id}', returning an empty list.")
            return []  # Return an empty list if no results
        logger.info(f"Fetched results for user '{user_id}'.")
        return results  # Return the fetched results
    except ValueError as e:
        logger.error(f"Error fetching results for user '{user_id}': {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Error fetching results for user '{user_id}': {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching results.")
    except Exception as e:
        logger.error(f"Unexpected error while fetching results for user '{user_id}': {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching results.")

# Update user result endpoint
@db_router.put("/update_result", tags=["User call"])
async def update_user_result(result_data: UpdateResultModel):
    """
    Update user result in the database.
    """
    try:
        update_success = update_user_result_in_db(
            result_data.user_id,
            result_data.task_id,
            result_data.status,
            result_data.chatgpt_response
        )
        
        if update_success:
            logger.info(f"Updated result for user '{result_data.user_id}', task '{result_data.task_id}'.")
            return {"message": "Result updated successfully"}
        else: 
            raise HTTPException(status_code=400, detail="Failed to update the result.")
    except ValueError as e:
        logger.error(f"Error updating result for user '{result_data.user_id}': {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Error updating result for user '{result_data.user_id}': {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the result.")
    except Exception as e:
        logger.error(f"Unexpected error while updating user result: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating the result.")
