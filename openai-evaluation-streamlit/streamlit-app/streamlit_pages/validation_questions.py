# validations_questions.py
import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import requests

load_dotenv()

fastapi_url = os.getenv("FASTAPI_URL")

def go_back_to_user_page():
    keys_to_remove = ['df', 'user_results', 'show_instructions', 'current_page', 'last_selected_row_index', 'chatgpt_response']
    
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

    st.session_state.page = 'user_page'

def go_to_login_page():
    for key in list(st.session_state.keys()):
        if key != 'page': 
            del st.session_state[key]
    
    # Set the page to login page
    st.session_state.page = 'login'

# Helper function to get JWT headers
def get_jwt_headers():
    token = st.session_state.get('jwt_token')
    if not token:
        st.error("No JWT token found. Please log in.")
        return None
    headers = {
        "Authorization": f"Bearer {token}"
    }
    return headers

# Helper function to handle API responses
def handle_api_response(response, success_message=None):
    if response.status_code == 401:
        st.error(response.json().get('detail', "Authentication error. Please log in again."))
        st.button("Go to Login Page", on_click=go_to_login_page)
        return None
    elif response.status_code == 200:
        if success_message:
            st.success(success_message)
        return response.json()
    else:
        st.error(f"API call failed: {response.status_code}")
        return None  

