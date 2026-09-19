"""Generation du flux d'evenements transactionnels bruts (verite terrain -> events).

Ce module ne fait QUE deriver des evenements coherents avec le panel mensuel
deja simule (source de verite pour le DPD/solde/stage) : il ne redecide pas
si un credit degrade, il raconte, a la journee pres, les mouvements qui
justifient l'etat mensuel deja connu. C'est ce flux, volumineux et non
pre-agrege, que le job Spark (spark_jobs/) devra retraiter pour retrouver
les features comportementales.
"""

import numpy as np
import pandas as pd

from ews_credit import config
from ews_credit.domain.event_rules import (
    montant_echeance,
    montant_mouvement_compte,
    nb_mouvements_compte,
    statut_echeance,
    survient_consultation_agence,
)

TYPE_ECHEANCE = "echeance_credit"
TYPE_MOUVEMENT = "mouvement_compte"
TYPE_DEPASSEMENT = "depassement_decouvert"
TYPE_CONSULTATION = "consultation_agence"


def _date_aleatoire_dans_le_mois(rng: np.random.Generator, date_releve: pd.Timestamp) -> pd.Timestamp:
    jour = int(rng.integers(1, 29))
    return date_releve.replace(day=jour)


def _evenement(rng: np.random.Generator, ligne: pd.Series, event_type: str, montant: float, statut: str = None) -> dict:
    return {
        "event_type": event_type,
        "credit_id": ligne["credit_id"],
        "client_id": ligne["client_id"],
        "pays": ligne["pays"],
        "date_evenement": _date_aleatoire_dans_le_mois(rng, ligne["date_releve"]),
        "montant_fcfa": montant,
        "statut": statut,
    }


def _evenements_d_une_ligne(rng: np.random.Generator, ligne: pd.Series) -> list[dict]:
    montant_du = montant_echeance(ligne["montant_initial_fcfa"], ligne["duree_mois"])
    evenements = [_evenement(rng, ligne, TYPE_ECHEANCE, montant_du, statut_echeance(ligne["dpd_jours"]))]

    for i in range(nb_mouvements_compte(rng, ligne["type_client"])):
        montant = montant_mouvement_compte(rng, ligne["revenu_mensuel_fcfa"], est_depot=(i == 0))
        evenements.append(_evenement(rng, ligne, TYPE_MOUVEMENT, montant))

    if ligne["depassement_decouvert_fcfa"] > 0:
        evenements.append(_evenement(rng, ligne, TYPE_DEPASSEMENT, ligne["depassement_decouvert_fcfa"]))

    if survient_consultation_agence(rng):
        evenements.append(_evenement(rng, ligne, TYPE_CONSULTATION, 0.0))

    return evenements


def generer_evenements(
    clients: pd.DataFrame, credits: pd.DataFrame, panel_mensuel: pd.DataFrame, seed: int = config.SEED
) -> pd.DataFrame:
    """Deroule, a la journee pres, les evenements coherents avec le panel mensuel."""
    rng = np.random.default_rng(seed + 3)

    panel_enrichi = panel_mensuel.merge(
        credits[["credit_id", "montant_initial_fcfa", "duree_mois"]], on="credit_id"
    ).merge(clients[["client_id", "pays", "type_client", "revenu_mensuel_fcfa"]], on="client_id")

    evenements = []
    for _, ligne in panel_enrichi.iterrows():
        evenements.extend(_evenements_d_une_ligne(rng, ligne))

    events_df = pd.DataFrame(evenements)
    events_df["event_id"] = [f"EVT{i:09d}" for i in range(len(events_df))]
    events_df["annee"] = events_df["date_evenement"].dt.year
    events_df["mois"] = events_df["date_evenement"].dt.month

    code_iso_par_pays = {p.nom: p.code_iso for p in config.PAYS_UMOA}
    events_df["pays_code"] = events_df["pays"].map(code_iso_par_pays)
    return events_df
