import pytest

from ews_credit.spark_jobs.evaluate_model import evaluer
from ews_credit.spark_jobs.sql_analysis import analyser_risque_par_pays_et_mois
from ews_credit.spark_jobs.train_model import entrainer_et_predire
from ews_credit.spark_jobs.training_dataset import (
    ajouter_poids_de_classe,
    construire_dataset_entrainement,
)

FEATURES = [
    ("C1", "2022-01", "paye_a_temps", 0, 1000.0, 1000.0, 1000.0, 1000.0, 0.0, 0.0),
    ("C2", "2022-01", "impaye", 3, 200.0, 400.0, 600.0, 800.0, 0.6, 0.8),
    ("C3", "2022-01", "impaye", 2, 300.0, 500.0, 700.0, 900.0, 0.4, 0.6),
] * 20  # repete pour avoir assez de lignes pour un split train/test non vide

LABELS = [("C1", "2022-01-05", 0), ("C2", "2022-01-05", 1), ("C3", "2022-01-05", 0)] * 20


@pytest.fixture
def dataset_pondere(spark):
    features = spark.createDataFrame(
        [(f"{c}_{i}", *reste) for i, (c, *reste) in enumerate(FEATURES)],
        schema=[
            "credit_id", "annee_mois", "statut_echeance", "retards_consecutifs",
            "solde_compte_fcfa", "solde_moyen_3m_fcfa", "solde_moyen_6m_fcfa", "solde_moyen_12m_fcfa",
            "ratio_utilisation_decouvert_3m", "frequence_incidents_6m",
        ],
    )
    labels = spark.createDataFrame(
        [(f"{c}_{i}", d, label) for i, (c, d, label) in enumerate(LABELS)],
        schema=["credit_id", "date_releve", "bascule_defaut_3m"],
    )
    dataset = construire_dataset_entrainement(features, labels)
    return ajouter_poids_de_classe(dataset)


def test_jointure_features_labels_conserve_toutes_les_lignes(dataset_pondere):
    assert dataset_pondere.count() == 60


def test_poids_de_classe_favorise_la_classe_minoritaire(dataset_pondere):
    poids = {row["bascule_defaut_3m"]: row["poids"] for row in dataset_pondere.select("bascule_defaut_3m", "poids").distinct().collect()}
    assert poids[1] > poids[0]  # la classe minoritaire (defaut) doit peser plus lourd


def test_pipeline_entrainement_produit_des_predictions_evaluables(dataset_pondere):
    _, predictions, test = entrainer_et_predire(dataset_pondere)
    assert test.count() > 0
    metriques = evaluer(predictions)
    assert 0.0 <= metriques.auc_roc <= 1.0
    assert 0.0 <= metriques.rappel_classe_positive <= 1.0


def test_analyse_sql_agrege_par_pays_et_mois(spark):
    features = spark.createDataFrame(
        [("C1", "2022-01", "paye_a_temps", 0, 100.0, 100.0, 100.0, 0.0, 0.0)],
        schema=[
            "credit_id", "annee_mois", "statut_echeance", "retards_consecutifs",
            "solde_compte_fcfa", "solde_moyen_3m_fcfa", "solde_moyen_12m_fcfa",
            "ratio_utilisation_decouvert_3m", "frequence_incidents_6m",
        ],
    )
    credits = spark.createDataFrame([("C1", "CLI1")], schema=["credit_id", "client_id"])
    clients = spark.createDataFrame([("CLI1", "Togo")], schema=["client_id", "pays"])

    resultat = analyser_risque_par_pays_et_mois(spark, features, credits, clients).collect()
    assert len(resultat) == 1
    assert resultat[0]["pays"] == "Togo"
