"""Écrit les sorties d'une série : resultats.json, junit.xml (lu par les CI), rapport.html (lu par un humain)."""

from __future__ import annotations

import html
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

LIBELLES = {"passe": "passe", "echec": "échec", "refus": "refus", None: "erreur"}


def bilan(passages: list[dict]) -> dict:
    compte = Counter(p.get("verdict") or "erreur" for p in passages)
    attendus = [p for p in passages if p.get("attendu")]
    return {
        "passages": len(passages),
        "passe": compte["passe"], "echec": compte["echec"], "refus": compte["refus"], "erreur": compte["erreur"],
        "avec_attendu": len(attendus),
        "conformes": sum(1 for p in attendus if p.get("verdict") == p["attendu"]),
        "duree_s": round(sum(p.get("duree_s", 0) for p in passages), 1),
        "cout_usd": round(sum(p.get("cout_usd", 0) for p in passages), 4),
    }


def resume(b: dict) -> str:
    texte = (f"{b['passages']} passages : {b['passe']} passe, {b['echec']} échec, {b['refus']} refus, "
             f"{b['erreur']} erreur · {b['duree_s']} s · {b['cout_usd']:.2f} $")
    if b["avec_attendu"]:
        texte += f" · conformes à l'attendu : {b['conformes']}/{b['avec_attendu']}"
    return texte


