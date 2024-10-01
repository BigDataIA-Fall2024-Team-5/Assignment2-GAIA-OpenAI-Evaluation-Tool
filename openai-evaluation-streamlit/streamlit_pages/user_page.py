import streamlit as st

# User Page for the Streamlit app
def user_page():
    if st.session_state.get('login_success', False):
        st.title("User Dashboard")

        # Welcome message with the user's name
        st.write(f"Welcome {st.session_state['user']}!")

        # Buttons for navigating to Explore Questions and View Summary pages
        st.button("Explore Questions", on_click=lambda: set_page('explore_questions'))
        st.button("View Summary", on_click=lambda: set_page('view_summary'))

        # Initialize logout confirmation in session state if not present
        if 'logout_confirmation' not in st.session_state:
            st.session_state['logout_confirmation'] = False

        # Show Logout button if logout confirmation is not triggered
        if not st.session_state['logout_confirmation']:
            st.button("Log Out", on_click=lambda: st.session_state.update(logout_confirmation=True))

        # If logout confirmation is triggered, show confirmation options
        if st.session_state['logout_confirmation']:
            st.warning("Are you sure you want to log out?")
            col1, col2 = st.columns(2)

            # Confirm Logout button
            col1.button("Confirm Logout", on_click=confirm_logout)

            # Cancel Logout button
            col2.button("Cancel Logout", on_click=cancel_logout)
    else:
        st.error("Please log in to access this page.")
        st.session_state.page = 'login'  # Redirect to login page if not logged in

# Function to set the page in session state
def set_page(page_name):
    st.session_state.page = page_name

# Function to handle logout action
def confirm_logout():
    # Clear session state except for 'page'
    for key in list(st.session_state.keys()):
        if key != 'page':
            del st.session_state[key]
    
    # Reset page to login and provide feedback
    st.session_state['page'] = 'login'
    st.session_state['logout_confirmation'] = False  # Reset confirmation state
    st.success("You have been logged out successfully.")

# Function to handle cancel logout action
def cancel_logout():
    st.session_state['logout_confirmation'] = False  # Reset confirmation state
