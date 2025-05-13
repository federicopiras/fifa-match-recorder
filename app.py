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
def select_team_stars_flexible(player_label, df):
    st.markdown(f"### 🧍‍♂️ {player_label}")

    search_input = st.text_input(f"Scrivi il nome della squadra ({player_label})", "")

    # Suggerimenti live
    team_names = df["Team"].unique()
    matching_teams = [team for team in team_names if search_input.lower() in team.lower()]

    selected_team = None
    team_info = None

    if matching_teams:
        selected_team = st.selectbox(f"Squadre trovate per '{search_input}'", matching_teams)
        team_info = df[df["Team"] == selected_team].iloc[0]
        st.write(f"**Campionato**: {team_info['Championship']}  \n**Nazionalità**: {team_info['Nationality']}")
    else:
        st.info("❌ Nessuna squadra trovata. Puoi cercarla per nazionalità e campionato.")
        nationality = st.selectbox(f"Nazione campionato ({player_label})", df["Nationality"].unique())
        championships = df[df["Nationality"] == nationality]["Championship"].unique()
        championship = st.selectbox(f"Campionato ({player_label})", championships)
        filtered_teams = df[(df["Nationality"] == nationality) & (df["Championship"] == championship)]["Team"].unique()
        selected_team = st.selectbox(f"Squadra ({player_label})", filtered_teams)
        if selected_team:
            team_info = df[df["Team"] == selected_team].iloc[0]

    # Inserimento manuale in caso nessuna squadra sia selezionata
    use_manual = st.checkbox(f"⚙️ Inserisci manualmente squadra ({player_label})")

    if use_manual:
        selected_team = st.text_input(f"Nome squadra manuale ({player_label})")
        championship = st.text_input(f"Campionato manuale ({player_label})")
        nationality = st.text_input(f"Nazionalità manuale ({player_label})")
    else:
        if team_info is not None:
            championship = team_info["Championship"]
            nationality = team_info["Nationality"]

    #stars = st.selectbox(f"Stelle squadra ({player_label})", [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5])
    stars = st.select_slider(
        f"⭐ Stelle squadra ({player_label})",
        options=[0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
    )

    return selected_team, stars, championship, nationality


st.title("FIFA Match Recorder 🎮")

# Seleziona la versione di FIFA a cui stai giocando
st.markdown("---")
fifa_versions = df_teams['fifa_version'].unique()
st.markdown("### 🎮 Seleziona la versione di FIFA")
selected_version = st.selectbox(" ", sorted(fifa_versions, reverse=True))
df_teams = df_teams[df_teams['fifa_version'] == selected_version]

# Inserimento dati giocatori e squadre
st.markdown("---")
st.markdown("<h2 style='color:#0072C6'>‍🤝‍🧑 Giocatori e squadre</h2>", unsafe_allow_html=True)
giocatori = ['Master', 'Peres', 'Ufo', 'Angi', 'Altro...']

# Giocatore 1
col1, col2 = st.columns(2)

with col1:
    player1_choice = st.selectbox("Giocatore 1", giocatori, index=0)
    if player1_choice == "Altro...":
        player1 = st.text_input("Inserisci nome Giocatore 1")
    else:
        player1 = player1_choice
    team1, stars1, champ1, nation1 = select_team_stars_flexible(player1, df_teams)

# Giocatore 2
with col2:
    player2_choice = st.selectbox("Giocatore 2", giocatori, index=1)
    if player2_choice == "Altro...":
        player2 = st.text_input("Inserisci nome Giocatore 2")
    else:
        player2 = player2_choice

    # ✅ Controllo che i due giocatori siano diversi
    if player1 == player2:
        st.warning("⚠️ I due giocatori devono essere diversi.")
        st.stop()
        
    team2, stars2, champ2, nation2 = select_team_stars_flexible(player2, df_teams)

st.markdown("---")
st.markdown("<h2 style='color:#0072C6'>🎯 Modalità Partita</h2>", unsafe_allow_html=True)
match_type = st.radio(
    "Come è finita la partita?",
    ["Secca", "Golden Gol", "Supplementari", "Rigori"]
)

st.markdown("---")
st.markdown("<h2 style='color:#0072C6'>‍🔢 Risultato</h2>", unsafe_allow_html=True)
goals1 = st.number_input(f"Gol segnati da {player1 or 'Giocatore 1'}", min_value=0, step=1)
goals2 = st.number_input(f"Gol segnati da {player2 or 'Giocatore 2'}", min_value=0, step=1)

st.markdown("---")
if st.button("💾 Registra Partita"):
    # save_match_to_csv(player1, team1, goals1, player2, team2, goals2, match_type)
    save_match_to_google_sheets(
        "fifa_match_results",
        player1, team1, goals1, stars1, champ1, nation1,
        player2, team2, goals2, stars2, champ2, nation2,
        match_type
    )
    st.success("✅ Partita registrata su Google Sheets!")

# Evidenzia il vincitore dopo il salvataggio
if goals1 > goals2:
    st.success(f"🏆 Vittoria di {player1}")
elif goals2 > goals1:
    st.success(f"🏆 Vittoria di {player2}")
else:
    st.info("🤝 Pareggio!")
