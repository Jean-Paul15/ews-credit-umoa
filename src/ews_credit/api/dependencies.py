"""Detient les donnees chargees au demarrage, injectees dans les routes."""

from ews_credit.api.repository import DonneesPortefeuille

_donnees: DonneesPortefeuille | None = None


def definir_donnees(donnees: DonneesPortefeuille) -> None:
    global _donnees
    _donnees = donnees


def get_donnees() -> DonneesPortefeuille:
    if _donnees is None:
        raise RuntimeError("Donnees non chargees : l'application n'a pas fini son demarrage.")
    return _donnees
