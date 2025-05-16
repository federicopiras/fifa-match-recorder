import streamlit as st
import pandas as pd
from save_match import load_from_google_sheets

@st.cache_data
def load_matches():
    return load_from_google_sheets("fifa_match_results")

@st.cache_data
def load_squads():
    return pd.read_csv("squads.csv", sep=";")

def run_analytics():
    st.title("📊 Analisi Partite FIFA")

    df = load_matches()
    squads = load_squads()

    # Selezione sezione
    sezione = st.radio("📂 Seleziona sezione", ["📈 Generale", "👤 Per giocatore", "⚔️ Testa a testa"])

    if sezione == "📈 Generale":
        st.header("📈 Statistiche generali")
        st.metric("Totale partite giocate", len(df))
        st.metric("Giocatori distinti", len(set(df['Player1']).union(set(df['Player2']))))
        st.metric("Gol totali", df['Goals1'].sum() + df['Goals2'].sum())

        st.metric("Gol medi a partita", round((df['Goals1'].sum() + df['Goals2'].sum()) / len(df), 2))
        st.metric("Pareggi", len(df[df['Winner'] == 'patta']))

        # Squadre e campionati utilizzati per FIFA selezionato
        fifa_selected = st.selectbox("🎮 Seleziona FIFA", df["fifa_version"].unique().tolist(), index=0)

        df_fifa = df[df["fifa_version"] == fifa_selected]
        squads_fifa = squads[squads["fifa_version"] == fifa_selected]

        used_teams = pd.concat([df_fifa["Team1"], df_fifa["Team2"]]).unique()
        used_championships = pd.concat([df_fifa["Championship1"], df_fifa["Championship2"]]).unique()

        st.subheader("✅ Squadre utilizzate")
        st.progress(len(used_teams) / len(squads_fifa["Team"].unique()))
        st.caption(f"{len(used_teams)} su {len(squads_fifa['Team'].unique())} squadre utilizzate")

        st.subheader("✅ Campionati utilizzati")
        st.progress(len(used_championships) / len(squads_fifa["Championship"].unique()))
        st.caption(f"{len(used_championships)} su {len(squads_fifa['Championship'].unique())} campionati utilizzati")

    elif sezione == "👤 Per giocatore":
        st.header("👤 Statistiche aggregate per giocatore")

        players = pd.concat([df['Player1'], df['Player2']]).dropna().unique()
        stats = []
        for player in players:
            partite_giocate = df[(df['Player1'] == player) | (df['Player2'] == player)]
            vittorie = len(df[df['Winner'] == player])
            pareggi = len(partite_giocate[partite_giocate['Winner'] == 'patta'])
            sconfitte = len(partite_giocate) - vittorie - pareggi
            gol_fatti = partite_giocate.apply(lambda x: x['Goals1'] if x['Player1'] == player else x['Goals2'], axis=1).sum()
            gol_subiti = partite_giocate.apply(lambda x: x['Goals2'] if x['Player1'] == player else x['Goals1'], axis=1).sum()

            # Conta stelle
            stelle = pd.concat([
                df[df['Player1'] == player]['Stars1'],
                df[df['Player2'] == player]['Stars2']
            ]).value_counts().sort_index()

            stats.append({
                "Giocatore": player,
                "Partite": len(partite_giocate),
                "Vittorie": vittorie,
                "Sconfitte": sconfitte,
                "Pareggi": pareggi,
                "Gol fatti": gol_fatti,
                "Gol subiti": gol_subiti,
                "Distribuzione stelle": stelle.to_dict()
            })

        df_stats = pd.DataFrame(stats).sort_values("Vittorie", ascending=False)
        st.dataframe(df_stats.drop(columns=["Distribuzione stelle"]))

        st.subheader("⭐ Distribuzione stelle usate")
        for row in stats:
            st.markdown(f"**{row['Giocatore']}**")
            st.bar_chart(pd.Series(row['Distribuzione stelle']))

    elif sezione == "⚔️ Testa a testa":
        st.header("⚔️ Confronto tra due giocatori")

        players = pd.concat([df['Player1'], df['Player2']]).dropna().unique()

        p1 = st.selectbox("Giocatore 1", players)
        p2 = st.selectbox("Giocatore 2", [p for p in players if p != p1])

        confronto = df[((df['Player1'] == p1) & (df['Player2'] == p2)) | ((df['Player1'] == p2) & (df['Player2'] == p1))]

        vittorie_p1 = len(confronto[confronto['Winner'] == p1])
        vittorie_p2 = len(confronto[confronto['Winner'] == p2])
        pareggi = len(confronto[confronto['Winner'] == 'patta'])

        gol_p1 = confronto.apply(lambda x: x['Goals1'] if x['Player1'] == p1 else x['Goals2'], axis=1).sum()
        gol_p2 = confronto.apply(lambda x: x['Goals1'] if x['Player1'] == p2 else x['Goals2'], axis=1).sum()

        st.subheader(f"Risultati tra {p1} e {p2}")
        st.metric(f"Vittorie {p1}", vittorie_p1)
        st.metric(f"Vittorie {p2}", vittorie_p2)
        st.metric("Pareggi", pareggi)

        st.subheader("Gol totali")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(f"{p1}", gol_p1)
        with col2:
            st.metric(f"{p2}", gol_p2)

        st.subheader("Storico partite")
        st.dataframe(confronto)
