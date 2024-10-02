from fastapi import APIRouter, HTTPException, Query
from scripts.api_utils.azure_sql_utils import fetch_all_users, remove_user, promote_to_admin, fetch_user_results, fetch_all_questions, update_user_result_in_db 
import logging
from pydantic import BaseModel

# Initialize logging
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

# Create a router for the database operations
db_router = APIRouter()

# Fetch all users endpoint
@db_router.get("/users", tags=["Admin User Management"])
async def get_all_users():
    """
    Fetch all users from the database.
    """
    try:
        users = fetch_all_users()
        logger.info(f"Fetched {len(users)} users from the database.")
        return users
    except HTTPException as e:
        logger.error(f"Error fetching users: {e.detail}")
        raise e  # Re-raise HTTPException with the original status and message
    except Exception as e:
        logger.error(f"Unexpected error while fetching users: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching users."
        )

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
        logger.info(f"User '{user_id}' deleted successfully by admin {admin}.")
        return {"message": f"User '{user_id}' deleted successfully by admin {admin}."}
    except HTTPException as e:
        logger.error(f"Error deleting user '{user_id}': {e.detail}")
        raise e  # Re-raise HTTPException with the original status and message
    except Exception as e:
        logger.error(f"Unexpected error while deleting user '{user_id}': {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while deleting the user."
        )

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
        logger.info(f"User '{user_id}' promoted to admin successfully by admin {admin}.")
        return {"message": f"User '{user_id}' promoted to admin successfully by admin {admin}."}
    except HTTPException as e:
        logger.error(f"Error promoting user '{user_id}': {e.detail}")
        raise e  # Re-raise HTTPException with the original status and message
    except Exception as e:
        logger.error(f"Unexpected error while promoting user '{user_id}': {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while promoting the user."
        )


# Model for updating the user result
class UpdateResultModel(BaseModel):
    user_id: str
    task_id: str
    status: str
    chatgpt_response: str

# Fetch all questions
@db_router.get("/questions", tags=["User call"])
async def get_all_questions():
    """
    Fetch all questions (GAIA dataset) from the database.
    """
    try:
        questions = fetch_all_questions()  # Azure SQL utils should handle conversions
        logger.info(f"Fetched {len(questions)} questions from the database.")
        return questions
    except Exception as e:
        logger.error(f"Unexpected error while fetching questions: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while fetching questions."
        )

# Fetch user-specific results
@db_router.get("/user_results/{user_id}", tags=["User call"])
async def get_user_results(user_id: str):
    """
    Fetch user-specific results from the database by user_id.
    """
    try:
        results = fetch_user_results(user_id)  # Azure SQL utils should handle conversions
        logger.info(f"Fetched results for user '{user_id}'.")
        return results
    except Exception as e:
        logger.error(f"Unexpected error while fetching user results: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while fetching results for user '{user_id}'."
        )

# Update user result
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
            raise HTTPException(
                status_code=400,
                detail="Failed to update the result."
            )
    except HTTPException as e:
        logger.error(f"HTTP Exception during result update: {e.detail}")
        raise e  # Re-raise the HTTP exception
    except Exception as e:
        logger.error(f"Unexpected error while updating user result: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while updating the result."
        )
