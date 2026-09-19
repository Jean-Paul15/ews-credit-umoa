"""Vue d'ensemble du portefeuille et simulation d'impact provisionnement IFRS9."""

from fastapi import APIRouter, Depends

from ews_credit.api.dependencies import get_donnees
from ews_credit.api.repository import DonneesPortefeuille
from ews_credit.api.schemas import (
    RepartitionParPays,
    SimulationProvisionnementReponse,
    SimulationProvisionnementRequete,
    VueEnsemblePortefeuille,
)
from ews_credit.api.scoring_adapter import niveau_alerte_ligne, score_ligne
from ews_credit.domain.provisionnement import calculer_ecl, stage_degrade_d_un_cran

router = APIRouter(prefix="/portefeuille", tags=["portefeuille"])


def _ecl_total(etat) -> float:
    return float(etat.apply(lambda l: calculer_ecl(l["solde_restant_du_fcfa"], l["stage_ifrs9"]), axis=1).sum())


def _repartition_par_pays(etat) -> list[RepartitionParPays]:
    etat = etat.copy()
    etat["ecl"] = etat.apply(lambda l: calculer_ecl(l["solde_restant_du_fcfa"], l["stage_ifrs9"]), axis=1)
    agrege = etat.groupby("pays").agg(nb_credits=("credit_id", "count"), ecl_fcfa=("ecl", "sum"))
    return [
        RepartitionParPays(pays=pays, nb_credits=int(ligne.nb_credits), ecl_fcfa=round(float(ligne.ecl_fcfa), 0))
        for pays, ligne in agrege.sort_values("ecl_fcfa", ascending=False).iterrows()
    ]


@router.get("/vue-ensemble", response_model=VueEnsemblePortefeuille)
def vue_ensemble(donnees: DonneesPortefeuille = Depends(get_donnees)) -> VueEnsemblePortefeuille:
    etat = donnees.etat_credits
    niveaux = etat.apply(niveau_alerte_ligne, axis=1)

    return VueEnsemblePortefeuille(
        nb_credits=len(etat),
        nb_alerte_faible=int((niveaux == "faible").sum()),
        nb_alerte_moyen=int((niveaux == "moyen").sum()),
        nb_alerte_eleve=int((niveaux == "eleve").sum()),
        ecl_total_fcfa=round(_ecl_total(etat), 0),
        repartition_par_pays=_repartition_par_pays(etat),
    )


@router.post("/simulation-provisionnement", response_model=SimulationProvisionnementReponse)
def simuler_provisionnement(
    requete: SimulationProvisionnementRequete, donnees: DonneesPortefeuille = Depends(get_donnees)
) -> SimulationProvisionnementReponse:
    etat = donnees.etat_credits.copy()
    ecl_avant = _ecl_total(etat)

    etat["score"] = etat.apply(score_ligne, axis=1)
    nb_a_degrader = int(len(etat) * requete.part_credits_degrades)
    credits_a_degrader = etat.sort_values("score", ascending=False).head(nb_a_degrader).index
    etat.loc[credits_a_degrader, "stage_ifrs9"] = etat.loc[credits_a_degrader, "stage_ifrs9"].apply(
        stage_degrade_d_un_cran
    )
    ecl_apres = _ecl_total(etat)

    variation_pct = ((ecl_apres - ecl_avant) / ecl_avant * 100) if ecl_avant else 0.0
    return SimulationProvisionnementReponse(
        ecl_avant_fcfa=round(ecl_avant, 0),
        ecl_apres_fcfa=round(ecl_apres, 0),
        variation_pct=round(variation_pct, 2),
    )
