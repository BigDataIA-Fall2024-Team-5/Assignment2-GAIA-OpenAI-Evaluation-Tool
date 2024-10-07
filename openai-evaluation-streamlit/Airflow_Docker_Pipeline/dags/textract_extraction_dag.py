from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import boto3
import os
import time

# Initialize the S3 and Textract clients
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name=os.getenv('AWS_REGION')
)

textract = boto3.client(
    'textract',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
    region_name=os.getenv('AWS_REGION')
)

# S3 bucket configuration
bucket_name = 's3-openai-evaluation-app-storage'
input_prefix = 'bronze/'
output_prefix = 'silver/pdf/textract/'

# Define function to list PDFs in S3
def list_pdfs_in_s3_folder(prefix):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    pdf_files = [item['Key'] for item in response.get('Contents', []) if item['Key'].endswith('.pdf')]
    return pdf_files

# Function to process PDFs with Amazon Textract and upload text to S3
def textract_process_and_upload():
    # List all PDFs in the 'test' and 'validation' subfolders
    pdf_files = list_pdfs_in_s3_folder(f'{input_prefix}test/') + list_pdfs_in_s3_folder(f'{input_prefix}validation/')
    
    # Initialize a counter for processed files
    processed_count = 0

    for pdf_key in pdf_files:
        # Start Textract job
        response = textract.start_document_text_detection(
            DocumentLocation={'S3Object': {'Bucket': bucket_name, 'Name': pdf_key}}
        )
        
        job_id = response['JobId']
        print(f"Started Textract job for {pdf_key}, job ID: {job_id}")
        
        # Wait for Textract job to complete
        status = 'IN_PROGRESS'
        while status == 'IN_PROGRESS':
            time.sleep(5)  # wait before checking status again
            response = textract.get_document_text_detection(JobId=job_id)
            status = response['JobStatus']
        
        if status == 'SUCCEEDED':
            text_content = ''
            pages = response.get('Blocks', [])
            for block in pages:
                if block['BlockType'] == 'LINE':
                    text_content += block['Text'] + '\n'

            # Define the output filename with .txt extension
            output_filename = os.path.basename(pdf_key).replace('.pdf', '.txt')
            output_key = f'{output_prefix}{output_filename}'

            # Upload the extracted text to S3
            s3.put_object(Bucket=bucket_name, Key=output_key, Body=text_content)
            print(f"Processed and uploaded: {output_key}")
            
            # Increment the counter
            processed_count += 1
        else:
            print(f"Textract job for {pdf_key} failed.")

    # Print the total count of processed files
    print(f"Total PDF files processed and uploaded: {processed_count}")

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Instantiate the DAG with a new name for Textract
with DAG(
    'textract_extraction_pipeline',
    default_args=default_args,
    description='Extract text from PDFs using Amazon Textract and store it in another S3 folder',
    schedule_interval=None,  # No schedule, only run when triggered
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    textract_extraction_task = PythonOperator(
        task_id='textract_extraction_task',
        python_callable=textract_process_and_upload,
    )

# Set task dependencies
textract_extraction_task
