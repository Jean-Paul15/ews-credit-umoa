"""Calcul du solde restant du d'un credit, regle metier pure."""

from ews_credit.config import SEUIL_DPD_STAGE_2


def solde_restant_du(montant_initial: float, duree_mois: int, mois_ecoules: int, dpd_jours: int) -> float:
    amortissement = max(0.0, 1 - mois_ecoules / duree_mois)
    if dpd_jours >= SEUIL_DPD_STAGE_2:
        # capital + interets de retard qui continuent de courir : le solde ne baisse plus
        amortissement = max(0.0, 1 - (mois_ecoules - dpd_jours / 30) / duree_mois)
    return round(montant_initial * amortissement, 0)
