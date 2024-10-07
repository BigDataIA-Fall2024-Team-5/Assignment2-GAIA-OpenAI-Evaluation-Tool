import os
import boto3
import fitz  # PyMuPDF
from botocore.exceptions import ClientError
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def process_pdf(**kwargs):
    ti = kwargs['ti']
    bucket = kwargs['bucket']
    bronze_folder = kwargs['bronze_folder']
    silver_folder = kwargs['silver_folder']
    
    print(f"Starting process_pdf with bucket: {bucket}, bronze_folder: {bronze_folder}, silver_folder: {silver_folder}")
    
    s3_hook = S3Hook(aws_conn_id='aws_region')
    s3_client = s3_hook.get_conn()
    
    pdf_list = ti.xcom_pull(task_ids='get_pdf_list')
    
    print(f"Retrieved pdf_list from XCom: {pdf_list}")
    
    if not pdf_list:
        print("No PDFs found to process.")
        return

    for pdf_key in pdf_list:
        local_pdf_path = None
        local_extracted_path = None
        try:
            local_pdf_path = f"/tmp/{os.path.basename(pdf_key)}"
            
            print(f"Attempting to download: {pdf_key}")
            print(f"Local PDF path: {local_pdf_path}")
            
            # Download the file using boto3
            try:
                s3_client.download_file(bucket, pdf_key, local_pdf_path)
                print(f"Downloaded {pdf_key} to {local_pdf_path}")
            except ClientError as e:
                print(f"Error downloading {pdf_key}: {str(e)}")
                continue
            
            # Check if the file was actually downloaded
            if not os.path.exists(local_pdf_path):
                print(f"Failed to download file: {local_pdf_path}")
                continue
            
            doc = fitz.open(local_pdf_path)
            text_content = ""
            for page in doc:
                text_content += page.get_text()
            doc.close()
            
            extracted_file_name = f"{os.path.splitext(os.path.basename(pdf_key))[0]}_extracted.txt"
            local_extracted_path = f"/tmp/{extracted_file_name}"
            with open(local_extracted_path, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"Extracted content saved to {local_extracted_path}")
            
            silver_key = f"{silver_folder}/PyMupdf/{extracted_file_name}"
            print(f"Attempting to upload to S3: {silver_key}")
            s3_client.upload_file(local_extracted_path, bucket, silver_key)
            print(f"Uploaded {local_extracted_path} to S3://{bucket}/{silver_key}")
            
        except Exception as e:
            print(f"Error processing {pdf_key}: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error args: {e.args}")
        
        finally:
            if local_pdf_path and os.path.exists(local_pdf_path):
                os.remove(local_pdf_path)
                print(f"Removed local file: {local_pdf_path}")
            if local_extracted_path and os.path.exists(local_extracted_path):
                os.remove(local_extracted_path)
                print(f"Removed local file: {local_extracted_path}")

    print(f"Finished processing {len(pdf_list)} PDFs")