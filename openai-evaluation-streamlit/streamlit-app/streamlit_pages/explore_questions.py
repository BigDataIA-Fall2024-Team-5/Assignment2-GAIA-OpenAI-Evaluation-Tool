import streamlit as st

def go_back_to_main():
    st.session_state.page = 'user_page'

# Explore Questions page
def run_explore_questions():
    st.title("Explore Questions")
    
    # Add a "Back" button to return to the main page
    st.button("Back to Main", on_click=go_back_to_main)

    # Button to go to validation split questions
    st.button("Validation Split Questions", on_click=lambda: st.session_state.update(page='validation_questions'))

    # Button to go to test split questions
    st.button("Test Split Questions", on_click=lambda: st.session_state.update(page='test_questions'))