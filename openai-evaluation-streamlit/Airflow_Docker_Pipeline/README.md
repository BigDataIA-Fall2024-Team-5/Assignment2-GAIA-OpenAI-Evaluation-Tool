# Airflow Docker Pipeline

This directory contains the setup and configuration for running Airflow with Docker to process PDF files stored in AWS S3. The pipeline consists of two DAGs for text extraction from PDFs: one using PyMuPDF (open-source) and the other using Amazon Textract (enterprise solution). The extracted text is stored back in S3 for further processing in downstream tasks.

## Table of Contents
- [Folder Structure](#folder-structure)
- [DAGs Overview](#dags-overview)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [License](#license)

## Folder Structure

📦 Airflow_Docker_Pipeline  
┣ 📂 config              # Configuration files for Airflow  
┣ 📂 dags                # Directory containing Airflow DAG scripts  
┃ ┣ 📜 pymupdf_extraction_dag.py   # DAG for processing PDFs with PyMuPDF  
┃ ┗ 📜 textract_extraction_dag.py   # DAG for processing PDFs with Amazon Textract  
┣ 📂 logs                # Directory where Airflow logs are stored  
┣ 📂 plugins             # Plugins folder for additional Airflow plugins  
┣ 📜 .env                # Environment variables file for Airflow and AWS credentials  
┣ 📜 docker-compose.yaml # Docker Compose file for setting up Airflow with dependencies  
┗ 📜 Dockerfile          # Dockerfile for installing additional dependencies in Airflow  
 

## DAGs Overview

### 1. PyMuPDF Extraction DAG (`pymupdf_extraction_dag.py`)
- **Description**: This DAG processes PDF files from S3 using the PyMuPDF library for text extraction.
- **Input**: PDFs located in `bronze/test/` and `bronze/validation/` directories in the S3 bucket.
- **Output**: Extracted text files uploaded to the `silver/pdf/pymupdf/` directory in the same S3 bucket.
- **Components**:
  - Lists PDF files in the S3 bucket.
  - Downloads each PDF file, extracts text using PyMuPDF, and uploads the text back to S3.

### 2. Amazon Textract Extraction DAG (`textract_extraction_dag.py`)
- **Description**: This DAG uses Amazon Textract to extract text from PDF files stored in the S3 bucket.
- **Input**: PDFs located in `bronze/test/` and `bronze/validation/` directories in the S3 bucket.
- **Output**: Extracted text files uploaded to the `silver/pdf/textract/` directory in the same S3 bucket.
- **Components**:
  - Lists PDF files in the S3 bucket.
  - Submits each PDF file to Amazon Textract for text extraction and waits for the processing to complete.
  - Uploads the extracted text back to S3.

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed on your machine.
- AWS credentials with access to S3 and Textract services.

### 1. Clone the Repository
git clone https://github.com/BigDataIA-Fall2024-Team-5/Assignment2-GAIA-OpenAI-Evaluation-Tool.git
cd Airflow_Docker_Pipeline

### 2. Configure Environment Variables
- Create a `.env` file in the root directory of the `Airflow_Docker_Pipeline` folder and add the following variables:

  AWS_ACCESS_KEY=your_aws_access_key  
  AWS_SECRET_KEY=your_aws_secret_key  
  AWS_REGION=your_aws_region  
  S3_BUCKET_NAME=your_s3_bucket_name  
  INPUT_PREFIX=bronze/  
  OUTPUT_PREFIX=silver/  

### 3. Start the Airflow Docker Containers
- Run the following command to build and start the Airflow containers:
  
  docker-compose up --build  

- Access the Airflow UI by navigating to `http://localhost:8080` in your web browser.

### 4. Trigger the DAGs
- In the Airflow UI, activate and trigger the `pymupdf_extraction_pipeline` and `textract_extraction_pipeline` DAGs. These will process PDFs using PyMuPDF and Textract respectively, then upload the extracted text to the configured S3 bucket.

## Usage

This project preprocesses PDF files associated with questions in the GAIA dataset, utilizing either **PyMuPDF** or **Amazon Textract**. Since the ChatGPT API doesn’t support direct PDF file input, text extraction is performed to convert the PDFs into text data, which can then be sent to the ChatGPT API for processing.

To get started with using this application:

1. **Start Airflow** to preprocess PDF files:
   - Navigate to the `Airflow_Docker_Pipeline` directory and start the Airflow Docker containers:

     ```bash
     cd Airflow_Docker_Pipeline
     docker-compose up -d
     ```

2. **Trigger the DAGs** in Airflow:
   - Access the Airflow UI by going to `http://localhost:8080` in your browser.
   - Manually trigger the `pymupdf_extraction_pipeline` and/or `textract_extraction_pipeline` to process the PDF files. These DAGs will extract text from the PDFs using the selected method (PyMuPDF or Textract) and upload the extracted text to your specified AWS S3 bucket.

3. **Use the Streamlit Application** to send questions and extracted text to ChatGPT for evaluation:
   - Once the preprocessing is complete, launch the Streamlit app by navigating to the `streamlit-app` folder:

     ```bash
     cd streamlit-app
     docker-compose up -d
     ```

   - Open your browser and go to `http://localhost:8501`.
   - Log in, select questions, and review the answers generated by ChatGPT, which uses the preprocessed text for questions that require it.

## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](../../LICENSE) file in the root directory.

