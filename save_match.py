import csv
import os
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import streamlit as st
import json

# Percorso del file CSV (nella stessa cartella del main script)
CSV_FILE = "match_results.csv"

def save_match_to_csv(player1, team1, goals1, stars1, player2, team2, goals2, stars2, match_type):
    match_data = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Player1": player1,
        "Team1": team1,
        "Goals1": goals1,
        "Stars1": stars1,
        "Player2": player2,
        "Team2": team2,
        "Goals2": goals2,
        "Stars2": stars2,
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
    # Recupera il dizionario delle credenziali dal file .streamlit/secrets.toml
    json_keyfile_dict = st.secrets["google"]

    # Definisce gli scope per l'accesso a Google Sheets e Google Drive
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    # Crea le credenziali dal dizionario JSON
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_keyfile_dict, scope)

    # Autorizza il client gspread
    client = gspread.authorize(creds)

    return client

# Salva anche su Google Sheets
def save_match_to_google_sheets(sheet_name, player1, team1, goals1, stars1, champ1, nation1,
        player2, team2, goals2, stars2, champ2, nation2, match_type):
    client = authenticate_google_sheets()
    sheet = client.open(sheet_name).sheet1

    winner = ""
    loser = ""
    if goals1 > goals2:
        winner = player1
        loser = player2
    elif goals1 < goals2:
        winner = player2
        loser = player1
    else:
        winner = "patta"
        loser = "patta"

    match_data = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        player1, team1, goals1, stars1, champ1, nation1,
        player2, team2, goals2, stars2, champ2, nation2,
        match_type, winner, loser
    ]

    sheet.append_row(match_data)


def load_from_google_sheets(sheet_name: str):
    client = authenticate_google_sheets()
    sheet = client.open(sheet_name).sheet1  # o usa .worksheet("nome") se usi tab diversi

    records = sheet.get_all_records()
    df = pd.DataFrame(records)

    return df