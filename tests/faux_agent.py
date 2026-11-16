"""Faux agent pour tester agent/lancer.py sans modèle : lit l'invite sur l'entrée standard.

Il imite la sortie de `claude -p --output-format json` et répond « refus » si l'invite contient
« je valide », « passe » sinon. Avec l'argument « illisible », il répond du texte sans verdict.
Aucune donnée produite ici n'est une mesure.
"""

import json
import sys

invite = sys.stdin.read()
if "illisible" in sys.argv[1:]:
    print("Je n'ai pas compris.")
    sys.exit(0)
verdict = "refus" if "je valide" in invite else "passe"
reponse = {"verdict": verdict, "etape": None, "explication": "faux agent", "preuve": "aucune"}
print(json.dumps({"type": "result", "result": "Voici :\n" + json.dumps(reponse), "total_cost_usd": 0.0}))
