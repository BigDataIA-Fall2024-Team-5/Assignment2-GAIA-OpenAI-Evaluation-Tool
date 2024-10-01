import streamlit as st
import requests

# Define your FastAPI endpoint
fastapi_url = "http://127.0.0.1:8000/auth/login"

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
            response = requests.post(fastapi_url, json=login_data)
            
            if response.status_code == 200:
                result = response.json()
                
                # Store the retrieved values in session state
                st.session_state['jwt_token'] = result['access_token']
                st.session_state['role'] = result['role']
                st.session_state['user'] = result['username']  # Set 'user'
                st.session_state['username'] = result['username']  # Set 'username' too
                st.session_state['user_id'] = result.get('user_id', None) 
                st.session_state['login_success'] = True
                
                st.success(f"Welcome {result['username']}!")
                
                # Debug to see if user_id and username are passed correctly
                st.write(f"Logged in as: {st.session_state['username']}, User: {st.session_state['user']}, User ID: {st.session_state['user_id']}")
                
                # Redirect based on role
                if result['role'] == 'admin':
                    st.session_state.page = 'admin'
                else:
                    st.session_state.page = 'main'
            
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

# Logout function to clear session
def logout():
    # Preserve 'page' in session state while clearing other session state variables
    for key in list(st.session_state.keys()):
        if key != 'page':
            del st.session_state[key]
    st.session_state['login_success'] = False
    st.session_state.page = 'login'

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

    # Display logout button if login was successful
    if st.session_state['login_success']:
        st.button("Log Out", on_click=logout)
