# data_handling

The **data_handling** folder contains scripts that manage data operations, including cloning repositories, caching, and loading datasets. These utilities streamline the process of setting up and managing the GAIA dataset for use in the OpenAI Evaluation App.

## Files

### clone_repo.py
This script is responsible for cloning the GAIA dataset repository. It automates the process of downloading the repository to a specified local directory.

#### Key Functions:
- **clone_repository(repo_url, clone_dir)**: 
  - Clones the specified Git repository into the provided directory. If the directory already exists, the function skips the cloning step. 
  - Uses `subprocess.run` to execute the Git command, ensuring the process completes successfully or logs an error.

### delete_cache.py
This script handles cache management by providing functionality to delete the cache directory. This is particularly useful for maintaining optimal storage and performance when reloading or updating datasets.

#### Key Functions:
- **delete_cache_folder(cache_dir)**: 
  - Deletes the specified cache directory and all its contents. 
  - Ensures files have the appropriate permissions to allow deletion and logs any errors encountered during the process.

### load_dataset.py
This script is used to load the GAIA dataset from Hugging Face, perform basic preprocessing, and return it as a Pandas DataFrame. It provides functionality to flatten nested data, convert columns, and add metadata for tracking dataset creation time.

#### Key Functions:
- **load_gaia_dataset(cache_dir, split_name='validation')**: 
  - Loads the specified split of the GAIA dataset from Hugging Face, caching it in the given directory.
  - Configures environment variables for Hugging Face to store the dataset in the specified cache directory.
  - Processes the dataset into a DataFrame, handling missing values and adding a 'created_date' column with the current timestamp.
  - Returns the processed DataFrame with essential columns, including `file_name`, `file_path`, and `result_status`.

- **preprocess_nested_data(df)**: 
  - Flattens the 'Annotator Metadata' column in the dataset, splitting it into multiple columns with descriptive names.
  - Renames columns for consistency and clarity, ensuring the DataFrame is ready for further processing or analysis.
  
These scripts facilitate efficient data preparation and management, enabling seamless loading, caching, and clearing of the GAIA dataset for analysis with ChatGPT.
