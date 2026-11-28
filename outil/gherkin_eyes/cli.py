"""gherkin-eyes : un agent qui regarde l'écran joue vos scénarios Gherkin, sans step definitions.

Exemples :
  gherkin-eyes features/ --url http://localhost:8080
  gherkin-eyes features/panier.feature --url docs/app/index.html --sans-fenetre
  gherkin-eyes features/ --url http://localhost:8080 --tags "not @wip" --passages 3 -j 4

Sorties (dossier --sortie, par défaut gherkin-eyes-rapport/) : rapport.html, junit.xml, resultats.json,
et la capture de l'écran final de chaque passage. Code de sortie : 0 si tout passe, 1 si un scénario
échoue ou est refusé, 2 si l'agent n'a pas pu répondre, 3 si la commande est mal écrite (option, URL,
tags, fichier .feature illisible).
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import __version__
from .agent import COMMANDE_DEFAUT, MODELE_DEFAUT, VERDICTS, VUES, anonymiser, jouer
from .gherkin import filtre_tags, lire, trouver
from .rapport import bilan, ecrire_html, ecrire_json, ecrire_junit, resume


ESPACEMENT_S = 3.0
SYNONYMES = {"ambigu": "refus", "échec": "echec", "pass": "passe", "fail": "echec", "ambiguous": "refus"}


def normaliser_url(url: str) -> str:
    if re.match(r"^[a-z][a-z0-9+.-]*://", url, re.I):
        return url
    chemin = Path(url).expanduser().resolve()
    if not chemin.exists():
        raise ErreurUsage(f"--url : ni URL (http://…) ni fichier existant : {url}")
    return chemin.as_uri()


def lisible(nom: str) -> str:
    return re.sub(r"[^\w-]+", "-", nom, flags=re.UNICODE).strip("-")[:60] or "scenario"


class ErreurUsage(Exception):
    pass


class _Analyseur(argparse.ArgumentParser):
    def error(self, message):  # argparse sortirait avec 2, le code « agent sans réponse »
        self.print_usage(sys.stderr)
        raise ErreurUsage(message)


def arguments(argv: list[str] | None) -> argparse.Namespace:
    p = _Analyseur(prog="gherkin-eyes", description=__doc__.split("\n")[0],
                                epilog=__doc__.split("\n", 2)[2], formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("chemins", nargs="+", type=Path, help="dossiers ou fichiers .feature")
    p.add_argument("--url", required=True, help="adresse de l'appli (http://…, file://… ou chemin d'un fichier HTML)")
    p.add_argument("--sortie", "--out", default="gherkin-eyes-rapport", type=Path, help="dossier des rapports")
    p.add_argument("--tags", help='filtre façon Cucumber, ex. "@panier and not @wip"')
    p.add_argument("--scenario", action="append", help="nom exact d'un scénario (répétable)")
    p.add_argument("--passages", "--runs", type=int, default=1, help="passages par scénario (défaut : 1)")
    p.add_argument("-j", "--parallele", type=int, default=1, help="passages joués en même temps (défaut : 1)")
    p.add_argument("--vue", "--view", choices=VUES, default="les-deux",
                   help="ce que voit l'agent : arbre d'accessibilité, capture d'écran, ou les deux (défaut)")
    p.add_argument("--sans-fenetre", "--headless", action="store_true",
                   help="WebKit de Playwright sans fenêtre (défaut : Chrome avec fenêtre)")
    p.add_argument("--modele", "--model", default=MODELE_DEFAUT, help=f"modèle de l'agent (défaut : {MODELE_DEFAUT})")
    p.add_argument("--commande", "--command", default=COMMANDE_DEFAUT,
                   help="commande d'agent qui lit l'invite sur stdin ; {mcp} et {modele} sont remplacés")
    p.add_argument("--delai", "--timeout", type=float, default=600, help="secondes par passage (défaut : 600)")
    p.add_argument("--relances", type=int, default=2,
                   help="relances d'un passage en erreur (navigateur ou modèle indisponible ; défaut : 2)")
    p.add_argument("--attendu", default="@attendu:",
                   help="préfixe de tag qui donne le verdict attendu, ex. @attendu:passe (défaut : @attendu:)")
    p.add_argument("--version", action="version", version=f"gherkin-eyes {__version__}")
    a = p.parse_args(argv)
    if a.passages < 1 or a.parallele < 1 or a.relances < 0:
        p.error("--passages et --parallele doivent valoir au moins 1, --relances au moins 0")
    return a


def main(argv: list[str] | None = None) -> int:
    try:
        a = arguments(argv)
        url = normaliser_url(a.url)
        garder = filtre_tags(a.tags)
        scenarios = [s for f in trouver(a.chemins) for s in lire(f) if garder(s.tags)]
    except (ErreurUsage, ValueError, FileNotFoundError, UnicodeDecodeError) as e:
        print(f"gherkin-eyes : {e}", file=sys.stderr)
        return 3
    return jouer_tout(a, url, scenarios)


def jouer_tout(a: argparse.Namespace, url: str, scenarios: list) -> int:
    if a.scenario:
        scenarios = [s for s in scenarios if s.nom in a.scenario or s.ident in a.scenario]
    if not scenarios:
        print("aucun scénario à jouer", file=sys.stderr)
        return 2
    sortie = a.sortie
    sortie.mkdir(parents=True, exist_ok=True)
    travaux = [(s, n) for n in range(1, a.passages + 1) for s in scenarios]
    rang = {id(s): i for i, s in enumerate(scenarios, 1)}  # préfixe unique : deux noms proches, deux dossiers
    racines = [Path.cwd(), sortie, *(c.resolve().parent if c.is_file() else c for c in a.chemins)]
    print(f"gherkin-eyes {__version__} · {len(scenarios)} scénarios × {a.passages} passage(s) · {url}")

    verrou, dernier_depart = threading.Lock(), [0.0]

    def un_passage(travail):
        s, n, essai = travail
        with verrou:  # départs espacés : plusieurs serveurs Playwright lancés d'un coup dépassent leur délai
            attente = dernier_depart[0] + (ESPACEMENT_S if a.parallele > 1 else 0) - time.monotonic()
            if attente > 0:
                time.sleep(attente)
            dernier_depart[0] = time.monotonic()
        suffixe = f"--essai{essai}" if essai else ""
        nom = f"{rang[id(s)]:03d}-{lisible(Path(s.fichier).stem)}--{lisible(s.nom)}--{n}{suffixe}"
        dossier = sortie / "passages" / nom
        try:
            r = jouer(s.gherkin(), url, dossier, vue=a.vue, sans_fenetre=a.sans_fenetre, modele=a.modele,
                      commande=a.commande, delai=a.delai, racines=racines)
        except Exception as e:  # un passage qui plante ne doit pas arrêter la série sans rapport
            r = {"duree_s": 0, "cout_usd": 0, "capture": None, "erreur": f"erreur interne : {e!r}"}
        attendu = next((t[len(a.attendu):] for t in s.tags if a.attendu and t.startswith(a.attendu)), None)
        attendu = SYNONYMES.get(attendu, attendu)
        if r.get("capture"):
            r["capture"] = Path(r["capture"]).resolve().relative_to(sortie.resolve()).as_posix()
        ligne = dict(id=s.ident, fichier=Path(s.fichier).name, scenario=s.nom, passage=n, passages_total=a.passages,
                     attendu=attendu if attendu in VERDICTS else None, gherkin=s.gherkin(), **r)
        print(f"  {s.ident} · passage {n} · {ligne.get('verdict', 'ERREUR')} · {ligne['duree_s']} s", flush=True)
        return ligne

    relances = []
    with ThreadPoolExecutor(max_workers=a.parallele) as pool:
        passages = list(pool.map(un_passage, [(s, n, 0) for s, n in travaux]))
        for essai in range(1, a.relances + 1):
            a_rejouer = [(i, travaux[i]) for i, p in enumerate(passages) if "erreur" in p]
            if not a_rejouer:
                break
            print(f"relance {essai} : {len(a_rejouer)} passage(s) en erreur")
            nouveaux = list(pool.map(un_passage, [(s, n, essai) for _, (s, n) in a_rejouer]))
            for (i, _), ligne in zip(a_rejouer, nouveaux):
                relances.append({k: passages[i][k] for k in ("id", "passage", "erreur", "duree_s", "cout_usd")})
                passages[i] = ligne

    entete = dict(outil=f"gherkin-eyes {__version__}", date=dt.datetime.now().isoformat(timespec="seconds"),
                  url=url, modele=a.modele, vue=a.vue, navigateur="webkit headless" if a.sans_fenetre else "chrome",
                  commande=a.commande, erreurs_relancees=relances)
    passages = json.loads(anonymiser(json.dumps(passages, ensure_ascii=False), racines))
    entete = json.loads(anonymiser(json.dumps(entete, ensure_ascii=False), racines))
    ecrire_json(sortie / "resultats.json", entete, passages)
    ecrire_junit(sortie / "junit.xml", passages)
    ecrire_html(sortie / "rapport.html", entete, passages)
    b = bilan(passages)
    if relances:
        print(f"{len(relances)} passage(s) relancé(s), coût en plus : {sum(r['cout_usd'] for r in relances):.2f} $")
    print(resume(b))
    print(f"rapport : {sortie / 'rapport.html'} · JUnit : {sortie / 'junit.xml'}")
    if b["erreur"]:
        return 2
    return 0 if b["passe"] == b["passages"] else 1


if __name__ == "__main__":
    sys.exit(main())
