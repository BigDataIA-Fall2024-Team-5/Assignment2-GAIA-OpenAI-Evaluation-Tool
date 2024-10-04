# Use Python 3.11
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /backend

# Copy the requirements.txt file into the container
COPY requirements.txt /backend/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend files (fast_api, api_utils, data_handling, etc.)
COPY . .

# Expose the port for FastAPI (default: 8000)
EXPOSE 8000

# Command to run FastAPI
CMD ["uvicorn", "fast_api.fast_main:app", "--host", "0.0.0.0", "--port", "8000"]