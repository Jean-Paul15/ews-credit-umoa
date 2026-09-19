from ews_credit.domain.ifrs9 import STAGE_DEFAUT, STAGE_DEGRADE, STAGE_SAIN
from ews_credit.domain.provisionnement import calculer_ecl, stage_degrade_d_un_cran


def test_ecl_croit_avec_la_severite_du_stage():
    ecl_sain = calculer_ecl(1_000_000, STAGE_SAIN)
    ecl_degrade = calculer_ecl(1_000_000, STAGE_DEGRADE)
    ecl_defaut = calculer_ecl(1_000_000, STAGE_DEFAUT)
    assert ecl_sain < ecl_degrade < ecl_defaut


def test_ecl_proportionnel_au_solde():
    assert calculer_ecl(2_000_000, STAGE_SAIN) == 2 * calculer_ecl(1_000_000, STAGE_SAIN)


def test_degradation_d_un_cran_suit_l_ordre_ifrs9():
    assert stage_degrade_d_un_cran(STAGE_SAIN) == STAGE_DEGRADE
    assert stage_degrade_d_un_cran(STAGE_DEGRADE) == STAGE_DEFAUT
    assert stage_degrade_d_un_cran(STAGE_DEFAUT) == STAGE_DEFAUT
