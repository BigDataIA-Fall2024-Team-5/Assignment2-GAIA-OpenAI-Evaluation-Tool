# validations_questions.py
import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import requests

load_dotenv()

fastapi_url = os.getenv("FASTAPI_URL")

def go_back_to_user_page():
    # List of keys to keep in session state
    keys_to_keep = [
        "password",
        "logout_confirmation",
        "user_id",
        "login_success",
        "role",
        "page",
        "jwt_token",
        "username",
        "user"
    ]
    
    # Remove all keys not in the keys_to_keep list
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]

    st.session_state.page = 'user_page'

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

def gotoexpirypage():
    st.session_state.page = 'session_expired'
    st.experimental_rerun()

# Helper function to handle API responses
def handle_api_response(response, success_message=None):
    if response.status_code == 401:
        st.error(response.json().get('detail', "Authentication error. Please log in again."))
        gotoexpirypage()
        return None
    elif response.status_code == 200:
        if success_message:
            st.success(success_message)
        return response.json()
    else:
        st.error(f"API call failed: {response.status_code}")
        return None  

# Helper function to update selected row index and rerun
def update_selected_row(selected_row_index):
    st.session_state.selected_row_index = selected_row_index

def update_page(increment):
    # Calculate max pages based on filtered DataFrame length
    filtered_df = apply_filters(
        st.session_state.user_results,
        st.session_state.selected_levels,
        st.session_state.selected_file_types,
        st.session_state.selected_statuses
    )
    
    max_page = (len(filtered_df) - 1) // 9
    new_page = st.session_state.current_page + increment
    st.session_state.current_page = max(0, min(new_page, max_page))  # Ensure the page is within bounds

