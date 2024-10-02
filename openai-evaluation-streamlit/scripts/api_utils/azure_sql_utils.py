#azure_sql_utils
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.types import NVARCHAR, Integer, DateTime
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from fastapi import HTTPException, status
import logging
import numpy as np

# Load environment variables
load_dotenv()

# Initialize logging
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

# Helper function to log and raise HTTP exceptions
def log_and_raise(status_code, detail, log_message):
    logger.warning(log_message)
    raise HTTPException(status_code=status_code, detail=detail)


# Centralized utility to get SQLAlchemy connection string
def get_sqlalchemy_connection_string():
    """
    Constructs an SQLAlchemy connection string for Azure SQL Database.
    """
    server = os.getenv('AZURE_SQL_SERVER')
    user = os.getenv('AZURE_SQL_USER')
    password = os.getenv('AZURE_SQL_PASSWORD')
    database = os.getenv('AZURE_SQL_DATABASE')

    if not all([server, user, password, database]):
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Missing database configuration.",
            "Azure SQL environment variables are missing."
        )

    return f"mssql+pymssql://{user}:{password}@{server}/{database}"


# Insert DataFrame to SQL
def insert_dataframe_to_sql(df, table_name):
    """
    Inserts DataFrame into Azure SQL Database (replaces existing table).
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                drop_table_query = text(f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE {table_name};")
                connection.execute(drop_table_query)
                transaction.commit()
            except Exception as e:
                transaction.rollback()
                log_and_raise(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Failed to drop existing table.",
                    f"Error dropping table '{table_name}': {e}"
                )

        # Insert the data into the new table
        df.to_sql(table_name, engine, if_exists='replace', index=False, dtype={
            'task_id': NVARCHAR(length=50),
            'Question': NVARCHAR(length='max'),
            'Level': Integer,
            'FinalAnswer': NVARCHAR(length='max'),
            'file_name': NVARCHAR(length=255),
            'file_path': NVARCHAR(length='max'),
            'Annotator_Metadata_Steps': NVARCHAR(length='max'),
            'Annotator_Metadata_Number_of_steps': NVARCHAR(length='max'),
            'Annotator_Metadata_How_long_did_this_take': NVARCHAR(length=100),
            'Annotator_Metadata_Tools': NVARCHAR(length='max'),
            'Annotator_Metadata_Number_of_tools': Integer,
            'user_result_status': NVARCHAR(length=50),
            'created_date': DateTime
        })

    except SQLAlchemyError as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Database error during data insertion.",
            f"SQLAlchemy error during data insertion: {e}"
        )

    except Exception as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Unexpected error during data insertion.",
            f"Unexpected error: {e}"
        )

def convert_numpy_types(data):
    """
    Helper function to convert numpy data types to native Python types.
    """
    if isinstance(data, np.generic):  # catches both int64, float64, etc.
        return data.item()  # convert to native Python type
    return data

# Fetch DataFrame from SQL
def fetch_all_questions(table_name='GaiaDataset'):
    """
    Fetches data from Azure SQL as a DataFrame.
    Returns the data as a JSON-serializable list of dictionaries.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, con=engine)
        
        # Convert DataFrame to JSON-serializable dictionary
        result = df.map(convert_numpy_types).to_dict(orient="records")
        return result

    except SQLAlchemyError as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Database error while fetching data.",
            f"SQLAlchemy error during data fetch: {e}"
        )

    except Exception as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Unexpected error while fetching data.",
            f"Unexpected error: {e}"
        )


# Fetch user results
def fetch_user_results(user_id):
    """
    Fetches the user-specific results from the Azure SQL Database.
    Returns the data as a JSON-serializable list of dictionaries.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        query = text("""
            SELECT 
                user_id, 
                task_id, 
                user_result_status,
                chatgpt_response 
            FROM user_results 
            WHERE user_id = :user_id
        """)
        with engine.connect() as connection:
            result = connection.execute(query, {"user_id": user_id}).fetchall()

        if result:
            df = pd.DataFrame(result, columns=['user_id', 'task_id', 'user_result_status', 'chatgpt_response'])
            
            # Convert DataFrame to JSON-serializable dictionary
            result = df.map(convert_numpy_types).to_dict(orient="records")

            return result
        
        # If no results, return an empty list
        return []

    except OperationalError as e:
        log_and_raise(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Service unavailable. Please try again later.",
            f"Operational error: {e}"
        )

    except SQLAlchemyError as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Database error while fetching results.",
            f"SQLAlchemy error: {e}"
        )

    except Exception as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Unexpected error while fetching results.",
            f"Unexpected error: {e}"
        )
def update_user_result_in_db(user_id, task_id, status, chatgpt_response, table_name='user_results'):
    """
    Updates user-specific result and ChatGPT response in the user_results table.
    Returns True if successful, False otherwise.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                update_query = text(f"""
                    MERGE INTO {table_name} AS target
                    USING (SELECT :user_id AS user_id, :task_id AS task_id, :status AS status, :chatgpt_response AS chatgpt_response) AS source
                    ON target.user_id = source.user_id AND target.task_id = source.task_id
                    WHEN MATCHED THEN
                        UPDATE SET user_result_status = source.status, chatgpt_response = source.chatgpt_response
                    WHEN NOT MATCHED THEN
                        INSERT (user_id, task_id, user_result_status, chatgpt_response) 
                        VALUES (source.user_id, source.task_id, source.status, source.chatgpt_response);
                """)

                # Execute the MERGE query
                result = connection.execute(update_query, {
                    'user_id': user_id,
                    'task_id': task_id,
                    'status': status,
                    'chatgpt_response': chatgpt_response
                })

                # Commit transaction
                transaction.commit()
                return True 

            except Exception as e:
                transaction.rollback()
                logger.error(f"Transaction error during result update: {e}")
                return False 

    except SQLAlchemyError as e:
        logger.error(f"SQLAlchemy error during update: {e}")
        return False 

    except Exception as e:
        logger.error(f"Unexpected error during update: {e}")
        return False  



