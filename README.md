# Assignment2-GAIA-OpenAI-Evaluation-Tool

Please refer to the [README.md](openai-evaluation-streamlit/README.md) inside the **openai-evaluation-streamlit** folder for detailed documentation on setup, features, and usage instructions.

## OpenAI Evaluation App - Quick Overview

Welcome to the **OpenAI Evaluation App**! This application leverages OpenAI's ChatGPT model to evaluate a dataset of questions. The app is designed to streamline the evaluation process by handling datasets with associated PDF files, uploading them to cloud storage, and storing results in a database. It includes a user-friendly web interface built using **Streamlit**, providing clear visual insights through **Matplotlib**. For a full guide on setting up and running the application, please refer to the main [README.md](openai-evaluation-streamlit/README.md) file in the **openai-evaluation-streamlit** folder.

## Key Features

- **GAIA Dataset Integration**: The app loads questions from the GAIA benchmark dataset, allowing users to evaluate how well ChatGPT's answers match the "final answer" provided in the dataset.
- **File Retrieval**: The application preprocesses PDF file formats and uploads these files to AWS S3 for secure storage.
- **Airflow Pipeline**: We now support automation via Airflow pipelines, responsible for processing PDF files associated with questions. The pipeline uses **PyMuPDF** (open source) and **Amazon Textract** (API/enterprise option) to extract text from the PDF files. Users can choose between these two preprocessed outputs when sending a question with an associated PDF file for evaluation.
- **ChatGPT Evaluation**: The core functionality revolves around using ChatGPT to generate answers for each question. The generated responses are then compared to the final answers in the dataset to determine their accuracy.
- **AWS S3 and Azure SQL Integration**: Files are securely stored in AWS S3, and processed data (including file paths and evaluation results) is pushed to an Azure SQL database.
- **User and Admin Management**: The app includes a role-based access control system. Admins can manage users, promote them to admin roles, or delete them. The system also includes a registration page for new users.
- **FastAPI and JWT Authentication**: The application now integrates **FastAPI** for handling all API requests, with **JWT tokenization** securing all API calls. Only the registration and login endpoints are public, while all other API calls require a valid JWT token for access.
- **Database Setup**: A setup script (`setup_database.py`) initializes Azure SQL tables and inserts default users.
- **Visualization with Matplotlib**: The app provides a visual representation of the evaluation results, helping users easily interpret ChatGPT's performance.

## Why This App?

This app makes it easy to:
- **Automate the evaluation** of large datasets using OpenAI's language models.
- **Handle multimedia files** including PDF, with automated file preprocessing.
- **Automate text extraction** from PDF files using Airflow pipelines with PyMuPDF or Amazon Textract options.
- **Secure API calls** using FastAPI and JWT tokenization for authenticated access.
- **Manage users and roles** with admin-level control for promoting or deleting users.
- **Setup Azure SQL tables** with the provided `setup_database.py` script.
- **Visualize results** and store them for future analysis with the help of cloud storage (AWS S3) and database systems (Azure SQL).
- **Enhance efficiency** in handling complex datasets by automating data preprocessing and storage.

For detailed instructions on how to set up and run the application, please refer to the **Main [README.md](openai-evaluation-streamlit/README.md)** file.

## Attestation

WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR
ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK

**Contribution**

- **Dharun Karthick Ramaraj**: 33.33%
- **Nikhil Godalla**: 33.33%
- **Linata Rajendra Deshmukh**: 33.33%

## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](LICENSE) file.
