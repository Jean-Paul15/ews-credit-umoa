"""Repartition geographique du portefeuille sur les pays de l'UMOA."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PaysUMOA:
    nom: str
    code_iso: str
    taux_bancarisation_pct: float  # [SOURCE REELLE] BCEAO IMF, SF4003A0AP, 2022


# [SOURCE REELLE] BCEAO / DBnomics, dataset IMF (Indicateurs de la microfinance),
# serie SF4003A0AP "Taux de bancarisation strict (base population adulte)", derniere
# annee disponible = 2022. Utilise comme poids relatif de taille de portefeuille
# bancarise par pays (proxy defendable en l'absence de repartition officielle du
# nombre de comptes de credit par pays).
PAYS_UMOA = [
    PaysUMOA("Côte d'Ivoire", "CI", 29.508),
    PaysUMOA("Bénin", "BJ", 35.708),
    PaysUMOA("Burkina Faso", "BF", 21.754),
    PaysUMOA("Mali", "ML", 24.011),
    PaysUMOA("Niger", "NE", 8.678),
    PaysUMOA("Sénégal", "SN", 22.468),
    PaysUMOA("Guinée-Bissau", "GW", 16.398),
    PaysUMOA("Togo", "TG", 29.757),
]
