"""Analyse declarative Spark SQL du risque par pays et par mois.

Pendant analogique, sur notre domaine, du TP « Data Warehouse distribue »
du cours (chiffre d'affaires par ville -> ici, frequence d'incidents par
pays) : vues temporaires + requete SQL textuelle plutot que l'API DataFrame.
"""

from pyspark.sql import DataFrame, SparkSession

REQUETE_RISQUE_PAR_PAYS_ET_MOIS = """
    SELECT
        cp.pays,
        f.annee_mois,
        COUNT(*) AS nb_credits,
        ROUND(AVG(f.frequence_incidents_6m), 4) AS taux_incidents_moyen,
        ROUND(AVG(f.retards_consecutifs), 2) AS retards_consecutifs_moyen,
        ROUND(AVG(f.ratio_utilisation_decouvert_3m), 4) AS ratio_decouvert_moyen
    FROM features f
    JOIN credit_pays cp ON f.credit_id = cp.credit_id
    GROUP BY cp.pays, f.annee_mois
    ORDER BY cp.pays, f.annee_mois
"""


def analyser_risque_par_pays_et_mois(
    spark: SparkSession, features: DataFrame, credits: DataFrame, clients: DataFrame
) -> DataFrame:
    credit_pays = credits.join(clients.select("client_id", "pays"), on="client_id").select("credit_id", "pays")

    features.createOrReplaceTempView("features")
    credit_pays.createOrReplaceTempView("credit_pays")

    return spark.sql(REQUETE_RISQUE_PAR_PAYS_ET_MOIS)
