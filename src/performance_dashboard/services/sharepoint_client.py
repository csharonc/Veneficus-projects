from pathlib import Path
import sys
DIR = Path(__file__).resolve().parent.parent
if str(DIR) not in sys.path:
    sys.path.append(str(DIR))

import msal
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse
import pandas as pd
import io
from performance_dashboard.utils import get_secret
from urllib.parse import quote
load_dotenv()

def get_folder_items():
    TENANT_ID = get_secret("SHAREPOINT_TENANT_ID")  
    CLIENT_ID = get_secret("SHAREPOINT_CLIENT_ID")  
    CLIENT_SECRET = get_secret("SHAREPOINT_VALUE")  
    SITE_URL = get_secret("SHAREPOINT_SITE")  
    
    # .strip() is essentieel voor GitHub Secrets om onzichtbare enters/spaties te verwijderen
    TARGET_FOLDER_PATH = get_secret("HR_CYCLE_FOLDER").strip() 

    parsed_url = urlparse(SITE_URL)
    hostname = parsed_url.netloc
    site_path = parsed_url.path.rstrip('/')
    
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    app = msal.ConfidentialClientApplication(
        CLIENT_ID, 
        authority=authority, 
        client_credential=CLIENT_SECRET
    )
    
    token_result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" not in token_result:
        return None, None, None

    headers = {'Authorization': f'Bearer {token_result["access_token"]}'}

    # Haal Site ID op
    site_endpoint = f"https://graph.microsoft.com/v1.0/sites/{hostname}:{site_path}"
    site_resp = requests.get(site_endpoint, headers=headers)
    site_resp.raise_for_status()
    site_id = site_resp.json().get('id')
    
    return None, headers, site_id

def get_file_content(headers, site_id, file_path):  
    # BELANGRIJK: Zorg dat het pad begint zonder slash voor de root:/ endpoint
    clean_path = file_path.lstrip('/')
    encoded_path = quote(clean_path, safe='/')
    
    download_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{encoded_path}:/content" 
    
    response = requests.get(download_url, headers=headers)
    
    if response.status_code == 200:
        return response.content
    else:
        # Dit print de werkelijke reden van Microsoft in je GitHub logs
        print(f"❌ Microsoft API Error {response.status_code}: {response.text}")
        return None   


def get_sharepoint_file(file, sheet_name=0, sub_folder=None):
    # Alles strippen van onbedoelde slashes en spaties
    hr_folder = get_secret("HR_CYCLE_FOLDER").strip().strip('/')
    
    if sub_folder:
        sub_folder = sub_folder.strip().strip('/')
        full_path = f"{hr_folder}/{sub_folder}/{file}"
    else:
        full_path = f"{hr_folder}/{file}"

    # Verwijder dubbele slashes mochten die er per ongeluk zijn
    full_path = full_path.replace("//", "/")

    _, headers, site_id = get_folder_items()
    if not headers:
        return None

    file_bytes = get_file_content(headers, site_id, full_path)
    
    if file_bytes:
        try:
            if file.endswith('.parquet'):
                return pd.read_parquet(io.BytesIO(file_bytes))
            else:
                return pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl', sheet_name=sheet_name)
        except Exception as e:
            print(f"❌ Pandas Error: {e}")
    return None

def upload_to_sharepoint(file_bytes, target_filename, sub_folder=None):
    hr_folder = get_secret("HR_CYCLE_FOLDER").strip().strip('/')
    _, headers, site_id = get_folder_items()
    
    if sub_folder:
        sub_folder = sub_folder.strip().strip('/')
        path = f"{hr_folder}/{sub_folder}/{target_filename}"
    else:
        path = f"{hr_folder}/{target_filename}"
    
    path = path.replace("//", "/").lstrip('/')
    encoded_path = quote(path, safe="/")
    
    upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{encoded_path}:/content"
    response = requests.put(upload_url, headers=headers, data=file_bytes)
    
    return response.status_code in [200, 201]

def main():
    file = "Werknemers_gegevens - Test.xlsx" 
    df = get_sharepoint_file(file, sheet_name="TraineesMaria")
    print(df)

if __name__ == "__main__":
    main()
