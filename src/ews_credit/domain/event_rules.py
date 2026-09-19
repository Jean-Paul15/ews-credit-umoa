"""Regles pures determinant quels evenements transactionnels emettre.

A partir d'un etat mensuel connu (dpd, solde, type de client), decide du
statut d'une echeance et du volume de mouvements de compte a generer. Ce
sont ces evenements, une fois ecrits en flux brut, que le job Spark devra
ensuite ré-agreger pour retrouver les features comportementales — la
logique ici doit donc rester deterministe (a rng donne) et independante
de tout format de sortie.
"""

import numpy as np

from ews_credit.config import SEUIL_DPD_STAGE_2

STATUT_A_TEMPS = "paye_a_temps"
STATUT_RETARD = "paye_en_retard"
STATUT_IMPAYE = "impaye"

NB_MOUVEMENTS_BORNES = {
    "Particulier": (3, 9),
    "PME": (6, 15),
}
PROBA_CONSULTATION_AGENCE = 0.02


def statut_echeance(dpd_jours: int) -> str:
    if dpd_jours >= SEUIL_DPD_STAGE_2:
        return STATUT_IMPAYE
    if dpd_jours > 0:
        return STATUT_RETARD
    return STATUT_A_TEMPS


def montant_echeance(montant_initial_fcfa: float, duree_mois: int) -> float:
    return round(montant_initial_fcfa / duree_mois, 0)


def nb_mouvements_compte(rng: np.random.Generator, type_client: str) -> int:
    lo, hi = NB_MOUVEMENTS_BORNES[type_client]
    return int(rng.integers(lo, hi + 1))


def montant_mouvement_compte(rng: np.random.Generator, revenu_mensuel_fcfa: float, est_depot: bool) -> float:
    if est_depot:
        return round(revenu_mensuel_fcfa * rng.uniform(0.2, 1.1), 0)
    return -round(revenu_mensuel_fcfa * rng.uniform(0.02, 0.35), 0)


def survient_consultation_agence(rng: np.random.Generator) -> bool:
    return rng.random() < PROBA_CONSULTATION_AGENCE
