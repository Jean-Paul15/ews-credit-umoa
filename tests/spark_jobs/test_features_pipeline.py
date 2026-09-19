import pytest

from ews_credit.spark_jobs.features_pipeline import construire_features_comportementales
from ews_credit.spark_jobs.schema import SCHEMA_EVENEMENTS

# Scenario construit a la main sur un seul credit, 5 mois, pour pouvoir
# verifier chaque feature par un calcul independant (cf. commentaires).
EVENEMENTS_SCENARIO = [
    ("E1", "echeance_credit", "C1", "CLI1", "2022-01-05", 1000.0, "paye_a_temps"),
    ("E2", "mouvement_compte", "C1", "CLI1", "2022-01-10", 500.0, None),
    ("E3", "mouvement_compte", "C1", "CLI1", "2022-01-20", -100.0, None),
    ("E4", "echeance_credit", "C1", "CLI1", "2022-02-05", 1000.0, "paye_en_retard"),
    ("E5", "mouvement_compte", "C1", "CLI1", "2022-02-10", 500.0, None),
    ("E6", "mouvement_compte", "C1", "CLI1", "2022-02-20", -600.0, None),
    ("E7", "echeance_credit", "C1", "CLI1", "2022-03-05", 1000.0, "impaye"),
    ("E8", "depassement_decouvert", "C1", "CLI1", "2022-03-15", 200.0, None),
    ("E9", "mouvement_compte", "C1", "CLI1", "2022-03-20", 200.0, None),
    ("E10", "echeance_credit", "C1", "CLI1", "2022-04-05", 1000.0, "impaye"),
    ("E11", "mouvement_compte", "C1", "CLI1", "2022-04-20", 300.0, None),
    ("E12", "echeance_credit", "C1", "CLI1", "2022-05-05", 1000.0, "paye_a_temps"),
    ("E13", "mouvement_compte", "C1", "CLI1", "2022-05-20", 100.0, None),
]


@pytest.fixture
def features_par_mois(spark):
    events = spark.createDataFrame(EVENEMENTS_SCENARIO, schema=SCHEMA_EVENEMENTS)
    resultat = construire_features_comportementales(events).orderBy("annee_mois")
    return {ligne["annee_mois"]: ligne.asDict() for ligne in resultat.collect()}


def test_retards_consecutifs_reflete_la_sequence_de_statuts(features_par_mois):
    # statuts : a_temps, retard, impaye, impaye, a_temps -> streak 0,1,2,3,0
    assert features_par_mois["2022-01"]["retards_consecutifs"] == 0
    assert features_par_mois["2022-02"]["retards_consecutifs"] == 1
    assert features_par_mois["2022-03"]["retards_consecutifs"] == 2
    assert features_par_mois["2022-04"]["retards_consecutifs"] == 3
    assert features_par_mois["2022-05"]["retards_consecutifs"] == 0


def test_solde_cumule_et_moyenne_glissante_3_mois(features_par_mois):
    # variations mensuelles : +400, -100, +200, +300, +100 -> cumul 400,300,500,800,900
    assert features_par_mois["2022-01"]["solde_compte_fcfa"] == 400
    assert features_par_mois["2022-05"]["solde_compte_fcfa"] == 900
    assert features_par_mois["2022-03"]["solde_moyen_3m_fcfa"] == pytest.approx((400 + 300 + 500) / 3)


def test_ratio_utilisation_decouvert_sur_3_mois_glissants(features_par_mois):
    # un seul depassement, en mars -> pese pour 1/3 sur mars/avril/mai
    assert features_par_mois["2022-02"]["ratio_utilisation_decouvert_3m"] == 0
    assert features_par_mois["2022-03"]["ratio_utilisation_decouvert_3m"] == pytest.approx(1 / 3)
    assert features_par_mois["2022-05"]["ratio_utilisation_decouvert_3m"] == pytest.approx(1 / 3)


def test_frequence_incidents_sur_6_mois_glissants(features_par_mois):
    # impayes en mars et avril seulement, fenetre cumulative (moins de 6 mois disponibles)
    assert features_par_mois["2022-02"]["frequence_incidents_6m"] == 0
    assert features_par_mois["2022-04"]["frequence_incidents_6m"] == pytest.approx(2 / 4)
    assert features_par_mois["2022-05"]["frequence_incidents_6m"] == pytest.approx(2 / 5)
