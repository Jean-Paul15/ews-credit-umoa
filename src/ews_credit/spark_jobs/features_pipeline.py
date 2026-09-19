"""Assemble les familles de features comportementales autour de l'agregation
mensuelle : point d'entree unique du feature engineering distribue."""

from pyspark.sql import DataFrame

from ews_credit.spark_jobs.balance_trend_features import ajouter_tendance_solde
from ews_credit.spark_jobs.delinquency_features import ajouter_retards_consecutifs
from ews_credit.spark_jobs.incident_features import ajouter_frequence_incidents
from ews_credit.spark_jobs.monthly_aggregation import agreger_par_credit_mois
from ews_credit.spark_jobs.overdraft_features import ajouter_ratio_utilisation_decouvert

COLONNES_FEATURES_FINALES = [
    "credit_id",
    "annee_mois",
    "statut_echeance",
    "retards_consecutifs",
    "solde_compte_fcfa",
    "solde_moyen_3m_fcfa",
    "solde_moyen_6m_fcfa",
    "solde_moyen_12m_fcfa",
    "ratio_utilisation_decouvert_3m",
    "frequence_incidents_6m",
]


def construire_features_comportementales(events: DataFrame) -> DataFrame:
    mensuel = agreger_par_credit_mois(events)
    mensuel = ajouter_retards_consecutifs(mensuel)
    mensuel = ajouter_tendance_solde(mensuel)
    mensuel = ajouter_ratio_utilisation_decouvert(mensuel)
    mensuel = ajouter_frequence_incidents(mensuel)
    return mensuel.select(*COLONNES_FEATURES_FINALES)
