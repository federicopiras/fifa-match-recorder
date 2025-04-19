import streamlit as st
import pandas as pd

# Carica squadre da CSV
@st.cache_data
def load_teams():
    df = pd.read_csv("squads.csv", header=0, sep=';')
    return df

df_teams = load_teams()

# Funzione per scegliere la squadra
def select_team(player_label):
    nationality = st.selectbox(f"Nazione campionato ({player_label})", df_teams["Nationality"].unique())
    championships = df_teams[df_teams["Nationality"] == nationality]["Championship"].unique()
    championship = st.selectbox(f"Campionato ({player_label})", championships)
    teams = df_teams[(df_teams["Nationality"] == nationality) & (df_teams["Championship"] == championship)]["Team"].unique()
    team = st.selectbox(f"Squadra scelta ({player_label})", teams)
    stars = st.selectbox(f"Stelle squadra ({player_label})", [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5])
    return team

st.title("FIFA Match Recorder 🎮")

st.subheader("🧑‍🤝‍🧑 Giocatori")
player1 = st.selectbox("Giocatore 1", ['Master', 'Peres', 'Ufo', 'Angi'])
player2 = st.selectbox("Giocatore 2", ['Peres', 'Master', 'Ufo', 'Angi'])

st.subheader("⚽ Selezione Squadre")
team1 = select_team(player1)
team2 = select_team(player2)

st.subheader("🎯 Modalità Partita")
match_type = st.radio(
    "Come è finita la partita?",
    ["Secca", "Golden Gol", "Supplementari", "Rigori"]
)

st.subheader("🔢 Risultato")
goals1 = st.number_input(f"Gol segnati da {player1 or 'Giocatore 1'}", min_value=0, step=1)
goals2 = st.number_input(f"Gol segnati da {player2 or 'Giocatore 2'}", min_value=0, step=1)

# Mostra dati quando si preme il pulsante
if st.button("💾 Registra Partita"):
    st.success("✅ Partita registrata (non ancora salvata)")
    st.write({
        "Giocatore 1": player1,
        "Squadra 1": team1,
        "Gol 1": goals1,
        "Giocatore 2": player2,
        "Squadra 2": team2,
        "Gol 2": goals2,
        "Modalità": match_type
    })
