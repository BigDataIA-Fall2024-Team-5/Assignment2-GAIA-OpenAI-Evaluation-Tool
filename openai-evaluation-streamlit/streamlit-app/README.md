# streamlit-app

The **streamlit-app** folder contains the frontend application for the OpenAI Evaluation App, built using Streamlit. It provides a user interface for exploring AI evaluations, managing users, and datasets.

## Files

### newapp.py
This is the main script for the Streamlit application, managing navigation between different pages and handling user session states.

#### Key Features:
- **Session Management**: Tracks the current page, user login status, and role.
- **User Pages**: Includes options to explore questions, view summaries, and manage user profiles.
- **Admin Pages**: Allows dataset and user management for admins.
- **Session Expired Page**: Handles expired user sessions.

## Project Structure

- **streamlit_pages/**: Contains the individual page scripts, such as `login_page.py`, `admin_page.py`, and more.
- **newapp.py**: Main script that runs the Streamlit application.
- **requirements.txt**: Lists the Python dependencies required for the app.
- **Dockerfile**: Included to facilitate containerization and deployment.

## Environment Variables
- **FASTAPI_URL**: URL of the FastAPI backend. Ensure this is correctly set in the Docker environment or `.env` file.

This application allows users and administrators to manage AI evaluations and explore dataset results through a user-friendly interface.
