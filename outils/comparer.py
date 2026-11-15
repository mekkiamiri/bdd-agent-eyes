#!/usr/bin/env python3
"""Compare les verdicts d'une configuration (agent ou Cucumber) à la vérité terrain des features.

Usage : python3 outils/comparer.py resultats/<config>/resultats.json [...]

Format d'un fichier de résultats (voir PROTOCOLE.md) :
{
  "config": "cucumber-playwright" | "agent-<modèle>",
  "date": "AAAA-MM-JJ",
  "scenarios": [
    {"id": "connexion.feature:Connexion réussie", "verdict": "passe|echec|refus",
     "duree_s": 4.2, "cout_usd": 0.0, "explication": "…"}
  ]
}

Aucun chiffre n'est publié tant qu'aucun fichier de résultats réel n'existe dans resultats/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from valider import RACINE, valider  # noqa: E402

VERDICTS = ("passe", "echec", "refus")


def verite_terrain() -> dict[str, str]:
    fonctionnalites, rapport = valider(RACINE / "features", RACINE / "docs" / "app")
    if rapport.erreurs:
        raise SystemExit("features invalides : lancer python3 outils/valider.py")
    return {f"{Path(f.fichier).name}:{s.nom}": s.attendu for f in fonctionnalites for s in f.scenarios}


def mesurer(resultats: dict, verite: dict[str, str]) -> dict:
    """Calcule les mesures du protocole pour un fichier de résultats."""
    lignes = {r["id"]: r for r in resultats["scenarios"]}
    inconnus = sorted(set(lignes) - set(verite))
    if inconnus:
        raise ValueError(f"scénarios inconnus : {inconnus}")
    for r in lignes.values():
        if r.get("verdict") not in VERDICTS:
            raise ValueError(f"verdict invalide pour {r['id']} : {r.get('verdict')}")
    m = {"config": resultats.get("config", "?"), "joues": len(lignes), "total": len(verite),
         "justes": 0, "faux_positifs": 0, "faux_negatifs": 0, "refus_justes": 0, "refus_injustes": 0,
         "duree_s": 0.0, "cout_usd": 0.0}
    for sid, attendu in verite.items():
        r = lignes.get(sid)
        if r is None:
            continue
        v = r["verdict"]
        m["duree_s"] += float(r.get("duree_s", 0))
        m["cout_usd"] += float(r.get("cout_usd", 0))
        if attendu == "passe":
            if v == "passe":
                m["justes"] += 1
            else:
                m["faux_negatifs"] += 1
                if v == "refus":
                    m["refus_injustes"] += 1
        else:
            # Scénario faux ou ambigu : le bon comportement est de le signaler (échec ou refus).
            if v == "passe":
                m["faux_positifs"] += 1
            else:
                m["justes"] += 1
                if attendu == "ambigu" and v == "refus":
                    m["refus_justes"] += 1
    return m


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    verite = verite_terrain()
    print("| Configuration | Joués | Justes | Faux positifs | Faux négatifs | Refus justes | Durée (s) | Coût (USD) |")
    print("|---|---|---|---|---|---|---|---|")
    for chemin in argv[1:]:
        m = mesurer(json.loads(Path(chemin).read_text(encoding="utf-8")), verite)
        print(f"| {m['config']} | {m['joues']}/{m['total']} | {m['justes']} | {m['faux_positifs']} | "
              f"{m['faux_negatifs']} | {m['refus_justes']} | {m['duree_s']:.1f} | {m['cout_usd']:.2f} |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
