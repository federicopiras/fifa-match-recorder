import streamlit as st
import pandas as pd
from save_match import load_from_google_sheets


@st.cache_data
def load_data():
    return load_from_google_sheets("fifa_match_results")


def run_analytics():
    st.title("📊 Statistiche Partite FIFA")

    df = load_data()

    st.markdown("## 🏆 Vittorie per giocatore")
    if "Winner" in df.columns:
        winners = df["Winner"].value_counts()
        st.bar_chart(winners)
    else:
        st.warning("Colonna 'Winner' non trovata nel file CSV.")

    st.markdown("## ⚽ Gol totali per giocatore")
    df_gol = pd.DataFrame({
        "Giocatore": pd.concat([df["Player1"], df["Player2"]]),
        "Gol": pd.concat([df["Goals1"], df["Goals2"]])
    })
    gol_tot = df_gol.groupby("Giocatore").sum().sort_values("Gol", ascending=False)
    st.bar_chart(gol_tot)

    st.markdown("## 🎽 Squadre più usate")
    squadre = pd.concat([df["Team1"], df["Team2"]]).value_counts().head(10)
    st.bar_chart(squadre)

    st.markdown("## 🗂️ Campionati più scelti")
    if "Championship1" in df.columns and "Championship2" in df.columns:
        campionati = pd.concat([df["Championship1"], df["Championship2"]]).value_counts().head(10)
        st.bar_chart(campionati)
    else:
        st.warning("Colonne 'Championship1' e/o 'Championship2' non trovate.")

    st.markdown("## 🎮 Statistiche per giocatore")
    giocatori = pd.concat([df["Player1"], df["Player2"]]).dropna().unique().tolist()
    giocatore_scelto = st.selectbox("Seleziona giocatore", giocatori)

    partite = df[(df["Player1"] == giocatore_scelto) | (df["Player2"] == giocatore_scelto)]
    st.write(f"📋 Partite giocate da {giocatore_scelto}:")
    st.dataframe(partite)