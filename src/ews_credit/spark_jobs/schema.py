"""Schema explicite du flux d'evenements bruts — evite l'inference Spark
(couteuse sur un gros volume et fragile si un champ est absent d'un fichier)."""

from pyspark.sql.types import DoubleType, StringType, StructField, StructType

SCHEMA_EVENEMENTS = StructType(
    [
        StructField("event_id", StringType(), nullable=False),
        StructField("event_type", StringType(), nullable=False),
        StructField("credit_id", StringType(), nullable=False),
        StructField("client_id", StringType(), nullable=False),
        StructField("date_evenement", StringType(), nullable=False),
        StructField("montant_fcfa", DoubleType(), nullable=False),
        StructField("statut", StringType(), nullable=True),
    ]
)
