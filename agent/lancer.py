#!/usr/bin/env python3
"""Fait jouer les scénarios Gherkin par un agent qui pilote un navigateur, et écrit resultats/.

Usage :
  python3 agent/lancer.py --config les-deux                      # tous les scénarios, 3 passages
  python3 agent/lancer.py --config arbre --scenario "panier.feature:Ajouter au panier" --passages 1
  python3 agent/lancer.py --config essai --commande "python3 tests/faux_agent.py"   # faux agent (tests)

Ce script n'est pas lancé en CI : il appelle un vrai modèle (payant). Il est testé avec un faux agent.

La commande d'agent reçoit la consigne et le scénario sur son entrée standard. Par défaut :
  claude -p --output-format json --strict-mcp-config --mcp-config agent/mcp-{config}.json
         --allowedTools mcp__playwright
avec un serveur MCP Playwright (@playwright/mcp 0.0.85) décrit dans agent/mcp-<config>.json :
  arbre    : arbre d'accessibilité, images retirées des réponses (--image-responses omit) ;
  capture  : outils par coordonnées (--caps vision), pas d'instantané d'accessibilité (--snapshot-mode none) ;
  les-deux : --caps vision et instantanés d'accessibilité.
« {config} » dans --commande est remplacé par le nom de la configuration.

Sortie de l'agent acceptée : le JSON de `claude -p --output-format json` (champs « result » et
« total_cost_usd ») ou du texte brut ; le dernier objet JSON contenant « verdict » fait foi.
Une réponse illisible n'est pas transformée en verdict : elle va dans « erreurs ».
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))
from valider import valider  # noqa: E402

COMMANDE_DEFAUT = ("claude -p --output-format json --setting-sources project --model claude-sonnet-5-5 "
                   "--strict-mcp-config --mcp-config agent/mcp-{config}.json --allowedTools mcp__playwright")
VERDICTS = ("passe", "echec", "refus")


def consigne() -> str:
    texte = (RACINE / "agent" / "CONSIGNE.md").read_text(encoding="utf-8")
    return texte.split("\n---\n", 1)[1].strip()


def scenarios() -> dict[str, str]:
    """id → texte Gherkin envoyé à l'agent : sans tags, sans descriptions, sans ligne « Piège : »."""
    fonctionnalites, rapport = valider(RACINE / "features", RACINE / "docs" / "app")
    if rapport.erreurs:
        raise SystemExit("features invalides : lancer python3 outils/valider.py")
    sortie = {}
    for f in fonctionnalites:
        for s in f.scenarios:
            lignes = ["# language: fr", f"Fonctionnalité: {f.nom}", ""]
            if f.contexte:
                lignes += ["  Contexte:"] + [f"    {e.mot}{e.texte}" for e in f.contexte] + [""]
            lignes += [f"  Scénario: {s.nom}"] + [f"    {e.mot}{e.texte}" for e in s.etapes]
            sortie[f"{Path(f.fichier).name}:{s.nom}"] = "\n".join(lignes) + "\n"
    return sortie


def invite(gherkin: str, url: str) -> str:
    return f"{consigne()}\n\nApplication : {url}\n\nScénario :\n```gherkin\n{gherkin}```\n"


def lire_reponse(sortie: str) -> tuple[dict | None, float]:
    """Retourne (verdict JSON ou None, coût en USD si l'outil le donne)."""
    texte, cout = sortie, 0.0
    try:
        enveloppe = json.loads(sortie)
        if isinstance(enveloppe, dict) and "result" in enveloppe:
            texte = str(enveloppe["result"])
            cout = float(enveloppe.get("total_cost_usd") or 0)
        elif isinstance(enveloppe, dict) and "verdict" in enveloppe:
            return enveloppe, cout
    except (json.JSONDecodeError, ValueError):
        pass
    decodeur, trouve = json.JSONDecoder(), None
    for i, c in enumerate(texte):
        if c != "{":
            continue
        try:
            objet, _ = decodeur.raw_decode(texte, i)
        except json.JSONDecodeError:
            continue
        if isinstance(objet, dict) and "verdict" in objet:
            trouve = objet
    return trouve, cout


def jouer(sid: str, gherkin: str, commande: list[str], url: str, delai: float) -> dict:
    debut = time.monotonic()
    try:
        fini = subprocess.run(commande, input=invite(gherkin, url), capture_output=True, text=True,
                              timeout=delai, cwd=RACINE)
        sortie, code = fini.stdout, fini.returncode
    except subprocess.TimeoutExpired:
        sortie, code = "", "délai dépassé"
    duree = round(time.monotonic() - debut, 2)
    verdict, cout = lire_reponse(sortie)
    ligne = {"id": sid, "duree_s": duree, "cout_usd": cout}
    if code != 0 or verdict is None or verdict.get("verdict") not in VERDICTS:
        ligne["erreur"] = f"code {code} ; sortie : {sortie[-300:]!r}"
        return ligne
    ligne.update(verdict=verdict["verdict"], etape=verdict.get("etape"),
                 explication=verdict.get("explication", ""), preuve=verdict.get("preuve", ""))
    return ligne


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--config", required=True, help="arbre, capture, les-deux (ou un nom libre avec --commande)")
    p.add_argument("--commande", default=COMMANDE_DEFAUT, help="commande d'agent ; {config} est remplacé")
    p.add_argument("--scenario", action="append", help="id « fichier.feature:Nom » (répétable) ; défaut : tous")
    p.add_argument("--passages", type=int, default=3)
    p.add_argument("--url", default=(RACINE / "docs" / "app" / "index.html").as_uri())
    p.add_argument("--sortie", default=str(RACINE / "resultats"))
    p.add_argument("--delai", type=float, default=600, help="secondes par scénario")
    a = p.parse_args(argv)

    tous = scenarios()
    choisis = a.scenario or list(tous)
    inconnus = [s for s in choisis if s not in tous]
    if inconnus:
        print("scénarios inconnus :", inconnus)
        return 2
    commande = shlex.split(a.commande.replace("{config}", a.config))
    fichier = Path(a.sortie) / f"agent-{a.config}" / "resultats.json"
    if fichier.exists():
        donnees = json.loads(fichier.read_text(encoding="utf-8"))
    else:
        donnees = {"config": f"agent-{a.config}", "scenarios": [], "erreurs": []}
    donnees.update(date=dt.date.today().isoformat(), commande=" ".join(commande), url=a.url)
    donnees.setdefault("erreurs", [])

    for _ in range(a.passages):
        for sid in choisis:
            deja = sum(1 for r in donnees["scenarios"] + donnees["erreurs"] if r["id"] == sid)
            ligne = jouer(sid, tous[sid], commande, a.url, a.delai)
            ligne["passage"] = deja + 1
            cible = "erreurs" if "erreur" in ligne else "scenarios"
            donnees[cible].append(ligne)
            print(f"{sid} · passage {ligne['passage']} · {ligne.get('verdict', 'ERREUR')} · {ligne['duree_s']} s")
            fichier.parent.mkdir(parents=True, exist_ok=True)
            fichier.write_text(json.dumps(donnees, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"écrit {fichier}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
