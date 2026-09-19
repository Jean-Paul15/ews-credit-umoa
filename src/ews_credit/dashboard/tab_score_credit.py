"""Onglet : consultation du score d'un credit precis (recherche ponctuelle)."""

import streamlit as st

from ews_credit.dashboard.api_client import recuperer_score_credit


def afficher() -> None:
    credit_id = st.text_input("Identifiant du crédit (ex. CRD200000)")
    if not credit_id:
        return

    resultat = recuperer_score_credit(credit_id)
    if resultat is None:
        st.error(f"Aucun crédit trouvé pour « {credit_id} ». Vérifiez l'identifiant et réessayez.")
        return

    col1, col2, col3 = st.columns(3)
    col1.metric("Score de risque", f"{resultat['score_risque']:.2f}")
    col2.metric("Niveau d'alerte", resultat["niveau_alerte"].capitalize())
    col3.metric("Retards consécutifs", resultat["retards_consecutifs"])
