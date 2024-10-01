from fastapi import APIRouter, HTTPException
from scripts.api_utils.amazon_s3_utils import init_s3_client, upload_files_to_s3_and_update_paths
import os

s3_router = APIRouter()

@s3_router.post("/upload")
async def upload_files(dataset: dict):
    access_key = os.getenv('AWS_ACCESS_KEY')
    secret_key = os.getenv('AWS_SECRET_KEY')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    s3_client = init_s3_client(access_key, secret_key)

    repo_dir = "/path/to/repo"
    updated_dataset = upload_files_to_s3_and_update_paths(dataset, s3_client, bucket_name, repo_dir)

    if updated_dataset:
        return {"message": "Files uploaded and dataset updated"}
    raise HTTPException(status_code=500, detail="Error uploading files")
