import os
import fitz  # PyMuPDF
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def process_pdf(**kwargs):
    ti = kwargs['ti']
    bucket = kwargs['bucket']
    bronze_folder = kwargs['bronze_folder']
    silver_folder = kwargs['silver_folder']
    
    print(f"Starting process_pdf with bucket: {bucket}, bronze_folder: {bronze_folder}, silver_folder: {silver_folder}")
    
    s3_hook = S3Hook(aws_conn_id='aws_region')
    
    pdf_list = ti.xcom_pull(task_ids='get_pdf_list')
    
    print(f"Retrieved pdf_list from XCom: {pdf_list}")
    
    if not pdf_list:
        print("No PDFs found to process.")
        return

    for pdf_key in pdf_list:
        try:
            local_pdf_path = f"/tmp/{os.path.basename(pdf_key)}"
            
            full_pdf_key = f"{bronze_folder}/{pdf_key}" if not pdf_key.startswith(bronze_folder) else pdf_key
            print(f"Attempting to download: {full_pdf_key}")
            
            s3_hook.download_file(key=full_pdf_key, bucket_name=bucket, local_path=local_pdf_path)
            print(f"Downloaded {full_pdf_key} to {local_pdf_path}")
            
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
            
            silver_key = f"{silver_folder}/{extracted_file_name}"
            print(f"Attempting to upload to S3: {silver_key}")
            s3_hook.load_file(filename=local_extracted_path, key=silver_key, bucket_name=bucket, replace=True)
            print(f"Uploaded {local_extracted_path} to S3://{bucket}/{silver_key}")
            
        except Exception as e:
            print(f"Error processing {pdf_key}: {str(e)}")
        
        finally:
            if os.path.exists(local_pdf_path):
                os.remove(local_pdf_path)
                print(f"Removed local file: {local_pdf_path}")
            if os.path.exists(local_extracted_path):
                os.remove(local_extracted_path)
                print(f"Removed local file: {local_extracted_path}")

    print(f"Finished processing {len(pdf_list)} PDFs")