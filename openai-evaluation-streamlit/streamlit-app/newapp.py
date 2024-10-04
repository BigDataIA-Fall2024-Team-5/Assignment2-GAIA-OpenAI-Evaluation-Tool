import streamlit as st
from streamlit_pages.login_page import login_page
from streamlit_pages.register_page import register_page
from streamlit_pages.admin_page import admin_page
from streamlit_pages.admin_dataset_management import admin_dataset_management_page
from streamlit_pages.admin_user_management import admin_user_management_page
from streamlit_pages.user_page import user_page
from streamlit_pages.explore_questions import run_explore_questions
from streamlit_pages.view_summary import run_view_summary

def main():
    # Ensure critical session state values are set and persist throughout the app's navigation
    st.session_state.setdefault('page', 'landing')
    st.session_state.setdefault('login_success', False)
    st.session_state.setdefault('username', '')
    st.session_state.setdefault('password', '')

    st.session_state.setdefault('jwt_token', '')
    st.session_state.setdefault('user_id', None)
    st.session_state.setdefault('user', '')
    st.session_state.setdefault('role', '')

    # Ensure user is logged in before accessing certain pages
    if st.session_state.page in ['user_page', 'explore_questions', 'admin', 'view_summary'] and not st.session_state['login_success']:
        st.error("Please log in to access this page.")
        st.session_state.page = 'login'  # Redirect to login page
        return

    # Display the page based on session state
    if st.session_state.page == 'landing':
        run_landing_page()
    elif st.session_state.page == 'login':
        login_page()
    elif st.session_state.page == 'register':
        register_page()
    elif st.session_state.page == 'user_page':
        user_page() 
    elif st.session_state.page == 'admin_page':
        admin_page()
    elif st.session_state.page == 'admin_dataset_management':
        admin_dataset_management_page()
    elif st.session_state.page == 'admin_user_management':
        admin_user_management_page()
    elif st.session_state.page == 'explore_questions':
        run_explore_questions()
    elif st.session_state.page == 'view_summary':
        run_view_summary()

# Callback functions for navigation
def go_to_login():
    st.session_state.page = 'login'

# Landing Page
def run_landing_page():
    st.title("OPEN AI EVALUATION APP")
    st.write("Would you like to assess AI's Answering Prowess?")
    st.button("Try It", on_click=go_to_login)

if __name__ == "__main__":
    main()
