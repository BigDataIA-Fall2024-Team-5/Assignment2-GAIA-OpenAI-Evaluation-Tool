import streamlit as st
import requests

fastapi_base_url = "http://127.0.0.1:8000/db"

# Function to fetch all users from FastAPI
def fetch_all_users():
    try:
        response = requests.get(f"{fastapi_base_url}/users")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching users: {e}")
        return []

# Function to delete a user using their `user_id`
def handle_delete_user(user_id, username):
    try:
        # Get the admin user_id and user (username) from session state
        admin_user_id = st.session_state.get('user_id', '')
        admin_user = st.session_state.get('user', '')  # Use 'user' session state instead of 'username'
        
        if not admin_user_id or not admin_user:
            st.error("Admin user_id or user not found. Please log in again.")
            return

        # Send DELETE request to FastAPI backend with admin's user_id
        delete_url = f"{fastapi_base_url}/users/{user_id}?admin={admin_user_id}"
        response = requests.delete(delete_url)
        response.raise_for_status()

        # Notify the user of success
        st.success(f"User '{username}' (ID: {user_id}) deleted successfully.")
    except requests.RequestException as e:
        st.error(f"Failed to delete user '{username}' (ID: {user_id}): {e}")

# Function to promote a user using their `user_id`
def handle_promote_user(user_id, username):
    try:
        admin_user_id = st.session_state.get('user_id', '')
        admin_user = st.session_state.get('user', '')  # Use 'user' session state instead of 'username'
        
        if not admin_user_id or not admin_user:
            st.error("Admin user_id or user not found. Please log in again.")
            return

        promote_url = f"{fastapi_base_url}/users/{user_id}/promote?admin={admin_user_id}"
        response = requests.put(promote_url)
        response.raise_for_status()

        # Notify the user of success
        st.success(f"User '{username}' (ID: {user_id}) promoted to admin successfully.")
    except requests.RequestException as e:
        st.error(f"Failed to promote user '{username}' (ID: {user_id}): {e}")

# Admin User Management Page
def admin_user_management_page():
    st.title("User Management")

    # Initialize session state for confirmation
    if 'confirm_deletion' not in st.session_state:
        st.session_state['confirm_deletion'] = None

    # Fetch all users from the FastAPI backend
    users = fetch_all_users()

    if users:
        st.write("Below is the list of users in the system:")
        for user in users:
            col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
            col1.write(user["user_id"])  # Display user_id
            col2.write(user["username"])  # Display username
            col3.write(user["role"])  # Display user role

            if user["role"] != "admin":
                col4.button(f"Promote to Admin", key=f"promote_{user['user_id']}", 
                            on_click=handle_promote_user, args=(user["user_id"], user["username"]))
            
            # Show confirmation button before deletion
            if st.session_state['confirm_deletion'] == user["user_id"]:
                col4.button(f"Confirm Delete", key=f"confirm_delete_{user['user_id']}",
                            on_click=handle_delete_user, args=(user["user_id"], user["username"]))
                col4.button(f"Cancel", key=f"cancel_delete_{user['user_id']}",
                            on_click=lambda: st.session_state.update(confirm_deletion=None))
            else:
                col4.button(f"Delete User", key=f"delete_{user['user_id']}",
                            on_click=lambda u=user["user_id"]: st.session_state.update(confirm_deletion=u))
    else:
        st.write("No users found.")

    st.button("Back to Admin", on_click=lambda: st.session_state.update(page='admin_page'))

    