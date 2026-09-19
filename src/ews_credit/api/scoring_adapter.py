"""Convertit une ligne de `etat_credits` (pandas) vers le domaine de scoring —
evite de dupliquer cette construction dans chaque route."""

import pandas as pd

from ews_credit.domain.scoring import FeaturesCredit, calculer_score_risque, niveau_alerte


def features_depuis_ligne(ligne: pd.Series) -> FeaturesCredit:
    return FeaturesCredit(
        retards_consecutifs=int(ligne["retards_consecutifs"]),
        solde_moyen_3m_fcfa=float(ligne["solde_moyen_3m_fcfa"]),
        solde_moyen_12m_fcfa=float(ligne["solde_moyen_12m_fcfa"]),
        ratio_utilisation_decouvert_3m=float(ligne["ratio_utilisation_decouvert_3m"]),
        frequence_incidents_6m=float(ligne["frequence_incidents_6m"]),
    )


def score_ligne(ligne: pd.Series) -> float:
    return calculer_score_risque(features_depuis_ligne(ligne))


def niveau_alerte_ligne(ligne: pd.Series) -> str:
    return niveau_alerte(score_ligne(ligne))
