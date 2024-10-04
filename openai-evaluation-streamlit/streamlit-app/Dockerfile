# Use Python 3.11 as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /streamlit-app

# Copy the requirements.txt file into the container
COPY requirements.txt /streamlit-app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application (newapp.py and streamlit_pages)
COPY . .

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run Streamlit app
CMD ["streamlit", "run", "newapp.py", "--server.port=8501", "--server.address=0.0.0.0"]