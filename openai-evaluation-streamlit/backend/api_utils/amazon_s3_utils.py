import os
import boto3
import logging
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

logger = logging.getLogger("uvicorn")

class S3Client:
    def __init__(self, client, bucket_name):
        self.client = client
        self.bucket_name = bucket_name

# Global variable for S3 client instance
s3_client_instance = None

# Initialize AWS S3 client
def init_s3_client(access_key=None, secret_key=None, session_token=None, region=None):
    """
    Initialize AWS S3 client.
    If no credentials are provided, the default AWS credential provider chain will be used.
    
    :param access_key: AWS Access Key ID
    :param secret_key: AWS Secret Access Key
    :param session_token: AWS Session Token (optional for temporary credentials)
    :param region: AWS region (optional)
    :return: Boto3 S3 client object or None if initialization fails
    """
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            aws_session_token=session_token,
            region_name=region
        )
        return s3_client
    except NoCredentialsError:
        raise NoCredentialsError("No AWS credentials found.")
    except PartialCredentialsError:
        raise PartialCredentialsError("Incomplete AWS credentials provided.")
    except Exception as e:
        raise Exception(f"Failed to initialize S3 client: {str(e)}")

# Function to initialize and store the S3 client globally
def initialize_s3_client_and_bucket(aws_access_key, aws_secret_key, bucket_name):
    global s3_client_instance
    if not s3_client_instance:
        s3_client = init_s3_client(aws_access_key, aws_secret_key)
        s3_client_instance = S3Client(client=s3_client, bucket_name=bucket_name)
    return s3_client_instance

# Function to get the S3 client instance
def get_s3_client():
    global s3_client_instance
    if not s3_client_instance:
        raise Exception("S3 client not initialized.")
    return s3_client_instance

# Find a file by name in the repository based on the split (e.g., 'test' or 'validation')
def find_file_in_repo(file_name, repo_dir, split_name):
    """
    Search for a file in the given repository directory for a specific split.
    
    :param file_name: Name of the file to find
    :param repo_dir: The base repository directory
    :param split_name: The dataset split (e.g., 'test', 'validation')
    :return: Path to the file if found, else None
    """
    search_path = os.path.join(repo_dir, "2023", split_name, file_name)
    if os.path.exists(search_path):
        print(f"File {file_name} found at {search_path}")
        return search_path
    else:
        print(f"File {file_name} not found in {search_path}")
        return None

# Upload files to S3 and update paths in the DataFrame
def upload_files_to_s3_and_update_paths(dataset, s3_client, bucket_name, repo_dir, split_name):
    """
    Upload files to S3 and update the file paths in the DataFrame.
    
    :param dataset: DataFrame containing the dataset with 'file_name' and 'file_path' columns
    :param s3_client: Initialized S3 client for uploading files
    :param bucket_name: Name of the S3 bucket
    :param repo_dir: Base directory of the repository where files are stored
    :param split_name: The split name of the dataset (e.g., 'test', 'validation')
    :return: The updated DataFrame with S3 file paths
    """
    total_files = 0
    files_uploaded = 0
    file_paths_updated = 0
    uploaded_file_types = set()  # Set to keep track of uploaded file types

    # Define the S3 folder as 'bronze/{split_name}/'
    s3_folder = f"bronze/{split_name}/"

    for index, row in dataset.iterrows():
        if 'file_name' in row and row['file_name']:
            total_files += 1  # Increment total file name counter

            # Find the file in the repository based on the split
            local_file_path = find_file_in_repo(row['file_name'], repo_dir, split_name)
            if local_file_path:
                # Define the S3 key, which includes the folder and the file name
                s3_key = f"{s3_folder}{row['file_name']}"

                # Upload to S3 (will overwrite if the file already exists)
                try:
                    s3_client.upload_file(local_file_path, bucket_name, s3_key)
                    # Update file path to S3 URL
                    dataset.at[index, 'file_path'] = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
                    print(f"Uploaded {row['file_name']} to S3 under {s3_folder}.")
                    files_uploaded += 1  # Increment files uploaded counter
                    file_paths_updated += 1  # Increment file paths updated counter

                    # Add the file type to the set
                    file_extension = os.path.splitext(row['file_name'])[1].lower()
                    uploaded_file_types.add(file_extension)  # Track unique file types
                except Exception as e:
                    print(f"Error uploading {row['file_name']} to S3: {e}")
            else:
                print(f"File {row['file_name']} not found in repository.")
    
    print(f"\nSummary for {split_name} split:")
    print(f"Total rows with file names: {total_files}")
    print(f"Total files uploaded to S3: {files_uploaded}")
    print(f"Total file paths updated in DataFrame: {file_paths_updated}")
    print(f"Uploaded file types: {', '.join(uploaded_file_types)}")

    return dataset

# Download file from S3
def download_file_from_s3(file_name, bucket_name, download_dir, s3_client):
    if not file_name or not bucket_name:
        print(f"Error: file_name or bucket_name is None. file_name: {file_name}, bucket_name: {bucket_name}")
        return None
    
    os.makedirs(download_dir, exist_ok=True)  # Create download directory if not exists
    file_path = os.path.join(download_dir, file_name)  # Define the local file path

    try:
        # Attempt to download the file from S3
        s3_client.download_file(bucket_name, file_name, file_path)
        print(f"Downloaded {file_name} from S3 to {file_path}")
        return file_path  # Return the path of the downloaded file
    except Exception as e:
        print(f"Error downloading {file_name} from S3: {e}")
        return None

# Read a PDF summary from S3
def read_pdf_summary_from_s3(file_name, extraction_method, s3_client, bucket_name):
    try:
        # Strip the '.pdf' extension from the file name if it exists
        file_base_name = file_name[:-4] if file_name.endswith('.pdf') else file_name

        # Select the folder based on the extraction method
        folder = "silver/pdf/textract" if extraction_method == "Amazon Textract" else "silver/pdf/pymupdf"
        summary_file = f"{folder}/{file_base_name}.txt"

        # Download the summary file from S3
        obj = s3_client.get_object(Bucket=bucket_name, Key=summary_file)
        summary = obj['Body'].read().decode('utf-8')
        return summary
    except s3_client.exceptions.NoSuchKey:
        return None
    except Exception as e:
        print(f"Error reading PDF summary from {extraction_method}: {e}")
        return None