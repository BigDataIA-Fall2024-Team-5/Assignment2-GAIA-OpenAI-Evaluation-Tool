import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

fastapi_url = os.getenv("FASTAPI_URL")
pipeline_url = f"{fastapi_url}/pipeline/process-dataset"

def go_to_login_page():
    # Clear all session state keys except 'page'
    for key in list(st.session_state.keys()):
        if key != 'page': 
            del st.session_state[key]
    
    # Set the page to login page
    st.session_state.page = 'login'

def gotoexpirypage():
    st.session_state.page = 'session_expired'
    st.experimental_rerun()

# Callback to trigger dataset processing logic with JWT authentication
def run_dataset_processing():
    try:
        # Retrieve the JWT token from session state
        token = st.session_state.get('jwt_token')
        if not token:
            st.error("No JWT token found. Please log in first.")
            return
        
        # Set up the headers with the JWT token
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Send POST request to FastAPI to start dataset processing
        response = requests.post(pipeline_url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            # Store the result in session state for display
            st.session_state['dataset_processing_status'] = "Dataset Processing Complete"
            st.session_state['dataset_processing_output'] = result['message']
        elif response.status_code == 401:
            # Handle unauthorized access (JWT token issues)
            st.session_state['dataset_processing_status'] = "Unauthorized access. Please log in again."
            # Add a button to redirect to the login page
            gotoexpirypage()
            return None
        else:
            st.session_state['dataset_processing_status'] = f"Error: {response.status_code} - {response.text}"

    except Exception as e:
        st.session_state['dataset_processing_status'] = f"An unexpected error occurred: {e}"

def admin_dataset_management_page():
    # Ensure session state variables are initialized
    if 'dataset_processing_status' not in st.session_state:
        st.session_state['dataset_processing_status'] = ''
    if 'dataset_processing_output' not in st.session_state:
        st.session_state['dataset_processing_output'] = ''

    st.title("Dataset Management")

    st.write("""
    This page allows you to manage the GAIA dataset. You can trigger the entire dataset processing pipeline,
    which includes cloning the repository, loading the dataset, uploading files to S3, and inserting records
    into Azure SQL.
    """)

    # Provide a button to trigger the main process
    st.button("Process Dataset", on_click=run_dataset_processing)

    # Check and display dataset processing status and output
    if st.session_state['dataset_processing_status']:
        st.write(st.session_state['dataset_processing_status'])
        st.text(st.session_state['dataset_processing_output'])

    # Back button to return to the Admin page
    st.button("Back to Admin", on_click=lambda: st.session_state.update(page='admin_page'))
