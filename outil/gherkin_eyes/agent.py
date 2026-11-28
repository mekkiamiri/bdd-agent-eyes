"""Fait jouer un scénario par un agent qui pilote un navigateur via Playwright MCP, et lit son verdict."""

from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

VERSION_MCP = "0.0.85"
MODELE_DEFAUT = "claude-sonnet-5-5"
COMMANDE_DEFAUT = ("claude -p --output-format json --setting-sources project --model {modele} "
                   "--strict-mcp-config --mcp-config {mcp} --allowedTools mcp__playwright")
VERDICTS = ("passe", "echec", "refus")
VUES = ("les-deux", "arbre", "capture")

CONSIGNE = """Tu es testeur. Tu joues le scénario Gherkin ci-dessous sur l'application ouverte dans le navigateur,
comme le ferait une personne qui ne connaît pas le code.

Règles :
1. Joue les étapes dans l'ordre. Avant chaque action, regarde l'écran (capture et arbre d'accessibilité).
2. N'agis que sur ce qui est visible et utilisable par une personne : pas de script, pas de modification
   du DOM, pas de clic forcé sur un élément désactivé.
3. Si une étape peut désigner plusieurs éléments, ou si un résultat attendu n'est pas observable à l'écran,
   ne devine pas : arrête-toi et réponds `refus`, en disant ce qui manque au scénario.
4. Si l'application ne fait pas ce que dit le scénario, réponds `echec` et décris ce que tu vois à la place.
5. Réponds `passe` seulement si tu as vu à l'écran chaque résultat attendu.
6. Juste avant de répondre, prends une capture de l'écran (browser_take_screenshot, sans nom de fichier) :
   elle sert de preuve dans le rapport.
7. Si les outils du navigateur ne répondent pas (serveur absent, délai dépassé), ne juge pas le scénario :
   réponds `erreur` et dis ce qui n'a pas marché.

Réponds uniquement par ce JSON :
{"verdict": "passe|echec|refus|erreur", "etape": <numéro de l'étape qui bloque ou null>,
 "explication": "<une ou deux phrases>", "preuve": "<ce que tu as vu à l'écran>"}"""


def invite(gherkin: str, url: str) -> str:
    return f"{CONSIGNE}\n\nApplication : {url}\n\nScénario :\n```gherkin\n{gherkin}```\n"


def config_mcp(vue: str, dossier_captures: Path, sans_fenetre: bool, fichier_local: bool) -> dict:
    """Configuration du serveur Playwright MCP pour un passage (navigateur neuf, captures dans le dossier)."""
    if vue not in VUES:
        raise ValueError(f"vue inconnue : {vue} (choix : {', '.join(VUES)})")
    args = [f"@playwright/mcp@{VERSION_MCP}", "--isolated", "--output-dir", str(dossier_captures)]
    if fichier_local:
        args.append("--allow-unrestricted-file-access")
    args += {"arbre": ["--image-responses", "omit"],
             "capture": ["--caps", "vision", "--snapshot-mode", "none"],
             "les-deux": ["--caps", "vision"]}[vue]
    args += ["--browser", "webkit", "--headless"] if sans_fenetre else ["--browser", "chrome"]
    return {"mcpServers": {"playwright": {"command": "npx", "args": args}}}


def lire_reponse(sortie: str) -> tuple[dict | None, float]:
    """Retourne (objet verdict de premier niveau, coût en USD si l'outil le donne).

    Règles (un faux « passe » est le pire défaut possible) :
    - seuls les objets JSON de premier niveau comptent (un « verdict » imbriqué ou cité est ignoré) ;
    - s'il y a plusieurs objets verdict de premier niveau qui se contredisent, c'est une erreur ;
    - la lecture tolérante (JSON presque valide) n'accepte jamais « passe ».
    """
    texte, cout = sortie, 0.0
    try:
        enveloppe = json.loads(sortie)
        if isinstance(enveloppe, dict) and "result" in enveloppe:
            if enveloppe.get("is_error"):
                return None, float(enveloppe.get("total_cost_usd") or 0)
            cout = float(enveloppe.get("total_cost_usd") or 0)
            if isinstance(enveloppe["result"], dict):
                return (enveloppe["result"] if "verdict" in enveloppe["result"] else None), cout
            texte = str(enveloppe["result"])
        elif isinstance(enveloppe, dict) and "verdict" in enveloppe:
            return enveloppe, cout
    except (json.JSONDecodeError, ValueError, TypeError):
        pass
    trouve = _verdict_premier_niveau(texte)
    if trouve is None and ("\\'" in texte or '\\"' in texte):
        # Échappements en trop (\' ou \") parfois écrits par le modèle : on les retire et on relit.
        trouve = _verdict_premier_niveau(texte.replace("\\'", "'").replace('\\"', '"'))
    if trouve is None:
        trouve = _lecture_tolerante(texte)
    return (None if trouve == "contradiction" else trouve), cout


def _verdict_premier_niveau(texte: str) -> dict | str | None:
    decodeur, trouves, i = json.JSONDecoder(), [], 0
    while i < len(texte):
        if texte[i] != "{":
            i += 1
            continue
        try:
            objet, fin = decodeur.raw_decode(texte, i)
        except json.JSONDecodeError:
            i += 1
            continue
        if isinstance(objet, dict) and "verdict" in objet:
            trouves.append(objet)
        i = fin  # on saute l'objet entier : ses objets imbriqués ne comptent pas
    if not trouves:
        return None
    if len({str(o.get("verdict")) for o in trouves}) > 1:
        return "contradiction"
    return trouves[-1]


