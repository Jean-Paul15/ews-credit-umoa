"""Onglet : simulation d'impact d'une degradation sur le provisionnement IFRS9."""

import streamlit as st

from ews_credit.dashboard.api_client import simuler_provisionnement


def afficher() -> None:
    st.caption(
        "Simule la dégradation d'un cran (Sain→Dégradé ou Dégradé→Défaut) des crédits "
        "au score de risque le plus élevé, et son impact sur le provisionnement IFRS 9."
    )
    part = st.slider("Part du portefeuille qui se dégrade", 0, 100, 10, step=5) / 100

    if st.button("Simuler"):
        with st.spinner("Simulation en cours..."):
            resultat = simuler_provisionnement(part)
        col1, col2, col3 = st.columns(3)
        col1.metric("ECL avant", f"{resultat['ecl_avant_fcfa']:,.0f} FCFA")
        col2.metric("ECL après", f"{resultat['ecl_apres_fcfa']:,.0f} FCFA")
        col3.metric("Variation", f"{resultat['variation_pct']:+.1f} %")
