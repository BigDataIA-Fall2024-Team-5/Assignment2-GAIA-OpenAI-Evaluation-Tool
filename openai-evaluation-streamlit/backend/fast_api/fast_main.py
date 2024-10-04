import os
import logging
from fastapi import FastAPI
from fast_api.auth import auth_router
from fast_api.s3_endpoints import s3_router
from fast_api.gpt_endpoints import gpt_router
from fast_api.db_endpoints import db_router
from fast_api.pipeline_endpoints import pipeline_router
from api_utils.amazon_s3_utils import initialize_s3_client_and_bucket, get_s3_client
from api_utils.chatgpt_utils import init_openai
from api_utils.azure_sql_utils import set_sqlalchemy_connection_params  # new function to set parameters

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """
    Startup event to initialize the S3 client, bucket, and OpenAI API at server startup.
    Retrieves credentials and configurations from environment variables.
    """
    
    # Initialize S3 Client and Bucket
    try:
        aws_access_key = os.getenv('AWS_ACCESS_KEY')
        aws_secret_key = os.getenv('AWS_SECRET_KEY')
        bucket_name = os.getenv('S3_BUCKET_NAME')

        if not aws_access_key or not aws_secret_key or not bucket_name:
            logger.error("AWS credentials or S3 bucket name missing in environment variables.")
        else:
            initialize_s3_client_and_bucket(aws_access_key, aws_secret_key, bucket_name)
            logger.info("S3 client and bucket initialized successfully at startup.")
    
    except Exception as e:
        logger.error(f"Failed to initialize S3 client and bucket: {str(e)}")

    # Initialize OpenAI API
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            init_openai(openai_api_key)
            logger.info("OpenAI API initialized successfully at startup.")
        else:
            logger.error("OpenAI API key not found. Please set 'OPENAI_API_KEY' in the environment.")
    
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI API: {str(e)}")
    
    # Set SQLAlchemy connection params (for Azure SQL)
    try:
        azure_sql_params = {
            "server": os.getenv('AZURE_SQL_SERVER'),
            "user": os.getenv('AZURE_SQL_USER'),
            "password": os.getenv('AZURE_SQL_PASSWORD'),
            "database": os.getenv('AZURE_SQL_DATABASE')
        }
        if not all(azure_sql_params.values()):
            logger.error("Azure SQL credentials missing in environment variables.")
        else:
            set_sqlalchemy_connection_params(azure_sql_params)
            logger.info("Azure SQL connection params set successfully at startup.")
    
    except Exception as e:
        logger.error(f"Failed to set Azure SQL connection params: {str(e)}")


# Include the routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(s3_router, prefix="/s3", tags=["S3"])
app.include_router(gpt_router, prefix="/gpt", tags=["ChatGPT"])
app.include_router(db_router, prefix="/db", tags=["Database"])
app.include_router(pipeline_router, prefix="/pipeline", tags=["Pipeline"])

# Root endpoint for checking if the app is running
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "FastAPI Backend for OpenAI Evaluation App"}
