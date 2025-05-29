import streamlit as st
import pandas as pd
from save_match import load_from_google_sheets
import altair as alt

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
        st.header("👤 Statistiche per singolo giocatore")
        players = pd.concat([df['Player1'], df['Player2']]).dropna().unique()
        selected_player = st.selectbox("Seleziona un giocatore", sorted(players))
        partite = df[(df['Player1'] == selected_player) | (df['Player2'] == selected_player)]
        vittorie = len(partite[partite['Winner'] == selected_player])
        pareggi = len(partite[partite['Winner'] == 'patta'])
        sconfitte = len(partite) - vittorie - pareggi
        gol_fatti = partite.apply(lambda x: x['Goals1'] if x['Player1'] == selected_player else x['Goals2'],
                                  axis=1).sum()
        gol_subiti = partite.apply(lambda x: x['Goals2'] if x['Player1'] == selected_player else x['Goals1'],
                                   axis=1).sum()
        miglior_vittoria = partite.loc[(partite['Winner'] == selected_player), ['Goals1', 'Goals2']]
        miglior_vittoria['diff'] = abs(miglior_vittoria['Goals1'] - miglior_vittoria['Goals2'])
        max_diff = miglior_vittoria['diff'].max() if not miglior_vittoria.empty else 0
        peggior_sconfitta = partite.loc[
            (partite['Winner'] != selected_player) & (partite['Winner'] != 'patta'), ['Goals1', 'Goals2']]
        peggior_sconfitta['diff'] = abs(peggior_sconfitta['Goals1'] - peggior_sconfitta['Goals2'])
        max_sconfitta = peggior_sconfitta['diff'].max() if not peggior_sconfitta.empty else 0
        st.subheader(f"📋 Statistiche per {selected_player}")
        st.metric("Partite giocate", len(partite))
        st.metric("Vittorie", vittorie)
        st.metric("Pareggi", pareggi)
        st.metric("Sconfitte", sconfitte)
        st.metric("Gol fatti", gol_fatti)
        st.metric("Gol subiti", gol_subiti)
        st.metric("Miglior vittoria (scarto)", max_diff)
        st.metric("Peggior sconfitta (scarto)", max_sconfitta)

        # Andamento ultime N partite con colore risultato
        st.subheader("📊 Andamento partite recenti")
        num_matches = st.slider("Numero di partite da visualizzare", min_value=5, max_value=30, value=10, step=1)

        ultimi = partite.tail(num_matches).copy()
        ultimi['risultato'] = ultimi.apply(
            lambda x: 'Vittoria' if x['Winner'] == selected_player else 'Sconfitta' if x['Winner'] != 'patta'
                    else 'Pareggio', axis=1)

        ultimi['scarto'] = ultimi.apply(
            lambda x: (x['Goals1'] - x['Goals2']) if x['Player1'] == selected_player else (x['Goals2'] - x['Goals1']),
            axis=1
        )
        ultimi['Timestamp'] = pd.to_datetime(ultimi['Timestamp'])

        chart = alt.Chart(ultimi.reset_index()).mark_bar().encode(
            x=alt.X('timestamp:T', title='Data'),
            y=alt.Y('scarto:Q', title='Differenza reti'),
            color=alt.Color('risultato:N', scale=alt.Scale(domain=['Vittoria', 'Pareggio', 'Sconfitta'],
                                                           range=['green', 'gray', 'red'])),
            tooltip=['timestamp', 'risultato', 'scarto']
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)

        # Squadre più usate
        squadre = pd.concat([
            partite[partite['Player1'] == selected_player]['Team1'],
            partite[partite['Player2'] == selected_player]['Team2']
        ]).value_counts()

        st.subheader("🏟️ Squadre più utilizzate")
        st.bar_chart(squadre.head(10))
        # Distribuzione stelle
        stars1 = partite[partite['Player1'] == selected_player]['Stars1'].dropna().astype(float)
        stars2 = partite[partite['Player2'] == selected_player]['Stars2'].dropna().astype(float)
        stelle_raw = pd.concat([stars1, stars2])
        if not stelle_raw.empty:
            stelle = stelle_raw.value_counts().sort_index()
            st.subheader("⭐ Distribuzione stelle")
            st.bar_chart(stelle)
        else:
            st.info("❕ Nessuna informazione sulle stelle disponibili per questo giocatore.")

        # Nazionalità / Campionati più giocati
        naz1 = partite[partite['Player1'] == selected_player][['Nationality1', 'Championship1']]
        naz2 = partite[partite['Player2'] == selected_player][['Nationality2', 'Championship2']]
        naz1.columns = ['Nazionalità', 'Campionato']
        naz2.columns = ['Nazionalità', 'Campionato']
        naz_tot = pd.concat([naz1, naz2])
        st.subheader("🌍 Nazionalità e Campionati più usati")
        combo = naz_tot.value_counts().reset_index(name='Partite')
        st.dataframe(combo)

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
