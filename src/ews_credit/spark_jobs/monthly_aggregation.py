"""Premiere passe distribuee : reduit le flux d'evenements bruts (1 ligne par
evenement) a une ligne par (credit_id, annee_mois) — la granularite sur
laquelle les features de tendance sont ensuite calculees."""

from pyspark.sql import DataFrame, functions as F

TYPE_ECHEANCE = "echeance_credit"
TYPE_MOUVEMENT = "mouvement_compte"
TYPE_DEPASSEMENT = "depassement_decouvert"
STATUT_IMPAYE = "impaye"


def agreger_par_credit_mois(events: DataFrame) -> DataFrame:
    events = events.withColumn("annee_mois", F.date_format("date_evenement", "yyyy-MM"))

    echeances = (
        events.filter(F.col("event_type") == TYPE_ECHEANCE)
        .groupBy("credit_id", "annee_mois")
        .agg(
            F.first("statut").alias("statut_echeance"),
            F.first("montant_fcfa").alias("montant_echeance_fcfa"),
        )
    )

    solde_compte = (
        events.filter(F.col("event_type") == TYPE_MOUVEMENT)
        .groupBy("credit_id", "annee_mois")
        .agg(F.sum("montant_fcfa").alias("solde_compte_variation_fcfa"))
    )

    depassements = (
        events.filter(F.col("event_type") == TYPE_DEPASSEMENT)
        .groupBy("credit_id", "annee_mois")
        .agg(F.sum("montant_fcfa").alias("montant_depassement_fcfa"))
    )

    return (
        echeances.join(solde_compte, on=["credit_id", "annee_mois"], how="left")
        .join(depassements, on=["credit_id", "annee_mois"], how="left")
        .fillna({"solde_compte_variation_fcfa": 0.0, "montant_depassement_fcfa": 0.0})
    )
