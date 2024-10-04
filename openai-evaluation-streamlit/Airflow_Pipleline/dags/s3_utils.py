from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def get_pdf_list(**kwargs):
    bucket = kwargs['bucket']
    s3_hook = S3Hook(aws_conn_id='aws_default')
    
    test_pdfs = s3_hook.list_keys(bucket_name=bucket, prefix='Bronze_pdf/test/', delimiter='/')
    validation_pdfs = s3_hook.list_keys(bucket_name=bucket, prefix='Bronze_pdf/validation/', delimiter='/')
    
    all_pdfs = test_pdfs + validation_pdfs
    pdf_list = [pdf for pdf in all_pdfs if pdf.lower().endswith('.pdf')]
    
    print(f"Found {len(pdf_list)} PDF files to process")
    return pdf_list