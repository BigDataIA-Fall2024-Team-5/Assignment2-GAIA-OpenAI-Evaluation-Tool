import os
import boto3
import time
from botocore.exceptions import ClientError
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def preprocess_pdf_with_textract(**kwargs):
    ti = kwargs['ti']
    bucket = kwargs['bucket']
    bronze_folder = kwargs['bronze_folder']
    silver_folder = kwargs['silver_folder']
    
    print(f"Starting preprocess_pdf_with_textract with bucket: {bucket}, bronze_folder: {bronze_folder}, silver_folder: {silver_folder}")
    
    # Use S3Hook to get AWS session
    s3_hook = S3Hook(aws_conn_id='aws_region')
    session = s3_hook.get_session()
    
    # Get the region from the session
    region_name = session.region_name
    if not region_name:
        raise ValueError("AWS region is not set in the Airflow connection.")
    
    print(f"Using AWS region: {region_name}")
    
    # Create S3 and Textract clients using the session and explicit region
    s3_client = session.client('s3', region_name='us-east-2')
    textract_client = session.client('textract', region_name='us-east-2')
    
    pdf_list = ti.xcom_pull(task_ids='get_pdf_list')
    
    print(f"Retrieved pdf_list from XCom: {pdf_list}")
    
    if not pdf_list:
        print("No PDFs found to process.")
        return

    processed_count = 0

    def wait_for_job_completion(job_id):
        while True:
            response = textract_client.get_document_text_detection(JobId=job_id)
            status = response['JobStatus']
            if status in ['SUCCEEDED', 'FAILED']:
                return status
            time.sleep(5)

    for pdf_key in pdf_list:
        try:
            print(f"Processing {pdf_key} with Textract")
            
            # Start Textract job
            response = textract_client.start_document_text_detection(
                DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': pdf_key}}
            )
            
            job_id = response['JobId']
            print(f"Started Textract job for {pdf_key}, job ID: {job_id}")
            
            # Wait for Textract job to complete
            job_status = wait_for_job_completion(job_id)
            
            if job_status == 'SUCCEEDED':
                response = textract_client.get_document_text_detection(JobId=job_id)
                text_content = ''
                for item in response['Blocks']:
                    if item['BlockType'] == 'LINE':
                        text_content += item['Text'] + '\n'

                # Define the output filename with .txt extension
                output_filename = os.path.basename(pdf_key).replace('.pdf', '_textract.txt')
                output_key = f'{silver_folder}/textract/{output_filename}'

                # Upload the extracted text to S3
                s3_client.put_object(Bucket=bucket, Key=output_key, Body=text_content)
                print(f"Processed and uploaded: {output_key}")
                
                processed_count += 1
            else:
                print(f"Textract job for {pdf_key} failed.")
            
        except ClientError as e:
            print(f"AWS error processing {pdf_key} with Textract: {str(e)}")
        except Exception as e:
            print(f"Unexpected error processing {pdf_key} with Textract: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            print(f"Error args: {e.args}")

    print(f"Finished processing {processed_count} out of {len(pdf_list)} PDFs with Textract")