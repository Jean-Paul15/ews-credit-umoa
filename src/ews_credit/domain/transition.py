"""Chaine d'etats DPD (Sain / petit retard / Stage 2 / Stage 3).

Logique metier pure : aucune dependance pandas ni I/O. Les probabilites de
base sont calibrees sur les frequences reelles Home Credit Default Risk
(cf. config.py) ; cette chaine les traduit en trajectoire mensuelle par
credit, modulee par le risque latent du client et un eventuel choc macro.
"""

import numpy as np

from ews_credit import config
from ews_credit.config import SEUIL_DPD_STAGE_2, SEUIL_DPD_STAGE_3

# "Petit retard" reste en Stage 1 (< SEUIL_DPD_STAGE_2) : la tres grande majorite
# des retards observes chez Home Credit (8.4% des echeances) se resorbent avant
# de devenir un vrai Stage 2, cf. PROBA_GUERISON_PETIT_RETARD dans config.py.
DPD_PETIT_RETARD = 10
DPD_STAGE_2 = 45
DPD_STAGE_3 = 95

# Bornes volontairement resserrees : le multiplicateur agit successivement sur
# trois transitions (entree en retard, aggravation Stage 2, aggravation Stage 3) ;
# un facteur trop large composerait de facon irrealiste sur un client a risque.
MULTIPLICATEUR_RISQUE_BORNES = (0.3, 2.2)


def multiplicateur_risque(score_latent: float) -> float:
    lo, hi = MULTIPLICATEUR_RISQUE_BORNES
    return lo + (hi - lo) * score_latent


def multiplicateur_choc(mois_relatif: int) -> float:
    # Le facteur reel BCEAO (x7 sur le provisionnement agrege, cf. config) se
    # traduit ici par trois transitions successives (entree en retard,
    # aggravation Stage 2, aggravation Stage 3) : sa racine cubique est
    # appliquee a chaque etape pour retrouver un choc final du bon ordre de
    # grandeur sans le composer artificiellement trois fois.
    if mois_relatif in config.MOIS_CHOC_MACRO:
        return config.INTENSITE_CHOC_MACRO ** (1 / 3)
    return 1.0


def simuler_trajectoire_dpd(rng: np.random.Generator, score_latent: float, n_mois: int) -> np.ndarray:
    dpd = np.zeros(n_mois, dtype=int)
    dpd_courant = 0
    mult_risque = multiplicateur_risque(score_latent)

    for mois in range(n_mois):
        mult = mult_risque * multiplicateur_choc(mois)

        if dpd_courant >= SEUIL_DPD_STAGE_3:
            dpd[mois] = dpd_courant  # Stage 3 : etat absorbant sur l'horizon du panel
            continue

        if dpd_courant == 0:
            proba_entree_retard = min(config.PROBA_BASE_SAIN_VERS_PETIT_RETARD * mult, 0.6)
            if rng.random() < proba_entree_retard:
                dpd_courant = DPD_PETIT_RETARD
        elif dpd_courant < SEUIL_DPD_STAGE_2:
            proba_guerison = max(min(config.PROBA_GUERISON_PETIT_RETARD / mult, 1.0), 0.0)
            if rng.random() < proba_guerison:
                dpd_courant = 0
            else:
                proba_aggravation = min(config.PROBA_BASE_PETIT_RETARD_VERS_STAGE2 * mult, 0.5)
                dpd_courant = DPD_STAGE_2 if rng.random() < proba_aggravation else DPD_PETIT_RETARD
        else:  # Stage 2 confirme (30-89j)
            proba_guerison = max(min(config.PROBA_GUERISON_STAGE2 / mult, 1.0), 0.0)
            if rng.random() < proba_guerison:
                dpd_courant = DPD_PETIT_RETARD
            else:
                proba_aggravation = min(config.PROBA_BASE_STAGE2_VERS_STAGE3 * mult, 0.5)
                dpd_courant = SEUIL_DPD_STAGE_3 if rng.random() < proba_aggravation else DPD_STAGE_2

        dpd[mois] = dpd_courant

    return dpd
