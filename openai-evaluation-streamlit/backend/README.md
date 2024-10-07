# Backend

This folder contains the core backend components that power the OpenAI Evaluation App. The backend is structured into three main subfolders for API utilities, data handling, and FastAPI endpoints. It also includes scripts for the main orchestration, database setup, and a Dockerfile for containerization.

## Files

- **main.py**:
  - This is the main orchestration script responsible for processing the GAIA dataset. It performs a sequence of tasks such as cloning the dataset repository, uploading files to AWS S3, and inserting processed data into Azure SQL. The `process_dataset()` function follows these steps:
    1. **Environment Setup**: Loads environment variables and sets up the Hugging Face cache directory.
    2. **Hugging Face Authentication**: Logs into Hugging Face using the provided token, enabling access to the GAIA dataset.
    3. **Repository Cloning**: Clones the GAIA dataset repository into a cache directory for processing.
    4. **Dataset Loading**: Loads the 'test' and 'validation' splits from the dataset for evaluation.
    5. **S3 and SQL Operations**: 
       - Initializes an S3 client and uploads files related to each dataset split to AWS S3, updating file paths.
       - Inserts the processed data into Azure SQL tables (`GaiaDataset_Test` and `GaiaDataset_Validation`).
    6. **Summary Report**: Generates a summary of each step, indicating whether each operation (S3 upload and SQL insertion) was successful.

- **setup_database.py**:
  - This script sets up the database schema for user management and results tracking. It creates the necessary tables in Azure SQL, including the `users` table (for user credentials and roles) and the `user_results` table (for storing ChatGPT evaluation outcomes). Default admin and user accounts are created during the setup process, with hashed passwords for security.

- **Dockerfile**:
  - The Dockerfile is used to containerize the backend application. It specifies the environment and dependencies required to run the FastAPI application within a container.
  - **Key Steps in the Dockerfile**:
    1. **Base Image**: Starts from `python:3.11-slim` to provide a lightweight Python environment.
    2. **Working Directory**: Sets `/backend` as the working directory within the container.
    3. **Dependency Installation**: Copies `requirements.txt` and installs dependencies using `pip`.
    4. **Copy Application Code**: Copies the backend code, including `fast_api`, `api_utils`, and `data_handling` folders.
    5. **Expose Port**: Exposes port `8000` for the FastAPI service.
    6. **Command to Run FastAPI**: The default command starts the FastAPI app using `uvicorn`, listening on all network interfaces at port `8000`.

    The FastAPI service can be accessed on `http://localhost:8000` once the container is running.

## Subfolders

1. **api_utils**:
   - Contains utility scripts for interacting with various APIs used in the app.
   - **Files**:
     - **amazon_s3_utils.py**: Manages file operations with AWS S3, including uploads and retrievals.
     - **azure_sql_utils.py**: Handles database interactions with Azure SQL, such as data insertion and querying.
     - **chatgpt_utils.py**: Integrates with OpenAI’s ChatGPT for generating responses and evaluating dataset questions.
   
2. **data_handling**:
   - Manages data-related operations, including data retrieval, preprocessing, and cleanup.
   - **Files**:
     - **clone_repo.py**: Clones the GAIA dataset repository for processing.
     - **delete_cache.py**: Handles cache clearing to maintain optimal performance.
     - **load_dataset.py**: Loads and prepares the GAIA dataset for evaluation and storage.

3. **fast_api**:
   - Contains FastAPI endpoints for the backend services. These endpoints handle requests for user management, data processing, and secure API interactions.
   - **Files**:
     - **auth.py**: Manages user authentication, including login, registration, and JWT token issuance.
     - **db_endpoints.py**: Provides API endpoints for database interactions related to user data and evaluation results.
     - **gpt_endpoints.py**: Handles endpoints for ChatGPT question evaluation.
     - **jwt_handler.py**: Provides functionality for JWT token generation and verification to secure API calls.
     - **pipeline_endpoints.py**: Exposes endpoints for triggering Airflow pipelines and other data-processing tasks.
     - **s3_endpoints.py**: Offers endpoints for interacting with AWS S3 for file uploads and downloads.

---

### Notes for `setup_database.py`:

- **Table Creation**: The script creates two primary tables:
  1. `users`: Stores user credentials, roles (admin or user), and hashed passwords.
  2. `user_results`: Tracks evaluation results for each user based on ChatGPT responses.

- **Default Users**: By default, the script seeds the database with an admin and a regular user for testing:
  - **Admin**: `username: admin`, `password: admin`
  - **User**: `username: user`, `password: user`

- **Environment Variables**: Database connection details are managed via environment variables. Ensure your `.env` file includes the necessary Azure SQL credentials (`AZURE_SQL_SERVER`, `AZURE_SQL_USER`, `AZURE_SQL_PASSWORD`, and `AZURE_SQL_DATABASE`).

Refer to the README files within each subfolder for more specific details on individual script functionalities.
