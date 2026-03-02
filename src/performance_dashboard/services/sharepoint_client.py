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

TENANT_ID = get_secret("SHAREPOINT_TENANT_ID")  
CLIENT_ID = get_secret("SHAREPOINT_CLIENT_ID")  
CLIENT_SECRET = get_secret("SHAREPOINT_VALUE")  
SITE_URL = get_secret("SHAREPOINT_SITE")  
HR_FOLDER = get_secret("HR_CYCLE_FOLDER")

def get_folder_items():
    """
    Authenticates with Microsoft Graph and retrieves items from the root folder.

    This function handles MSAL authentication, extracts the Site ID, and performs 
    a diagnostic check by listing all items within the HR_FOLDER.

    Returns:
        Tuple: A tuple containing:
            - items (Optional[List[dict]]): A list of items found in the folder.
            - headers (Optional[dict]): Authorization headers including the access token.
            - site_id (Optional[str]): The unique SharePoint Site ID.
    """

    parsed_url = urlparse(SITE_URL)
    hostname = parsed_url.netloc
    site_path = parsed_url.path.rstrip('/')

    # MSAL Authentication
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
            folder_endpoint = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{HR_FOLDER}:/children"
            print(f"\n📁 Content of map '{HR_FOLDER}':")
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


def get_file_content(headers: dict, site_id: str, file_path: str):  
    """
    Downloads the raw binary content of a specific file from Microsoft Graph.

    Args:
        headers (dict): Authorization headers with a valid access token.
        site_id (str): The unique ID of the SharePoint site.
        file_path (str): The URL-encoded path to the file.

    Returns:
        Optional[bytes]: The raw file bytes if successful, None otherwise.
    """
    download_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{file_path}:/content"

    print(f"DEBUG: Full URL: {download_url}")
    response = requests.get(download_url, headers=headers)   

    if response.status_code == 200:
        print("Respone.status-code = 200")
        return response.content  # Dit zijn de ruwe bytes van je bestand
    else:
        print(f"Error when downloading: {response.status_code}")
        return None    


def get_sharepoint_file(file: str, sheet_name=0, sub_folder = None):
    """
    Downloads a file from SharePoint and converts it into a Pandas DataFrame.

    Supports both .parquet and .xlsx formats. For Parquet files, it verifies 
    the file integrity by checking the 'PAR1' magic header.

    Args:
        file (str): The name of the file including the extension.
        sheet_name (Union[str, int], optional): The Excel sheet name or index. Defaults to 0.
        sub_folder (Optional[str], optional): Optional sub-path within the HR_FOLDER.

    Returns:
        Optional[pd.DataFrame]: A DataFrame containing the file data, or None if the 
            download or conversion fails.
    """
    if sub_folder:
        sub_folder = sub_folder.strip('/')     


    file_path = f"{HR_FOLDER}/{sub_folder}/{file}" if sub_folder else f"{HR_FOLDER}/{file}"
    encoded_path = quote(file_path, safe='/')

    _, headers, site_id = get_folder_items() 

    file_bytes = get_file_content(headers, site_id, encoded_path)  

    if file_bytes:
            if file.endswith('.parquet') and not file_bytes.startswith(b'PAR1'):
                print(f"❌ Corrupt bestand: Bytes beginnen niet met PAR1. Inhoud: {file_bytes[:50]}")
                return None

            try:
                if file.endswith('.parquet'):
                    print("⏳ Parquet engine aanroepen...")
                    df = pd.read_parquet(io.BytesIO(file_bytes))
                    
                    # Check op df zonder de Ambiguous error
                    if df is not None:
                        print(f"✅ File is legit. Rijen: {len(df)}, Type: {type(df)}")
                    return df
                    
                elif file.endswith(".xlsx"):
                    print("⏳ Excel engine aanroepen...")
                    return pd.read_excel(io.BytesIO(file_bytes), engine='openpyxl', sheet_name=sheet_name)
                    
            except Exception as e:
                print(f"❌ Error during conversion of {file}: {str(e)}")
                return None


def upload_to_sharepoint(file_bytes, target_filename, sub_folder=None):
    """
    Uploads a byte stream to a specified location on SharePoint.

    Uses the Microsoft Graph 'content' API for the upload. The result of the 
    operation (success or error status) is printed to the console.

    Args:
        file_bytes (bytes): The raw binary data to be uploaded.
        target_filename (str): The name the file should have on SharePoint.
        sub_folder (Optional[str], optional): Target sub-directory within HR_FOLDER.
    """
    _, headers, site_id = get_folder_items()

    # Pad opbouwen
    path = f"{HR_FOLDER}/{sub_folder}/{target_filename}" if sub_folder else f"{HR_FOLDER}/{target_filename}"
    encoded_path = quote(path, safe="/")
    
    # Microsoft Graph upload endpoint
    upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/{encoded_path}:/content"

    response = requests.put(upload_url, headers=headers, data=file_bytes)

    if response.status_code in [200, 201]:
        print(f"✅ Status code is successful for file: {target_filename}")
        print(response.status_code, response.text)
    else:
        print(f"❌ Error while uploading: {response.status_code} - {response.text}")



def main():
    file = "Werknemers_gegevens - Test.xlsx" #use this to test func
    df = get_sharepoint_file(file, sheet_name="TraineesMaria")
    print(df)



if __name__ == "__main__":
    main()
