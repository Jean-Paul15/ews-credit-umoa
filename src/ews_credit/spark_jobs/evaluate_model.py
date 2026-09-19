"""Evaluation du modele : AUC-ROC/PR + precision/rappel/F1 sur la classe
positive (la seule qui compte pour un EWS — predire correctement les 0
majoritaires n'a aucune valeur metier)."""

from dataclasses import asdict, dataclass

from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.sql import DataFrame

from ews_credit.spark_jobs.training_dataset import COLONNE_LABEL

LABEL_POSITIF = 1.0


@dataclass(frozen=True)
class MetriquesEvaluation:
    auc_roc: float
    auc_pr: float
    precision_classe_positive: float
    rappel_classe_positive: float
    f1_classe_positive: float

    def as_dict(self) -> dict:
        return asdict(self)


def evaluer(predictions: DataFrame) -> MetriquesEvaluation:
    binaire = BinaryClassificationEvaluator(labelCol=COLONNE_LABEL, rawPredictionCol="rawPrediction")
    auc_roc = binaire.evaluate(predictions, {binaire.metricName: "areaUnderROC"})
    auc_pr = binaire.evaluate(predictions, {binaire.metricName: "areaUnderPR"})

    multi = MulticlassClassificationEvaluator(labelCol=COLONNE_LABEL, predictionCol="prediction")
    precision = multi.evaluate(predictions, {multi.metricName: "precisionByLabel", multi.metricLabel: LABEL_POSITIF})
    rappel = multi.evaluate(predictions, {multi.metricName: "recallByLabel", multi.metricLabel: LABEL_POSITIF})
    f1 = multi.evaluate(predictions, {multi.metricName: "fMeasureByLabel", multi.metricLabel: LABEL_POSITIF})

    return MetriquesEvaluation(
        auc_roc=round(auc_roc, 4),
        auc_pr=round(auc_pr, 4),
        precision_classe_positive=round(precision, 4),
        rappel_classe_positive=round(rappel, 4),
        f1_classe_positive=round(f1, 4),
    )
