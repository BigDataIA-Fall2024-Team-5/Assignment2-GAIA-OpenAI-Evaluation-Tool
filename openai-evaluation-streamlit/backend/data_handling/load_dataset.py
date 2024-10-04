import os
import pandas as pd
from datasets import load_dataset
from datetime import datetime

# Load the GAIA dataset using Hugging Face with authentication
def load_gaia_dataset(cache_dir, split_name='validation'):
    """
    Load the GAIA dataset from Hugging Face with the given split name.
    Automatically adds 'created_date' column with the current timestamp.
    
    :param cache_dir: Directory to cache the dataset.
    :param split_name: The dataset split to load ('validation', 'test', etc.).
    :return: Loaded and preprocessed DataFrame with 'created_date' column.
    """
    # Set environment variables for Hugging Face
    os.environ["HF_HOME"] = cache_dir
    os.environ["HF_DATASETS_CACHE"] = cache_dir  # Set the datasets cache directory explicitly
    
    # Ensure that the cache directory exists
    os.makedirs(cache_dir, exist_ok=True)

    # Specify the configuration to load
    config_name = '2023_all'  # Available: ['2023_all', '2023_level1', '2023_level2', '2023_level3']

    # Load the dataset into the specified cache directory
    ds = load_dataset('gaia-benchmark/GAIA', config_name, trust_remote_code=True, cache_dir=cache_dir)

    # Attempt to convert to DataFrame
    try:
        # Convert to DataFrame based on the provided split name
        df = pd.DataFrame(ds[split_name])
        
        # Flatten the 'Annotator Metadata' column
        df = preprocess_nested_data(df)
        
        # Data cleaning: Convert 'file_name' and 'file_path' columns to string and handle NaNs
        if 'file_name' in df.columns:
            df['file_name'] = df['file_name'].astype(str).fillna('')  # Convert to string and replace NaNs with empty strings
        if 'file_path' in df.columns:
            df['file_path'] = df['file_path'].astype(str).fillna('')  # Convert to string and replace NaNs with empty strings
        
        # Add a new column 'result_status' with an initial value 'N/A'
        df['result_status'] = 'N/A'
        
        # **Add the 'created_date' column with the current timestamp**
        df['created_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"Dataset for split '{split_name}' successfully converted to DataFrame with 'created_date'.")
    except Exception as e:
        print(f"Error converting dataset for split '{split_name}' to DataFrame: {e}")
        return None

    return df

# Flatten the 'Annotator Metadata' column
def preprocess_nested_data(df):
    if 'Annotator Metadata' in df.columns:
        # Normalize the 'Annotator Metadata' column into separate columns
        metadata_df = pd.json_normalize(df['Annotator Metadata'])
        # Rename columns to include a prefix for clarity
        metadata_df.columns = [f"Annotator_Metadata_{col}" for col in metadata_df.columns]
        # Concatenate with the original DataFrame, dropping the original 'Annotator Metadata' column
        df = pd.concat([df.drop(columns=['Annotator Metadata']), metadata_df], axis=1)
    
    df = df.rename(columns={
        'Final answer': 'FinalAnswer',
        'Annotator_Metadata_Number of steps': 'Annotator_Metadata_Number_of_steps',
        'Annotator_Metadata_How long did this take?': 'Annotator_Metadata_How_long_did_this_take',
        'Annotator_Metadata_Number of tools': 'Annotator_Metadata_Number_of_tools'
    })
    
    return df
