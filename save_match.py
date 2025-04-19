import csv
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import streamlit as st

# Percorso del file CSV (nella stessa cartella del main script)
CSV_FILE = "match_results.csv"

def save_match_to_csv(player1, team1, goals1, player2, team2, goals2, match_type):
    match_data = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Player1": player1,
        "Team1": team1,
        "Goals1": goals1,
        "Player2": player2,
        "Team2": team2,
        "Goals2": goals2,
        "MatchType": match_type
    }

    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=match_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(match_data)

# Autenticazione per Google Sheets
def authenticate_google_sheets():

    # Carica il percorso del file JSON dalle variabili di Streamlit

    # Stampa per vedere cosa contiene st.secrets
    json_keyfile = st.secrets["google"]["json_keyfile"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)
    return client

# Salva anche su Google Sheets
def save_match_to_google_sheets(sheet_name, player1, team1, goals1, player2, team2, goals2, match_type):
    client = authenticate_google_sheets()
    sheet = client.open(sheet_name).sheet1

    match_data = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        player1, team1, goals1,
        player2, team2, goals2,
        match_type
    ]

    sheet.append_row(match_data)
