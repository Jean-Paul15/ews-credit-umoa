"""Point d'entree FastAPI : `uvicorn ews_credit.api.main:app`."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from ews_credit.api.dependencies import definir_donnees
from ews_credit.api.repository import charger_donnees
from ews_credit.api.routes_credits import router as router_credits
from ews_credit.api.routes_portefeuille import router as router_portefeuille

RACINE_PROJET = Path(__file__).resolve().parents[3]
DOSSIER_SYNTHETIC = Path(os.environ.get("EWS_DATA_SYNTHETIC", RACINE_PROJET / "data" / "synthetic"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    definir_donnees(charger_donnees(DOSSIER_SYNTHETIC))
    yield


app = FastAPI(
    title="EWS-Credit UMOA",
    description="Score de risque et simulation d'impact provisionnement IFRS 9.",
    lifespan=lifespan,
)
app.include_router(router_credits)
app.include_router(router_portefeuille)


@app.get("/health")
def health() -> dict:
    return {"statut": "ok"}
