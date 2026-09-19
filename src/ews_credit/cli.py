"""Points d'entree CLI : `python -m ews_credit.cli <portfolio|events> ...`."""

import argparse
from pathlib import Path

import pandas as pd

from ews_credit import config
from ews_credit.generation.events import generer_evenements
from ews_credit.generation.jsonl_writer import ecrire_evenements_partitionnes
from ews_credit.generation.portfolio import generer_portefeuille

RACINE_PROJET = Path(__file__).resolve().parents[2]
DOSSIER_SYNTHETIC_PAR_DEFAUT = RACINE_PROJET / "data" / "synthetic"
DOSSIER_EVENTS_PAR_DEFAUT = RACINE_PROJET / "data" / "raw" / "events"


def _commande_portfolio(args: argparse.Namespace) -> None:
    args.sortie.mkdir(parents=True, exist_ok=True)
    portefeuille = generer_portefeuille(args.n_clients, seed=args.seed)

    portefeuille.clients.to_csv(args.sortie / "clients.csv", index=False)
    portefeuille.credits.to_csv(args.sortie / "credits.csv", index=False)
    portefeuille.panel_mensuel.to_csv(args.sortie / "panel_mensuel.csv", index=False)
    portefeuille.labels.to_csv(args.sortie / "labels.csv", index=False)

    print(f"Clients            : {len(portefeuille.clients):,}")
    print(f"Crédits            : {len(portefeuille.credits):,}")
    print(f"Lignes panel       : {len(portefeuille.panel_mensuel):,}")
    print(f"Lignes labels      : {len(portefeuille.labels):,}")
    print(f"Taux bascule 3m    : {portefeuille.labels['bascule_defaut_3m'].mean():.2%}")
    print(f"Sortie écrite dans : {args.sortie}")


def _commande_events(args: argparse.Namespace) -> None:
    clients = pd.read_csv(args.source / "clients.csv", encoding="utf-8")
    credits = pd.read_csv(args.source / "credits.csv", encoding="utf-8")
    panel = pd.read_csv(args.source / "panel_mensuel.csv", parse_dates=["date_releve"], encoding="utf-8")

    events_df = generer_evenements(clients, credits, panel, seed=args.seed)
    nb_partitions = ecrire_evenements_partitionnes(events_df, args.sortie)

    print(f"Événements générés : {len(events_df):,}")
    print(f"Partitions écrites : {nb_partitions}")
    print(f"Sortie écrite dans : {args.sortie}")


def _construire_parseur() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Outils de génération EWS-Credit UMOA.")
    sous_commandes = parser.add_subparsers(dest="commande", required=True)

    portfolio = sous_commandes.add_parser("portfolio", help="Génère le portefeuille synthétique (vérité terrain).")
    portfolio.add_argument("--n-clients", type=int, default=15_000)
    portfolio.add_argument("--seed", type=int, default=config.SEED)
    portfolio.add_argument("--sortie", type=Path, default=DOSSIER_SYNTHETIC_PAR_DEFAUT)
    portfolio.set_defaults(func=_commande_portfolio)

    events = sous_commandes.add_parser("events", help="Génère le flux d'événements bruts depuis le portefeuille.")
    events.add_argument("--source", type=Path, default=DOSSIER_SYNTHETIC_PAR_DEFAUT)
    events.add_argument("--sortie", type=Path, default=DOSSIER_EVENTS_PAR_DEFAUT)
    events.add_argument("--seed", type=int, default=config.SEED)
    events.set_defaults(func=_commande_events)

    return parser


def main() -> None:
    args = _construire_parseur().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
