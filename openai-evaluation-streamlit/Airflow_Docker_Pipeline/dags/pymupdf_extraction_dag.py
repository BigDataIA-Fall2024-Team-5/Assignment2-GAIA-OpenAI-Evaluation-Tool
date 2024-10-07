from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import boto3
import fitz  # PyMuPDF
import os


# Initialize the S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_KEY'),
)

# S3 bucket configuration
bucket_name = 's3-openai-evaluation-app-storage' 
input_prefix = 'bronze/'
output_prefix = 'silver/pdf/pymupdf/'

# Define function to list PDFs in S3
def list_pdfs_in_s3_folder(prefix):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    pdf_files = [item['Key'] for item in response.get('Contents', []) if item['Key'].endswith('.pdf')]
    return pdf_files

# Function to process PDFs and upload text to S3
def pymupdf_process_and_upload():
    # List all PDFs in the 'test' and 'validation' subfolders
    pdf_files = list_pdfs_in_s3_folder(f'{input_prefix}test/') + list_pdfs_in_s3_folder(f'{input_prefix}validation/')
    
    # Initialize a counter for processed files
    processed_count = 0

    for pdf_key in pdf_files:
        # Download the PDF file
        pdf_obj = s3.get_object(Bucket=bucket_name, Key=pdf_key)
        pdf_content = pdf_obj['Body'].read()

        # Process the PDF with PyMuPDF to extract text
        doc = fitz.open(stream=pdf_content, filetype='pdf')
        text_content = ''
        for page in doc:
            text_content += page.get_text()

        # Define the output filename with .txt extension
        output_filename = os.path.basename(pdf_key).replace('.pdf', '.txt')
        output_key = f'{output_prefix}{output_filename}'

        # Upload the processed text to S3
        s3.put_object(Bucket=bucket_name, Key=output_key, Body=text_content)
        print(f"Processed and uploaded: {output_key}")
        
        # Increment the counter
        processed_count += 1

    # Print the total count of processed files
    print(f"Total PDF files processed and uploaded: {processed_count}")


# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Instantiate the DAG with a new name
with DAG(
    'pymupdf_extraction_pipeline',
    default_args=default_args,
    description='Extract text from PDFs using PyMuPDF and store it in another S3 folder',
    schedule_interval=None, 
    start_date=datetime(2024, 1, 1),
    catchup=False,
) as dag:

    pymupdf_extraction_task = PythonOperator(
        task_id='pymupdf_extraction_task',
        python_callable=pymupdf_process_and_upload,
    )

# Set task dependencies
pymupdf_extraction_task
