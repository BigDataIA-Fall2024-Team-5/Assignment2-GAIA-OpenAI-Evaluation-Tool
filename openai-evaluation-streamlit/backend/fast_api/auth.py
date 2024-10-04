import logging
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from fast_api.jwt_handler import create_access_token, hash_password, verify_password, validate_password_strength
from api_utils.azure_sql_utils import fetch_user_from_sql, insert_user_to_sql

# Initialize logging
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

# Create a custom router for authentication
auth_router = APIRouter()

# Pydantic models for user requests
class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    password: str
    confirm_password: str


# Helper function to log and raise HTTP exceptions
def log_and_raise(status_code, detail, log_message):
    logger.warning(log_message)
    raise HTTPException(status_code=status_code, detail=detail)


# Login endpoint
@auth_router.post("/login")
async def login(user: UserLogin):
    logger.info(f"Login attempt for user '{user.username}'.") 
    db_user = fetch_user_from_sql(user.username)
    
    # If the user is not found, log and return specific message
    if not db_user:
        log_and_raise(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            log_message=f"Login attempt failed: User '{user.username}' does not exist."
        )
    
    # If the password is incorrect, log and return specific message
    if not verify_password(user.password, db_user["password"]):
        log_and_raise(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            log_message=f"Login attempt failed: Incorrect password for user '{user.username}'."
        )
    
    # Create a JWT token for the user
    token = create_access_token({"sub": db_user["username"]})
    
    user_role = db_user.get("role")
    logger.info(f"User '{db_user['username']}' successfully logged in as {user_role}.")
    
    # Return the access token, role, userid, and username
    logger.info(f"JWT token generated for user '{db_user['username']}'.")
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": str(db_user["user_id"]),  # Convert UUID to string
        "username": db_user["username"],
        "role": db_user["role"]
    }

# Registration endpoint
@auth_router.post("/register")
async def register(user: UserRegister):
    logger.info(f"Registration attempt for user '{user.username}'.")  # Log registration attempt
    try:
        # Validate if passwords match
        if user.password != user.confirm_password:
            log_and_raise(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Passwords do not match",
                log_message=f"Registration attempt failed for user '{user.username}' due to password mismatch."
            )
        
        # Check if the username already exists in the database
        if fetch_user_from_sql(user.username):
            log_and_raise(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists",
                log_message=f"Registration attempt failed for user '{user.username}' as the user already exists."
            )
        
        # Validate password strength
        validate_password_strength(user.password)
        
        # Hash the password and insert the new user into the database
        hashed_password = hash_password(user.password)
        insert_user_to_sql(user.username, hashed_password, "user")
        
        # Log the successful registration
        logger.info(f"User '{user.username}' registered successfully.")
        
        return {"message": "User registered successfully"}
    
    except HTTPException as e:
        # Log and raise HTTP exceptions with appropriate status codes and messages
        logger.error(f"Registration failed for user '{user.username}': {e.detail}")
        raise e

    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Unexpected error during registration for user '{user.username}': {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )

