"""Nombre de retards consecutifs : illustration canonique d'un calcul
"streak" en Spark via window functions (rupture de sequence -> groupe -> rang)."""

from pyspark.sql import DataFrame, Window, functions as F

STATUT_A_TEMPS = "paye_a_temps"


def ajouter_retards_consecutifs(mensuel: DataFrame) -> DataFrame:
    fenetre_credit = Window.partitionBy("credit_id").orderBy("annee_mois")

    est_en_retard = (F.col("statut_echeance") != STATUT_A_TEMPS).cast("int")
    changement_de_statut = F.coalesce(
        (est_en_retard != F.lag(est_en_retard).over(fenetre_credit)).cast("int"), F.lit(1)
    )
    id_groupe_retard = F.sum(changement_de_statut).over(
        fenetre_credit.rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )

    fenetre_groupe = Window.partitionBy("credit_id", id_groupe_retard).orderBy("annee_mois")
    rang_dans_le_groupe = F.row_number().over(fenetre_groupe)

    retards_consecutifs = F.when(est_en_retard == 1, rang_dans_le_groupe).otherwise(F.lit(0))
    return mensuel.withColumn("retards_consecutifs", retards_consecutifs)
