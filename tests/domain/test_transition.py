import numpy as np

from ews_credit.config import MOIS_CHOC_MACRO, SEUIL_DPD_STAGE_3
from ews_credit.domain.transition import (
    multiplicateur_choc,
    multiplicateur_risque,
    simuler_trajectoire_dpd,
)


def test_multiplicateur_risque_croissant_avec_le_score():
    assert multiplicateur_risque(0.0) < multiplicateur_risque(0.5) < multiplicateur_risque(1.0)


def test_multiplicateur_choc_neutre_hors_periode_de_choc():
    mois_hors_choc = max(MOIS_CHOC_MACRO) + 1
    assert multiplicateur_choc(mois_hors_choc) == 1.0


def test_multiplicateur_choc_amplifie_pendant_la_periode_de_choc():
    assert multiplicateur_choc(MOIS_CHOC_MACRO[0]) > 1.0


def test_stage_3_est_un_etat_absorbant():
    rng = np.random.default_rng(0)
    trajectoire = simuler_trajectoire_dpd(rng, score_latent=1.0, n_mois=60)
    premier_defaut = np.argmax(trajectoire >= SEUIL_DPD_STAGE_3)
    if trajectoire[premier_defaut] >= SEUIL_DPD_STAGE_3:
        assert (trajectoire[premier_defaut:] >= SEUIL_DPD_STAGE_3).all()


def test_client_a_faible_risque_degrade_moins_souvent_qu_un_client_a_risque_eleve():
    rng = np.random.default_rng(1)
    n_simulations = 300

    taux_defaut_faible_risque = np.mean(
        [simuler_trajectoire_dpd(rng, 0.05, 36)[-1] >= SEUIL_DPD_STAGE_3 for _ in range(n_simulations)]
    )
    taux_defaut_risque_eleve = np.mean(
        [simuler_trajectoire_dpd(rng, 0.95, 36)[-1] >= SEUIL_DPD_STAGE_3 for _ in range(n_simulations)]
    )

    assert taux_defaut_faible_risque < taux_defaut_risque_eleve
