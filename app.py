import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from save_match import save_match_to_csv, save_match_to_google_sheets, authenticate_google_sheets

# Carica squadre da CSV
@st.cache_data
def load_teams():
    df = pd.read_csv("squads.csv", header=0, sep=';')
    return df

df_teams = load_teams()

# Funzione per scegliere la squadra
def select_team_stars(player_label):
    st.markdown(f"### 🧍‍♂️ {player_label}")
    nationality = st.selectbox(f"Nazione campionato ({player_label})", df_teams["Nationality"].unique())
    championships = df_teams[df_teams["Nationality"] == nationality]["Championship"].unique()
    championship = st.selectbox(f"Campionato ({player_label})", championships)
    teams = df_teams[(df_teams["Nationality"] == nationality) & (df_teams["Championship"] == championship)]["Team"].unique()
    team = st.selectbox(f"Squadra scelta ({player_label})", teams)
    stars = st.selectbox(f"Stelle squadra ({player_label})", [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5])
    return team, stars

st.title("FIFA Match Recorder 🎮")

st.subheader("🧑‍🤝‍🧑 Giocatori")
giocatori = ['Master', 'Peres', 'Ufo', 'Angi', 'Altro...']

# Giocatore 1
player1_choice = st.selectbox("Giocatore 1", giocatori)
if player1_choice == "Altro...":
    player1 = st.text_input("Inserisci nome Giocatore 1")
else:
    player1 = player1_choice

# Giocatore 2
player2_choice = st.selectbox("Giocatore 2", giocatori)
if player2_choice == "Altro...":
    player2 = st.text_input("Inserisci nome Giocatore 2")
else:
    player2 = player2_choice

st.subheader("⚽ Selezione Squadre")
team1, stars1 = select_team_stars(player1)
team2, stars2 = select_team_stars(player2)

st.subheader("🎯 Modalità Partita")
match_type = st.radio(
    "Come è finita la partita?",
    ["Secca", "Golden Gol", "Supplementari", "Rigori"]
)

st.subheader("🔢 Risultato")
goals1 = st.number_input(f"Gol segnati da {player1 or 'Giocatore 1'}", min_value=0, step=1)
goals2 = st.number_input(f"Gol segnati da {player2 or 'Giocatore 2'}", min_value=0, step=1)

if st.button("💾 Registra Partita"):
    # save_match_to_csv(player1, team1, goals1, player2, team2, goals2, match_type)
    save_match_to_google_sheets("fifa_match_results", player1, team1, goals1, stars1, player2, team2, goals2, stars2, match_type)
    st.success("✅ Partita registrata su CSV e Google Sheets!")
