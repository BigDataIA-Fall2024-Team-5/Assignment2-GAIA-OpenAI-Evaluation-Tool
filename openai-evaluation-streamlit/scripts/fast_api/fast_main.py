import os
import logging
from fastapi import FastAPI
from scripts.fast_api.auth import auth_router
from scripts.fast_api.s3_endpoints import s3_router
from scripts.fast_api.gpt_endpoints import gpt_router
from scripts.fast_api.db_endpoints import db_router
from scripts.fast_api.pipeline_endpoints import pipeline_router
from scripts.api_utils.amazon_s3_utils import initialize_s3_client_and_bucket, get_s3_client

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    """Initialize S3 client and bucket at startup."""
    aws_access_key = os.getenv('AWS_ACCESS_KEY')
    aws_secret_key = os.getenv('AWS_SECRET_KEY')
    bucket_name = os.getenv('S3_BUCKET_NAME')

    # Initialize the S3 client and bucket
    initialize_s3_client_and_bucket(aws_access_key, aws_secret_key, bucket_name)
    logger.info("S3 client initialized at startup.")

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
