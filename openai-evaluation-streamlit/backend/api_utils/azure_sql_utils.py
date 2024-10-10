import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.types import NVARCHAR, Integer, DateTime
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging
import numpy as np
import pyodbc

# Initialize logging
logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

# Global variable to store SQLAlchemy connection params
_sqlalchemy_params = None

def set_sqlalchemy_connection_params(params: dict):
    """
    Set the SQLAlchemy connection parameters (server, user, password, database).
    This will be called from fast_main.py.
    """
    global _sqlalchemy_params
    _sqlalchemy_params = params

def get_sqlalchemy_connection_string():
    """
    Constructs an SQLAlchemy connection string for Azure SQL Database using pyodbc.
    """
    if not _sqlalchemy_params:
        raise ValueError("Azure SQL connection parameters not set. Call set_sqlalchemy_connection_params first.")
    
    server = _sqlalchemy_params['server']
    user = _sqlalchemy_params['user']
    password = _sqlalchemy_params['password']
    database = _sqlalchemy_params['database']

    # Using pyodbc with ODBC Driver 17 for SQL Server
    return f"mssql+pyodbc://{user}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"


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
                raise RuntimeError(f"Error dropping table '{table_name}': {e}")

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
            'result_status': NVARCHAR(length=50),
            'created_date': DateTime
        })

        print("Data inserted successfuly to Azure SQL")

    except SQLAlchemyError as e:
        raise RuntimeError(f"SQLAlchemy error during data insertion: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error during data insertion: {e}")

def convert_numpy_types(data):
    """
    Helper function to convert numpy data types to native Python types.
    """
    if isinstance(data, np.generic):  # catches both int64, float64, etc.
        return data.item()  # convert to native Python type
    return data

# Fetch DataFrame from SQL
def fetch_all_questions(table_name):
    """
    Fetches data from Azure SQL as a DataFrame.
    Returns the data as a JSON-serializable list of dictionaries.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        query = text(f"SELECT * FROM {table_name}")
        
        # Use connection.execute to fetch data, then create a DataFrame
        with engine.connect() as connection:
            result_proxy = connection.execute(query)
            # Fetch all data from the executed query
            result = result_proxy.fetchall()
            # Get column names from the result proxy
            columns = result_proxy.keys()
            
            # Convert the result to a DataFrame
            df = pd.DataFrame(result, columns=columns)
        
        # Convert numpy data types in DataFrame to JSON-serializable dictionary
        json_result = df.map(convert_numpy_types).to_dict(orient="records")
        return json_result

    except SQLAlchemyError as e:
        raise RuntimeError(f"SQLAlchemy error during data fetch: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error while fetching data: {e}")


from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, SQLAlchemyError
import pandas as pd

# Fetch user results with dataset_split and optional model_name filtering
def fetch_user_results(user_id, dataset_split, model_name=None):
    """
    Fetches the user-specific results from the Azure SQL Database filtered by dataset_split
    and optionally by model_name.
    Returns the data as a JSON-serializable list of dictionaries.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)

        # Base SQL query
        query = """
            SELECT 
                user_id, 
                task_id, 
                user_result_status,
                chatgpt_response,
                model_name
            FROM user_results 
            WHERE user_id = :user_id AND dataset_split = :dataset_split
        """

        # Include model_name filter if provided
        if model_name:
            query += " AND model_name = :model_name"
        
        # Prepare query parameters
        params = {"user_id": user_id, "dataset_split": dataset_split}
        if model_name:
            params["model_name"] = model_name

        with engine.connect() as connection:
            result = connection.execute(text(query), params).fetchall()

        if result:
            # Convert the result to a DataFrame
            df = pd.DataFrame(result, columns=['user_id', 'task_id', 'user_result_status', 'chatgpt_response', 'model_name'])
            
            # Convert DataFrame to JSON-serializable dictionary
            result = df.applymap(convert_numpy_types).to_dict(orient="records")

            return result
        
        # If no results, return an empty list
        return []

    except OperationalError as e:
        raise RuntimeError(f"Operational error: {e}")

    except SQLAlchemyError as e:
        raise RuntimeError(f"SQLAlchemy error while fetching results: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error while fetching results: {e}")




# Update user result
def update_user_result_in_db(user_id, task_id, status, chatgpt_response, dataset_split, model_name, table_name='user_results'):
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
                # Now also match on dataset_split and model_name to update the correct row
                update_query = text(f"""
                    MERGE INTO {table_name} AS target
                    USING (
                        SELECT :user_id AS user_id, :task_id AS task_id, :status AS status, 
                               :chatgpt_response AS chatgpt_response, :dataset_split AS dataset_split, 
                               :model_name AS model_name
                    ) AS source
                    ON target.user_id = source.user_id 
                       AND target.task_id = source.task_id 
                       AND target.dataset_split = source.dataset_split
                       AND target.model_name = source.model_name
                    WHEN MATCHED THEN
                        UPDATE SET user_result_status = source.status, 
                                   chatgpt_response = source.chatgpt_response
                    WHEN NOT MATCHED THEN
                        INSERT (user_id, task_id, user_result_status, chatgpt_response, dataset_split, model_name) 
                        VALUES (source.user_id, source.task_id, source.status, source.chatgpt_response, source.dataset_split, source.model_name);
                """)

                # Execute the MERGE query
                result = connection.execute(update_query, {
                    'user_id': user_id,
                    'task_id': task_id,
                    'status': status,
                    'chatgpt_response': chatgpt_response,
                    'dataset_split': dataset_split,
                    'model_name': model_name
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
        raise RuntimeError(f"Operational error: {e}")

    except SQLAlchemyError as e:
        raise RuntimeError(f"SQLAlchemy error: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")


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
                raise RuntimeError(f"SQLAlchemy error during user insertion: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error during user insertion: {e}")


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
        raise RuntimeError(f"Operational error: {e}")

    except SQLAlchemyError as e:
        raise RuntimeError(f"SQLAlchemy error: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")


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
                    raise ValueError(f"User '{user_id}' not found during deletion.")

            except SQLAlchemyError as e:
                transaction.rollback()
                raise RuntimeError(f"SQLAlchemy error during deletion: {e}")

    except OperationalError as e:
        raise RuntimeError(f"Operational error: {e}")

    except SQLAlchemyError as e:
        raise RuntimeError(f"SQLAlchemy error: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")


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
                    raise ValueError(f"User '{user_id}' not found for promotion.")

            except SQLAlchemyError as e:
                transaction.rollback()
                raise RuntimeError(f"SQLAlchemy error during promotion: {e}")

    except OperationalError as e:
        raise RuntimeError(f"Operational error: {e}")

    except SQLAlchemyError as e:
        raise RuntimeError(f"SQLAlchemy error: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")
