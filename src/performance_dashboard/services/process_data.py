from pathlib import Path
import sys
DIR = Path(__file__).resolve().parent.parent.parent
if str(DIR) not in sys.path:
    sys.path.append(str(DIR))

import io
import pandas as pd
from performance_dashboard.services.sharepoint_client import get_sharepoint_file, upload_to_sharepoint
from performance_dashboard.utils import get_secret

# path1 = BASE_DIR / "performance_dashboard" / "data"/ "raw" / "Peer_Feedback" / "peer_1.parquet"
# path2 = BASE_DIR / "performance_dashboard" / "data"/ "raw" / "Opdrachtgever_Feedback" / "opdrachtgever_1.parquet"

def define_paths():
    path1 = "opdrachtgever_1.parquet"
    path2 = "peer_1.parquet"
    return path1, path2

def get_mapping():
    mapping = {
        1: ["de uitvoerder", "functioneel", "duidelijk", "focus op taak", "fijn teamlid", "taakgericht", "is een betrouwbare uitvoerder"],
        2: ["de doorvrager", "productie-waardig", "gebruikersgericht", "focus op waarde", "de verbinder", "projectgericht", "de kritische partner"],
        3: ["de systeemdenker", "de standaard", "richtinggevend", "focus op keten", "de kartrekker", "toekomstgericht", "de expert"],
        4: ["is een project-eigenaar"],
        0: ["heeft sturing nodig"]
    }

    id_to_q = {
    'zEFBRre0JvuV' : "Analyse & Probleemoplossing", 
    'xrpnryUhvlwC' : "Kwaliteit & Vakmanschap", 
    'tNNOU1qabV2K' : "Visualisatie & Verhaal", 
    'b4j7QEttWAM0' : "Business & Context",
    'PbZsX4a9wSCB' : "Samenwerken & Communicatie", 
    'fGbuwROaGceQ' : "Eigenaarschap & Initiatief", 
    'YeoMmpNa3umy' : "Waarde & Vakmanschap ", #CHECK
    'swelQCdUyu9d' : "Eigenaarschap & Resultaat ", #CHECK
    'vQmeObrQ7BdE' : "Communicatie & Invloed" #CHECK
    }
    return mapping, id_to_q

def get_df(path1, path2):
    sub_folder = "TypeformData/transformed_responses" #get_secret("TRANSFORMED_RESPONSES_FOLDER")

    # df1 = pd.read_parquet(path1, engine="pyarrow")
    # df2 = pd.read_parquet(path2, engine="pyarrow")
    df1 = get_sharepoint_file(file = path1, sub_folder=sub_folder)
    df2 = get_sharepoint_file(file = path2, sub_folder=sub_folder)
    if df1 and df2:
        print("Successfully retrieved both DataFrames")
    #Combine into one df
    df = pd.concat([df1, df2], ignore_index= True)
    return df

def get_answer_scores(path1, path2):
    mapping, id_to_q = get_mapping()
    df = get_df(path1, path2)
    question_ids = df["question_id"][df["question_type"] == "multiple_choice"].to_list()

    filtered_df = df[df["question_id"].isin(question_ids)].copy()
    filtered_df["clean_answer"] = filtered_df["answer_value"].str.lower().str.strip()

    def get_score(text):
        for key, values in mapping.items():
            if any(text.startswith(v) for v in values):
                return key
        print("No valid answer found, have you checked the mapping?")
        return None

    filtered_df["score"] = filtered_df["clean_answer"].apply(get_score)
    answers = dict(zip(filtered_df["question_id"], filtered_df["score"]))

    #Add the date to the dict
    filtered_df["date"] = pd.to_datetime(filtered_df["submitted_at"]).dt.date
    answers["date"] = filtered_df["date"][0]

    #Transform to df
    temp_dict = answers
    row_index = temp_dict.pop("date")
    answers_df = pd.DataFrame([answers], index = [row_index])

    clean_df = answers_df.rename(columns = id_to_q)
    print(clean_df)
    return clean_df


def main():
    path1, path2 = define_paths()
    df = get_answer_scores(path1, path2)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=True)
    file_bytes = output.getvalue()

    # 3. Uploaden naar de 'processed_responses' map
    target_folder = "TypeformData/combined_data" #get_secret("PROCESSED_RESPONSES_FOLDER")
    target_filename = "processed_feedback_test.xlsx" # Voor nu even gehardcoded
    
    success = upload_to_sharepoint(
        file_bytes=file_bytes, 
        target_filename=target_filename, 
        sub_folder=target_folder
    )

    if success:
        print("🚀 ETL proces succesvol afgerond en geüpload naar SharePoint.")
    else:
        print("❌ ETL proces mislukt tijdens upload.")

if __name__ == "__main__":
    main()