def display_question_table(df):
    # Pagination controls
    col1, col2 = st.columns([9, 1])
    if col1.button("Previous", key="previous_button"):
        if st.session_state.current_page > 0:
            st.session_state.current_page -= 1
    if col2.button("Next", key="next_button"):
        if st.session_state.current_page < (len(df) // 7):
            st.session_state.current_page += 1

    # Define pagination parameters
    page_size = 9
    current_page = st.session_state.current_page
    start_idx = current_page * page_size
    end_idx = start_idx + page_size

    # Select the current page of questions to display
    current_df = df.iloc[start_idx:end_idx]

    # Style the table for display
    def style_dataframe_with_borders(df):
        return df.style.set_table_styles(
            [{
                'selector': 'table',
                'props': [('border', '3px solid black'), ('width', '100%')]
            }, {
                'selector': 'th',
                'props': [('border', '2px solid black'), ('font-weight', 'bold')]
            }, {
                'selector': 'td',
                'props': [('border', '2px solid black'), ('width', '100%')]
            }]
        )

    # Filter to show only the 'Question' and 'Level' columns
    question_df = current_df[['Question', 'Level']]
    question_df.index.name = 'ID'
    styled_df = style_dataframe_with_borders(question_df)

    # Display the styled table in Streamlit
    st.dataframe(styled_df, use_container_width=True)

    return current_df

# Fetch questions from FastAPI dynamically using the `dataset_split` query parameter
def fetch_questions_from_fastapi(dataset_split="validation"):
    try:
        headers = get_jwt_headers()
        if headers is None:
            return pd.DataFrame()

        # Pass the dataset split as a query parameter in the URL
        response = requests.get(f"{fastapi_url}/db/questions?dataset_split={dataset_split}", headers=headers)
        json_data = handle_api_response(response)

        if json_data:
            return pd.DataFrame(json_data)
        else:
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching questions: {e}")
        return pd.DataFrame()

# Fetch user results from FastAPI with dataset_split query parameter
def fetch_user_results_from_fastapi(user_id, dataset_split="validation"):
    try:
        headers = get_jwt_headers()
        if headers is None:
            return pd.DataFrame()

        # Pass dataset_split as a query parameter
        response = requests.get(f"{fastapi_url}/db/user_results/{user_id}?dataset_split={dataset_split}", headers=headers)
        json_data = handle_api_response(response)

        if json_data:
            return pd.DataFrame(json_data)
        else:
            return pd.DataFrame()

    except Exception as e:
        st.error(f"Error fetching user results: {e}")
        return pd.DataFrame()

# Update user result using FastAPI
def update_user_result_in_fastapi(user_id, task_id, status, chatgpt_response, dataset_split="validation"):
    try:
        headers = get_jwt_headers()
        if headers is None:
            return

        # Include dataset_split in the data being sent
        data = {
            "user_id": user_id,
            "task_id": task_id,
            "status": status,
            "chatgpt_response": chatgpt_response,
            "dataset_split": dataset_split 
        }

        # Send the updated result to the FastAPI endpoint
        response = requests.put(f"{fastapi_url}/db/update_result", json=data, headers=headers)
        handle_api_response(response, success_message="Result updated successfully!")

    except Exception as e:
        st.error(f"Error updating result: {e}")



# Fetch PDF summary from FastAPI
def fetch_pdf_summary_from_fastapi(file_name, extraction_method):
    try:
        headers = get_jwt_headers()
        if headers is None:
            return None

        data = {
            "file_name": file_name,
            "extraction_method": extraction_method
        }

        response = requests.post(f"{fastapi_url}/s3/fetch_pdf_summary/", json=data, headers=headers)
        json_data = handle_api_response(response)

        if json_data:
            return json_data.get('summary', None)
        else:
            return None

    except Exception as e:
        st.error(f"Error fetching PDF summary: {e}")
        return None


# Function to get chatgpt response using FastAPI
def get_chatgpt_response_via_fastapi(question, instructions=None, preprocessed_data=None):
    try:
        headers = get_jwt_headers()
        if headers is None:
            return None

        data = {
            "question": question,
            "instructions": instructions,
            "preprocessed_data": preprocessed_data
        }

        response = requests.post(f"{fastapi_url}/gpt/ask", json=data, headers=headers)
        json_data = handle_api_response(response)

        if json_data:
            return json_data.get("response", "No response from ChatGPT")
        else:
            return None

    except Exception as e:
        st.error(f"Error communicating with FastAPI: {e}")
        return None

# Function to compare response using FastAPI
def compare_and_update_status_via_fastapi(selected_row, chatgpt_response, instructions):
    try:
        headers = get_jwt_headers()
        if headers is None:
            return None

        data = {
            "row": selected_row.to_dict(),
            "chatgpt_response": chatgpt_response,
            "instructions": instructions
        }

        response = requests.post(f"{fastapi_url}/gpt/compare", json=data, headers=headers)
        json_data = handle_api_response(response)

        if json_data:
            return json_data.get("comparison_result", "Error")
        else:
            return None

    except Exception as e:
        st.error(f"Error comparing response: {e}")
        return None

# Callback function for handling 'Send to ChatGPT'
def handle_send_to_chatgpt(selected_row, selected_row_index, preprocessed_data):
    user_id = st.session_state.get('user_id') 

    # Get the current status from the user_results table
    current_status = st.session_state.user_results.loc[selected_row_index, 'user_result_status']

    # Get the response status from the user_results table
    chatgpt_response = st.session_state.user_results.loc[selected_row_index, 'chatgpt_response']

    # Determine if instructions should be used based on the current status
    use_instructions = current_status.startswith("Incorrect")
    
    # Call ChatGPT API, passing the preprocessed file data instead of a URL
    chatgpt_response = get_chatgpt_response_via_fastapi(
        selected_row['Question'], 
        instructions=st.session_state.instructions if use_instructions else None, 
        preprocessed_data=preprocessed_data
    )

    if chatgpt_response:
        # Compare response with the final answer
        status = compare_and_update_status_via_fastapi(selected_row, chatgpt_response, st.session_state.instructions if use_instructions else None)
        
        # Update the status in session state immediately
        st.session_state.user_results.at[selected_row_index, 'user_result_status'] = status
    
        # Now use the refactored update function to update the user result in FastAPI
        update_user_result_in_fastapi(user_id, selected_row['task_id'], status, chatgpt_response)

        # Store ChatGPT response in session state
        st.session_state.chatgpt_response = chatgpt_response

        # Ensure the UI reflects the updated status immediately
        st.session_state.final_status_updated = True

        # Show instructions if the response is incorrect
        if status in ['Correct with Instruction', 'Incorrect with Instruction', 'Incorrect without Instruction']:
            st.session_state.show_instructions = True
        else:
            st.session_state.show_instructions = False


def initialize_session_state(df):
    # Initialize session state for pagination and instructions
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 0
    if 'df' not in st.session_state:
        st.session_state.df = df
    if 'instructions' not in st.session_state:
        st.session_state.instructions = ""  # Initialize instructions state
    if 'show_instructions' not in st.session_state:
        st.session_state.show_instructions = False  # Flag to control text area display
    if 'chatgpt_response' not in st.session_state:
        st.session_state.chatgpt_response = None  # Store the ChatGPT response
    if 'final_status_updated' not in st.session_state:
        st.session_state.final_status_updated = False  # Track if the final status was updated


# Sidebar Filters
def add_sidebar_filters(df):

    st.sidebar.header("Filters")

    # Filter by 'Level'
    levels = sorted(df['Level'].unique()) if 'Level' in df.columns else []
    selected_levels = st.sidebar.multiselect(
        "Select Levels",
        options=levels,
        default=[]
    )

    # Filter by 'Associated File Type'
    # Replace empty or missing file names with 'No File'
    file_types = df['file_name'].apply(lambda x: os.path.splitext(x)[1] if pd.notna(x) and x != "" else "No File")
    file_types = sorted(file_types.unique())
    selected_file_types = st.sidebar.multiselect(
        "Select File Types",
        options=file_types,
        default=[] 
    )

    # Filter by 'User Result Status'
    result_statuses = sorted(df['user_result_status'].unique()) if 'user_result_status' in df.columns else []
    selected_statuses = st.sidebar.multiselect(
        "Select User Result Status",
        options=result_statuses,
        default=[] 
    )

    return selected_levels, selected_file_types, selected_statuses

# Function to apply the filters to the DataFrame
def apply_filters(df, selected_levels, selected_file_types, selected_statuses):
    # Filter by 'Level'
    if selected_levels:
        df = df[df['Level'].isin(selected_levels)]

    # Filter by 'Associated File Type'
    if selected_file_types:
        df = df[df['file_name'].apply(lambda x: os.path.splitext(x)[1]).isin(selected_file_types)]

    # Filter by 'User Result Status'
    if selected_statuses:
        df = df[df['user_result_status'].isin(selected_statuses)]

    # Reset pagination when filters are applied
    st.session_state.current_page = 0

    return df

def run_validation_questions():

    # Fetch the questions from FastAPI
    df = fetch_questions_from_fastapi(dataset_split="validation")

    # Initialize session state for pagination and instructions
    initialize_session_state(df)

    # Fetch user-specific results from FastAPI
    user_id = st.session_state.get('user_id')
    user_results = fetch_user_results_from_fastapi(user_id, dataset_split="validation")

    # Check if user_results is empty
    if user_results is None or user_results.empty:
        user_results = pd.DataFrame({
            'task_id': st.session_state.df['task_id'],
            'user_result_status': ['N/A'] * len(st.session_state.df),
            'chatgpt_response': ['N/A'] * len(st.session_state.df)
        })

    # Check if both dataframes contain the 'task_id' column
    if 'task_id' in st.session_state.df.columns and 'task_id' in user_results.columns:
        merged_df = st.session_state.df.merge(
            user_results[['task_id', 'user_result_status', 'chatgpt_response']],
            on='task_id',
            how='left'
        )

        # After merging user_results with GaiaDataset, fill missing 'user_result_status' with 'N/A'
        merged_df['user_result_status'] = merged_df['user_result_status'].fillna('N/A')
        merged_df['chatgpt_response'] = merged_df['chatgpt_response'].fillna('N/A')

        st.session_state.user_results = merged_df  # Store merged DataFrame in session state

        # Add a "Back" button to return to the user page in the sidebar using a callback
        st.sidebar.button("Back to Home Page", on_click=go_back_to_user_page, key="back_button_sidebar")

        # Apply filters in the sidebar
        selected_levels, selected_file_types, selected_statuses = add_sidebar_filters(st.session_state.user_results)

        # Apply the selected filters to the dataframe
        filtered_df = apply_filters(st.session_state.user_results, selected_levels, selected_file_types, selected_statuses)

        # Reset pagination after filtering
        if len(filtered_df) < st.session_state.current_page * 9:
            st.session_state.current_page = 0

        # Proceed with displaying the question table based on filtered data
        if not filtered_df.empty:
            current_df = display_question_table(filtered_df)

            # Only allow row selection if the DataFrame is not empty
            if not current_df.empty:
                selected_row_index = st.selectbox(
                    "Select Question Index",
                    options=current_df.index.tolist(),
                    format_func=lambda x: f"{x}: {current_df.loc[x, 'Question'][:50]}...",
                    key=f"selectbox_{st.session_state.current_page}"
                )

                # Selected row from the table
                selected_row = current_df.loc[selected_row_index]
                st.write("**Question:**", selected_row['Question'])
                st.write("**Expected Final Answer:**", selected_row['FinalAnswer'])

                # Get the current status from user-specific results
                current_status = selected_row['user_result_status']
                chatgpt_response = selected_row['chatgpt_response']

                # Get the file name and file path (S3 URL) if available
                file_name = selected_row.get('file_name', None)
                file_url = selected_row.get('file_path', None)
                preprocessed_data = None
            else:
                st.warning("No results available for the selected filters. Please adjust your filters.")
                selected_row = None  # Ensure `selected_row` is not used if there are no results
        else:
            st.warning("No data available. Please try adjusting the filters.")
            selected_row = None  # Ensure `selected_row` is not used if there is no filtered data

    else:
        st.error("Error: 'task_id' is missing in one of the datasets.")
        if st.button("Back"):
            go_back_to_user_page()

    # Only proceed if a row was successfully selected
    if selected_row is not None:
        current_status = selected_row['user_result_status']
        chatgpt_response = selected_row['chatgpt_response']

        # Get the file name and file path (S3 URL) if available
        file_name = selected_row.get('file_name', None)
        preprocessed_data = None

        # Handle PDF file types and unsupported files
        file_extension = os.path.splitext(file_name)[1].lower() if file_name else None
        show_chatgpt_button = False  # Flag to control whether the "Send to ChatGPT" button is shown

        # Fetch the PDF summary and display options
        if file_extension == '.pdf':
            st.write("**File Type:** PDF")

            # Let the user select the extraction method (PyMuPDF or Amazon Textract)
            extraction_method = st.radio(
                "Choose PDF extraction method:",
                ("PyMuPDF", "Amazon Textract"),
                index=0
            )

            # Fetch the PDF summary from FastAPI
            pdf_summary = fetch_pdf_summary_from_fastapi(file_name, extraction_method)
            if pdf_summary:
                st.write(f"**PDF Summary ({extraction_method}):**")
                st.write(pdf_summary)
                preprocessed_data = pdf_summary  # Use this data for sending to ChatGPT
                show_chatgpt_button = True  # Allow ChatGPT button for PDF
        else:
            if file_extension:
                st.error(f"Unsupported file type: {file_extension}")
                show_chatgpt_button = False  # Disable ChatGPT button for unsupported files
            else:
                preprocessed_data = None  # No file, but we can still send the question to ChatGPT
                show_chatgpt_button = True  # Allow ChatGPT button for questions with no file

        # Update session state for instructions when selecting a new question
        if 'last_selected_row_index' not in st.session_state or st.session_state.last_selected_row_index != selected_row_index:
            # Conditions to show the Edit Instructions box:
            # Show instructions if the result is 'Correct with Instructions', 'Incorrect with Instructions', or 'Incorrect without Instruction'
            if current_status in ['Correct with Instruction', 'Incorrect with Instruction', 'Incorrect without Instruction']:
                st.session_state.instructions = selected_row.get('Annotator_Metadata_Steps', '')  # Pre-fill from dataset
                st.session_state.show_instructions = True  # Show the instructions box
            else:
                st.session_state.instructions = selected_row.get('Annotator_Metadata_Steps', '')
                st.session_state.show_instructions = False  # Hide instructions by default

            st.session_state.last_selected_row_index = selected_row_index
            st.session_state.chatgpt_response = None  # Reset ChatGPT response

        # Display ChatGPT response if available
        if st.session_state.chatgpt_response:
            st.write(f"**ChatGPT's Response:** {st.session_state.chatgpt_response}")

        # Conditionally show either "Send to ChatGPT" button or "Send to ChatGPT with Instructions" button
        if not st.session_state.show_instructions and current_status != "Correct with Instruction":
            # Show "Send to ChatGPT" button if no instructions are required
            if show_chatgpt_button:
                if st.button("Send to ChatGPT", on_click=handle_send_to_chatgpt, args=(selected_row, selected_row_index, preprocessed_data), key=f"send_chatgpt_{selected_row_index}"):
                    # ChatGPT response will be processed in handle_send_to_chatgpt
                    pass
        else:
            # If the response was incorrect, prompt for instructions and show "Send to ChatGPT with Instructions"
            st.write("**The response was incorrect. Please provide instructions.**")

            # Pre-fill instructions from the dataset or previous inputs
            st.session_state.instructions = st.text_area(
                "Edit Instructions (Optional)",
                value=st.session_state.instructions,
                key=f"instructions_{selected_row_index}"  # Unique key for each question
            )

            # Show "Send to ChatGPT with Instructions" button instead
            if st.button("Send to ChatGPT with Instructions", key=f'send_button_{selected_row_index}'):
                # Use the updated instructions to query ChatGPT
                chatgpt_response = get_chatgpt_response_via_fastapi(
                    selected_row['Question'], 
                    instructions=st.session_state.instructions, 
                    preprocessed_data=preprocessed_data
                )

                if chatgpt_response:
                    st.write(f"**ChatGPT's Response with Instructions:** {chatgpt_response}")

                    # Compare and update status based on ChatGPT's response
                    status = compare_and_update_status_via_fastapi(selected_row, chatgpt_response, st.session_state.instructions)
                    st.session_state.user_results.at[selected_row_index, 'user_result_status'] = status
                    current_status = status  # Update current_status

                    # Update the user-specific status in the Azure SQL Database
                    update_user_result_in_fastapi(user_id=user_id, task_id=selected_row['task_id'], status=status, chatgpt_response=chatgpt_response)

                    # Update show_instructions flag based on new status
                    if status in ['Correct with Instruction', 'Incorrect with Instruction', 'Incorrect without Instruction']:
                        st.session_state.show_instructions = True
                    else:
                        st.session_state.show_instructions = False

                    # Store the new ChatGPT response
                    st.session_state.chatgpt_response = chatgpt_response

        # Function to apply background color based on the Final Result Status
        def style_status_based_on_final_result(status):
            # Strip any leading/trailing spaces and make the check case-insensitive
            if status.strip().lower().startswith("correct"):
                # Green background for Correct statuses
                return 'background-color: #38761d; padding: 10px; border-radius: 5px;'
            else:
                # Red background for non-Correct statuses
                return 'background-color: #d62929; padding: 10px; border-radius: 5px;'

        # Get the background color based on the Final Result Status
        background_style = style_status_based_on_final_result(current_status)

        # Apply the same background color style to both "Final Result Status" and "Latest ChatGPT Response"
        st.markdown(f'<div style="{background_style}"><strong>Final Result Status:</strong> {current_status}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="{background_style}"><strong>Latest ChatGPT Response:</strong> {chatgpt_response}</div>', unsafe_allow_html=True)
