"""Segmentation clientele et types de credit du portefeuille."""

TYPES_CLIENT = ["Particulier", "PME"]
POIDS_TYPE_CLIENT = [0.82, 0.18]  # portefeuille de detail majoritaire particuliers

TYPES_CREDIT = ["Consommation", "Habitat", "Decouvert", "Equipement PME"]
POIDS_TYPE_CREDIT = {
    "Particulier": [0.62, 0.18, 0.20, 0.0],
    "PME": [0.0, 0.0, 0.35, 0.65],
}

REVENU_MENSUEL_MEDIAN_FCFA = {
    "Particulier": 180_000,
    "PME": 950_000,
}
REVENU_MENSUEL_SIGMA_LOG = {
    "Particulier": 0.55,
    "PME": 0.65,
}
