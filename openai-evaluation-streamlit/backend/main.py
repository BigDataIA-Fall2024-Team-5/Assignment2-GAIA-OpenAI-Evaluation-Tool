import os
from dotenv import load_dotenv
from huggingface_hub import login
from data_handling.clone_repo import clone_repository
from data_handling.load_dataset import load_gaia_dataset
from datetime import datetime
from data_handling.delete_cache import delete_cache_folder
from api_utils.amazon_s3_utils import init_s3_client, upload_files_to_s3_and_update_paths
from api_utils.azure_sql_utils import insert_dataframe_to_sql, set_sqlalchemy_connection_params  # Import the setter function


# Load environment variables from .env file
load_dotenv()

# TO RUN IN COMMAND LINE USE python -m backend.main inside poetry shell
def process_dataset():
    try:
        # Set the environment variable for Hugging Face cache directory
        cache_dir = './.cache'
        os.environ["HF_HOME"] = cache_dir
        os.environ["HF_DATASETS_CACHE"] = cache_dir

        # Ensure that the cache directory exists
        os.makedirs(cache_dir, exist_ok=True)

        # Get the environment variables
        hf_token = os.getenv('HF_TOKEN')
        aws_access_key = os.getenv('AWS_ACCESS_KEY')
        aws_secret_key = os.getenv('AWS_SECRET_KEY')
        bucket_name = os.getenv('S3_BUCKET_NAME')
        repo_url = os.getenv('GAIA_REPO_URL')

        # Get Azure SQL connection environment variables
        azure_sql_params = {
            "server": os.getenv('AZURE_SQL_SERVER'),
            "user": os.getenv('AZURE_SQL_USER'),
            "password": os.getenv('AZURE_SQL_PASSWORD'),
            "database": os.getenv('AZURE_SQL_DATABASE')
        }

        # Set the connection parameters for Azure SQL
        set_sqlalchemy_connection_params(azure_sql_params)

        # Ensure tokens are available
        if not hf_token:
            return "Error: Hugging Face token not found in environment variables."

        # Programmatically login to Hugging Face without adding to Git credentials
        login(token=hf_token, add_to_git_credential=False)

        # Step 1: Clone the repository
        clone_dir = os.path.join(cache_dir, "gaia_repo")
        clone_repository(repo_url, clone_dir)

        # Initialize a summary dictionary to track steps
        summary = {
            'repository_cloned': clone_dir,
            'test_split': {
                'status': 'Not Processed',
                's3_uploaded': False,
                'sql_inserted': False,
                'records': 0
            },
            'validation_split': {
                'status': 'Not Processed',
                's3_uploaded': False,
                'sql_inserted': False,
                'records': 0
            }
        }

        # Step 2: Load the dataset for both 'test' and 'validation' splits
        df_split = load_gaia_dataset(cache_dir, split_name='test')
        df_validation = load_gaia_dataset(cache_dir, split_name='validation')

        # Process test split if loaded
        if df_split is not None:
            summary['test_split']['status'] = 'Loaded'
            summary['test_split']['records'] = len(df_split)
            
            # Step 3: Initialize S3 client
            s3_client = init_s3_client(aws_access_key, aws_secret_key)

            # Step 4: Upload 'test' split files to S3 and update paths
            df_split = upload_files_to_s3_and_update_paths(df_split, s3_client, bucket_name, clone_dir, split_name='test')
            summary['test_split']['s3_uploaded'] = True

            # Step 5: Insert the updated 'test' DataFrame into Azure SQL Database
            insert_dataframe_to_sql(df_split, "GaiaDataset_Test")
            summary['test_split']['sql_inserted'] = True

        # Process validation split if loaded
        if df_validation is not None:
            summary['validation_split']['status'] = 'Loaded'
            summary['validation_split']['records'] = len(df_validation)

            # Step 4: Upload 'validation' split files to S3 and update paths
            df_validation = upload_files_to_s3_and_update_paths(df_validation, s3_client, bucket_name, clone_dir, split_name='validation')
            summary['validation_split']['s3_uploaded'] = True

            # Step 5: Insert the updated 'validation' DataFrame into Azure SQL Database
            insert_dataframe_to_sql(df_validation, "GaiaDataset_Validation")
            summary['validation_split']['sql_inserted'] = True

        # Optional: Delete the cache directory
        # delete_cache_folder(cache_dir)

        # Construct a detailed summary message
        summary_message = f"""
        Dataset processing summary:
        1. Repository cloned successfully to: {summary['repository_cloned']}
        
        2. Test Split:
           - Status: {summary['test_split']['status']}
           - Records Processed: {summary['test_split']['records']}
           - S3 Upload: {'Success' if summary['test_split']['s3_uploaded'] else 'Failed'}
           - Azure SQL Insertion: {'Success' if summary['test_split']['sql_inserted'] else 'Failed'}
        
        3. Validation Split:
           - Status: {summary['validation_split']['status']}
           - Records Processed: {summary['validation_split']['records']}
           - S3 Upload: {'Success' if summary['validation_split']['s3_uploaded'] else 'Failed'}
           - Azure SQL Insertion: {'Success' if summary['validation_split']['sql_inserted'] else 'Failed'}
        """

        return summary_message

    except Exception as e:
        return f"Error: {str(e)}"


if __name__ == "__main__":
    print(process_dataset())
