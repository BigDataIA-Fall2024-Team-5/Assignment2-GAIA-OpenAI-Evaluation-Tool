import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.types import NVARCHAR, Integer, DateTime
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from fastapi import HTTPException, status

# Load environment variables
load_dotenv()

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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Missing database configuration.")
    
    return f"mssql+pymssql://{user}:{password}@{server}/{database}"


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
            except Exception:
                transaction.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to drop existing table.")
        
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
    
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error during data insertion.")
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error during data insertion.")


def fetch_dataframe_from_sql(table_name='GaiaDataset'):
    """
    Fetches data from Azure SQL as a DataFrame.
    """
    try:
        connection_string = get_sqlalchemy_connection_string()
        engine = create_engine(connection_string)
        
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, con=engine)
        return df
    
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching data.")
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error while fetching data.")


def fetch_user_results(user_id):
    """
    Fetches the user-specific results from the Azure SQL Database with enhanced error handling.
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
            return df
        return pd.DataFrame()

    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable. Please try again later.")
    
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error while fetching results.")
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error while fetching results.")


def update_user_result(user_id, task_id, status, chatgpt_response, table_name='user_results'):
    """
    Updates user-specific result and ChatGPT response in the user_results table.
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
                connection.execute(update_query, {
                    'user_id': user_id, 
                    'task_id': task_id, 
                    'status': status, 
                    'chatgpt_response': chatgpt_response
                })
                transaction.commit()
            except Exception:
                transaction.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error during result update.")

    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error during result update.")
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error during result update.")


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
    
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable. Please try again later.")
    
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred, please contact support.")
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


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
            except SQLAlchemyError:
                transaction.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error inserting user.")
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error occurred during user insertion.")


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
    
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable. Please try again later.")
    
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred, please contact support.")
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


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
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
            
            except SQLAlchemyError:
                transaction.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error during user deletion.")

    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable. Please try again later.")
    
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred, please contact support.")
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")


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
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
            
            except SQLAlchemyError:
                transaction.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error during user promotion.")

    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable. Please try again later.")
    
    except SQLAlchemyError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error occurred, please contact support.")
    
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred.")
