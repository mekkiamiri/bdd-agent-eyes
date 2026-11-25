#!/usr/bin/env python3
"""Rapport de robustesse de la référence Cucumber : les 17 scénarios rejoués sur une autre interface.

Usage : python3 outils/rapport_robustesse.py [target/surefire-reports] [--reference DOSSIER_V1]
                                              [--resume FICHIER.md] [--json FICHIER.json]

Lit les rapports JUnit XML de Surefire (mêmes règles que outils/verifier_pieges.py) et compare chaque
scénario à sa vérité terrain :
- @attendu:passe : conforme s'il passe ; sinon il est « cassé » (l'interface a changé, pas le comportement) ;
- @attendu:echec / @attendu:ambigu : conforme s'il échoue (assertion, délai dépassé ou étape non définie).
Un piège qui échoue reste conforme, mais l'étape en échec est affichée. Avec --reference (rapports du même
lancement sur l'appli d'origine), un scénario qui échoue sur une autre étape qu'avant est signalé « raison
changée » : il échoue toujours, mais plus pour la raison prévue par sa vérité terrain.

Code de sortie : 0 si aucun scénario n'est cassé ni absent, 1 sinon.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from valider import RACINE, valider  # noqa: E402
from verifier_pieges import lire_rapports  # noqa: E402


def etape_en_echec(detail: str) -> str:
    """Première étape Gherkin citée dans la pile d'appels (« at ✽.j'ajoute "Marteau" au panier(file:…) »)."""
    m = re.search(r"✽\.(.+?)\((?:file|classpath):", detail)
    if m:
        return m.group(1).strip()
    m = re.search(r"The step '([^']+)' is undefined", detail)
    return f"{m.group(1)} (non définie)" if m else ""


def comparer(resultats: dict[str, tuple[str, str]],
             reference: dict[str, tuple[str, str]] | None = None) -> list[dict]:
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
            ligne = {"id": f"{Path(f.fichier).name}:{s.nom}", "attendu": s.attendu, "obtenu": obtenu,
                     "conforme": obtenu in permis, "etape": etape_en_echec(detail),
                     "detail": " ".join(detail.split())[:240]}
            if reference is not None:
                avant, detail_avant = reference.get(nom, ("absent", ""))
                ligne["avant"] = avant
                ligne["etape_avant"] = etape_en_echec(detail_avant)
                ligne["raison_changee"] = (ligne["conforme"] and obtenu != "passe"
                                           and (avant, ligne["etape_avant"]) != (obtenu, ligne["etape"]))
            lignes.append(ligne)
    return lignes


def resume_markdown(lignes: list[dict]) -> str:
    casses = [ligne for ligne in lignes if not ligne["conforme"]]
    justes = [ligne for ligne in lignes if ligne["attendu"] == "passe"]
    changees = [ligne for ligne in lignes if ligne.get("raison_changee")]
    out = [f"### Robustesse Cucumber : {len(casses)} scénario(s) cassé(s) sur {len(lignes)}",
           "",
           f"Scénarios justes qui passent encore : {sum(1 for ligne in justes if ligne['conforme'])}/{len(justes)}."]
    if any("avant" in ligne for ligne in lignes):
        out.append(f"Pièges qui échouent encore, mais sur une autre étape qu'avant (raison changée) : {len(changees)}.")
    out += ["",
            "| Scénario | Attendu | Avant | Obtenu | Conforme | Étape en échec (avant → maintenant) |",
            "|---|---|---|---|---|---|"]
    for ligne in lignes:
        conforme = "oui" if ligne["conforme"] else "**non**"
        if ligne.get("raison_changee"):
            conforme = "oui, **raison changée**"
        etapes = ligne["etape"]
        if ligne.get("etape_avant") != ligne["etape"] and "avant" in ligne:
            etapes = f"{ligne['etape_avant'] or '—'} → {ligne['etape'] or '—'}"
        out.append(f"| {ligne['id']} | {ligne['attendu']} | {ligne.get('avant', '')} | {ligne['obtenu']} | "
                   f"{conforme} | {etapes.replace('|', '/')} |")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    args, resume, sortie_json, reference = [], None, None, None
    i = 1
    while i < len(argv):
        if argv[i] == "--reference":
            reference, i = argv[i + 1], i + 2
        elif argv[i] == "--resume":
            resume, i = argv[i + 1], i + 2
        elif argv[i] == "--json":
            sortie_json, i = argv[i + 1], i + 2
        else:
            args.append(argv[i])
            i += 1
    dossier = Path(args[0]) if args else RACINE / "target" / "surefire-reports"
    lignes = comparer(lire_rapports(dossier), lire_rapports(Path(reference)) if reference else None)
    texte = resume_markdown(lignes)
    print(texte)
    if resume:
        with open(resume, "a", encoding="utf-8") as f:
            f.write(texte)
    if sortie_json:
        casses = [ligne["id"] for ligne in lignes if not ligne["conforme"]]
        changees = [ligne["id"] for ligne in lignes if ligne.get("raison_changee")]
        Path(sortie_json).write_text(json.dumps({"scenarios": len(lignes), "casses": len(casses),
                                                 "liste_casses": casses, "raison_changee": changees,
                                                 "detail": lignes},
                                                ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 1 if any(not ligne["conforme"] for ligne in lignes) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
