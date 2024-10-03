import streamlit as st

# Function to handle logout action
def confirm_logout():
    # Only clear session variables related to authentication and user-specific data
    for key in list(st.session_state.keys()):
        if key not in ['page']:  # Keep the 'page' session state to manage navigation
            del st.session_state[key]
    
    # Navigate to the login page
    st.session_state['page'] = 'login'
    st.success("You have been logged out successfully.")

# Function to handle cancel logout action
def cancel_logout():
    st.session_state['logout_confirmation'] = False

# Admin Dashboard Page
def admin_page():

    # Admin Dashboard UI
    st.title("Admin Dashboard")
    st.write(f"Welcome {st.session_state['user']} to the Admin Dashboard!")

    # Admin action buttons
    st.button("Manage Dataset", on_click=lambda: st.session_state.update(page='admin_dataset_management'))
    st.button("Manage Users", on_click=lambda: st.session_state.update(page='admin_user_management'))

    # Initialize logout confirmation in session state if not present
    if 'logout_confirmation' not in st.session_state:
        st.session_state['logout_confirmation'] = False

    # If logout confirmation is not triggered, show the Logout button
    if not st.session_state['logout_confirmation']:
        st.button("Logout", on_click=lambda: st.session_state.update(logout_confirmation=True))

    # Show confirmation buttons if logout is triggered
    if st.session_state['logout_confirmation']:
        st.warning("Are you sure you want to log out?")
        col1, col2 = st.columns(2)

        # Show Confirm Logout button
        col1.button("Confirm Logout", on_click=confirm_logout)

        # Show Cancel Logout button
        col2.button("Cancel Logout", on_click=cancel_logout)