def _lecture_tolerante(texte: str) -> dict | None:
    """Dernier recours : objet presque JSON (guillemets non échappés dans une phrase), lu champ par champ dans
    l'ordre de la consigne. Jamais pour « passe » : un passe illisible est une erreur, relancée."""
    texte = texte.replace("\\'", "'")
    v = list(re.finditer(r'\{\s*"verdict"\s*:\s*"(echec|refus|erreur)"', texte))
    if not v or re.search(r'"verdict"\s*:\s*"passe"', texte):
        return None
    reste = texte[v[-1].start():]
    etape = re.search(r'"etape"\s*:\s*(\d+|null)', reste)
    expl = re.search(r'"explication"\s*:\s*"(.*?)"\s*,\s*"preuve"', reste, re.S)
    preuve = re.search(r'"preuve"\s*:\s*"(.*)"\s*}', reste, re.S)
    return {"verdict": v[-1].group(1),
            "etape": int(etape.group(1)) if etape and etape.group(1) != "null" else None,
            "explication": expl.group(1).replace('\\"', '"') if expl else "",
            "preuve": preuve.group(1).replace('\\"', '"') if preuve else "",
            "lecture": "tolerante"}


def derniere_capture(dossier: Path) -> Path | None:
    images = [p for p in dossier.glob("*") if p.suffix.lower() in (".png", ".jpeg", ".jpg", ".webp")]
    return max(images, key=lambda p: (p.stat().st_mtime, p.name)) if images else None


def _executer(cmd: list[str], entree: str, delai: float, cwd: Path) -> tuple[str, int | str, str]:
    """Lance la commande dans son propre groupe de processus : au délai dépassé, on tue tout le groupe
    (CLI d'agent, npx, serveur Playwright MCP, navigateur), pas seulement le premier processus."""
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding="utf-8", errors="replace", cwd=cwd,
                                start_new_session=(os.name == "posix"))
    except OSError as e:
        return "", "commande impossible à lancer", f"{cmd[0]} : {e}"
    try:
        sortie, err = proc.communicate(entree, timeout=delai)
        return sortie, proc.returncode, err
    except subprocess.TimeoutExpired:
        try:
            if os.name == "posix":
                os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()
        except OSError:
            pass
        proc.communicate()
        return "", "délai dépassé", ""


def jouer(gherkin: str, url: str, dossier: Path, *, vue: str = "les-deux", sans_fenetre: bool = False,
          modele: str = MODELE_DEFAUT, commande: str = COMMANDE_DEFAUT, delai: float = 600,
          racines: list[Path] | None = None) -> dict:
    """Joue un scénario dans un navigateur neuf. Retourne verdict, explication, preuve, durée, coût, capture."""
    if dossier.exists():
        shutil.rmtree(dossier)  # jamais la capture d'une série précédente comme preuve
    captures = dossier / "captures"
    captures.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="gherkin-eyes-") as tmp:
        mcp = Path(tmp) / "mcp.json"  # hors du dossier de sortie : il contient des chemins absolus
        mcp.write_text(json.dumps(config_mcp(vue, captures.resolve(), sans_fenetre, url.startswith("file:"))),
                       encoding="utf-8")
        cmd = [m.replace("{mcp}", str(mcp)).replace("{modele}", modele) for m in shlex.split(commande)]
        debut = time.monotonic()
        sortie, code, err = _executer(cmd, invite(gherkin, url), delai, dossier)
        duree = round(time.monotonic() - debut, 2)
    (dossier / "sortie-agent.txt").write_text(anonymiser(sortie, (racines or []) + [dossier]), encoding="utf-8")
    verdict, cout = lire_reponse(sortie)
    capture = derniere_capture(captures)
    ligne = {"duree_s": duree, "cout_usd": round(cout, 4), "capture": str(capture) if capture else None}
    if code == 0 and verdict and verdict.get("verdict") == "erreur":
        ligne["erreur"] = "navigateur indisponible selon l'agent : " + str(verdict.get("explication", ""))[:300]
        return ligne
    if code != 0 or verdict is None or verdict.get("verdict") not in VERDICTS:
        ligne["erreur"] = f"code {code} ; sortie : {(sortie or err)[-300:]!r}"
        return ligne
    etape = verdict.get("etape")
    ligne.update(verdict=verdict["verdict"], etape=etape if isinstance(etape, int) else None,
                 explication=str(verdict.get("explication", "")), preuve=str(verdict.get("preuve", "")))
    if verdict.get("lecture"):
        ligne["lecture"] = verdict["lecture"]
    return ligne


def anonymiser(texte: str, racines: list[Path]) -> str:
    """Retire des sorties les chemins locaux (dossiers donnés, dossier personnel, fichiers temporaires)."""
    for r in sorted({str(x.resolve()) for x in racines}, key=len, reverse=True):
        if len(Path(r).parts) < 3:  # jamais « / » ni « /tmp » : on effacerait les « // » des URL
            continue
        texte = texte.replace(Path(r).as_uri() + "/", "").replace(r + "/", "")
    texte = re.sub(r"/(?:private/)?var/folders/[^\s\"'<]+", "<fichier temporaire>", texte)
    texte = re.sub(r"[A-Za-z]:\\{1,2}Users\\{1,2}[^\\\s\"'<]+", "~", texte)
    return re.sub(r"/(?:Users|home)/[^/\s\"'<]+", "~", texte)
