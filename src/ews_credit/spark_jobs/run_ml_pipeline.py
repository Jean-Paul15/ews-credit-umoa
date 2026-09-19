"""Point d'entree spark-submit : chaine complete HDFS -> Spark SQL -> ML -> evaluation.

Exemple (depuis le conteneur spark-master) :

    spark-submit --master spark://spark-master:7077 \
        run_ml_pipeline.py --racine-hdfs hdfs://namenode:9000
"""

import argparse
import json

from pyspark.sql import SparkSession

from ews_credit.spark_jobs.evaluate_model import evaluer
from ews_credit.spark_jobs.sql_analysis import analyser_risque_par_pays_et_mois
from ews_credit.spark_jobs.train_model import entrainer_et_predire
from ews_credit.spark_jobs.training_dataset import ajouter_poids_de_classe, construire_dataset_entrainement


def executer(racine_hdfs: str) -> None:
    spark = SparkSession.builder.appName("ews-credit-ml-pipeline").getOrCreate()
    try:
        features = spark.read.parquet(f"{racine_hdfs}/features")
        labels = spark.read.option("header", True).csv(f"{racine_hdfs}/synthetic/labels.csv", inferSchema=True)
        credits = spark.read.option("header", True).csv(f"{racine_hdfs}/synthetic/credits.csv", inferSchema=True)
        clients = spark.read.option("header", True).csv(f"{racine_hdfs}/synthetic/clients.csv", inferSchema=True)

        analyse = analyser_risque_par_pays_et_mois(spark, features, credits, clients)
        analyse.write.mode("overwrite").parquet(f"{racine_hdfs}/analyse_risque_pays")
        print(f"Analyse Spark SQL ecrite : {analyse.count():,} lignes (pays x mois)")

        dataset = ajouter_poids_de_classe(construire_dataset_entrainement(features, labels))
        modele, predictions, test = entrainer_et_predire(dataset)
        metriques = evaluer(predictions)

        print(f"Dataset d'entrainement : {dataset.count():,} lignes, test : {test.count():,} lignes")
        print("Metriques :", json.dumps(metriques.as_dict(), indent=2))

        modele.write().overwrite().save(f"{racine_hdfs}/modele_ews")
        spark.createDataFrame([metriques.as_dict()]).write.mode("overwrite").json(f"{racine_hdfs}/metriques_modele")
    finally:
        spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline ML distribue EWS-Credit.")
    parser.add_argument("--racine-hdfs", default="hdfs://namenode:9000")
    args = parser.parse_args()
    executer(args.racine_hdfs)
