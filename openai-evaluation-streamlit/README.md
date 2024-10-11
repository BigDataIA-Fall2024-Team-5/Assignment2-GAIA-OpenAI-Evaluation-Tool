# Assignment2-GAIA-OpenAI-Evaluation-Tool

- **Code Lab Link: [[CodeLabs](https://codelabs-preview.appspot.com/?file_id=1jgfeDPBayTyQ2fWvncs1wMqrmskJkVCiFLTdYfeTh1k#0)] [[Google Drive Link](https://docs.google.com/document/d/1r1LFc9etDrDeeF5DGEBVaOHluS64qKRh/edit?usp=drive_link&ouid=117337672169848470672&rtpof=true&sd=true)] [[Github Location](docs/Assignment2_OpenAI_Evaluation_App.docx)]**
- **Presentation Video Link: [[Google Drive Link](https://drive.google.com/file/d/1FgN-lEHbVfYQ6hQLEsMZnDbP6LPa-EFJ/view?usp=drive_link)] [[Github Location](demo/Assignment%202%20demo.mp4)]**
- **FAST API Link: [[FastAPI deployed in EC2 Instance](http://3.145.73.49:8000/)]**
- **Streamlit Application Link: [[Streamlit Aookucation deployed in EC2 Instance](http://3.145.73.49:8501/)]**
- **Docker Repository: [[Docker Repository](https://hub.docker.com/repositories/dharunramaraj)]**
- **PDF Evaluation Link: [[Google Drive Link](https://drive.google.com/file/d/1W5_tsqub1gHULE9xUUKbs1mgiOS16O1t/view?usp=sharing)] [[Github Location](docs/PDF_Extraction_API_Evaluation.pdf)]**
- **Github Projects: [[Github projects](https://github.com/orgs/BigDataIA-Fall2024-Team-5/projects/4)]**




## OpenAI Evaluation App - Overview

This application leverages OpenAI's ChatGPT model to evaluate a dataset of questions from the GAIA dataset. The app automates text extraction from PDF files, uploads them to AWS S3, and stores evaluation results in an Azure SQL database. It includes a web interface built with **Streamlit**, integrated with **FastAPI** for backend services, and secured using JWT tokenization. The app is fully containerized using **Docker Compose** for easy deployment.

**Structural Diagram**:
![Structural Diagram](diagrams/Structural%20Diagram.png)

## Table of Contents

1. [Key Features](#key-features)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Usage](#usage)
5. [License](#license)

## Key Features

- **GAIA Dataset Integration**: The app loads questions from the GAIA benchmark dataset, enabling users to evaluate ChatGPT's answers compared to a predefined "final answer" for each question.
- **Automated Text Extraction with Airflow**: An Airflow pipeline is responsible for processing PDF files associated with the GAIA dataset questions. The pipeline utilizes **PyMuPDF** (open source) and **Amazon Textract** (enterprise option) for text extraction, giving users the flexibility to choose which preprocessed data source to use.
- **ChatGPT Evaluation**: The app generates answers using ChatGPT for each question in the dataset. For questions linked to PDF files, the preprocessed text from PyMuPDF or Amazon Textract is included in the evaluation request.
- **AWS S3 and Azure SQL Integration**: The app securely stores processed files in AWS S3 and saves evaluation data (including file paths and results) in an Azure SQL database.
- **User and Admin Management with FastAPI**: The application includes role-based access with JWT tokenization. Admin users can manage datasets and promote or delete users.
- **Secure API with JWT Authentication**: FastAPI endpoints are secured with JWT tokens. Only registration and login endpoints are public, while all other API calls require a valid JWT token.
- **Visualization with Matplotlib**: The app includes visualization features using **Matplotlib** to help users interpret ChatGPT’s evaluation performance.

## Project Structure

📦 Assignment2-GAIA-OpenAI-Evaluation-Tool  
├── 📂 openai-evaluation-streamlit  
│   ├── 📂 Airflow_Docker_Pipeline        # Airflow DAGs and pipeline scripts for PDF processing  
│   ├── 📂 backend                        # Backend folder with FastAPI service and utilities  
│   │   ├── 📂 api_utils                  # Utilities for API interactions (AWS, Azure SQL, ChatGPT)  
│   │   ├── 📂 data_handling              # Data processing scripts (cloning repo, loading dataset)  
│   │   ├── 📂 fast_api                   # FastAPI endpoints and authentication  
│   │   ├── 📜 Dockerfile                 # Dockerfile for FastAPI  
│   │   ├── 📜 main.py                    # Main Pipeline for loading backend  
│   │   ├── 📜 requirements.txt           # Dependencies for FastAPI  
│   │   └── 📜 setup_database.py          # Database setup script  
│   ├── 📂 streamlit-app                  # Streamlit app with multiple pages  
│   │   ├── 📂 streamlit_pages            # Streamlit pages for different functionalities  
│   │   ├── 📜 Dockerfile                 # Dockerfile for Streamlit app  
│   │   ├── 📜 newapp.py                  # Main entry point for the Streamlit app  
│   │   └── 📜 requirements.txt           # Dependencies for Streamlit  
├── 📜 docker-compose.yml                 # Docker Compose configuration for FastAPI and Streamlit  
├── 📜 .env                               # Environment variables for the application  
├── 📜 poetry.lock                        # Poetry lock file for dependency management  
├── 📜 pyproject.toml                     # Poetry configuration file  
└── 📜 LICENSE                            # MIT License file  


### Folder Documentation

- **[Airflow_Docker_Pipeline](Airflow_Docker_Pipeline/README.md)**: Contains the Airflow DAGs and scripts for automating PDF processing workflows.
- **[backend](backend/README.md)**: Includes the FastAPI backend service for authentication, dataset processing, and API utilities.
  - **[api_utils](backend/api_utils/README.md)**: Utility scripts for interacting with AWS S3, Azure SQL, and the ChatGPT API, providing essential backend functionality.
  - **[fast_api](backend/fast_api/README.md)**: FastAPI endpoints for authentication, dataset management, and pipeline processing, along with JWT-based security features.
  - **[data_handling](backend/data_handling/README.md)**: Scripts for cloning repositories, loading datasets, and preprocessing data, enabling smooth data operations.
- **[streamlit-app](streamlit-app/README.md)**: The Streamlit application with a multi-page setup for user interactions, visualizations, and admin functions.
   - **[streamlit_pages](streamlit-app/streamlit_pages/README.md)**: Detailed documentation for each Streamlit page within the `streamlit-app`, covering the login, registration, user dashboard, and admin functionalities.

### Backend Workflow Diagram
![Backend Workflow Diagram](diagrams/Backend%20Workflow%20Diagram.png)

## Installation

To set up the application locally, follow these steps:

### Prerequisites

Make sure you have the following installed:
- Docker and Docker Compose
- Python 3.11
- AWS account for S3 storage
- Azure SQL database
- OpenAI API key
- Hugging Face account and token

1. Clone the Repository and Navigate to the Directory:

   git clone https://github.com/BigDataIA-Fall2024-Team-5/Assignment2-GAIA-OpenAI-Evaluation-Tool.git 
   cd openai-evaluation-streamlit  

2. Set Up Environment Variables:

   Create a `.env` file in the root of the project and add your credentials:

   HF_TOKEN='your-hugging-face-token'  
   OPENAI_API_KEY='your-openai-api-key'  
   AWS_ACCESS_KEY='your-aws-access-key'  
   AWS_SECRET_KEY='your-aws-secret-key'  
   S3_BUCKET_NAME='your-s3-bucket-name'  
   AZURE_SQL_SERVER='your-azure-sql-server'  
   AZURE_SQL_DATABASE='your-azure-sql-database'  
   AZURE_SQL_USER='your-azure-sql-username'  
   AZURE_SQL_PASSWORD='your-azure-sql-password'  
   FASTAPI_URL='http://fastapi:8000'  

3. Run Initial Setup Scripts:

   Before starting the Docker containers, run the following scripts to set up the database and process the dataset:
   cd backend
   python -m setup_database.py
   python -m main.py
   cd ..

4. Build and Run with Docker Compose:

   From the root directory, use Docker Compose to build and start the containers:

   docker-compose up --build  

   This command will start both the FastAPI service on `http://localhost:8000` and the Streamlit app on `http://localhost:8501`.

## Usage

Once the application is up and running, you can access it at `http://localhost:8501`. The main features are accessible through the Streamlit interface:

1. **User Registration and Login**:
   - Navigate to the login page to create an account or log in.
   - Once logged in, you will receive a JWT token to access secure API endpoints.

2. **Question Evaluation**:
   - Load and evaluate questions from the GAIA dataset. For questions with associated PDF files, you can choose between text extracted by PyMuPDF or Amazon Textract.

3. **Admin Dashboard**:
   - Admin users can manage the dataset, promote or delete users.

4. **Visualization**:
   - View graphical summaries of ChatGPT’s performance on the questions, which helps in assessing the accuracy of the model.

## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](../LICENSE) file.
