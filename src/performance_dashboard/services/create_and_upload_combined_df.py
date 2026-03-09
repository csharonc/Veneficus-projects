"""
Module for retrieving, combining, and moving SharePoint files containing response data.
"""

import sys
from pathlib import Path
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
DIR = Path(__file__).resolve().parent.parent.parent
if str(DIR) not in sys.path:
    sys.path.append(str(DIR))

from performance_dashboard.utils import get_secret
from performance_dashboard.services.sharepoint_client import *

target_filename="Combined_data.xlsx"
combined_df_folder = get_secret("COMBINED_RESPONSES_FOLDER")
transformed_data_folder = get_secret("TRANSFORMED_RESPONSES_FOLDER")
processed_data_folder = get_secret("PROCESSED_RESPONSES_FOLDER")

def combine_newest_files():
    """
    Retrieves the newest files from the transformed data folder in SharePoint,
    extracts them into pandas DataFrames, and concatenates them.

    Returns:
        tuple: A combined pandas DataFrame and a list of processed file names.
               Returns None implicitly if no dataframes are found.
    """
    items, _, _ = get_folder_items(transformed_data_folder)

    processed_items, _, _ = get_folder_items(processed_data_folder)
    processed_filenames = {item.get("name") for item in processed_items if "file" in item}

    df_list = []
    file_info_list = []
    for item in items:
        file_name = item.get("name")
        if file_name not in processed_filenames:
            print(f"🔄 Processing new file: {file_name}")
            df = get_sharepoint_file(file_name, sub_folder = transformed_data_folder)
            if df is None:
                print(f"Empty df found: {file_name}")
            else:
                df_list.append(df)
                file_info_list.append({"name": file_name, "id": item.get("id")})
        else:
            print(f"Skipping (already processed): {file_name}")

    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
        return combined_df, file_info_list
    else:
        print("No dataframes found to concat.")

def move_files(file_info_list):
    """
    Moves a given list of files to the 'processed' folder in SharePoint 
    using the Microsoft Graph API.

    Args:
        file_names (list): A list of strings representing the names of the files to move.
    """
    items, headers, site_id = get_folder_items(sub_folder="TypeformData")
    processed_folder_id = next((i['id'] for i in items if i['name'] == "processed"), None)
    
    for file in file_info_list:
        file_id = file['id']
        file_name = file['name']
            
        if file_id:
            move_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{file_id}"
                
            move_data = {
                    "parentReference": {"id": processed_folder_id},
                    "name": file_name 
            }

            response = requests.patch(move_url, headers=headers, json=move_data)
                        
            if response.status_code in [200, 201]:
                print(f"Moved: {file_name}")
            else:
                print(f"Error while moving {file_name}: {response.text}")

def main():
    """
    Main execution sequence: combines new files, uploads the merged dataframe 
    to SharePoint, and moves the source files to a processed directory.
    """
    result = combine_newest_files()
    if result:
        combined_df, file_names = result
        upload_and_merge(combined_df, target_filename, combined_df_folder)
        move_files(file_names)
    else:
        print("No results, nothing to do")

if __name__ == "__main__":
    main()