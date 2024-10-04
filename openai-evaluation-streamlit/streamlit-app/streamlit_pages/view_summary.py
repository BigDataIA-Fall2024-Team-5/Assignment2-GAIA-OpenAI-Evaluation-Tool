import os
from dotenv import load_dotenv
import requests
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

load_dotenv()

fastapi_url = os.getenv("FASTAPI_URL")

def go_back_to_main():
    st.session_state.page = 'user_page'


def go_to_login_page():
    for key in list(st.session_state.keys()):
        if key != 'page': 
            del st.session_state[key]
    
    # Set the page to login page
    st.session_state.page = 'login'

# Fetch questions (GAIA dataset) from FastAPI with dataset_split
def fetch_questions_from_fastapi(dataset_split="validation"):
    try:
        # Retrieve the token from session state
        token = st.session_state.get('jwt_token')

        # Add the token to the Authorization header
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Send request with JWT token in headers, and include dataset_split query parameter
        response = requests.get(f"{fastapi_url}/db/questions?dataset_split={dataset_split}", headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        # Convert the response to a DataFrame
        return pd.DataFrame(response.json())

    except requests.exceptions.HTTPError as http_err:
        # Handle authentication errors
        if response.status_code == 401:
            st.error(response.json().get('detail', "Authentication error. Please log in again."))
            st.button("Go to Login Page", on_click=go_to_login_page)
        else:
            st.error(f"HTTP error occurred: {http_err}")
        return None

    except requests.exceptions.RequestException as e:
        # Handle other request errors
        st.error(f"Error fetching questions: {e}")
        return None

# Fetch user-specific results from FastAPI with dataset_split
def fetch_user_results_from_fastapi(user_id, dataset_split="validation"):
    try:
        # Retrieve the token from session state
        token = st.session_state.get('jwt_token')

        # Add the token to the Authorization header
        headers = {
            "Authorization": f"Bearer {token}"
        }

        # Send request with JWT token in headers, and include dataset_split query parameter
        response = requests.get(f"{fastapi_url}/db/user_results/{user_id}?dataset_split={dataset_split}", headers=headers)
        response.raise_for_status()  # Raise an error for bad responses

        # Convert the response to a DataFrame
        return pd.DataFrame(response.json())

    except requests.exceptions.HTTPError as http_err:
        # Handle authentication errors
        if response.status_code == 401:
            st.error(response.json().get('detail', "Authentication error. Please log in again."))
            st.button("Go to Login Page", on_click=go_to_login_page)
        else:
            st.error(f"HTTP error occurred: {http_err}")
        return None

    except requests.exceptions.RequestException as e:
        # Handle other request errors
        st.error(f"Error fetching user results: {e}")
        return None


# Main summary page logic
def run_summary_page(df, user_results_df):

    # Ensure 'task_id' is of string type in both DataFrames
    df['task_id'] = df['task_id'].astype(str)
    user_results_df['task_id'] = user_results_df['task_id'].astype(str)

    # Check if 'user_result_status' exists in the main dataset before merging and drop it to avoid conflict
    if 'user_result_status' in df.columns:
        df = df.drop(columns=['user_result_status'])

    # Perform the merge with 'task_id' to combine user results
    merged_df = df.merge(
        user_results_df[['task_id', 'user_result_status']], 
        on='task_id', 
        how='left'
    )

    # If user_result_status is missing after the merge, fill it with 'N/A'
    if 'user_result_status' not in merged_df.columns:
        st.warning("'user_result_status' column missing after merge. Filling with 'N/A'.")
        merged_df['user_result_status'] = 'N/A'
    else:
        # Fill missing user_result_status values with 'N/A'
        merged_df['user_result_status'] = merged_df['user_result_status'].fillna('N/A')

    # Filter answered questions (exclude 'N/A' status)
    answered_df = merged_df[merged_df['user_result_status'] != 'N/A']
    unanswered_count = len(merged_df) - len(answered_df)

    # Create a bar chart for 'user_result_status'
    if not answered_df.empty:
        status_counts = answered_df['user_result_status'].value_counts()

        st.write("### Result Status Distribution (Answered Questions Only)")

        # Plot the bar chart
        fig, ax = plt.subplots()
        status_counts.plot(kind='bar', ax=ax, color='skyblue')
        ax.set_xlabel('Result Status')
        ax.set_ylabel('Count')
        ax.set_title('Distribution of Answered Questions by Result Status')
        st.pyplot(fig)

        # Display the detailed counts for each result status
        st.write("### Detailed Result Status Counts")
        st.write(status_counts)
    else:
        st.write("No answered questions to display.")

    # Display total number of questions and answered questions
    st.write(f"**Total Questions in the Dataset:** {len(merged_df)}")
    st.write(f"**Total Answered Questions:** {len(answered_df)}")
    st.write(f"**Total Unanswered Questions:** {unanswered_count}")

    # Explanation of result statuses
    st.write("### Explanation of Result Statuses:")
    st.write("""
    - **Correct without Instruction**: The answer was correct on the first attempt, without needing any instructions.
    - **Correct with Instruction**: The answer was correct after providing additional instructions.
    - **Incorrect without Instruction**: The answer was incorrect on the first attempt, without using instructions.
    - **Incorrect with Instruction**: The answer remained incorrect even after providing additional instructions.
    """)

# Call the view summary function
def run_view_summary():
    
    st.title("Summary of Results")

    # Add a "Back" button to return to the main page
    st.button("Back to Main", on_click=go_back_to_main)

    # Allow the user to select dataset split
    dataset_split = st.radio(
        "Select Dataset Split:",
        options=["test", "validation"],
        index=1  # Default to validation
    )

    # Fetch the main dataset (GAIA dataset) from FastAPI with the selected dataset split
    df = fetch_questions_from_fastapi(dataset_split=dataset_split)
    
    # Fetch user-specific results with the selected dataset split
    user_results_df = fetch_user_results_from_fastapi(st.session_state['user_id'], dataset_split=dataset_split)

    # Ensure the main dataset was fetched successfully
    if df is None:
        st.error("Failed to load the main dataset from FastAPI.")
        return
    
    # If user_results_df is None (no results found for the user), create an empty DataFrame
    if user_results_df is None or user_results_df.empty:
        st.write("No user results found. Please complete some questions.")
        user_results_df = pd.DataFrame(columns=['task_id', 'user_result_status', 'chatgpt_response'])  # Empty DataFrame

    # Call the summary page with the fetched data
    run_summary_page(df, user_results_df)
