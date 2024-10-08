# Use Python 3.11
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /backend

# Install system dependencies for pyodbc and SQL Server ODBC driver
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl gnupg unixodbc unixodbc-dev && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | tee /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt file into the container
COPY requirements.txt /backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files (fast_api, api_utils, data_handling, etc.)
COPY . .

# Expose the port for FastAPI (default: 8000)
EXPOSE 8000

# Command to run FastAPI
CMD ["uvicorn", "fast_api.fast_main:app", "--host", "0.0.0.0", "--port", "8000"]
