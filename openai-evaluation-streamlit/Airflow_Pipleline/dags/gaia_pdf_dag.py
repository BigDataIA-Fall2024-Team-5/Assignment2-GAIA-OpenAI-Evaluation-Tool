from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from pdf_processing_utils import process_pdf
from s3_utils import get_pdf_list, test_s3_connection
from textract_processing import preprocess_pdf_with_textract
# Define your S3 bucket and folder names
S3_BUCKET = 's3-openai-evaluation-app-storage'
BRONZE_FOLDER = 'bronze'
SILVER_FOLDER = 'Silver_pdf'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 3),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'gaia_pdf_processing',
    default_args=default_args,
    description='Process GAIA PDF files using PyMuPDF',
    schedule_interval=timedelta(days=1),
)

test_s3_connection_task = PythonOperator(
    task_id='test_s3_connection',
    python_callable=test_s3_connection,
    op_kwargs={'bucket': S3_BUCKET},
    dag=dag,
)

get_pdf_list_task = PythonOperator(
    task_id='get_pdf_list',
    python_callable=get_pdf_list,
    op_kwargs={'bucket': S3_BUCKET},
    dag=dag,
)

process_pdf_task = PythonOperator(
    task_id='process_pdf',
    python_callable=process_pdf,
    op_kwargs={
        'bucket': S3_BUCKET,
        'bronze_folder': BRONZE_FOLDER,
        'silver_folder': SILVER_FOLDER,
    },
    dag=dag,
)
preprocess_pdf_textract_task = PythonOperator(
    task_id='preprocess_pdf_with_textract',
    python_callable=preprocess_pdf_with_textract,
    op_kwargs={
        'bucket': S3_BUCKET,
        'bronze_folder': BRONZE_FOLDER,
        'silver_folder': SILVER_FOLDER,
    },
    dag=dag,
)

test_s3_connection_task >> get_pdf_list_task >> [process_pdf_task, preprocess_pdf_textract_task]