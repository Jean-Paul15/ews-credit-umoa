"""Score de risque EWS a partir des features comportementales.

Regle metier transparente (pas un modele entraine) : combinaison ponderee
et normalisee des 4 familles de features du pipeline Spark. Choix assume
pour un POC explicable dans le temps imparti — cf. docs/fiche_tp pour les
limites et la piste d'un modele supervise (EBM/XGBoost) sur ces memes
features.
"""

from dataclasses import dataclass

PONDERATION_RETARDS_CONSECUTIFS = 0.35
PONDERATION_TENDANCE_SOLDE = 0.25
PONDERATION_RATIO_DECOUVERT = 0.20
PONDERATION_FREQUENCE_INCIDENTS = 0.20

RETARDS_CONSECUTIFS_SATURATION = 6  # au-dela, le sous-score de retard est deja maximal
BAISSE_SOLDE_SATURATION_PCT = -0.5  # une chute de 50% du solde moyen sature le sous-score

SEUIL_ALERTE_MOYEN = 0.3
SEUIL_ALERTE_ELEVE = 0.6


@dataclass(frozen=True)
class FeaturesCredit:
    retards_consecutifs: int
    solde_moyen_3m_fcfa: float
    solde_moyen_12m_fcfa: float
    ratio_utilisation_decouvert_3m: float
    frequence_incidents_6m: float


def _sous_score_retards(retards_consecutifs: int) -> float:
    return min(retards_consecutifs / RETARDS_CONSECUTIFS_SATURATION, 1.0)


def _sous_score_tendance_solde(solde_3m: float, solde_12m: float) -> float:
    if solde_12m <= 0:
        return 0.0
    variation_pct = (solde_3m - solde_12m) / abs(solde_12m)
    if variation_pct >= 0:
        return 0.0
    return min(variation_pct / BAISSE_SOLDE_SATURATION_PCT, 1.0)


def calculer_score_risque(features: FeaturesCredit) -> float:
    score = (
        PONDERATION_RETARDS_CONSECUTIFS * _sous_score_retards(features.retards_consecutifs)
        + PONDERATION_TENDANCE_SOLDE * _sous_score_tendance_solde(features.solde_moyen_3m_fcfa, features.solde_moyen_12m_fcfa)
        + PONDERATION_RATIO_DECOUVERT * min(features.ratio_utilisation_decouvert_3m, 1.0)
        + PONDERATION_FREQUENCE_INCIDENTS * min(features.frequence_incidents_6m, 1.0)
    )
    return round(min(max(score, 0.0), 1.0), 4)


def niveau_alerte(score_risque: float) -> str:
    if score_risque >= SEUIL_ALERTE_ELEVE:
        return "eleve"
    if score_risque >= SEUIL_ALERTE_MOYEN:
        return "moyen"
    return "faible"
