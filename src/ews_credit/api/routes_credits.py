"""Endpoints credits : score individuel et liste des credits a surveiller."""

from fastapi import APIRouter, Depends, HTTPException

from ews_credit.api.dependencies import get_donnees
from ews_credit.api.repository import DonneesPortefeuille
from ews_credit.api.schemas import CreditARisque, ScoreCredit
from ews_credit.api.scoring_adapter import niveau_alerte_ligne, score_ligne
from ews_credit.domain.scoring import SEUIL_ALERTE_MOYEN

router = APIRouter(prefix="/credits", tags=["credits"])


@router.get("/{credit_id}/score", response_model=ScoreCredit)
def score_credit(credit_id: str, donnees: DonneesPortefeuille = Depends(get_donnees)) -> ScoreCredit:
    lignes = donnees.etat_credits.loc[donnees.etat_credits["credit_id"] == credit_id]
    if lignes.empty:
        raise HTTPException(status_code=404, detail=f"Credit {credit_id} introuvable.")

    ligne = lignes.iloc[0]
    return ScoreCredit(
        credit_id=credit_id,
        score_risque=score_ligne(ligne),
        niveau_alerte=niveau_alerte_ligne(ligne),
        retards_consecutifs=int(ligne["retards_consecutifs"]),
        stage_ifrs9=int(ligne["stage_ifrs9"]),
    )


@router.get("/a-risque", response_model=list[CreditARisque])
def credits_a_risque(limite: int = 100, donnees: DonneesPortefeuille = Depends(get_donnees)) -> list[CreditARisque]:
    """Les credits les plus a surveiller (score au-dessus du seuil d'alerte moyen), tries du plus risque au moins risque."""
    etat = donnees.etat_credits.copy()
    etat["score_risque"] = etat.apply(score_ligne, axis=1)
    etat["niveau_alerte"] = etat.apply(niveau_alerte_ligne, axis=1)

    a_surveiller = etat.loc[etat["score_risque"] >= SEUIL_ALERTE_MOYEN].sort_values("score_risque", ascending=False)
    return [
        CreditARisque(
            credit_id=ligne.credit_id,
            pays=ligne.pays,
            type_credit=ligne.type_credit,
            score_risque=ligne.score_risque,
            niveau_alerte=ligne.niveau_alerte,
            stage_ifrs9=int(ligne.stage_ifrs9),
            solde_restant_du_fcfa=float(ligne.solde_restant_du_fcfa),
            retards_consecutifs=int(ligne.retards_consecutifs),
        )
        for ligne in a_surveiller.head(limite).itertuples()
    ]
