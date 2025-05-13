import streamlit as st
import pandas as pd
from save_match import save_match_to_google_sheets
from utils import select_team_stars_flexible


@st.cache_data
def load_teams():
    df = pd.read_csv("squads.csv", header=0, sep=';')
    return df


def run_match_recorder():
    st.title("🏟️ FIFA Match Recorder 🎮")

    df_teams = load_teams()

    st.markdown("### 🎮 Seleziona la versione di FIFA")
    fifa_versions = df_teams['fifa_version'].unique()
    selected_version = st.selectbox(" ", sorted(fifa_versions, reverse=True))
    df_teams = df_teams[df_teams['fifa_version'] == selected_version]

    st.subheader("🧑‍🤝‍🧑 Giocatori")
    giocatori = ['Master', 'Peres', 'Ufo', 'Angi', 'Altro...']

    # Giocatore 1
    player1_choice = st.selectbox("Giocatore 1", giocatori, index=0)
    if player1_choice == "Altro...":
        player1 = st.text_input("Inserisci nome Giocatore 1")
    else:
        player1 = player1_choice

    # Giocatore 2
    player2_choice = st.selectbox("Giocatore 2", giocatori, index=1)
    if player2_choice == "Altro...":
        player2 = st.text_input("Inserisci nome Giocatore 2")
    else:
        player2 = player2_choice

    if player1 == player2:
        st.warning("⚠️ I due giocatori devono essere diversi.")
        st.stop()

    st.subheader("⚽ Selezione Squadre")
    team1, stars1, champ1, nation1 = select_team_stars_flexible(player1, df_teams)
    team2, stars2, champ2, nation2 = select_team_stars_flexible(player2, df_teams)

    st.subheader("🎯 Modalità Partita")
    match_type = st.selectbox(
        "Scegli la modalità di fine partita",
        ["⚔️ Secca", "💀 Golden Gol", "🕐 Supplementari", "🎯 Rigori"]
    )

    st.subheader("🔢 Risultato")
    goals1 = st.number_input(f"Gol segnati da {player1}", min_value=0, step=1)
    goals2 = st.number_input(f"Gol segnati da {player2}", min_value=0, step=1)

    if st.button("💾 Registra Partita"):
        save_match_to_google_sheets(
            "fifa_match_results",
            player1, team1, goals1, stars1, champ1, nation1,
            player2, team2, goals2, stars2, champ2, nation2,
            match_type
        )
        st.success("✅ Partita registrata con successo!")

    # Evidenzia il vincitore dopo il salvataggio
    if goals1 > goals2:
        st.success(f"🏆 Vittoria di {player1}")
    elif goals2 > goals1:
        st.success(f"🏆 Vittoria di {player2}")
    else:
        st.info("🤝 Pareggio!")