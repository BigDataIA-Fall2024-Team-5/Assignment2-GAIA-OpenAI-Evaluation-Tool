import os
import fitz  # PyMuPDF
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def process_pdf(**kwargs):
    ti = kwargs['ti']
    bucket = kwargs['bucket']
    bronze_folder = kwargs['bronze_folder']
    silver_folder = kwargs['silver_folder']
    
    s3_hook = S3Hook(aws_conn_id='aws_default')
    pdf_list = ti.xcom_pull(task_ids='get_pdf_list')
    
    for pdf_key in pdf_list:
        local_pdf_path = f"/tmp/{os.path.basename(pdf_key)}"
        
        # Download PDF from bronze folder
        s3_hook.download_file(key=pdf_key, bucket_name=bucket, local_path=local_pdf_path)
        
        # Extract content using PyMuPDF
        doc = fitz.open(local_pdf_path)
        text_content = ""
        for page in doc:
            text_content += page.get_text()
        
        # Save extracted content to a text file
        extracted_file_name = f"{os.path.splitext(os.path.basename(pdf_key))[0]}_extracted.txt"
        local_extracted_path = f"/tmp/{extracted_file_name}"
        with open(local_extracted_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        # Upload extracted content to silver folder
        silver_key = f"{silver_folder}/{extracted_file_name}"
        s3_hook.load_file(filename=local_extracted_path, key=silver_key, bucket_name=bucket, replace=True)
        
        # Clean up local files
        os.remove(local_pdf_path)
        os.remove(local_extracted_path)
        
        print(f"Processed and uploaded: {silver_key}")