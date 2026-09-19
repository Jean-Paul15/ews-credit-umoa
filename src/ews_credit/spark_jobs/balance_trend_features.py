"""Tendance du solde de compte sur 3/6/12 mois glissants.

Le solde n'est pas un champ observe directement : il est reconstruit par
somme cumulative des mouvements de compte (depots/retraits), ordonnes
dans le temps — un cas d'usage typique de window function distribuee."""

from pyspark.sql import DataFrame, Window, functions as F

FENETRES_MOIS = {"3m": 3, "6m": 6, "12m": 12}


def ajouter_tendance_solde(mensuel: DataFrame) -> DataFrame:
    fenetre_credit = Window.partitionBy("credit_id").orderBy("annee_mois")

    mensuel = mensuel.withColumn(
        "solde_compte_fcfa",
        F.sum("solde_compte_variation_fcfa").over(
            fenetre_credit.rowsBetween(Window.unboundedPreceding, Window.currentRow)
        ),
    )

    for suffixe, n_mois in FENETRES_MOIS.items():
        fenetre_glissante = fenetre_credit.rowsBetween(-(n_mois - 1), Window.currentRow)
        mensuel = mensuel.withColumn(f"solde_moyen_{suffixe}_fcfa", F.avg("solde_compte_fcfa").over(fenetre_glissante))

    return mensuel
