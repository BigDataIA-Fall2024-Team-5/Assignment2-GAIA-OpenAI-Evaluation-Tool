import os
from dotenv import load_dotenv
import streamlit as st
import requests

load_dotenv()

fastapi_url = os.getenv("FASTAPI_URL")

registration_url = f"{fastapi_url}/auth/register"

# Callback function to go back to login page
def go_to_login():
    # Reset registration success and input values when going back
    st.session_state['registration_success'] = False
    st.session_state['username'] = ''
    st.session_state['password'] = ''
    st.session_state['confirm_password'] = ''
    st.session_state.page = 'login'

# Function to handle the registration logic
def handle_register():
    username = st.session_state['username']
    password = st.session_state['password']
    confirm_password = st.session_state['confirm_password']
    
    # Check if any of the fields are empty
    if not username or not password or not confirm_password:
        st.error("All fields are required.")
    else:
        # Prepare data for FastAPI registration
        registration_data = {
            "username": username,
            "password": password,
            "confirm_password": confirm_password
        }

        try:
            with st.spinner('Creating account...'):
                # Make POST request to FastAPI
                response = requests.post(registration_url, json=registration_data)
                
                if response.status_code == 200:
                    st.success("Account created successfully! Please log in with your new credentials.")
                    st.session_state['registration_success'] = True
                    # Clear the input fields after successful registration
                    st.session_state['username'] = ''
                    st.session_state['password'] = ''
                    st.session_state['confirm_password'] = ''
                elif response.status_code == 400:
                    st.error(f"Registration failed: {response.json().get('detail', 'Bad request')}")
                elif response.status_code == 409:
                    st.error(f"Registration failed: Username '{username}' already exists.")
                elif response.status_code == 500:
                    st.error("Server error. Please try again later.")
                else:
                    st.error(f"Unexpected error: {response.status_code}")

        except requests.exceptions.RequestException as e:
            st.error(f"Registration request failed: {e}")

# Registration page UI
def register_page():
    st.title("Register a New Account")

    # Ensure that session state variables are initialized
    if 'registration_success' not in st.session_state:
        st.session_state['registration_success'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = ''
    if 'password' not in st.session_state:
        st.session_state['password'] = ''
    if 'confirm_password' not in st.session_state:
        st.session_state['confirm_password'] = ''

    # Show the registration form if the registration hasn't been successful yet
    if not st.session_state['registration_success']:
        # Display input fields without the form
        st.session_state['username'] = st.text_input("Username", value=st.session_state['username'])
        st.session_state['password'] = st.text_input("Password", type="password", value=st.session_state['password'])
        st.session_state['confirm_password'] = st.text_input("Confirm Password", type="password", value=st.session_state['confirm_password'])

        # Use a regular button with on_click to handle registration
        st.button("Register", on_click=handle_register)

    # Always display the Back to Login button, and reset registration success when clicked
    st.button("Back to Login", on_click=go_to_login, key="manual_login_button")
