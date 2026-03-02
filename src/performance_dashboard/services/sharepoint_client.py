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
    # 1. Setup Configuration from Env
    # Note: MSAL 'Application' auth requires a TENANT_ID
    TENANT_ID = get_secret("SHAREPOINT_TENANT_ID")  
    CLIENT_ID = get_secret("SHAREPOINT_CLIENT_ID")  
    CLIENT_SECRET = get_secret("SHAREPOINT_VALUE")  
    SITE_URL = "https://veneficus.sharepoint.com/sites/VeneficusDataSafe" #get_secret("SHAREPOINT_SITE")  


    TARGET_FOLDER_PATH = "HR Cycle" #get_secret("HR_CYCLE_FOLDER")

    # 2. Extract Hostname and Site Path for Graph
    parsed_url = urlparse(SITE_URL)
    hostname = parsed_url.netloc
    site_path = parsed_url.path.rstrip('/')

    # 3. MSAL Authentication
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=authority,
        client_credential=CLIENT_SECRET
        )

    token_result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    if "access_token" not in token_result:
        print(f"❌ Auth Failed: {token_result.get('error_description')}")
        return

    headers = {'Authorization': f'Bearer {token_result["access_token"]}'}


    def diagnose_sharepoint_graph():
        try:
            # 1. Check connection to the site
            site_endpoint = f"https://graph.microsoft.com/v1.0/sites/{hostname}:{site_path}"
            site_resp = requests.get(site_endpoint, headers=headers)
            site_resp.raise_for_status()
            print(f"✅ Connected with site: {site_resp.json().get('displayName')}")
            site_id = site_resp.json().get('id')
            print(f"✅ Found Site ID: {site_id}")

            # 2. Check the folder and list children
            # Syntax: /sites/{id}:/drive/root:/{path}:/children
            folder_endpoint = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{TARGET_FOLDER_PATH}:/children"
            print(f"\n📁 Content of map '{TARGET_FOLDER_PATH}':")
            response = requests.get(folder_endpoint, headers=headers)          

            if response.status_code == 404:
                print(" ❌ Map not found, check path.")
                return
            response.raise_for_status()
            items = response.json().get('value', [])

            if not items:
                print("(No documents found in this map)")         

            for item in items:
                # 'file' key only exists if the item is a file (not a subfolder)
                item_type = "📄" if "file" in item else "📁"
                name = item.get('name')
                web_url = item.get('webUrl')
                print(f"   {item_type} Naam: {name}")
                print(f"      URL: {web_url}")
            return items, headers, site_id

        except Exception as e:
            print(f"❌ Error: {e}")

    items, headers, site_id = diagnose_sharepoint_graph()
    return items, headers, site_id


def get_file_content(headers, site_id, file_path):  
    # De endpoint om de ruwe inhoud van een bestand op te halen
    download_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{file_path}:/content"

    print(f"DEBUG: Full URL: {download_url}")
    response = requests.get(download_url, headers=headers)   

    if response.status_code == 200:
        return response.content  # Dit zijn de ruwe bytes van je bestand
    else:
        print(f"Error when downloading: {response.status_code}")
        return None    





def get_sharepoint_file(file, sheet_name=0, sub_folder = None):
    # 1. Haal map-namen op uit de environment
    hr_folder = "HR Cycle" #get_secret("HR_CYCLE_FOLDER").strip('/')
    if sub_folder:
        sub_folder = sub_folder.strip('/')     

    # Pad opbouwen
    file_path = f"{hr_folder}/{sub_folder}/{file}" if sub_folder else f"{hr_folder}/{file}"
    encoded_path = quote(file_path, safe='/')

    # 3. Haal alleen headers en site_id op (de items lijst hebben we niet nodig voor pad-downloads
    _, headers, site_id = get_folder_items() 

    # 4. Haal de data op
    file_bytes = get_file_content(headers, site_id, encoded_path)  

    # 5. Zet bytes om naar df
    if file_bytes:
        try: # Check extensie voor de juiste pandas reader
            if file.endswith('.parquet'):
                return pd.read_parquet(io.BytesIO(file_bytes))
            else:
                return pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl', sheet_name=sheet_name)

        except Exception as e:
            print(f"❌ Error when reading DataFrame {file}: {e}")
            return None

    print(f"❌ No data found for: {file_path}")
    return None


def upload_to_sharepoint(file_bytes, target_filename, sub_folder=None):
    hr_folder = "HR Cycle" #get_secret("HR_CYCLE_FOLDER")
    _, headers, site_id = get_folder_items()

    # Pad opbouwen
    path = f"{hr_folder}/{sub_folder}/{target_filename}" if sub_folder else f"{hr_folder}/{target_filename}"
    encoded_path = quote(path, safe="/")

    # Microsoft Graph upload endpoint
    upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{encoded_path}:/content"
    response = requests.put(upload_url, headers=headers, data=file_bytes)

    if response.status_code in [200, 201]:
        print(f"✅ Bestand succesvol geüpload: {target_filename}")
        return True

    else:
        print(f"❌ Upload mislukt: {response.status_code} - {response.text}")
        return False



def main():
    file = "Werknemers_gegevens - Test.xlsx"
    df = get_sharepoint_file(file, sheet_name="TraineesMaria")
    print(df)



if __name__ == "__main__":
    main()
