"""Calcul de la cible du modele EWS a partir du panel mensuel genere."""

import numpy as np
import pandas as pd

from ews_credit.domain.ifrs9 import STAGE_DEFAUT


def _bascule_a_venir_par_credit(stage_ifrs9: np.ndarray, horizon_mois: int) -> np.ndarray:
    est_defaut = stage_ifrs9 == STAGE_DEFAUT
    n = len(est_defaut)
    label = np.zeros(n, dtype=int)
    for i in range(n):
        fenetre = est_defaut[i + 1 : i + 1 + horizon_mois]
        label[i] = int(fenetre.any())
    return label


def calculer_labels_bascule_defaut(panel: pd.DataFrame, horizon_mois: int = 3) -> pd.DataFrame:
    """Pour chaque (credit, mois) hors defaut, indique si le credit bascule en Stage 3
    dans les `horizon_mois` mois suivants — c'est la cible que le modele EWS doit predire.
    Calcule strictement a partir du futur du panel : aucune fuite d'information vers les
    variables explicatives disponibles a la date du releve.
    """
    panel_triee = panel.sort_values(["credit_id", "mois_relatif"]).reset_index(drop=True)
    nom_colonne = f"bascule_defaut_{horizon_mois}m"

    panel_triee[nom_colonne] = 0
    for _, indices in panel_triee.groupby("credit_id").groups.items():
        sous_serie = panel_triee.loc[indices, "stage_ifrs9"].to_numpy()
        panel_triee.loc[indices, nom_colonne] = _bascule_a_venir_par_credit(sous_serie, horizon_mois)

    colonnes = ["credit_id", "client_id", "mois_relatif", "date_releve", "stage_ifrs9", nom_colonne]
    labels = panel_triee.loc[panel_triee["stage_ifrs9"] != STAGE_DEFAUT, colonnes]
    return labels.reset_index(drop=True)
