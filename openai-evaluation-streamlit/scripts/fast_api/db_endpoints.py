from fastapi import APIRouter, HTTPException, Query
from scripts.api_utils.azure_sql_utils import fetch_all_users, remove_user, promote_to_admin
import logging

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
