import streamlit as st

# Define the callback function that will be called when the button is clicked
def go_to_login_page():
    # Clear session state except the 'page' key
    for key in list(st.session_state.keys()):
        if key != 'page': 
            del st.session_state[key]

    # Navigate to the login page
    st.session_state.page = 'login'
    
def session_expired_page():
    st.title("Session Expired")

    st.write("Your session has expired. For security reasons, we automatically log you out after a period of inactivity.")
    st.write("Please click the button below to log in again and continue using the application.")

    # Button to navigate back to the login page, using on_click to call the callback function
    st.button("Re-login", on_click=go_to_login_page)