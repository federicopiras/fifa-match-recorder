import streamlit as st
from match_recorder import run_match_recorder
from analytics import run_analytics

st.set_page_config(page_title="FIFA Match Recorder", layout="wide")

# Navigazione
pagina = st.sidebar.radio("📚 Seleziona sezione", ["🏟️ Registra partita", "📊 Analytics"])

if pagina == "🏟️ Registra partita":
    run_match_recorder()

elif pagina == "📊 Analytics":
    run_analytics()
