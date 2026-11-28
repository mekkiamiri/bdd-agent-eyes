#!/usr/bin/env python3
"""Juge à l'aveugle : les verdicts de gherkin-eyes correspondent-ils à l'écran ? Grille : revue/GRILLE-JUGE.md.

  python3 revue/juge_aveugle.py preparer outil/exemple /tmp/juge     # tire 10 passages, les anonymise (P01…P10)
  python3 revue/juge_aveugle.py juger /tmp/juge                      # un juge neuf par passage (appel payant)
  python3 revue/juge_aveugle.py comparer /tmp/juge revue/juge-aveugle.json   # accord juge / agent

Le juge ne reçoit que le scénario (sans tags ni pièges) et la capture de l'écran final ; jamais le verdict,
l'explication de l'agent, ni le nom du fichier .feature. La clé (P01 → passage) reste dans cles.json,
que le juge ne voit pas : chaque juge travaille dans un dossier qui ne contient que son passage.
"""

from __future__ import annotations

import json
import random
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

GRAINE = 2026
MODELE_JUGE = "claude-opus-5-5"
COMMANDE = ["claude", "-p", "--output-format", "json", "--setting-sources", "project", "--strict-mcp-config",
            "--model", MODELE_JUGE, "--allowedTools", "Read"]

ETAPE_1 = """Tu es juge. On te donne un scénario Gherkin et la capture de l'écran final d'une application,
prise par quelqu'un qui a joué ce scénario. Tu ne sais pas ce qu'il a conclu. Regarde l'image {image}
(lis-la avec l'outil Read) et applique cette grille.

Pour chaque étape « Alors » ou « Et » qui décrit un résultat attendu : ce résultat est-il visible sur la capture
(oui, non, illisible) ?
Puis un verdict :
- passe : chaque résultat attendu est visible sur la capture ;
- echec : la capture montre un état qui contredit le scénario (autre texte, autre valeur, bouton grisé qu'il fallait utiliser…) ;
- refus : la capture montre que le scénario est ambigu (une étape peut désigner plusieurs éléments visibles)
  ou qu'un résultat attendu ne peut pas s'observer à l'écran ;
- indetermine : l'écran final ne permet pas de trancher.

Scénario :
```gherkin
{gherkin}```

Réponds uniquement par ce JSON :
{{"resultats": [{{"etape": "<texte>", "visible": "oui|non|illisible"}}], "verdict": "passe|echec|refus|indetermine",
 "justification": "<deux phrases au plus>"}}"""

ETAPE_2 = """Tu es juge. On te donne un scénario Gherkin, la capture de l'écran final d'une application (image {image},
lis-la avec l'outil Read), et ce qu'une personne qui a joué le scénario dit avoir vu à l'écran.
Ce qu'elle a vu est-il conforme à la capture ?
- oui : tout ce qui est visible sur la capture est conforme à ce qu'elle dit ;
- partiellement : au moins une de ses affirmations est contredite par la capture ;
- non : elle décrit un autre écran.
Ses affirmations sur des écrans antérieurs, invisibles sur la capture finale, ne comptent pas comme contredites.

Scénario :
```gherkin
{gherkin}```

Ce qu'elle dit avoir vu : « {preuve} »

Réponds uniquement par ce JSON :
{{"preuve_conforme": "oui|partiellement|non", "ecarts": "<ce qui est contredit, ou vide>"}}"""


