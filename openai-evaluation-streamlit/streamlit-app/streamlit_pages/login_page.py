import os
from dotenv import load_dotenv
import streamlit as st
import requests

# Load environment variables from .env file
load_dotenv()

fastapi_url = os.getenv("FASTAPI_URL")

login_url = f"{fastapi_url}/auth/login"

def go_to_register():
    st.session_state['login_success'] = False
    st.session_state['user'] = ''
    st.session_state['username'] = ''  # Clear username as well
    st.session_state['password'] = ''
    st.session_state.page = 'register'

# Callback function to handle login
def on_login_click():
    username = st.session_state['username']
    password = st.session_state['password']
    
    login_data = {"username": username, "password": password}

    try:
        with st.spinner('Logging in...'):
            response = requests.post(login_url, json=login_data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Store the retrieved values in session state
                st.session_state['jwt_token'] = result['access_token']
                st.session_state['user_id'] = result.get('user_id', None)
                st.session_state['role'] = result['role'] 

                st.session_state['user'] = result['username'] 
                st.session_state['username'] = result['username']  
                st.session_state['login_success'] = True
                
                st.success(f"Welcome {result['username']}!")
                
                # Redirect based on role
                if result['role'] == 'admin':
                    st.session_state.page = 'admin_page'
                else:
                    st.session_state.page = 'user_page'
            
            elif response.status_code == 404:
                st.error("Login failed: User not found.")
            
            elif response.status_code == 401:
                st.error("Login failed: Incorrect password.")
            
            elif response.status_code == 400:
                st.error("Login failed: Bad request. Please check your input.")
            
            elif response.status_code == 500:
                st.error("Login failed: Server error. Please try again later.")
            
            else:
                st.error(f"Unexpected error: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        st.error(f"Login request failed: {e}")

# Login page UI
def login_page():
    st.title("Login to Your Account")
    
    # Display login form if login hasn't been successful yet
    if not st.session_state['login_success']:
        st.text_input("Username", key='username', value=st.session_state['username'])
        st.text_input("Password", key='password', type="password", value=st.session_state['password'])

        # Trigger login when login button is clicked
        st.button("Login", on_click=on_login_click)
        st.button("Create New Account", on_click=go_to_register, key="register_button")

