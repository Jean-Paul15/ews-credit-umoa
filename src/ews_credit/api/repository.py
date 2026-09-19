"""Chargement des donnees generees (portefeuille + features Spark) en memoire.

L'API sert des resultats deja calcules par le pipeline batch (generation +
Spark) : elle ne recalcule jamais rien depuis les evenements bruts, ce qui
la garde legere et independante d'un cluster Spark actif en permanence.
"""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

COLONNES_ETAT_PANEL = ["credit_id", "stage_ifrs9", "solde_restant_du_fcfa"]
COLONNES_ETAT_FEATURES = [
    "credit_id",
    "retards_consecutifs",
    "solde_moyen_3m_fcfa",
    "solde_moyen_12m_fcfa",
    "ratio_utilisation_decouvert_3m",
    "frequence_incidents_6m",
]


@dataclass(frozen=True)
class DonneesPortefeuille:
    clients: pd.DataFrame
    credits: pd.DataFrame
    etat_credits: pd.DataFrame  # derniere situation connue (stage, solde, features)


def _derniere_ligne_par_credit(df: pd.DataFrame, colonne_ordre: str) -> pd.DataFrame:
    return df.sort_values(colonne_ordre).groupby("credit_id").tail(1)


def charger_donnees(racine_synthetic: Path) -> DonneesPortefeuille:
    clients = pd.read_csv(racine_synthetic / "clients.csv", encoding="utf-8")
    credits = pd.read_csv(racine_synthetic / "credits.csv", encoding="utf-8")
    panel = pd.read_csv(racine_synthetic / "panel_mensuel.csv", encoding="utf-8")
    features = pd.read_parquet(racine_synthetic / "features")

    dernier_etat_panel = _derniere_ligne_par_credit(panel, "mois_relatif")[COLONNES_ETAT_PANEL]
    dernier_etat_features = _derniere_ligne_par_credit(features, "annee_mois")[COLONNES_ETAT_FEATURES]
    etat_credits = dernier_etat_panel.merge(dernier_etat_features, on="credit_id", how="inner")

    credit_client_pays = credits[["credit_id", "client_id", "type_credit"]].merge(
        clients[["client_id", "pays"]], on="client_id"
    )
    etat_credits = etat_credits.merge(credit_client_pays, on="credit_id", how="left")

    return DonneesPortefeuille(clients=clients, credits=credits, etat_credits=etat_credits)
