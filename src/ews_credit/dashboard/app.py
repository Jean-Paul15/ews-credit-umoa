"""Dashboard Streamlit EWS-Credit — consomme l'API FastAPI, jamais les
fichiers directement. `streamlit run src/ews_credit/dashboard/app.py`."""

import requests
import streamlit as st

from ews_credit.dashboard import tab_credits_a_risque, tab_score_credit, tab_simulation, tab_vue_ensemble

st.set_page_config(page_title="EWS-Credit UMOA", layout="wide")
st.title("Système d'alerte précoce — portefeuille de crédits UMOA")

ONGLETS = {
    "Vue d'ensemble": tab_vue_ensemble,
    "Crédits à surveiller": tab_credits_a_risque,
    "Score d'un crédit": tab_score_credit,
    "Simulation provisionnement": tab_simulation,
}

try:
    conteneurs = st.tabs(list(ONGLETS.keys()))
    for conteneur, module in zip(conteneurs, ONGLETS.values()):
        with conteneur:
            module.afficher()
except requests.exceptions.ConnectionError:
    st.error(
        "Impossible de joindre l'API EWS-Credit. Vérifiez qu'elle tourne "
        "(`uvicorn ews_credit.api.main:app`) et que EWS_API_URL pointe dessus."
    )
