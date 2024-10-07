# fast_api

The **fast_api** folder contains the core FastAPI endpoints that power the backend services for the OpenAI Evaluation App. These endpoints provide functionality for user authentication, database operations, dataset processing, and interactions with AWS S3 and ChatGPT. Each endpoint is organized within its own script for modularity and ease of maintenance.

## Files

### auth.py
This script handles user authentication, providing endpoints for logging in and registering users. It uses JWT tokens to manage secure access to the application's endpoints.

#### Key Endpoints:
- **/login**: Authenticates a user by verifying their username and password, then issues a JWT token for authorized access to other endpoints.
- **/register**: Registers a new user, ensuring the password meets security requirements. It hashes the password before storing it in the database.

### db_endpoints.py
This script provides endpoints for managing users and accessing data stored in Azure SQL. It includes endpoints for admin functions, user-specific queries, and updating evaluation results.

#### Key Endpoints:
- **/users**: Retrieves all users in the database. Accessible to admin users.
- **/users/{user_id}**: Deletes a specified user. Requires admin privileges.
- **/users/{user_id}/promote**: Promotes a specified user to the admin role.
- **/questions**: Retrieves all questions from the specified dataset split (e.g., 'test' or 'validation').
- **/user_results/{user_id}**: Fetches evaluation results specific to a user for a given dataset split.
- **/update_result**: Updates a user’s evaluation result based on ChatGPT's response and the expected answer.

### fast_main.py
This is the main entry script for the FastAPI application. It initializes the app, sets up global configurations for AWS S3, OpenAI, and Azure SQL on startup, and includes routers for authentication, S3 operations, ChatGPT interactions, database, and pipeline operations.

#### Key Features:
- **Startup Event**: Initializes S3 client, OpenAI API, and Azure SQL connection settings.
- **Routers Included**: Imports routers from other scripts, mapping them to their respective prefixes and tags for structured endpoint access.
- **Root Endpoint**: Provides a basic health check endpoint at `/` to confirm the app is running.

### gpt_endpoints.py
This script handles interactions with ChatGPT, including generating responses and comparing them against expected answers. It provides endpoints to retrieve ChatGPT responses for user questions and evaluate their accuracy.

#### Key Endpoints:
- **/ask**: Sends a question to ChatGPT and returns the generated response.
- **/compare**: Compares ChatGPT's response with the expected answer based on a structured prompt and returns a match status.

### jwt_handler.py
This script manages JWT token creation and validation, as well as password hashing and validation. It includes functions to ensure password strength and securely handle user authentication.

#### Key Functions:
- **create_access_token**: Creates a JWT token for authenticated sessions.
- **decode_token**: Decodes and verifies the JWT token, raising errors if invalid or expired.
- **validate_password_strength**: Ensures passwords meet security requirements, such as length and character composition.
- **hash_password** and **verify_password**: Provide secure hashing and verification for user passwords.

### pipeline_endpoints.py
This script provides endpoints to trigger data processing tasks, specifically for managing the GAIA dataset. It allows users to start data processing workflows that integrate with other backend services.

#### Key Endpoints:
- **/process-dataset**: Initiates the dataset processing pipeline, enabling automated loading, preprocessing, and storage of GAIA dataset splits.

### s3_endpoints.py
This script provides endpoints for interacting with files stored in AWS S3. It includes functionality for retrieving preprocessed PDF summaries stored in S3 based on the selected extraction method.

#### Key Endpoints:
- **/fetch_pdf_summary**: Retrieves a summary of a PDF file from S3, processed either through Amazon Textract or PyMuPDF.

---

These scripts collectively form the backend services for the OpenAI Evaluation App, enabling secure, scalable, and modular interactions with external services like AWS, Azure SQL, and OpenAI's ChatGPT. The **fast_api** folder provides a structured approach to managing authentication, data storage, processing pipelines, and evaluation operations.
