"""Test d'integration : le pipeline de generation complet produit un
portefeuille coherent (tables alignees, pas de fuite d'information)."""

from ews_credit.generation.portfolio import generer_portefeuille

N_CLIENTS = 300


def test_generer_portefeuille_produit_des_tables_coherentes():
    portefeuille = generer_portefeuille(N_CLIENTS, seed=1)

    assert len(portefeuille.clients) == N_CLIENTS
    assert set(portefeuille.credits["client_id"]).issubset(set(portefeuille.clients["client_id"]))
    assert set(portefeuille.panel_mensuel["credit_id"]).issubset(set(portefeuille.credits["credit_id"]))
    assert "_score_risque_latent" not in portefeuille.clients.columns  # interne, jamais expose


def test_labels_ne_couvrent_jamais_les_credits_deja_en_defaut():
    portefeuille = generer_portefeuille(N_CLIENTS, seed=1)
    lignes_en_defaut = portefeuille.panel_mensuel.loc[portefeuille.panel_mensuel["stage_ifrs9"] == 3, "credit_id"]
    credits_labellises_en_defaut = set(portefeuille.labels["credit_id"]) & set(lignes_en_defaut)
    # un credit peut apparaitre dans labels a un mois SAIN puis defaut plus tard,
    # mais aucune ligne de labels ne doit elle-meme etre au stage defaut
    assert (portefeuille.labels["stage_ifrs9"] == 3).sum() == 0


def test_generation_reproductible_avec_la_meme_graine():
    p1 = generer_portefeuille(N_CLIENTS, seed=7)
    p2 = generer_portefeuille(N_CLIENTS, seed=7)
    assert p1.labels["bascule_defaut_3m"].sum() == p2.labels["bascule_defaut_3m"].sum()
