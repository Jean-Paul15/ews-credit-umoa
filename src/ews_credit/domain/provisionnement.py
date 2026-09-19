"""Provisionnement IFRS 9 (Expected Credit Loss) simplifie.

Taux indicatifs usuels de la litterature IFRS 9 par stage (pas une
calibration BCEAO specifique — a la difference des constantes de
config/risque.py, aucune donnee reelle UMOA ne publie ce taux par stage
au niveau credit). Sert a simuler l'ORDRE DE GRANDEUR de l'impact d'une
degradation de portefeuille, pas a produire un chiffre comptable exact.
"""

from ews_credit.domain.ifrs9 import STAGE_DEFAUT, STAGE_DEGRADE, STAGE_SAIN

TAUX_PROVISION_PAR_STAGE = {
    STAGE_SAIN: 0.01,
    STAGE_DEGRADE: 0.10,
    STAGE_DEFAUT: 0.60,
}


def calculer_ecl(solde_restant_du_fcfa: float, stage_ifrs9: int) -> float:
    """Expected Credit Loss simplifie pour un credit : solde * taux du stage."""
    return round(solde_restant_du_fcfa * TAUX_PROVISION_PAR_STAGE[stage_ifrs9], 0)


def stage_degrade_d_un_cran(stage_ifrs9: int) -> int:
    if stage_ifrs9 == STAGE_SAIN:
        return STAGE_DEGRADE
    return STAGE_DEFAUT
