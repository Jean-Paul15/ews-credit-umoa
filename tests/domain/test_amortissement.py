from ews_credit.domain.amortissement import solde_restant_du


def test_solde_initial_egal_au_montant_emprunte():
    assert solde_restant_du(montant_initial=1_000_000, duree_mois=12, mois_ecoules=0, dpd_jours=0) == 1_000_000


def test_solde_nul_a_l_echeance_sans_retard():
    assert solde_restant_du(montant_initial=1_000_000, duree_mois=12, mois_ecoules=12, dpd_jours=0) == 0


def test_solde_decroit_avec_le_temps_hors_retard():
    solde_tot = solde_restant_du(1_000_000, 12, 3, 0)
    solde_tard = solde_restant_du(1_000_000, 12, 6, 0)
    assert solde_tard < solde_tot


def test_solde_ne_decroit_plus_une_fois_en_stage_2():
    solde_sain = solde_restant_du(1_000_000, 12, 6, dpd_jours=0)
    solde_stage2 = solde_restant_du(1_000_000, 12, 6, dpd_jours=45)
    assert solde_stage2 >= solde_sain
