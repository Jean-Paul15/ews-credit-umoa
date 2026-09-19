"""Entrainement distribue (Spark MLlib) du modele de bascule vers le defaut.

Regression logistique poids-equilibree : plus simple qu'un GBT mais
directement interpretable (coefficients par feature), coherent avec
l'exigence d'explicabilite deja posee par domain/scoring.py — ce modele
entraine vient la COMPLETER avec un signal statistique, pas la remplacer.
"""

from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import StandardScaler, VectorAssembler
from pyspark.sql import DataFrame

from ews_credit.spark_jobs.training_dataset import COLONNE_LABEL, COLONNES_FEATURES_NUMERIQUES


def construire_pipeline() -> Pipeline:
    assembleur = VectorAssembler(inputCols=COLONNES_FEATURES_NUMERIQUES, outputCol="features_brutes")
    normaliseur = StandardScaler(inputCol="features_brutes", outputCol="features")
    regression = LogisticRegression(featuresCol="features", labelCol=COLONNE_LABEL, weightCol="poids")
    return Pipeline(stages=[assembleur, normaliseur, regression])


def entrainer_et_predire(dataset: DataFrame, seed: int = 42) -> tuple[PipelineModel, DataFrame, DataFrame]:
    train, test = dataset.randomSplit([0.75, 0.25], seed=seed)
    modele = construire_pipeline().fit(train)
    predictions = modele.transform(test)
    return modele, predictions, test
