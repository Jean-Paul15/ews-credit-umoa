from ews_credit.domain.ifrs9 import (
    STAGE_DEFAUT,
    STAGE_DEGRADE,
    STAGE_SAIN,
    est_basculement_vers_defaut,
    stage_depuis_dpd,
)


def test_stage_sain_sous_le_seuil():
    assert stage_depuis_dpd(0) == STAGE_SAIN
    assert stage_depuis_dpd(29) == STAGE_SAIN


def test_stage_degrade_entre_les_deux_seuils():
    assert stage_depuis_dpd(30) == STAGE_DEGRADE
    assert stage_depuis_dpd(89) == STAGE_DEGRADE


def test_stage_defaut_au_dela_du_seuil():
    assert stage_depuis_dpd(90) == STAGE_DEFAUT
    assert stage_depuis_dpd(400) == STAGE_DEFAUT


def test_basculement_detecte_uniquement_l_entree_en_defaut():
    assert est_basculement_vers_defaut(STAGE_DEGRADE, STAGE_DEFAUT) is True
    assert est_basculement_vers_defaut(STAGE_SAIN, STAGE_DEGRADE) is False
    assert est_basculement_vers_defaut(STAGE_DEFAUT, STAGE_DEFAUT) is False
