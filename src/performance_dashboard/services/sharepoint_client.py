import msal
import requests
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import pandas as pd
import io
load_dotenv()

def get_folder_items():
    # 1. Setup Configuration from Env
    # Note: MSAL 'Application' auth requires a TENANT_ID
    TENANT_ID = os.getenv("SHAREPOINT_TENANT_ID")  
    CLIENT_ID = os.getenv("SHAREPOINT_CLIENT_ID")  
    CLIENT_SECRET = os.getenv("SHAREPOINT_VALUE")  
    SITE_URL = os.getenv("SHAREPOINT_SITE")  # e.g., https://veneficus.sharepoint.com/sites/VeneficusDataSafe  
   
    # The folder path relative to the Document Library root (usually 'Shared Documents')
    # In Graph, we don't need the full /sites/... prefix if we address the site by path first.
    TARGET_FOLDER_PATH = os.getenv("SHAREPOINT_TARGET_FOLDER")  
 
    # 2. Extract Hostname and Site Path for Graph
    parsed_url = urlparse(SITE_URL)
    hostname = parsed_url.netloc
    site_path = parsed_url.path.rstrip('/')
   
    # 3. MSAL Authentication
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    app = msal.ConfidentialClientApplication(CLIENT_ID, authority=authority, client_credential=CLIENT_SECRET)
   
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
                print("   (No documents found in this map)")
           
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
    
    response = requests.get(download_url, headers=headers)
    
    if response.status_code == 200:
        return response.content  # Dit zijn de ruwe bytes van je bestand
    else:
        print(f"Fout bij downloaden: {response.status_code}")
        return None    


def get_sharepoint_file(file, sheet_name = 0):
    #get url's
    TARGET_FOLDER_PATH = os.getenv("SHAREPOINT_TARGET_FOLDER")
    file_path = f"{TARGET_FOLDER_PATH}/{file}"

    #get folder items and info
    items, headers, site_id = get_folder_items()
    df = pd.DataFrame(items)
    df = df[df.name == file]
    file_id = df["id"] 
    file_bytes = get_file_content(headers, site_id, file_path)
    
    if file_bytes:
        df= pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl', sheet_name = sheet_name)
        return df
 
if __name__ == "__main__":
    file = "Werknemers_gegevens - Test.xlsx" 
    df = get_sharepoint_file(file)