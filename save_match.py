import pandas as pd
from datetime import datetime

# Funzione per registrare la partita nel CSV
def save_match_to_csv(player1, team1, goals1, player2, team2, goals2, match_type):
    # Crea un dizionario con i dati della partita
    data = {
        "Player 1": player1,
        "Team 1": team1,
        "Goals 1": goals1,
        "Player 2": player2,
        "Team 2": team2,
        "Goals 2": goals2,
        "Match Type": match_type,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Aggiungi i dati a un DataFrame
    df = pd.DataFrame([data])

    # Se il file CSV esiste già, aggiungi i dati, altrimenti creane uno nuovo
    file_path = "match_results.csv"
    try:
        existing_df = pd.read_csv(file_path)
        df = pd.concat([existing_df, df], ignore_index=True)
    except FileNotFoundError:
        pass  # Se il file non esiste, creerà un nuovo file

    # Salva i dati nel CSV
    df.to_csv(file_path, index=False)
