from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def test_s3_connection(**kwargs):
    bucket = kwargs['bucket']
    s3_hook = S3Hook(aws_conn_id='aws_region')
    
    session = s3_hook.get_session()
    s3_client = session.client('s3')
    response = s3_client.list_buckets()
    buckets = response['Buckets']
    print(f"S3 Connection successful. Found {len(buckets)} buckets.")
    for bucket_info in buckets:
        print(f"- {bucket_info['Name']}")
    
    objects = s3_client.list_objects_v2(Bucket=bucket)
    if 'Contents' in objects:
        print(f"Found {len(objects['Contents'])} objects in bucket '{bucket}':")
        for obj in objects['Contents'][:10]:  # Limit to first 10 objects
            print(f"- {obj['Key']}")
    else:
        print(f"No objects found in bucket '{bucket}'")

def get_pdf_list(**kwargs):
    bucket = kwargs['bucket']
    s3_hook = S3Hook(aws_conn_id='aws_region')
    
    test_pdfs = s3_hook.list_keys(bucket_name=bucket, prefix='bronze/test/', delimiter='/')
    validation_pdfs = s3_hook.list_keys(bucket_name=bucket, prefix='bronze/validation/', delimiter='/')
    
    print(f"Found {len(test_pdfs)-1} PDFs in test folder")
    print(f"Found {len(validation_pdfs)-1} PDFs in validation folder")
    
    all_pdfs = test_pdfs + validation_pdfs
    pdf_list = [pdf for pdf in all_pdfs if pdf.lower().endswith('.pdf')]
    
    print(f"Total PDFs to process: {len(pdf_list)}")
    for pdf in pdf_list:
        print(f"  - {pdf}")
    
    return pdf_list