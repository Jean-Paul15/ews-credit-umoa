"""Assemblage du panel comportemental mensuel — coeur du dataset EWS.

Orchestration seule : la chaine d'etats DPD vit dans domain/transition.py,
le calcul du solde dans domain/amortissement.py.
"""

import numpy as np
import pandas as pd

from ews_credit import config
from ews_credit.domain.amortissement import solde_restant_du
from ews_credit.domain.ifrs9 import stage_depuis_dpd
from ews_credit.domain.transition import multiplicateur_risque, simuler_trajectoire_dpd

PROBA_DEPASSEMENT_DECOUVERT_BASE = 0.10 / 6  # rapportee au multiplicateur de risque max


def _tirer_depassement_decouvert(rng: np.random.Generator, solde: float, score_latent: float) -> float:
    proba = PROBA_DEPASSEMENT_DECOUVERT_BASE * multiplicateur_risque(score_latent)
    if rng.random() >= proba:
        return 0.0
    return round(solde * rng.uniform(0.05, 0.4), 0)


def _generer_lignes_credit(
    rng: np.random.Generator, credit: pd.Series, score_latent: float, mois_debut: int, mois_fin: int
) -> list[dict]:
    n_mois = mois_fin - mois_debut
    dpd_trajectoire = simuler_trajectoire_dpd(rng, score_latent, n_mois)
    est_decouvert = credit["type_credit"] == "Decouvert"

    lignes = []
    for i, mois_relatif in enumerate(range(mois_debut, mois_fin)):
        dpd = int(dpd_trajectoire[i])
        solde = solde_restant_du(credit["montant_initial_fcfa"], credit["duree_mois"], i, dpd)
        depassement = _tirer_depassement_decouvert(rng, solde, score_latent) if est_decouvert else 0.0

        lignes.append(
            {
                "credit_id": credit["credit_id"],
                "client_id": credit["client_id"],
                "mois_relatif": mois_relatif,
                "dpd_jours": dpd,
                "stage_ifrs9": stage_depuis_dpd(dpd),
                "solde_restant_du_fcfa": solde,
                "depassement_decouvert_fcfa": depassement,
            }
        )
    return lignes


def generer_panel_mensuel(
    clients: pd.DataFrame, credits: pd.DataFrame, seed: int = config.SEED
) -> pd.DataFrame:
    """Genere le panel mensuel (une ligne par credit actif et par mois)."""
    rng = np.random.default_rng(seed + 2)
    score_par_client = clients.set_index("client_id")["_score_risque_latent"]

    lignes = []
    for _, credit in credits.iterrows():
        mois_debut = int(credit["mois_octroi_relatif"])
        mois_fin = min(mois_debut + int(credit["duree_mois"]), config.HORIZON_PANEL_MOIS)
        if mois_fin <= mois_debut:
            continue
        score_latent = score_par_client.loc[credit["client_id"]]
        lignes.extend(_generer_lignes_credit(rng, credit, score_latent, mois_debut, mois_fin))

    panel = pd.DataFrame(lignes)
    panel["date_releve"] = pd.to_datetime(config.DATE_DEBUT_PANEL) + pd.to_timedelta(
        panel["mois_relatif"] * 30, unit="D"
    )
    return panel
