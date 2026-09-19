"""Onglet : liste priorisee des credits a surveiller — le coeur d'un EWS
(le charge de risque doit voir la liste a traiter, pas chercher un par un)."""

import pandas as pd
import streamlit as st

from ews_credit.dashboard.api_client import recuperer_credits_a_risque

COLONNES_AFFICHEES = {
    "credit_id": "Crédit",
    "pays": "Pays",
    "type_credit": "Type",
    "score_risque": "Score",
    "niveau_alerte": "Alerte",
    "stage_ifrs9": "Stage IFRS9",
    "solde_restant_du_fcfa": "Solde restant dû (FCFA)",
    "retards_consecutifs": "Retards consécutifs",
}


def afficher() -> None:
    st.caption("Crédits dont le score de risque dépasse le seuil d'alerte moyen, du plus au moins risqué.")
    limite = st.slider("Nombre de crédits à afficher", 10, 300, 50, step=10)

    credits = recuperer_credits_a_risque(limite)
    if not credits:
        st.success("Aucun crédit au-dessus du seuil d'alerte actuellement.")
        return

    tableau = pd.DataFrame(credits)[list(COLONNES_AFFICHEES)].rename(columns=COLONNES_AFFICHEES)
    st.dataframe(
        tableau,
        use_container_width=True,
        hide_index=True,
        column_config={"Score": st.column_config.ProgressColumn("Score", min_value=0.0, max_value=1.0)},
    )
