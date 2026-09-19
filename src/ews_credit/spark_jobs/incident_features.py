"""Frequence d'incidents de paiement (echeances impayees) sur 6 mois glissants."""

from pyspark.sql import DataFrame, Window, functions as F

STATUT_IMPAYE = "impaye"


def ajouter_frequence_incidents(mensuel: DataFrame) -> DataFrame:
    fenetre_glissante = Window.partitionBy("credit_id").orderBy("annee_mois").rowsBetween(-5, Window.currentRow)

    est_impaye = (F.col("statut_echeance") == STATUT_IMPAYE).cast("double")
    return mensuel.withColumn("frequence_incidents_6m", F.avg(est_impaye).over(fenetre_glissante))
