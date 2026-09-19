"""Ecriture du flux d'evenements en JSON Lines, partitionne façon Hive.

Arborescence `pays_code=XX/annee=YYYY/mois=MM/part-0000.jsonl` : directement
compatible avec un chemin HDFS et avec la decouverte de partitions de Spark
(`spark.read.json(..., basePath=...)`), sans transformation supplementaire.
"""

import json
from pathlib import Path

import pandas as pd

COLONNES_PARTITION = ["pays_code", "annee", "mois"]
COLONNES_EVENEMENT = [
    "event_id",
    "event_type",
    "credit_id",
    "client_id",
    "date_evenement",
    "montant_fcfa",
    "statut",
]


def _ligne_en_json(ligne: pd.Series) -> str:
    enregistrement = {colonne: ligne[colonne] for colonne in COLONNES_EVENEMENT}
    enregistrement["date_evenement"] = ligne["date_evenement"].strftime("%Y-%m-%d")
    return json.dumps(enregistrement, ensure_ascii=False)


def ecrire_evenements_partitionnes(events_df: pd.DataFrame, dossier_racine: Path) -> int:
    """Ecrit un fichier `part-0000.jsonl` par partition (pays_code, annee, mois)."""
    dossier_racine.mkdir(parents=True, exist_ok=True)
    nb_fichiers = 0

    for cles_partition, groupe in events_df.groupby(COLONNES_PARTITION):
        pays_code, annee, mois = cles_partition
        dossier_partition = dossier_racine / f"pays_code={pays_code}" / f"annee={annee}" / f"mois={mois:02d}"
        dossier_partition.mkdir(parents=True, exist_ok=True)

        lignes_json = groupe.apply(_ligne_en_json, axis=1)
        (dossier_partition / "part-0000.jsonl").write_text("\n".join(lignes_json), encoding="utf-8")
        nb_fichiers += 1

    return nb_fichiers
