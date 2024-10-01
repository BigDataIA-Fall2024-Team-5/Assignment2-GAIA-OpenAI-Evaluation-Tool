# fast_main
import logging
from fastapi import FastAPI
from scripts.fast_api.auth import auth_router
from scripts.fast_api.s3_endpoints import s3_router
from scripts.fast_api.gpt_endpoints import gpt_router
from scripts.fast_api.db_endpoints import db_router
from scripts.fast_api.pipeline_endpoints import pipeline_router

# Set up basic logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

# Include the routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(s3_router, prefix="/s3", tags=["S3"])
app.include_router(gpt_router, prefix="/gpt", tags=["ChatGPT"])
app.include_router(db_router, prefix="/db", tags=["Database"])
app.include_router(pipeline_router, prefix="/pipeline", tags=["Pipeline"])  # Include the pipeline router

# Root endpoint for checking if the app is running
@app.get("/")
async def root():
    logger.info("Root endpoint accessed")  # Log when the root endpoint is accessed
    return {"message": "FastAPI Backend for OpenAI Evaluation App"}
