"""Client HTTP vers l'API EWS-Credit — le dashboard n'accede jamais aux
fichiers de donnees directement, uniquement via ces appels."""

import os

import requests

URL_API = os.environ.get("EWS_API_URL", "http://localhost:8000")


def recuperer_vue_ensemble() -> dict:
    reponse = requests.get(f"{URL_API}/portefeuille/vue-ensemble", timeout=10)
    reponse.raise_for_status()
    return reponse.json()


def recuperer_score_credit(credit_id: str) -> dict | None:
    reponse = requests.get(f"{URL_API}/credits/{credit_id}/score", timeout=10)
    if reponse.status_code == 404:
        return None
    reponse.raise_for_status()
    return reponse.json()


def recuperer_credits_a_risque(limite: int = 50) -> list[dict]:
    reponse = requests.get(f"{URL_API}/credits/a-risque", params={"limite": limite}, timeout=10)
    reponse.raise_for_status()
    return reponse.json()


def simuler_provisionnement(part_credits_degrades: float) -> dict:
    reponse = requests.post(
        f"{URL_API}/portefeuille/simulation-provisionnement",
        json={"part_credits_degrades": part_credits_degrades},
        timeout=10,
    )
    reponse.raise_for_status()
    return reponse.json()
