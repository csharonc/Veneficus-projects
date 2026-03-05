import sys
from pathlib import Path
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
DIR = Path().resolve().parent
if str(DIR) not in sys.path:
    sys.path.append(str(DIR))

from performance_dashboard.utils import get_secret
from performance_dashboard.services.sharepoint_client import *


target_filename="Combined_data.xlsx"
combined_df_folder = get_secret("COMBINED_RESPONSES_FOLDER")
transformed_data_folder = get_secret("TRANSFORMED_RESPONSES_FOLDER")
processed_data_folder = get_secret("PROCESSED_RESPONSES_FOLDER")

def combine_newest_files():
    items, headers, site_id = get_folder_items(transformed_data_folder)

    df_list = []
    file_names = []
    for item in items:
        item_type = "file" if "file" in item else "map"
        if item_type == "file":
            file_name = item.get("name")
            file_names.append(file_name)
            df = get_sharepoint_file(file_name, sub_folder = transformed_data_folder)
            if df is None:
                print(f"Empty df found: {file_name}")
            else:
                df_list.append(df)

    if df_list:
        combined_df = pd.concat(df_list, ignore_index=True)
        return combined_df, file_names
    else:
        print("No dataframes found to concat.")

def move_files(file_names):
    items, headers, site_id = get_folder_items(sub_folder="TypeformData")
    
    for item in items:
        if item['name'] == 'processed' and 'folder' in item:
            processed_folder_id = item['id']
            break
    
    for file_name in file_names:
        file_id = next((i['id'] for i in items if i['name'] == file_name), None)
            
        if file_id:
            move_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{file_id}"
                
            # De 'parentReference' update verplaatst het bestand
            move_data = {
                    "parentReference": {"id": processed_folder_id},
                    "name": file_name # Je kunt hier eventueel ook de naam aanpassen
            }

            response = requests.patch(move_url, headers=headers, json=move_data)
                        
            if response.status_code in [200, 201]:
                print(f"✅ Moved: {file_name}")
            else:
                print(f"❌ Error while moving {file_name}: {response.text}")

def main():
    result = combine_newest_files()
    if result:
        combined_df, file_names = result
        upload_and_merge(combined_df, target_filename, combined_df_folder)
        move_files(file_names)
    else:
        print("No results, nothing to do")

if __name__ == "__main__":
    main()