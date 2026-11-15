#!/usr/bin/env python3
"""Génère docs/scenarios.js (les scénarios Gherkin lus par la page de démo).

Usage : python3 outils/construire_page.py          # écrit docs/scenarios.js
        python3 outils/construire_page.py --check  # échoue si le fichier n'est pas à jour
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from valider import RACINE, valider  # noqa: E402

SORTIE = RACINE / "docs" / "scenarios.js"


def contenu() -> str:
    fonctionnalites, rapport = valider(RACINE / "features", RACINE / "docs" / "app")
    if rapport.erreurs:
        raise SystemExit("features invalides : lancer python3 outils/valider.py")
    donnees = []
    for f in fonctionnalites:
        for s in f.scenarios:
            donnees.append({
                "id": f"{Path(f.fichier).name}:{s.nom}",
                "fonctionnalite": f.nom,
                "parcours": f.parcours,
                "nom": s.nom,
                "attendu": s.attendu,
                "piege": s.piege,
                "etapes": [{"mot": e.mot.strip(), "texte": e.texte, "contexte": True} for e in f.contexte]
                + [{"mot": e.mot.strip(), "texte": e.texte, "contexte": False} for e in s.etapes],
            })
    return ("// Généré par outils/construire_page.py à partir de features/*.feature : ne pas modifier.\n"
            "window.SCENARIOS = " + json.dumps(donnees, ensure_ascii=False, indent=1) + ";\n")


def main(argv: list[str]) -> int:
    attendu = contenu()
    if "--check" in argv:
        actuel = SORTIE.read_text(encoding="utf-8") if SORTIE.exists() else ""
        if actuel != attendu:
            print("docs/scenarios.js n'est pas à jour : lancer python3 outils/construire_page.py")
            return 1
        print("docs/scenarios.js à jour")
        return 0
    SORTIE.write_text(attendu, encoding="utf-8")
    print(f"écrit {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
