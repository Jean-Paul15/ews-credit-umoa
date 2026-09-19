"""Onglet : sante globale du portefeuille."""

import pandas as pd
import streamlit as st

from ews_credit.dashboard.api_client import recuperer_vue_ensemble


def afficher() -> None:
    vue = recuperer_vue_ensemble()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Crédits suivis", f"{vue['nb_credits']:,}")
    col2.metric("Alerte faible", f"{vue['nb_alerte_faible']:,}")
    col3.metric("Alerte moyenne", f"{vue['nb_alerte_moyen']:,}")
    col4.metric("Alerte élevée", f"{vue['nb_alerte_eleve']:,}")
    st.metric("Provisionnement IFRS 9 estimé (ECL)", f"{vue['ecl_total_fcfa']:,.0f} FCFA")

    st.subheader("Répartition du portefeuille par pays")
    repartition = pd.DataFrame(vue["repartition_par_pays"]).set_index("pays")
    repartition.columns = ["Nombre de crédits", "ECL (FCFA)"]
    col_gauche, col_droite = st.columns(2)
    col_gauche.bar_chart(repartition["Nombre de crédits"])
    col_droite.bar_chart(repartition["ECL (FCFA)"])
    st.dataframe(repartition, use_container_width=True)
