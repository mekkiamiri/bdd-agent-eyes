"""Faux agent pour les tests de gherkin-eyes : aucun modèle, aucun navigateur.

Lit l'invite sur stdin, imite la sortie JSON de la CLI d'agent, et écrit une petite image dans le dossier
de captures lu dans la configuration MCP (--mcp-config). Règle : « refus » si le scénario contient
« Ajouter" » seul, « echec » s'il contient « Tournevis », « passe » sinon. Argument « illisible » :
texte sans verdict. Aucune donnée produite ici n'est une mesure.
"""

import base64
import json
import sys
from pathlib import Path

PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg==")

args = sys.argv[1:]
invite = sys.stdin.read()
if "--mcp-config" in args:
    mcp = json.loads(Path(args[args.index("--mcp-config") + 1]).read_text(encoding="utf-8"))
    a = mcp["mcpServers"]["playwright"]["args"]
    (Path(a[a.index("--output-dir") + 1]) / "page-1.png").write_bytes(PNG)
if "navigateur-absent" in args:
    print(json.dumps({"result": '{"verdict": "erreur", "etape": null, "explication": "CONNECT_TIMEOUT"}'}))
    sys.exit(0)
if "presque-json" in args:
    print(json.dumps({"result": '{"verdict": "refus", "etape": 1, "explication": "l\\\'étape « je clique sur "Ajouter" »", "preuve": "trois boutons"}'}))
    sys.exit(0)
if "illisible" in args:
    print("Je n'ai pas compris.")
    sys.exit(0)
verdict = "refus" if 'clique sur "Ajouter"' in invite else "echec" if "Tournevis" in invite else "passe"
reponse = {"verdict": verdict, "etape": 1 if verdict != "passe" else None, "explication": "faux agent",
           "preuve": "aucune"}
print(json.dumps({"type": "result", "result": "Voici :\n" + json.dumps(reponse), "total_cost_usd": 0.01}))
