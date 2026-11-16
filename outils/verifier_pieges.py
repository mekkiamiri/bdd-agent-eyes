#!/usr/bin/env python3
"""Vérifie que Cucumber échoue bien sur chaque scénario faux ou ambigu, comme étiqueté.

Usage : python3 outils/verifier_pieges.py --lancer          # lance Maven puis vérifie
        python3 outils/verifier_pieges.py [target/surefire-reports]   # vérifie des rapports déjà produits

Commande Maven lancée par --lancer (la même qu'en CI) :
  mvn -B test -Dcucumber.filter.tags="not @attendu:passe" -Dmaven.test.failure.ignore=true

Règles, scénario par scénario (rapports JUnit XML de Surefire, nommage « Fonctionnalité - Scénario ») :
- @attendu:echec  : le scénario doit échouer sur une assertion ou un délai dépassé (l'appli ne fait pas ce qui est écrit) ;
- @attendu:ambigu : échec de ce type, ou étape non définie ;
- tout autre résultat (succès, scénario absent, erreur d'infrastructure comme un navigateur absent) est une erreur.
"""

from __future__ import annotations

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from valider import RACINE, valider  # noqa: E402

COMMANDE = ["mvn", "-B", "test", "-Dcucumber.filter.tags=not @attendu:passe", "-Dmaven.test.failure.ignore=true"]
SIGNES_ECHEC = ("AssertionFailedError", "TimeoutError", "Timeout ")
SIGNES_NON_DEFINIE = ("UndefinedStepException", "is undefined", "Undefined")


def classer(cas: ET.Element) -> tuple[str, str]:
    """Retourne (« passe » | « echec » | « non définie » | « non joué » | « erreur inattendue », détail)."""
    for balise in ("failure", "error", "skipped"):
        el = cas.find(balise)
        if el is None:
            continue
        detail = " ".join(filter(None, [el.get("type"), el.get("message"), el.text]))
        if any(s in detail for s in SIGNES_NON_DEFINIE):
            return "non définie", detail
        if balise != "skipped" and any(s in detail for s in SIGNES_ECHEC):
            return "echec", detail
        return ("non joué" if balise == "skipped" else "erreur inattendue"), detail
    return "passe", ""


def lire_rapports(dossier: Path) -> dict[str, tuple[str, str]]:
    resultats = {}
    for fichier in sorted(dossier.glob("TEST-*.xml")):
        for cas in ET.parse(fichier).getroot().iter("testcase"):
            resultats[cas.get("name", "")] = classer(cas)
    return resultats


def verifier(resultats: dict[str, tuple[str, str]], afficher: bool = False) -> list[str]:
    fonctionnalites, rapport = valider(RACINE / "features", RACINE / "docs" / "app")
    if rapport.erreurs:
        return ["features invalides : lancer python3 outils/valider.py"]
    erreurs = []
    for f in fonctionnalites:
        for s in f.scenarios:
            if s.attendu == "passe":
                continue
            nom = f"{f.nom} - {s.nom}"
            obtenu, detail = resultats.get(nom, ("absent", ""))
            permis = ("echec",) if s.attendu == "echec" else ("echec", "non définie")
            etat = "ok " if obtenu in permis else "KO "
            if afficher:
                print(f"  {etat} @attendu:{s.attendu:<6} {obtenu:<18} {nom}")
            if obtenu not in permis:
                erreurs.append(f"{nom} : attendu {' ou '.join(permis)}, obtenu {obtenu} {detail[:160]}".rstrip())
    return erreurs


def main(argv: list[str]) -> int:
    args = [a for a in argv[1:] if a != "--lancer"]
    if "--lancer" in argv:
        subprocess.run(COMMANDE, cwd=RACINE, check=True)
    dossier = Path(args[0]) if args else RACINE / "target" / "surefire-reports"
    erreurs = verifier(lire_rapports(dossier), afficher=True)
    for e in erreurs:
        print("ERREUR ·", e)
    print("OK : chaque piège fait échouer Cucumber comme prévu" if not erreurs else f"{len(erreurs)} erreur(s)")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
