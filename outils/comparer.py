#!/usr/bin/env python3
"""Compare les verdicts d'une configuration (agent ou Cucumber) à la vérité terrain des features.

Usage : python3 outils/comparer.py resultats/<config>/resultats.json [...]

Format d'un fichier de résultats (voir PROTOCOLE.md ; écrit par agent/lancer.py) :
{
  "config": "cucumber-playwright" | "agent-<configuration>",
  "date": "AAAA-MM-JJ",
  "scenarios": [
    {"id": "connexion.feature:Connexion réussie", "passage": 1, "verdict": "passe|echec|refus",
     "duree_s": 4.2, "cout_usd": 0.0, "explication": "…"}
  ]
}
Un même scénario apparaît une fois par passage (3 passages dans le protocole). Si « passage » manque,
l'ordre d'apparition fait foi.

Mesures, comptées sur tous les passages (un passage = un verdict) :
- justes, faux positifs, faux négatifs, refus justes, refus injustes ;
- réussite par passage (part de verdicts justes au passage k), sa moyenne et sa variance entre passages ;
- stabilité : nombre de scénarios dont tous les passages donnent le même verdict ;
- durée et coût : totaux, et variance de la durée par scénario (moyenne des variances).

Aucun chiffre n'est publié tant qu'aucun fichier de résultats réel n'existe dans resultats/.
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from valider import RACINE, valider  # noqa: E402

VERDICTS = ("passe", "echec", "refus")


def verite_terrain() -> dict[str, str]:
    fonctionnalites, rapport = valider(RACINE / "features", RACINE / "docs" / "app")
    if rapport.erreurs:
        raise SystemExit("features invalides : lancer python3 outils/valider.py")
    return {f"{Path(f.fichier).name}:{s.nom}": s.attendu for f in fonctionnalites for s in f.scenarios}


def regrouper(resultats: dict, verite: dict[str, str]) -> dict[str, list[dict]]:
    """Regroupe les lignes par scénario, triées par passage. Lève ValueError si le fichier est incohérent."""
    groupes: dict[str, list[dict]] = defaultdict(list)
    for r in resultats["scenarios"]:
        if r.get("id") not in verite:
            raise ValueError(f"scénario inconnu : {r.get('id')}")
        if r.get("verdict") not in VERDICTS:
            raise ValueError(f"verdict invalide pour {r['id']} : {r.get('verdict')}")
        groupes[r["id"]].append(dict(r))
    for sid, lignes in groupes.items():
        for rang, r in enumerate(lignes, 1):
            r.setdefault("passage", rang)
        lignes.sort(key=lambda r: r["passage"])
        passages = [r["passage"] for r in lignes]
        if len(set(passages)) != len(passages):
            raise ValueError(f"passage en double pour {sid} : {passages}")
    return dict(groupes)


def juste(attendu: str, verdict: str) -> bool:
    # Scénario juste : il doit passer. Faux ou ambigu : il faut le signaler (échec ou refus).
    return verdict == "passe" if attendu == "passe" else verdict != "passe"


def mesurer(resultats: dict, verite: dict[str, str]) -> dict:
    """Calcule les mesures du protocole pour un fichier de résultats."""
    groupes = regrouper(resultats, verite)
    m = {"config": resultats.get("config", "?"), "scenarios_joues": len(groupes), "total": len(verite),
         "verdicts": 0, "justes": 0, "faux_positifs": 0, "faux_negatifs": 0,
         "refus_justes": 0, "refus_injustes": 0, "stables": 0, "duree_s": 0.0, "cout_usd": 0.0}
    par_passage: dict[int, list[bool]] = defaultdict(list)
    variances_duree = []
    for sid, lignes in groupes.items():
        attendu = verite[sid]
        for r in lignes:
            v = r["verdict"]
            ok = juste(attendu, v)
            m["verdicts"] += 1
            m["justes"] += ok
            m["duree_s"] += float(r.get("duree_s", 0))
            m["cout_usd"] += float(r.get("cout_usd", 0))
            par_passage[r["passage"]].append(ok)
            if attendu == "passe" and not ok:
                m["faux_negatifs"] += 1
                m["refus_injustes"] += v == "refus"
            if attendu != "passe" and not ok:
                m["faux_positifs"] += 1
            if attendu == "ambigu" and v == "refus":
                m["refus_justes"] += 1
        m["stables"] += len({r["verdict"] for r in lignes}) == 1
        if len(lignes) > 1:
            variances_duree.append(statistics.pvariance([float(r.get("duree_s", 0)) for r in lignes]))
    taux = [sum(oks) / len(oks) for _, oks in sorted(par_passage.items())]
    m["reussite_par_passage"] = taux
    m["reussite_moyenne"] = statistics.fmean(taux) if taux else 0.0
    m["reussite_variance"] = statistics.pvariance(taux) if len(taux) > 1 else 0.0
    m["variance_duree_s2"] = statistics.fmean(variances_duree) if variances_duree else 0.0
    return m


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    verite = verite_terrain()
    print("| Configuration | Scénarios | Verdicts justes | Réussite (moy. ± var.) | Faux positifs | Faux négatifs "
          "| Refus justes | Stables | Durée (s) | Coût (USD) |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for chemin in argv[1:]:
        m = mesurer(json.loads(Path(chemin).read_text(encoding="utf-8")), verite)
        print(f"| {m['config']} | {m['scenarios_joues']}/{m['total']} | {m['justes']}/{m['verdicts']} | "
              f"{m['reussite_moyenne']:.2f} ± {m['reussite_variance']:.3f} | {m['faux_positifs']} | "
              f"{m['faux_negatifs']} | {m['refus_justes']} | {m['stables']}/{m['scenarios_joues']} | "
              f"{m['duree_s']:.1f} | {m['cout_usd']:.2f} |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
