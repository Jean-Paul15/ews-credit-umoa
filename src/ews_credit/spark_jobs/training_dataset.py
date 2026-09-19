"""Assemble le dataset d'entrainement : jointure features Spark x labels.

Les labels (bascule_defaut_3m) sont calcules par generation/labels.py a
partir de la verite terrain (sans fuite d'information, cf. ce module) et
ingeres dans HDFS comme une source au meme titre que les evenements bruts.
"""

from pyspark.sql import DataFrame, functions as F

COLONNES_FEATURES_NUMERIQUES = [
    "retards_consecutifs",
    "solde_moyen_3m_fcfa",
    "solde_moyen_6m_fcfa",
    "solde_moyen_12m_fcfa",
    "ratio_utilisation_decouvert_3m",
    "frequence_incidents_6m",
]
COLONNE_LABEL = "bascule_defaut_3m"


def construire_dataset_entrainement(features: DataFrame, labels: DataFrame) -> DataFrame:
    labels_avec_mois = labels.withColumn("annee_mois", F.substring("date_releve", 1, 7))
    jointure = features.join(
        labels_avec_mois.select("credit_id", "annee_mois", COLONNE_LABEL),
        on=["credit_id", "annee_mois"],
        how="inner",
    )
    return jointure.select(*COLONNES_FEATURES_NUMERIQUES, COLONNE_LABEL, "credit_id", "annee_mois")


def ajouter_poids_de_classe(dataset: DataFrame) -> DataFrame:
    """Poids equilibre standard (comme sklearn class_weight='balanced') pour
    compenser le fort desequilibre (~1% de bascules vers le defaut)."""
    comptes = dict(dataset.groupBy(COLONNE_LABEL).count().collect())
    total = sum(comptes.values())
    poids_positif = total / (2 * comptes.get(1, 1))
    poids_negatif = total / (2 * comptes.get(0, 1))
    return dataset.withColumn(
        "poids", F.when(F.col(COLONNE_LABEL) == 1, poids_positif).otherwise(poids_negatif)
    )
