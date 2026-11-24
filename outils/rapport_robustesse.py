#!/usr/bin/env python3
"""Rapport de robustesse de la référence Cucumber : les 17 scénarios rejoués sur une autre interface.

Usage : python3 outils/rapport_robustesse.py [target/surefire-reports] [--resume FICHIER.md] [--json FICHIER.json]

Lit les rapports JUnit XML de Surefire (mêmes règles que outils/verifier_pieges.py) et compare chaque
scénario à sa vérité terrain :
- @attendu:passe : conforme s'il passe ; sinon il est « cassé » (l'interface a changé, pas le comportement) ;
- @attendu:echec / @attendu:ambigu : conforme s'il échoue (assertion, délai dépassé ou étape non définie).
Un piège qui échoue reste conforme, mais la raison de l'échec est affichée : elle peut avoir changé.

Code de sortie : 0 si aucun scénario n'est cassé ni absent, 1 sinon.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from valider import RACINE, valider  # noqa: E402
from verifier_pieges import lire_rapports  # noqa: E402


def comparer(resultats: dict[str, tuple[str, str]]) -> list[dict]:
    fonctionnalites, rapport = valider(RACINE / "features", RACINE / "docs" / "app")
    if rapport.erreurs:
        raise SystemExit("features invalides : lancer python3 outils/valider.py")
    lignes = []
    for f in fonctionnalites:
        for s in f.scenarios:
            nom = f"{f.nom} - {s.nom}"
            obtenu, detail = resultats.get(nom, ("absent", ""))
            if s.attendu == "passe":
                permis = ("passe",)
            elif s.attendu == "echec":
                permis = ("echec",)
            else:
                permis = ("echec", "non définie")
            lignes.append({"id": f"{Path(f.fichier).name}:{s.nom}", "attendu": s.attendu, "obtenu": obtenu,
                           "conforme": obtenu in permis, "detail": " ".join(detail.split())[:240]})
    return lignes


def resume_markdown(lignes: list[dict]) -> str:
    casses = [ligne for ligne in lignes if not ligne["conforme"]]
    justes = [ligne for ligne in lignes if ligne["attendu"] == "passe"]
    out = [f"### Robustesse Cucumber : {len(casses)} scénario(s) cassé(s) sur {len(lignes)}",
           "",
           f"Scénarios justes qui passent encore : {sum(1 for ligne in justes if ligne['conforme'])}/{len(justes)}.",
           "",
           "| Scénario | Attendu | Obtenu | Conforme | Détail (début) |",
           "|---|---|---|---|---|"]
    for ligne in lignes:
        detail = ligne["detail"][:140].replace("|", "\\|")
        out.append(f"| {ligne['id']} | {ligne['attendu']} | {ligne['obtenu']} | "
                   f"{'oui' if ligne['conforme'] else '**non**'} | {detail} |")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    args, resume, sortie_json = [], None, None
    i = 1
    while i < len(argv):
        if argv[i] == "--resume":
            resume, i = argv[i + 1], i + 2
        elif argv[i] == "--json":
            sortie_json, i = argv[i + 1], i + 2
        else:
            args.append(argv[i])
            i += 1
    dossier = Path(args[0]) if args else RACINE / "target" / "surefire-reports"
    lignes = comparer(lire_rapports(dossier))
    texte = resume_markdown(lignes)
    print(texte)
    if resume:
        with open(resume, "a", encoding="utf-8") as f:
            f.write(texte)
    if sortie_json:
        casses = [ligne["id"] for ligne in lignes if not ligne["conforme"]]
        Path(sortie_json).write_text(json.dumps({"scenarios": len(lignes), "casses": len(casses),
                                                 "liste_casses": casses, "detail": lignes},
                                                ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 1 if any(not ligne["conforme"] for ligne in lignes) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
