import pandas as pd
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

def load_data(user_id):
        try:
            FILE_PATH = BASE_DIR / "data" / "processed" / "employee_name.xlsx"
            df_peer = pd.read_excel(FILE_PATH, sheet_name="Peer Reviews", index_col=0)
            df_client = pd.read_excel(FILE_PATH, sheet_name="Opdrachtgever Reviews", index_col=0)
            df_peer.index = pd.to_datetime(df_peer.index)
            df_client.index = pd.to_datetime(df_client.index)   
            return df_peer, df_client
        except Exception as e:
            print(f"Fout bij het laden van data voor {user_id}: {e}")
            return None, None

def create_dummies():
    a = [
    {"Datum": "2024-01-15", "Waarde & Vakmanschap": 2, "Eigenaarschap & Resultaat": 2, "Communicatie & Invloed": 2, "Analyse & Probleemoplossing": 2, "Kwaliteit & Vakmanschap": 2, "Visualisatie & Verhaal": 2, "Business & Context": 2, "Samenwerken & Communicatie": 2, "Eigenaarschap & Initiatief": 2},
    {"Datum": "2024-04-15", "Waarde & Vakmanschap": 3, "Eigenaarschap & Resultaat": 2, "Communicatie & Invloed": 3, "Analyse & Probleemoplossing": 3, "Kwaliteit & Vakmanschap": 2, "Visualisatie & Verhaal": 3, "Business & Context": 2, "Samenwerken & Communicatie": 2, "Eigenaarschap & Initiatief": 3},
    {"Datum": "2024-07-15", "Waarde & Vakmanschap": 4, "Eigenaarschap & Resultaat": 3, "Communicatie & Invloed": 4, "Analyse & Probleemoplossing": 3, "Kwaliteit & Vakmanschap": 3, "Visualisatie & Verhaal": 4, "Business & Context": 3, "Samenwerken & Communicatie": 3, "Eigenaarschap & Initiatief": 3},
    {"Datum": "2024-10-15", "Waarde & Vakmanschap": 5, "Eigenaarschap & Resultaat": 4, "Communicatie & Invloed": 4, "Analyse & Probleemoplossing": 4, "Kwaliteit & Vakmanschap": 4, "Visualisatie & Verhaal": 4, "Business & Context": 3, "Samenwerken & Communicatie": 4, "Eigenaarschap & Initiatief": 4}
    ]
    a = pd.DataFrame(a)

    b = [
    {"Datum": "2024-02-01", "Waarde & Vakmanschap": 3, "Eigenaarschap & Resultaat": 2, "Communicatie & Invloed": 3, "Analyse & Probleemoplossing": 3, "Kwaliteit & Vakmanschap": 2, "Visualisatie & Verhaal": 3, "Business & Context": 2, "Samenwerken & Communicatie": 3, "Eigenaarschap & Initiatief": 2},
    {"Datum": "2024-05-01", "Waarde & Vakmanschap": 4, "Eigenaarschap & Resultaat": 3, "Communicatie & Invloed": 3, "Analyse & Probleemoplossing": 4, "Kwaliteit & Vakmanschap": 3, "Visualisatie & Verhaal": 2, "Business & Context": 2, "Samenwerken & Communicatie": 2, "Eigenaarschap & Initiatief": 3},
    {"Datum": "2024-08-01", "Waarde & Vakmanschap": 4, "Eigenaarschap & Resultaat": 4, "Communicatie & Invloed": 2, "Analyse & Probleemoplossing": 4, "Kwaliteit & Vakmanschap": 3, "Visualisatie & Verhaal": 2, "Business & Context": 3, "Samenwerken & Communicatie": 2, "Eigenaarschap & Initiatief": 4},
    {"Datum": "2024-11-01", "Waarde & Vakmanschap": 5, "Eigenaarschap & Resultaat": 5, "Communicatie & Invloed": 2, "Analyse & Probleemoplossing": 4, "Kwaliteit & Vakmanschap": 4, "Visualisatie & Verhaal": 2, "Business & Context": 4, "Samenwerken & Communicatie": 1, "Eigenaarschap & Initiatief": 4}
    ]
    b = pd.DataFrame(b)
    
    c = [
    {"Datum": "2024-03-10", "Waarde & Vakmanschap": 2, "Eigenaarschap & Resultaat": 3, "Communicatie & Invloed": 2, "Analyse & Probleemoplossing": 2, "Kwaliteit & Vakmanschap": 2, "Visualisatie & Verhaal": 2, "Business & Context": 2, "Samenwerken & Communicatie": 2, "Eigenaarschap & Initiatief": 2},
    {"Datum": "2024-06-10", "Waarde & Vakmanschap": 2, "Eigenaarschap & Resultaat": 3, "Communicatie & Invloed": 2, "Analyse & Probleemoplossing": 2, "Kwaliteit & Vakmanschap": 3, "Visualisatie & Verhaal": 3, "Business & Context": 2, "Samenwerken & Communicatie": 3, "Eigenaarschap & Initiatief": 2},
    {"Datum": "2024-09-10", "Waarde & Vakmanschap": 3, "Eigenaarschap & Resultaat": 4, "Communicatie & Invloed": 3, "Analyse & Probleemoplossing": 3, "Kwaliteit & Vakmanschap": 3, "Visualisatie & Verhaal": 3, "Business & Context": 3, "Samenwerken & Communicatie": 3, "Eigenaarschap & Initiatief": 3},
    {"Datum": "2024-12-10", "Waarde & Vakmanschap": 3, "Eigenaarschap & Resultaat": 1, "Communicatie & Invloed": 4, "Analyse & Probleemoplossing": 4, "Kwaliteit & Vakmanschap": 3, "Visualisatie & Verhaal": 4, "Business & Context": 3, "Samenwerken & Communicatie": 4, "Eigenaarschap & Initiatief": 3}
    ]
    c = pd.DataFrame(c)
    
    return a, b, c



    
def load_subskills_map():
    sub_map = {
        'Waarde & Vakmanschap': ['Domeinkennis', 'Methodisch werken', 'Best practices'],
        'Eigenaarschap & Resultaat': ['Doelgerichtheid', 'Verantwoordelijkheid nemen', 'Timemanagement'],
        'Communicatie & Invloed': ['Overtuigingskracht', 'Impact maken', 'Onderhandelen'],
        'Analyse & Probleemoplossing': ['Kritisch denken', 'Data-extractie', 'Root cause analyse'],
        'Kwaliteit & Vakmanschap': ['Code review', 'Test-automatisering', 'Versiebeheer (Git)'],
        'Visualisatie & Verhaal': ['Storytelling met data', 'UX/UI design basics', 'Dashboarding'],
        'Business & Context': ['Stakeholder management', 'Bedrijfsprocessen', 'Marktanalyse'],
        'Samenwerken & Communicatie': ['Actief luisteren', 'Feedback geven/ontvangen', 'Teambuilding'],
        'Eigenaarschap & Initiatief': ['Proactiviteit', 'Zelfsturing', 'Innovatiekracht']
    }
    return sub_map