def display_question_table(df):
    # Pagination controls without forcing rerun
    col1, col2 = st.columns([9, 1])
    if col1.button("Previous", key="previous_button") and st.session_state.current_page > 0:
        update_page(-1)
    if col2.button("Next", key="next_button"):
        update_page(1)

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
            [   
                {'selector': 'table', 'props': [('border-collapse', 'collapse')]},
                {'selector': 'th', 'props': [('font-weight', 'bold'), ('text-align', 'left'), ('border', '1px solid black')]},
                {'selector': 'td', 'props': [('text-align', 'left'), ('border', '1px solid black')]}
            ]
        )

    # Filter to show only the 'Question' and 'Level' columns
    question_df = current_df[['Question', 'Level']]
    question_df.index.name = 'ID'
    styled_df = style_dataframe_with_borders(question_df)

    # Display the styled table in Streamlit
    st.dataframe(styled_df, height=300, width=700)
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
        
        model_name = st.session_state.get('model_choice')
        # Include model_name and dataset_split in the data being sent
        data = {
            "user_id": user_id,
            "task_id": task_id,
            "status": status,
            "chatgpt_response": chatgpt_response,
            "dataset_split": dataset_split,
            "model_name": model_name
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

        model_name = st.session_state.get('model_choice')
        data = {
            "question": question,
            "instructions": instructions,
            "preprocessed_data": preprocessed_data,
            "model_name": model_name
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
    if 'session_expired' not in st.session_state:
        st.session_state.session_expired= False  # Track if the final status was updated
    if 'selected_row_index' not in st.session_state:
        st.session_state.selected_row_index = 0
    if 'user_results' not in st.session_state:
        st.session_state.user_results = None
    if 'model_choice' not in st.session_state:
        st.session_state.model_choice = 'gpt-3.5-turbo'
    


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
    # Apply filters based on the selected options
    if selected_levels:
        df = df[df['Level'].isin(selected_levels)]

    if selected_file_types:
        df = df[df['file_name'].apply(lambda x: os.path.splitext(x)[1] if pd.notna(x) and x != "" else "No File").isin(selected_file_types)]

    if selected_statuses:
        df = df[df['user_result_status'].isin(selected_statuses)]

    # Check if the filtered dataframe is empty
    if df.empty:
        st.warning("No data available with the selected filters.")
    else:
        # Ensure pagination respects the bounds of the filtered dataframe
        max_page = (len(df) - 1) // 9
        if st.session_state.current_page > max_page:
            st.session_state.current_page = max_page

    return df


def run_validation_questions():
    # Fetch the questions from FastAPI
    df = fetch_questions_from_fastapi(dataset_split="validation")
    initialize_session_state(df)
    user_id = st.session_state.get('user_id')

    # Display model selection below the question table
    model_choice = st.radio(
        "Select Model",
        options=["gpt-3.5-turbo", "gpt-4"],
        index=0
    )

    # Fetch user-specific results if not yet loaded or when model changes
    if st.session_state.get('user_results') is None or st.session_state.get('model_choice') != model_choice:
        # Set the current model choice
        st.session_state['model_choice'] = model_choice

        # Fetch user-specific results for the selected model
        user_results = fetch_user_results_from_fastapi(user_id, dataset_split="validation")
        if user_results is None or user_results.empty:
            user_results = pd.DataFrame({
                'task_id': df['task_id'],
                'user_result_status': ['N/A'] * len(df),
                'chatgpt_response': ['N/A'] * len(df),
                'model_name': [model_choice] * len(df)
            })
        
        # Filter by model name and store in session state
        filtered_user_results = user_results[user_results['model_name'] == model_choice]
        st.session_state['user_results'] = filtered_user_results

        # Reset other related session variables for a fresh start
        st.session_state.chatgpt_response = None
        st.session_state.selected_row_index = 0  # Start fresh for the new model
    
    # Ensure 'user_results' is a valid DataFrame for merging and include 'file_name' from df
    if not isinstance(st.session_state['user_results'], pd.DataFrame):
        st.session_state['user_results'] = pd.DataFrame(columns=['task_id', 'user_result_status', 'chatgpt_response', 'model_name'])

    # Merge user results with the main DataFrame and ensure 'file_name' column is included
    merged_df = df.merge(
        st.session_state['user_results'][['task_id', 'user_result_status', 'chatgpt_response']],
        on='task_id',
        how='left'
    ).fillna({'user_result_status': 'N/A', 'chatgpt_response': 'N/A'})

    # Assign merged results back to session state
    st.session_state.user_results = merged_df

    # Define a function to update the 'show_instructions' flag based on 'user_result_status'
    def update_show_instructions(status):
        return (
            status not in ["N/A", "Correct without Instruction"] and 
            (status.startswith("Incorrect") or status == "Correct with Instruction")
        )

    # Apply sidebar filters
    st.sidebar.button("Back to Home Page", on_click=go_back_to_user_page, key="back_button_sidebar")
    selected_levels, selected_file_types, selected_statuses = add_sidebar_filters(st.session_state.user_results)
    st.session_state.selected_levels, st.session_state.selected_file_types, st.session_state.selected_statuses = selected_levels, selected_file_types, selected_statuses

    # Apply the filters and check if there is any data to display
    filtered_df = apply_filters(st.session_state.user_results, selected_levels, selected_file_types, selected_statuses)
    if filtered_df.empty:
        st.warning("No data available with the selected filters.")
        return

    # Display the filtered question table with pagination
    current_df = display_question_table(filtered_df)

    # Allow row selection for interaction
    selected_row_index = st.selectbox(
        "Select Question Index",
        options=current_df.index.tolist(),
        format_func=lambda x: f"{x}: {current_df.loc[x, 'Question'][:50]}...",
        index=0,
        key="selectbox"
    )

    # Update session state when selecting a new question or model change
    if st.session_state.get('last_selected_row_index') != selected_row_index or st.session_state.get('model_choice') == model_choice:
        selected_row = current_df.loc[selected_row_index]
        current_status = selected_row['user_result_status']
        
        # Use the function to update 'show_instructions'
        st.session_state.show_instructions = update_show_instructions(current_status)
        
        # Populate instructions for the selected row
        st.session_state.instructions = selected_row.get('Annotator_Metadata_Steps', '') 
        st.session_state.last_selected_row_index = selected_row_index
        st.session_state.chatgpt_response = None  # Reset ChatGPT response for new selection

    # Retrieve the selected row
    selected_row = current_df.loc[selected_row_index]

    # Display question details and allow ChatGPT interactions
    st.write("**Question:**", selected_row['Question'])
    st.write("**Expected Final Answer:**", selected_row['FinalAnswer'])
    current_status = selected_row['user_result_status']
    chatgpt_response = selected_row['chatgpt_response']
    
    # Handle file types and display the "Send to ChatGPT" button as appropriate
    file_name = selected_row.get('file_name', None)
    file_extension = os.path.splitext(file_name)[1].lower() if file_name else None
    preprocessed_data, show_chatgpt_button = None, False

    if file_extension == '.pdf':
        st.write("**File Type:** PDF")
        extraction_method = st.radio("Choose PDF extraction method:", ("PyMuPDF", "Amazon Textract"), index=0)
        pdf_summary = fetch_pdf_summary_from_fastapi(file_name, extraction_method)
        if pdf_summary:
            st.write(f"**PDF Summary ({extraction_method}):**")
            st.write(pdf_summary)
            preprocessed_data = pdf_summary
            show_chatgpt_button = True
    elif file_extension:
        st.error(f"Unsupported file type: {file_extension}")
    else:
        preprocessed_data = None
        show_chatgpt_button = True

    # Display ChatGPT response if it exists
    if st.session_state.chatgpt_response:
        st.write(f"**ChatGPT's Response:** {st.session_state.chatgpt_response}")

    # Check if instructions should be shown
    if not st.session_state.show_instructions:
        if show_chatgpt_button:
            # Button to send to ChatGPT without instructions
            if st.button("Send to ChatGPT", key=f"send_chatgpt_{selected_row_index}"):
                handle_send_to_chatgpt(selected_row, selected_row_index, preprocessed_data)
                
                # After updating, print the ChatGPT response
                if st.session_state.chatgpt_response:
                    st.write(f"**ChatGPT's Response:** {st.session_state.chatgpt_response}")
                    st.experimental_rerun()
    else:
        st.write("**The response was incorrect or requires instructions. Please provide them below.**")
        st.session_state.instructions = st.text_area(
            "Edit Instructions (Optional)",
            value=st.session_state.instructions,
            key=f"instructions_{selected_row_index}"
        )
        
        # Button to send to ChatGPT with instructions
        if st.button("Send to ChatGPT with Instructions", key=f'send_button_{selected_row_index}'):
            # Fetch the ChatGPT response with instructions
            chatgpt_response = get_chatgpt_response_via_fastapi(
                selected_row['Question'], 
                instructions=st.session_state.instructions, 
                preprocessed_data=preprocessed_data
            )

            if chatgpt_response:
                # Update ChatGPT response and status in session state
                st.session_state.chatgpt_response = chatgpt_response
                st.write(f"**ChatGPT's Response with Instructions:** {st.session_state.chatgpt_response}")
                
                # Update the user result status
                status = compare_and_update_status_via_fastapi(selected_row, chatgpt_response, st.session_state.instructions)
                st.session_state.user_results.at[selected_row_index, 'user_result_status'] = status
                update_user_result_in_fastapi(user_id=user_id, task_id=selected_row['task_id'], status=status, chatgpt_response=chatgpt_response)
                st.session_state.show_instructions = update_show_instructions(status)

    # Function to apply background color based on the Final Result Status
    def style_status_based_on_final_result(status):
        if status.strip().lower().startswith("correct"):
            return 'background-color: #38761d; padding: 10px; border-radius: 5px;'
        else:
            return 'background-color: #d62929; padding: 10px; border-radius: 5px;'

    background_style = style_status_based_on_final_result(current_status)

    # Display the Final Result Status and ChatGPT Response with appropriate background color
    st.markdown(f'<div style="{background_style}"><strong>Final Result Status:</strong> {current_status}</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="{background_style}"><strong>Latest ChatGPT Response:</strong> {st.session_state.chatgpt_response}</div>', unsafe_allow_html=True)