def ecrire_json(chemin: Path, entete: dict, passages: list[dict]) -> None:
    donnees = dict(entete, bilan=bilan(passages), passages=passages)
    chemin.write_text(json.dumps(donnees, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


_CONTROLE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _xml(texte: str) -> str:
    """Retire les caractères interdits en XML 1.0 (couleurs ANSI, NUL…) : sinon le JUnit est illisible."""
    return _CONTROLE.sub("", texte or "")


def ecrire_junit(chemin: Path, passages: list[dict]) -> None:
    """Un testsuite par fichier .feature, un testcase par passage. échec → failure, refus → failure
    de type « refus » (le scénario doit être réécrit), erreur de l'agent → error."""
    par_fichier: dict[str, list[dict]] = defaultdict(list)
    for p in passages:
        par_fichier[p["fichier"]].append(p)
    total = bilan(passages)
    racine = ET.Element("testsuites", name="gherkin-eyes", tests=str(total["passages"]),
                        failures=str(total["echec"] + total["refus"]), errors=str(total["erreur"]),
                        time=f"{total['duree_s']:.2f}")
    for fichier, liste in par_fichier.items():
        b = bilan(liste)
        suite = ET.SubElement(racine, "testsuite", name=fichier, tests=str(len(liste)),
                              failures=str(b["echec"] + b["refus"]), errors=str(b["erreur"]), skipped="0",
                              time=f"{sum(p.get('duree_s', 0) for p in liste):.2f}")
        for p in liste:
            nom = p["scenario"] + (f" [passage {p['passage']}]" if p.get("passages_total", 1) > 1 else "")
            cas = ET.SubElement(suite, "testcase", classname=fichier.removesuffix(".feature"), name=_xml(nom),
                                time=f"{p.get('duree_s', 0):.2f}")
            verdict = p.get("verdict")
            if verdict == "echec":
                ET.SubElement(cas, "failure", type="echec", message=_xml(p.get("explication", ""))).text = _xml(p.get("preuve", ""))
            elif verdict == "refus":
                ET.SubElement(cas, "failure", type="refus",
                              message=_xml("scénario ambigu : " + p.get("explication", ""))).text = _xml(p.get("preuve", ""))
            elif verdict is None:
                ET.SubElement(cas, "error", type="agent", message=_xml(p.get("erreur", "erreur")))
            sortie = f"{p.get('explication', '')}\n{p.get('preuve', '')}".strip()
            if p.get("capture"):
                sortie += f"\n[[ATTACHMENT|{p['capture']}]]"
            if p.get("lecture"):
                sortie += f"\n(réponse lue en mode tolérant : JSON mal formé, à relire)"
            if sortie:
                ET.SubElement(cas, "system-out").text = _xml(sortie)
    ET.indent(racine)
    chemin.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(racine, encoding="unicode") + "\n",
                      encoding="utf-8")


CSS = """
body{background:#121416;color:#e9e4d8;font:15px/1.5 ui-monospace,Menlo,monospace;margin:0;padding:32px}
h1{font:400 34px Georgia,serif;margin:0 0 4px}h1 em{color:#ffb000;font-style:normal}
.meta{color:#9a958a;margin-bottom:24px}.bilan{display:flex;gap:16px;flex-wrap:wrap;margin:16px 0 28px}
.bilan div{border:1px solid #2c3034;padding:10px 16px;border-radius:6px}.bilan b{font-size:26px;display:block}
table{border-collapse:collapse;width:100%}td,th{border-top:1px solid #2c3034;padding:10px 8px;vertical-align:top;text-align:left}
th{color:#9a958a;font-weight:400}.v{font-weight:600;white-space:nowrap}.passe{color:#7bd389}.echec{color:#ff6b5b}
.refus{color:#ffb000}.erreur{color:#b48ead}.non{color:#ff6b5b}img{max-width:260px;border:1px solid #2c3034;border-radius:4px}
details summary{cursor:pointer;color:#9a958a}pre{white-space:pre-wrap;color:#c8c2b4;margin:6px 0}
.preuve{color:#9a958a;font-size:13px;margin-top:6px}
"""


def ecrire_html(chemin: Path, entete: dict, passages: list[dict]) -> None:
    b = bilan(passages)
    e = html.escape
    cases = [("passe", b["passe"]), ("echec", b["echec"]), ("refus", b["refus"]), ("erreur", b["erreur"])]
    tuiles = "".join(f'<div><b class="{k}">{n}</b>{LIBELLES.get(k, k)}</div>' for k, n in cases)
    if b["avec_attendu"]:
        tuiles += f'<div><b>{b["conformes"]}/{b["avec_attendu"]}</b>conformes à l\'attendu</div>'
    tuiles += f'<div><b>{b["duree_s"]} s</b>durée cumulée</div><div><b>{b["cout_usd"]:.2f} $</b>coût</div>'
    rangs = []
    for p in passages:
        v = p.get("verdict")
        classe = v or "erreur"
        attendu = ""
        if p.get("attendu"):
            ok = v == p["attendu"]
            attendu = f'<br><span class="{"" if ok else "non"}">attendu : {e(LIBELLES[p["attendu"]])}{"" if ok else " ✗"}</span>'
        etape = f" (étape {p['etape']})" if p.get("etape") else ""
        if p.get("lecture"):
            etape += '<br><span class="meta">réponse mal formée, lue en mode tolérant</span>'
        texte = e(p.get("explication") or p.get("erreur", ""))
        preuve = f'<div class="preuve">Vu à l\'écran : {e(p["preuve"])}</div>' if p.get("preuve") else ""
        image = (f'<a href="{e(p["capture"])}"><img src="{e(p["capture"])}" alt="écran final"></a>'
                 if p.get("capture") else '<span class="meta">pas de capture</span>')
        rangs.append(
            f'<tr><td><b>{e(p["scenario"])}</b><br><span class="meta">{e(p["fichier"])} · passage {p["passage"]}'
            f' · {p.get("duree_s", 0)} s</span><details><summary>scénario envoyé</summary><pre>{e(p["gherkin"])}</pre>'
            f'</details></td><td class="v {classe}">{e(LIBELLES.get(v, "erreur"))}{etape}{attendu}</td>'
            f'<td>{texte}{preuve}</td><td>{image}</td></tr>')
    page = f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>gherkin-eyes · rapport</title>
<style>{CSS}</style></head><body>
<h1>gherkin-<em>eyes</em> · rapport</h1>
<div class="meta">{e(entete["date"])} · {e(entete["url"])} · modèle {e(entete["modele"])} · vue {e(entete["vue"])}
 · navigateur {e(entete["navigateur"])}</div>
<div class="bilan">{tuiles}</div>
<table><tr><th>Scénario</th><th>Verdict</th><th>Explication de l'agent</th><th>Écran final</th></tr>
{''.join(rangs)}</table>
<p class="meta">passe : chaque résultat attendu a été vu à l'écran · échec : l'appli ne fait pas ce que dit le scénario ·
refus : le scénario est ambigu ou son résultat n'est pas observable, à réécrire.</p>
</body></html>
"""
    chemin.write_text(page, encoding="utf-8")
