"""Ratio d'utilisation des depassements de decouvert sur les 3 derniers mois."""

from pyspark.sql import DataFrame, Window, functions as F


def ajouter_ratio_utilisation_decouvert(mensuel: DataFrame) -> DataFrame:
    fenetre_glissante = Window.partitionBy("credit_id").orderBy("annee_mois").rowsBetween(-2, Window.currentRow)

    a_depasse_ce_mois = (F.col("montant_depassement_fcfa") > 0).cast("double")
    return mensuel.withColumn("ratio_utilisation_decouvert_3m", F.avg(a_depasse_ce_mois).over(fenetre_glissante))
