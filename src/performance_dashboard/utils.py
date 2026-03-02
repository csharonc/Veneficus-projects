import sys
from pathlib import Path
DIR = Path(__file__).resolve().parent.parent.parent
if str(DIR) not in sys.path:
    sys.path.append(str(DIR))

import pandas as pd
from pathlib import Path
import streamlit as st
import os


def create_dummies(): #NOT NEEDED AFTER FINALIZATION
    """
    Creates three dummy DataFrames representing performance scores over time.

    Each DataFrame contains a 'Datum' (Date) column and several skill categories 
    with numerical scores, simulating different assessment periods or sources.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: A tuple of three 
            Pandas DataFrames (a, b, and c).
    """
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
    """
    Returns a mapping of high-level skill categories to specific sub-skills.

    This map is used to categorize individual competencies under broader 
    performance themes like 'Value & Craftsmanship' or 'Communication'.

    Returns:
        Dict[str, List[str]]: A dictionary where keys are main skill categories 
            and values are lists of associated sub-skills.
    """
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

def get_secret(key):
    """
    Retrieves a secret value from Streamlit secrets or environment variables.

    The function first attempts to access the key via st.secrets. If that 
    fails (e.g., during local development without a secrets.toml), 
    it falls back to os.getenv.

    Args:
        key (str): The name of the secret/environment variable to retrieve.

    Returns:
        Optional[str]: The secret value if found, otherwise None.
    """
    try: 
        return st.secrets(key)
    except Exception:
         return os.getenv(key)