import streamlit as st
import pandas as pd


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
