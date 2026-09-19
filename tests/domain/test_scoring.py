from ews_credit.domain.scoring import FeaturesCredit, calculer_score_risque, niveau_alerte


def _features(**overrides) -> FeaturesCredit:
    base = dict(
        retards_consecutifs=0,
        solde_moyen_3m_fcfa=1000.0,
        solde_moyen_12m_fcfa=1000.0,
        ratio_utilisation_decouvert_3m=0.0,
        frequence_incidents_6m=0.0,
    )
    base.update(overrides)
    return FeaturesCredit(**base)


def test_credit_parfaitement_sain_a_un_score_nul():
    assert calculer_score_risque(_features()) == 0.0


def test_score_croit_avec_les_retards_consecutifs():
    score_sans_retard = calculer_score_risque(_features(retards_consecutifs=0))
    score_avec_retards = calculer_score_risque(_features(retards_consecutifs=3))
    assert score_avec_retards > score_sans_retard


def test_chute_du_solde_augmente_le_score():
    score_stable = calculer_score_risque(_features(solde_moyen_3m_fcfa=1000, solde_moyen_12m_fcfa=1000))
    score_en_chute = calculer_score_risque(_features(solde_moyen_3m_fcfa=400, solde_moyen_12m_fcfa=1000))
    assert score_en_chute > score_stable


def test_score_toujours_borne_entre_0_et_1():
    score_pire_cas = calculer_score_risque(
        _features(retards_consecutifs=50, solde_moyen_3m_fcfa=-500, solde_moyen_12m_fcfa=1000,
                  ratio_utilisation_decouvert_3m=5.0, frequence_incidents_6m=5.0)
    )
    assert 0.0 <= score_pire_cas <= 1.0


def test_niveaux_d_alerte_respectent_les_seuils():
    assert niveau_alerte(0.1) == "faible"
    assert niveau_alerte(0.4) == "moyen"
    assert niveau_alerte(0.8) == "eleve"
