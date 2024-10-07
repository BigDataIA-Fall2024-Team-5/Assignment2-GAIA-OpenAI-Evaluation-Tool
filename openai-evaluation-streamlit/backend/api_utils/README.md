# api_utils

The **api_utils** folder contains utility scripts to facilitate interactions with various APIs and services used by the OpenAI Evaluation App. These utilities streamline operations with AWS S3, Azure SQL, and OpenAI's ChatGPT, enabling file management, data storage, and question evaluation.

## Files

### amazon_s3_utils.py
This script handles file operations with AWS S3, such as uploading, downloading, and finding files within a repository structure. It is responsible for managing the S3 client and providing functions to interact with files stored in AWS.

#### Key Functions:
- **init_s3_client**: Initializes an S3 client using the provided AWS credentials. It can also use the default AWS credential chain if credentials are not specified.
- **initialize_s3_client_and_bucket**: Sets up the S3 client and stores it globally for future use, simplifying the process of accessing S3.
- **get_s3_client**: Retrieves the globally initialized S3 client.
- **find_file_in_repo**: Locates a file in the specified directory based on the dataset split (e.g., 'test' or 'validation').
- **upload_files_to_s3_and_update_paths**: Uploads files to a designated S3 bucket and updates the paths in the dataset to reflect the S3 URLs. It also prints a summary of uploaded files and tracks file types.
- **download_file_from_s3**: Downloads a specified file from S3 to a local directory.
- **read_pdf_summary_from_s3**: Retrieves the content of a PDF summary file stored in S3, allowing users to choose between Amazon Textract and PyMuPDF extraction methods.

### azure_sql_utils.py
This script provides utilities for interacting with Azure SQL Database. It enables connection setup, data insertion, and fetching operations, specifically designed to handle user data and ChatGPT evaluation results.

#### Key Functions:
- **set_sqlalchemy_connection_params**: Sets global SQLAlchemy connection parameters, such as server, user, and database name.
- **get_sqlalchemy_connection_string**: Constructs and returns the SQLAlchemy connection string based on the set parameters.
- **insert_dataframe_to_sql**: Inserts a DataFrame into Azure SQL, replacing any existing data in the target table. This is primarily used to store the GAIA dataset after processing.
- **fetch_all_questions**: Retrieves all questions from a specified table in Azure SQL and returns them as a JSON-serializable list.
- **fetch_user_results**: Fetches user-specific results filtered by dataset split from the database, returning JSON-compatible data.
- **update_user_result_in_db**: Updates or inserts user-specific results, allowing both existing and new results to be handled seamlessly.
- **fetch_user_from_sql**: Retrieves user information based on the username for authentication purposes.
- **insert_user_to_sql**: Inserts a new user with a hashed password into the `users` table.
- **fetch_all_users**: Fetches a list of all users in the database.
- **remove_user**: Deletes a user and their associated results from the database.
- **promote_to_admin**: Updates a user's role to admin in the database.

### chatgpt_utils.py
This script integrates with OpenAI's ChatGPT API to handle question evaluation and result comparison. It is configured to process user queries and validate ChatGPT's responses against a reference answer.

#### Key Functions:
- **init_openai**: Initializes the OpenAI API client using the provided API key. This function needs to be called before any API requests.
- **get_chatgpt_response**: Sends a question along with optional instructions and preprocessed data to ChatGPT, then retrieves a concise response. This function is configured to limit the response to a maximum number of sentences, words, and tokens.
- **compare_and_update_status**: Compares ChatGPT's response with the expected answer using a prompt designed for accuracy evaluation. The function returns a status indicating whether the response matches the original answer based on key information and factual accuracy.

These scripts collectively enhance the backend's ability to manage cloud storage, handle SQL operations, and interact with ChatGPT for seamless question evaluation.