def preparer(source: Path, travail: Path) -> None:
    donnees = json.loads((source / "resultats.json").read_text(encoding="utf-8"))
    valides = [p for p in donnees["passages"] if p.get("verdict") and p.get("capture")]
    par_attendu = {k: [p for p in valides if p.get("attendu") == k] for k in ("passe", "echec", "refus")}
    hasard = random.Random(GRAINE)
    tirage = par_attendu["echec"][:3] + par_attendu["refus"][:3] + hasard.sample(par_attendu["passe"], 4)
    hasard.shuffle(tirage)
    travail.mkdir(parents=True, exist_ok=True)
    cles = {}
    for i, p in enumerate(tirage, 1):
        code = f"P{i:02d}"
        d = travail / code
        d.mkdir(exist_ok=True)
        shutil.copy(source / p["capture"], d / "ecran.png")
        (d / "scenario.feature").write_text(p["gherkin"], encoding="utf-8")
        (d / "preuve.txt").write_text(p.get("preuve", ""), encoding="utf-8")
        cles[code] = {k: p.get(k) for k in ("id", "passage", "verdict", "attendu", "capture")}
    (travail / "cles.json").write_text(json.dumps(cles, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(cles)} passages préparés dans {travail}")


def appeler(invite: str, dossier: Path) -> dict:
    fini = subprocess.run(COMMANDE, input=invite, capture_output=True, text=True, cwd=dossier, timeout=600)
    enveloppe = json.loads(fini.stdout)
    texte = str(enveloppe.get("result", ""))
    debut, fin = texte.find("{"), texte.rfind("}")
    reponse = json.loads(texte[debut:fin + 1])
    reponse["cout_usd"] = float(enveloppe.get("total_cost_usd") or 0)
    return reponse


def juger(travail: Path) -> None:
    for d in sorted(p for p in travail.iterdir() if p.is_dir()):
        if (d / "juge.json").exists():
            continue
        # Dossier isolé : seulement l'image et le scénario (la preuve n'est donnée qu'à l'étape 2).
        isole = d / "isole"
        isole.mkdir(exist_ok=True)
        shutil.copy(d / "ecran.png", isole / "ecran.png")
        image = str((isole / "ecran.png").resolve())
        gherkin = (d / "scenario.feature").read_text(encoding="utf-8")
        e1 = appeler(ETAPE_1.format(image=image, gherkin=gherkin), isole)
        e2 = appeler(ETAPE_2.format(image=image, gherkin=gherkin,
                                    preuve=(d / "preuve.txt").read_text(encoding="utf-8")), isole)
        (d / "juge.json").write_text(json.dumps({"etape1": e1, "etape2": e2}, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
        print(f"{d.name} · juge : {e1.get('verdict')} · preuve : {e2.get('preuve_conforme')}")


def comparer(travail: Path, sortie: Path) -> None:
    cles = json.loads((travail / "cles.json").read_text(encoding="utf-8"))
    lignes = []
    for code, cle in sorted(cles.items()):
        j = json.loads((travail / code / "juge.json").read_text(encoding="utf-8"))
        v = j["etape1"]["verdict"]
        accord = "indetermine" if v == "indetermine" else ("accord" if v == cle["verdict"] else "desaccord")
        lignes.append(dict(code=code, id=cle["id"], agent=cle["verdict"], attendu=cle["attendu"], juge=v,
                           accord=accord, justification=j["etape1"].get("justification", ""),
                           preuve_conforme=j["etape2"].get("preuve_conforme"), ecarts=j["etape2"].get("ecarts", ""),
                           cout_usd=round(j["etape1"]["cout_usd"] + j["etape2"]["cout_usd"], 4)))
    bilan = {"passages": len(lignes), **Counter(x["accord"] for x in lignes),
             "preuve": dict(Counter(x["preuve_conforme"] for x in lignes)),
             "cout_juge_usd": round(sum(x["cout_usd"] for x in lignes), 2), "modele_juge": MODELE_JUGE}
    sortie.write_text(json.dumps({"bilan": bilan, "passages": lignes}, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    print(json.dumps(bilan, ensure_ascii=False))
    for x in lignes:
        print(f"{x['code']} {x['id']} · agent {x['agent']} · juge {x['juge']} · {x['accord']} · preuve {x['preuve_conforme']}")


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("preparer", "juger", "comparer"):
        sys.exit(__doc__)
    {"preparer": lambda: preparer(Path(sys.argv[2]), Path(sys.argv[3])),
     "juger": lambda: juger(Path(sys.argv[2])),
     "comparer": lambda: comparer(Path(sys.argv[2]), Path(sys.argv[3]))}[sys.argv[1]]()
