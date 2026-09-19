"""Point d'entree spark-submit.

Exemple (depuis le conteneur spark-master, une fois les events ingeres dans
HDFS via docker/ingest_to_hdfs.sh) :

    spark-submit --master spark://spark-master:7077 \
        run_feature_pipeline.py --entree hdfs://namenode:9000/events \
        --sortie hdfs://namenode:9000/features
"""

import argparse

from pyspark.sql import SparkSession

from ews_credit.spark_jobs.features_pipeline import construire_features_comportementales
from ews_credit.spark_jobs.schema import SCHEMA_EVENEMENTS


def executer(entree: str, sortie: str) -> None:
    spark = SparkSession.builder.appName("ews-credit-feature-engineering").getOrCreate()
    try:
        events = spark.read.schema(SCHEMA_EVENEMENTS).option("basePath", entree).json(f"{entree}/*/*/*/*.jsonl")
        features = construire_features_comportementales(events)
        features.write.mode("overwrite").partitionBy("annee_mois").parquet(sortie)
        print(f"Lignes de features ecrites : {features.count():,}")
    finally:
        spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature engineering distribue EWS-Credit.")
    parser.add_argument("--entree", required=True, help="Chemin (HDFS ou local) des evenements bruts partitionnes.")
    parser.add_argument("--sortie", required=True, help="Chemin (HDFS ou local) de sortie des features Parquet.")
    args = parser.parse_args()
    executer(args.entree, args.sortie)