# Fetch user information
def fetch_user_from_sql(username):
    """
    Fetch user information based on username.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        query = text("SELECT user_id, username, password, role FROM users WHERE username = :username")
        with engine.connect() as connection:
            result = connection.execute(query, {"username": username}).fetchone()

        if result:
            return dict(result._mapping)
        return None

    except OperationalError as e:
        log_and_raise(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Service unavailable. Please try again later.",
            f"Operational error: {e}"
        )

    except SQLAlchemyError as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Database error occurred, please contact support.",
            f"SQLAlchemy error: {e}"
        )

    except Exception as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "An unexpected error occurred.",
            f"Unexpected error: {e}"
        )


# Insert user to SQL
def insert_user_to_sql(username, hashed_password, role):
    """
    Inserts a new user with a hashed password into the users table.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        insert_user_query = text("""
            INSERT INTO users (user_id, username, password, role)
            VALUES (NEWID(), :username, :password, :role)
        """)

        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                connection.execute(insert_user_query, {
                    'username': username,
                    'password': hashed_password,
                    'role': role
                })
                transaction.commit()
            except SQLAlchemyError as e:
                transaction.rollback()
                log_and_raise(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Error inserting user.",
                    f"SQLAlchemy error during user insertion: {e}"
                )

    except Exception as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Unexpected error occurred during user insertion.",
            f"Unexpected error: {e}"
        )


# Fetch all users
def fetch_all_users():
    """
    Fetch all users from the database.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        query = text("SELECT user_id, username, role FROM users")
        with engine.connect() as connection:
            result = connection.execute(query).fetchall()

        return [row._asdict() for row in result]

    except OperationalError as e:
        log_and_raise(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Service unavailable. Please try again later.",
            f"Operational error: {e}"
        )

    except SQLAlchemyError as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Database error occurred, please contact support.",
            f"SQLAlchemy error: {e}"
        )

    except Exception as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "An unexpected error occurred.",
            f"Unexpected error: {e}"
        )


# Remove user
def remove_user(user_id: str):
    """
    Remove a user from the database along with related user_results.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                # Delete related user_results
                delete_results_query = text("DELETE FROM user_results WHERE user_id = :user_id")
                connection.execute(delete_results_query, {"user_id": user_id})

                # Delete user
                delete_user_query = text("DELETE FROM users WHERE user_id = :user_id")
                result = connection.execute(delete_user_query, {"user_id": user_id})

                if result.rowcount > 0:
                    transaction.commit()
                    return True
                else:
                    log_and_raise(
                        status.HTTP_404_NOT_FOUND,
                        "User not found.",
                        f"Failed to find user '{user_id}' during deletion."
                    )

            except SQLAlchemyError as e:
                transaction.rollback()
                log_and_raise(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Error during user deletion.",
                    f"SQLAlchemy error during deletion: {e}"
                )

    except OperationalError as e:
        log_and_raise(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Service unavailable. Please try again later.",
            f"Operational error: {e}"
        )

    except SQLAlchemyError as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Database error occurred, please contact support.",
            f"SQLAlchemy error: {e}"
        )

    except Exception as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "An unexpected error occurred.",
            f"Unexpected error: {e}"
        )


# Promote user to admin
def promote_to_admin(user_id: str):
    """
    Promote a user to admin role by their user_id.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        query = text("UPDATE users SET role = 'admin' WHERE user_id = :user_id")
        with engine.connect() as connection:
            transaction = connection.begin()
            try:
                result = connection.execute(query, {"user_id": user_id})
                transaction.commit()

                if result.rowcount > 0:
                    return True
                else:
                    log_and_raise(
                        status.HTTP_404_NOT_FOUND,
                        "User not found.",
                        f"Failed to find user '{user_id}' for promotion."
                    )

            except SQLAlchemyError as e:
                transaction.rollback()
                log_and_raise(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Error during user promotion.",
                    f"SQLAlchemy error during promotion: {e}"
                )

    except OperationalError as e:
        log_and_raise(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "Service unavailable. Please try again later.",
            f"Operational error: {e}"
        )

    except SQLAlchemyError as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Database error occurred, please contact support.",
            f"SQLAlchemy error: {e}"
        )

    except Exception as e:
        log_and_raise(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "An unexpected error occurred.",
            f"Unexpected error: {e}"
        )
