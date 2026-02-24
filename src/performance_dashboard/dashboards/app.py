import sys
from pathlib import Path
DIR = Path(__file__).resolve().parent.parent.parent
if str(DIR) not in sys.path:
    sys.path.append(str(DIR))
print(sys.path)

import streamlit as st 
import plotly.graph_objects as go
import warnings
import pandas as pd
import plotly.express as px
from performance_dashboard.utils import load_data, load_subskills_map
from performance_dashboard.services.sharepoint_client import get_folder_items, get_file_content


warnings.filterwarnings("ignore", message="missing ScriptRunContext")

st.set_page_config(page_title="Skill Dashboard", layout="wide", page_icon=":bar_chart:")

@st.cache_data #Just reload to see changes in code
def get_user_data(person_id):
    df_peer, df_client = load_data(person_id)
    # List all unique skills from both files
    all_skills = df_peer.columns.to_list() + df_client.columns.to_list()
    if "Datum" in all_skills: 
        all_skills.remove("Datum")
    return df_peer, df_client, all_skills

# 2. VISUALISATION
def create_combined_radar(df_p, df_c):
    peer_latest = df_p.iloc[-1].drop('Datum', errors='ignore')
    client_latest = df_c.iloc[-1].drop('Datum', errors='ignore')

    full_profile = pd.concat([peer_latest, client_latest])

    r_values = full_profile.tolist() + [full_profile.iloc[0]]
    theta_values = full_profile.index.tolist() + [full_profile.index[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=r_values,
        theta=theta_values,
        fill='toself',
        line_color='blue',
        name='Mijn Profiel'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 4])
        ),
        margin=dict(l=80, r=80, t=20, b=20),
        showlegend=False
    )
    return fig

def render_progression_plot(df, title, selected_skills):
    st.write(f"#### {title}")
    colors = px.colors.qualitative.Pastel

    if len(df) > 1: # Line plot for multiple measuring points
        fig = go.Figure()
        for i, skill in enumerate(selected_skills):
            if skill in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['Datum'], 
                        y=df[skill],
                        mode='lines+markers',
                        opacity=0.7,
                        line=dict(color=colors[i % len(colors)]),
                        marker=dict(color="red", size=10),
                        name=skill 
                    )
                )

        fig.update_xaxes(tickvals=df["Datum"])
        fig.update_yaxes(range=[0, 4.2]) 
        fig.update_layout(
            hovermode="x unified",
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True) 
    
    elif len(df) == 1: # Bar plot for when there's only 1 measuring point
        row = df.iloc[0]
        scores = [row[skill] for skill in selected_skills if skill in df.columns]
        skills_scores = [skill for skill in selected_skills if skill in df.columns]
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=skills_scores,
                y=scores,
                marker_color=colors[:len(skills_scores)], 
                opacity=0.8,
                width = 0.4
            )
        )

        fig.update_layout(
            height=350,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False
        )
        fig.update_yaxes(range=[-2, 4.2], tickvals=[0, 1, 2, 3, 4])
        st.plotly_chart(fig, use_container_width=True)

# 3. PAGE SELECTION

def show_home_page(df_p, df_c):     
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Vergelijking: Peer vs. Opdrachtgever")
        st.plotly_chart(create_combined_radar(df_p, df_c), use_container_width=True)
    with col2:
        st.subheader("Details")
        st.info(f"Laatste Peer Feedback: {df_p.index[-1].date()}")
        st.success(f"Laatste Opdrachtgever: {df_c.index[-1].date()}")
        st.write("De radar chart toont de meest recente scores van beide bronnen.")

def show_progression_page(df_p, df_c, skills):
    st.title("Gedetailleerde Progressie")
    #Select here the default skills shown
    selected_skills = st.sidebar.multiselect("Kies vaardigheden:", options = skills, default = (skills[1], skills[-2]))
    
    col_plot, col_info = st.columns([2, 1])
    with col_plot:
        render_progression_plot(df_p, "Ontwikkeling volgens Peers", selected_skills)
        st.divider()
        render_progression_plot(df_c, "Ontwikkeling volgens Opdrachtgever", selected_skills)
    
    #Add a column with subskills based on each selected skill
    with col_info:
        st.markdown("#### Op welke subskills focus jij je?")  
        sub_map = load_subskills_map() 
        for skill in selected_skills:
            st.markdown(f"**{skill}**")
            
            items = sub_map.get(skill, "Geen details beschikbaar.")
            if isinstance(items, str):
                items = items.split(',')

            html_list = ""
            for item in items:
                html_list += f"<li>{item.strip()}</li>"
            
            st.markdown(f"<small><ul>{html_list}</ul></small>", unsafe_allow_html=True)
            st.markdown("---")

# 4. AUTH & MAIN

if "ingelogd" not in st.session_state:
    st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    st.title("Inloggen Trainee Portal")
    email = st.text_input("Voer hier je email in") 
    password = st.text_input("Voer hier je wachtwoord in", type= "password")
    
    # Get personal data + password for verification
    FILE_PATH = DIR / "performance_dashboard" / "data" / "processed" / "Werknemers_gegevens - Test.xlsx"
    info = pd.read_excel(FILE_PATH, index_col=0, sheet_name= "TraineesMaria")

    shrpt_info = get

    if st.button("Inloggen"):
        matches = info.loc[info["Emailadres"] == email, ["Wachtwoord", "Persoons_ID"]]
        if matches.empty:
            st.error("Dit e-mailadres en/of wachtwoord zijn incorrect. Ga naar de accountmanager als je je wachtwoord bent vergeten.")
        else:
            user_id = matches["Persoons_ID"].iloc[0]

            #Authentification
            if matches["Wachtwoord"].iloc[0] == password: 
                try:        
                    df_peer, df_client = load_data(user_id= user_id)
                    if df_peer is not None and df_client is not None: #Check if both files are available
                        st.session_state.ingelogd = True
                        st.session_state.user_id = user_id
                        st.rerun()
                    else:
                        st.write("Op dit moment is er nog niet genoeg data om het dashboard te bouwen.")
                except Exception as e:
                    print(f"Fout bij het laden van data voor {user_id}: {e}")
            else:
                st.error("Dit e-mailadres en/of wachtwoord zijn incorrect. Ga naar de accountmanager als je je wachtwoord bent vergeten.")


else:
    def main():
        df_p, df_c, skills = get_user_data(st.session_state.user_id)
        
        st.sidebar.title(f"Welkom, {st.session_state.user_id}")
        page = st.sidebar.radio("Navigatie", ["Hoofdpagina", "Progressie Detail"])
        
        if page == "Hoofdpagina":
            show_home_page(df_p, df_c)
        elif page == "Progressie Detail":
            show_progression_page(df_p, df_c, skills)

        if st.sidebar.button("Uitloggen"):
            st.session_state.ingelogd = False
            st.rerun()

    if __name__ == "__main__":
        main()