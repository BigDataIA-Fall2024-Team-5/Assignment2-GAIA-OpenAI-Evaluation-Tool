#Validating AWS Connection with airflow

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 4),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    's3_connection_test',
    default_args=default_args,
    description='A simple DAG to test S3 connection',
    schedule_interval=timedelta(days=1),
)

def test_s3_connection():
    hook = S3Hook(aws_conn_id='aws_region')
    session = hook.get_session()
    s3_client = session.client('s3')
    response = s3_client.list_buckets()
    buckets = response['Buckets']
    print(f"S3 Connection successful. Found {len(buckets)} buckets.")
    for bucket in buckets:
        print(f"- {bucket['Name']}")
    
    # Now let's list objects in a specific bucket
    bucket_name = 's3-openai-evaluation-app-storage'
    objects = s3_client.list_objects_v2(Bucket=bucket_name)
    if 'Contents' in objects:
        print(f"Found {len(objects['Contents'])} objects in bucket '{bucket_name}':")
        for obj in objects['Contents']:
            print(f"- {obj['Key']}")
    else:
        print(f"No objects found in bucket '{bucket_name}'")

test_s3_task = PythonOperator(
    task_id='test_s3_connection',
    python_callable=test_s3_connection,
    dag=dag,
)