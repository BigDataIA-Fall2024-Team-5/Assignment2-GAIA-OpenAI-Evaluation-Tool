# Streamlit Pages

This folder contains the individual pages for the Streamlit application, each designed for specific functionality within the **OpenAI Evaluation App**. Below is a summary of each page and its primary role within the app.

### 1. `login_page.py`
- **Purpose**: Allows users to log in with their username and password.
- **Key Features**:
  - Validates user credentials through the FastAPI backend.
  - On successful login, redirects users based on their role (admin or regular user).
  - Provides a button for new users to navigate to the registration page.

### 2. `register_page.py`
- **Purpose**: Allows new users to create an account.
- **Key Features**:
  - Collects username, password, and password confirmation.
  - Sends registration data to the FastAPI backend.
  - Redirects to the login page upon successful registration.
  
### 3. `session_expired_page.py`
- **Purpose**: Notifies users when their session has expired.
- **Key Features**:
  - Provides a re-login button, which clears session data and redirects users to the login page.

### 4. `user_page.py`
- **Purpose**: Serves as the main dashboard for regular users.
- **Key Features**:
  - Displays a welcome message with the user’s name.
  - Provides navigation buttons to explore questions and view summary pages.
  - Includes a logout button with confirmation functionality.

### 5. `view_summary.py`
- **Purpose**: Displays a summary of the user's performance.
- **Key Features**:
  - Fetches question data and user-specific results from the FastAPI backend.
  - Shows the distribution of answer statuses with a bar chart.
  - Lists detailed counts for each result status and explains what each status means.
  - Allows users to select between different dataset splits (e.g., test and validation).

### 6. `explore_questions.py`
- **Purpose**: Provides options for users to explore questions from different dataset splits.
- **Key Features**:
  - Allows users to choose between validation and test questions.
  - Navigates to the corresponding questions page based on the user’s selection.

### 7. `validation_questions.py`
- **Purpose**: Displays and allows interaction with questions from the validation split.
- **Key Features**:
  - Fetches validation questions and user results.
  - Allows users to filter questions by level, file type, and result status.
  - Enables users to send questions to ChatGPT for evaluation and update the result status accordingly.
  - Includes pagination and a way to interact with associated PDF files.

### 8. `test_questions.py`
- **Purpose**: Displays questions from the test split for manual review.
- **Key Features**:
  - Similar to `validation_questions.py`, but with no final answer for comparison.
  - Users can manually check and update results without automatic evaluation.

### 9. `admin_page.py`
- **Purpose**: Main dashboard for admin users.
- **Key Features**:
  - Allows access to dataset and user management pages.
  - Includes a logout button with confirmation.

### 10. `admin_user_management.py`
- **Purpose**: Enables admins to manage users within the app.
- **Key Features**:
  - Fetches and displays a list of all users.
  - Allows admin users to promote other users to admin or delete them.
  - Includes confirmation steps for deletion.

### 11. `admin_dataset_management.py`
- **Purpose**: Allows admins to manage and process the GAIA dataset.
- **Key Features**:
  - Provides a button to trigger the dataset processing pipeline.
  - Displays the status of the dataset processing.
  - Includes a back button to navigate back to the main admin dashboard.

Each of these pages is designed to interact with the FastAPI backend, which handles authentication, data retrieval, and user management. The app’s navigation is managed via `st.session_state` to maintain state across pages.
