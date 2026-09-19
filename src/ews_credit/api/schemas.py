"""Contrats de reponse HTTP (Pydantic) — l'API n'expose que ces formes,
jamais les DataFrames internes directement."""

from pydantic import BaseModel


class ScoreCredit(BaseModel):
    credit_id: str
    score_risque: float
    niveau_alerte: str
    retards_consecutifs: int
    stage_ifrs9: int


class RepartitionParPays(BaseModel):
    pays: str
    nb_credits: int
    ecl_fcfa: float


class VueEnsemblePortefeuille(BaseModel):
    nb_credits: int
    nb_alerte_faible: int
    nb_alerte_moyen: int
    nb_alerte_eleve: int
    ecl_total_fcfa: float
    repartition_par_pays: list[RepartitionParPays]


class CreditARisque(BaseModel):
    credit_id: str
    pays: str
    type_credit: str
    score_risque: float
    niveau_alerte: str
    stage_ifrs9: int
    solde_restant_du_fcfa: float
    retards_consecutifs: int


class SimulationProvisionnementRequete(BaseModel):
    part_credits_degrades: float  # entre 0 et 1


class SimulationProvisionnementReponse(BaseModel):
    ecl_avant_fcfa: float
    ecl_apres_fcfa: float
    variation_pct: float
