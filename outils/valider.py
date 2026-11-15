#!/usr/bin/env python3
"""Validateur des scénarios Gherkin de bdd-agent-eyes (bibliothèque standard seulement).

Usage : python3 outils/valider.py [features/] [docs/app/]

Il vérifie trois choses :
1. la syntaxe : un sous-ensemble de Gherkin en français (# language: fr, Fonctionnalité,
   Contexte, Scénario, Soit/Quand/Alors/Et/Mais, tags, descriptions) ;
2. la vérité terrain : chaque scénario porte un seul tag @attendu:passe|echec|ambigu,
   et les scénarios faux ou ambigus expliquent le piège (« Piège : … ») ;
3. le lien feature → parcours → appli : chaque fonctionnalité vise un parcours de
   docs/app/parcours.json, chaque étape d'un scénario « passe » correspond au vocabulaire,
   chaque libellé cité existe dans le parcours, et chaque libellé du parcours existe dans
   le code de l'appli (index.html ou app.js).

Code de sortie 1 s'il reste des erreurs.
"""

from __future__ import annotations

import html
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

MOTS_ETAPE = ("Étant donné que ", "Étant donné ", "Etant donné ", "Soit ", "Quand ", "Lorsque ",
              "Alors ", "Et ", "Mais ", "* ")
FAMILLE = {"Étant donné que ": "soit", "Étant donné ": "soit", "Etant donné ": "soit", "Soit ": "soit",
           "Quand ": "quand", "Lorsque ": "quand", "Alors ": "alors"}
ATTENDUS = ("passe", "echec", "ambigu")

# Vocabulaire des étapes : le même que les step definitions Java (Etapes.java).
# Chaque paramètre entre guillemets est typé ; le type dit où chercher le libellé dans le parcours.
VOCABULAIRE = [
    (r'je suis sur la page "(?P<ecran>[^"]+)"', "je suis sur la page {string}"),
    (r"je suis connecté", "je suis connecté"),
    (r'je saisis "(?P<libre>[^"]*)" dans le champ "(?P<champ>[^"]+)"', "je saisis {string} dans le champ {string}"),
    (r'je clique sur "(?P<bouton>[^"]+)"', "je clique sur {string}"),
    (r"j'ajoute \"(?P<produit>[^\"]+)\" au panier", "j'ajoute {string} au panier"),
    (r'je coche "(?P<case>[^"]+)"', "je coche {string}"),
    (r'je vois "(?P<texte>[^"]+)"', "je vois {string}"),
    (r'je ne vois pas "(?P<texte>[^"]+)"', "je ne vois pas {string}"),
    (r"le panier contient (?P<nombre>\d+) articles?", "le panier contient {int} article(s)"),
    (r'le total est "(?P<montant>\d+,\d\d €)"', "le total est {string}"),
    (r'le bouton "(?P<bouton>[^"]+)" est désactivé', "le bouton {string} est désactivé"),
]
VOCABULAIRE_RE = [(re.compile("^" + motif + "$"), expr) for motif, expr in VOCABULAIRE]

# type de paramètre -> clés du parcours où le libellé doit exister
OU_CHERCHER = {"champ": ("champs",), "bouton": ("boutons",), "produit": ("produits",),
               "case": ("cases",), "texte": ("textes",)}


@dataclass
class Etape:
    ligne: int
    mot: str
    texte: str


@dataclass
class Scenario:
    ligne: int
    nom: str
    tags: list[str] = field(default_factory=list)
    description: list[str] = field(default_factory=list)
    etapes: list[Etape] = field(default_factory=list)

    @property
    def attendu(self) -> str | None:
        valeurs = [t.split(":", 1)[1] for t in self.tags if t.startswith("@attendu:")]
        return valeurs[0] if len(valeurs) == 1 else None

    @property
    def piege(self) -> str:
        for d in self.description:
            if d.startswith("Piège :"):
                return d[len("Piège :"):].strip()
        return ""


@dataclass
class Fonctionnalite:
    fichier: str
    nom: str = ""
    tags: list[str] = field(default_factory=list)
    description: list[str] = field(default_factory=list)
    contexte: list[Etape] = field(default_factory=list)
    scenarios: list[Scenario] = field(default_factory=list)

    @property
    def parcours(self) -> str | None:
        valeurs = [t.split(":", 1)[1] for t in self.tags if t.startswith("@parcours:")]
        return valeurs[0] if len(valeurs) == 1 else None


class Rapport:
    def __init__(self) -> None:
        self.erreurs: list[str] = []
        self.notes: list[str] = []

    def erreur(self, ou: str, msg: str) -> None:
        self.erreurs.append(f"{ou} : {msg}")

    def note(self, ou: str, msg: str) -> None:
        self.notes.append(f"{ou} : {msg}")


# ---------------------------------------------------------------- 1. syntaxe

def analyser(texte: str, fichier: str, rapport: Rapport) -> Fonctionnalite:
    """Analyse un fichier .feature (sous-ensemble de Gherkin en français)."""
    f = Fonctionnalite(fichier)
    lignes = texte.splitlines()
    premiere = next((l.strip() for l in lignes if l.strip()), "")
    if premiere != "# language: fr":
        rapport.erreur(f"{fichier}:1", "la première ligne doit être « # language: fr »")
    tags: list[str] = []
    bloc = None  # None, "fonctionnalite", "contexte", "scenario"
    courant: Scenario | None = None
    for n, brut in enumerate(lignes, 1):
        ligne = brut.strip()
        ou = f"{fichier}:{n}"
        if not ligne or ligne.startswith("#"):
            continue
        if ligne.startswith("@"):
            for t in ligne.split():
                if not re.fullmatch(r"@[\w:.-]+", t):
                    rapport.erreur(ou, f"tag mal formé « {t} »")
                tags.append(t)
            continue
        if ligne.startswith("Fonctionnalité:"):
            if f.nom:
                rapport.erreur(ou, "une seule Fonctionnalité par fichier")
            f.nom, f.tags, tags, bloc = ligne.split(":", 1)[1].strip(), tags, [], "fonctionnalite"
            if not f.nom:
                rapport.erreur(ou, "Fonctionnalité sans nom")
            continue
        if not f.nom:
            rapport.erreur(ou, "texte avant « Fonctionnalité: »")
            continue
        if ligne == "Contexte:":
            if f.scenarios or f.contexte:
                rapport.erreur(ou, "le Contexte doit précéder les scénarios et être unique")
            if tags:
                rapport.erreur(ou, "pas de tag sur un Contexte")
                tags = []
            bloc, courant = "contexte", None
            continue
        if ligne.startswith(("Scénario:", "Scenario:")):
            nom = ligne.split(":", 1)[1].strip()
            if not nom:
                rapport.erreur(ou, "Scénario sans nom")
            if any(s.nom == nom for s in f.scenarios):
                rapport.erreur(ou, f"nom de scénario en double « {nom} »")
            courant = Scenario(n, nom, tags)
            f.scenarios.append(courant)
            tags, bloc = [], "scenario"
            continue
        if ligne.startswith(("Plan du scénario:", "Exemples:", "Règle:", '"""', "|")):
            rapport.erreur(ou, f"« {ligne.split()[0]} » n'est pas pris en charge en v0")
            continue
        if tags:
            rapport.erreur(ou, "des tags doivent précéder une Fonctionnalité ou un Scénario")
            tags = []
        mot = next((m for m in MOTS_ETAPE if ligne.startswith(m)), None)
        if mot:
            etape = Etape(n, mot, ligne[len(mot):].strip())
            if bloc == "contexte":
                f.contexte.append(etape)
            elif bloc == "scenario" and courant is not None:
                courant.etapes.append(etape)
            else:
                rapport.erreur(ou, "étape hors d'un Contexte ou d'un Scénario")
            continue
        # Texte libre : description de la fonctionnalité ou du scénario (avant les étapes).
        if bloc == "fonctionnalite":
            f.description.append(ligne)
        elif bloc == "scenario" and courant is not None and not courant.etapes:
            courant.description.append(ligne)
        else:
            rapport.erreur(ou, f"ligne non reconnue « {ligne} »")
    if tags:
        rapport.erreur(f"{fichier}:{len(lignes)}", "tags en fin de fichier sans scénario")
    if not f.nom:
        rapport.erreur(f"{fichier}:1", "aucune « Fonctionnalité: »")
    _verifier_structure(f, rapport)
    return f


def _verifier_structure(f: Fonctionnalite, rapport: Rapport) -> None:
    if f.contexte and f.contexte[0].mot in ("Et ", "Mais "):
        rapport.erreur(f"{f.fichier}:{f.contexte[0].ligne}", "le Contexte commence par « Et » ou « Mais »")
    for s in f.scenarios:
        ou = f"{f.fichier}:{s.ligne}"
        if not s.etapes:
            rapport.erreur(ou, f"scénario « {s.nom} » sans étape")
            continue
        if s.etapes[0].mot in ("Et ", "Mais "):
            rapport.erreur(ou, f"scénario « {s.nom} » commence par « Et » ou « Mais »")
        familles = [FAMILLE.get(e.mot) for e in s.etapes if FAMILLE.get(e.mot)]
        if "alors" not in familles:
            rapport.erreur(ou, f"scénario « {s.nom} » sans « Alors » : rien n'est vérifié")
        ordre = {"soit": 0, "quand": 1, "alors": 2}
        rangs = [ordre[x] for x in familles]
        if rangs != sorted(rangs):
            rapport.erreur(ou, f"scénario « {s.nom} » : ordre Soit → Quand → Alors non respecté")
        # 2. vérité terrain
        attendus = [t for t in s.tags if t.startswith("@attendu:")]
        if len(attendus) != 1 or s.attendu not in ATTENDUS:
            rapport.erreur(ou, f"scénario « {s.nom} » : il faut exactement un tag @attendu:passe|echec|ambigu")
        elif s.attendu != "passe" and not s.piege:
            rapport.erreur(ou, f"scénario « {s.nom} » ({s.attendu}) : expliquer le piège par une ligne « Piège : … »")
    if len([t for t in f.tags if t.startswith("@parcours:")]) != 1:
        rapport.erreur(f"{f.fichier}:1", "la Fonctionnalité doit porter exactement un tag @parcours:<id>")


# ------------------------------------------------- 3. lien feature → parcours → appli

def charger_parcours(dossier_app: Path) -> dict:
    return json.loads((dossier_app / "parcours.json").read_text(encoding="utf-8"))["parcours"]


def _motif_texte(texte: str, valeurs: list[str]) -> re.Pattern:
    """« Bonjour {email} » devient une regex où {…} vaut l'une des valeurs du parcours."""
    morceaux = re.split(r"\{[^}]+\}", texte)
    alt = "(?:" + "|".join(re.escape(v) for v in valeurs) + ")" if valeurs else "(?!)"
    return re.compile("^" + alt.join(re.escape(m) for m in morceaux) + "$")


def verifier_parcours_dans_appli(parcours: dict, dossier_app: Path, rapport: Rapport) -> None:
    """Chaque libellé déclaré dans parcours.json doit exister dans le code de l'appli."""
    source = "\n".join(html.unescape((dossier_app / nom).read_text(encoding="utf-8"))
                       for nom in ("index.html", "app.js"))
    for pid, p in parcours.items():
        libelles = [p.get("ecran", "")]
        for cle in ("champs", "boutons", "produits", "cases", "textes", "valeurs"):
            libelles += p.get(cle, [])
        for lib in libelles:
            morceaux = [m for m in re.split(r"\{[^}]+\}", lib) if m.strip()]
            if not lib or not all(m in source for m in morceaux):
                rapport.erreur(f"parcours.json/{pid}", f"« {lib} » introuvable dans index.html ou app.js")
        for dep in p.get("depend_de", []):
            if dep not in parcours:
                rapport.erreur(f"parcours.json/{pid}", f"dépend d'un parcours inconnu « {dep} »")


def _portee(parcours: dict, pid: str) -> dict:
    """Libellés accessibles depuis un parcours : le sien et ceux dont il dépend."""
    vus, a_voir, portee = set(), [pid], {}
    while a_voir:
        courant = a_voir.pop()
        if courant in vus or courant not in parcours:
            continue
        vus.add(courant)
        for cle, val in parcours[courant].items():
            if isinstance(val, list):
                portee.setdefault(cle, []).extend(val)
        a_voir += parcours[courant].get("depend_de", [])
    return portee


def resoudre_etape(texte: str, parcours: dict, pid: str) -> list[str]:
    """Retourne la liste des problèmes de l'étape (liste vide si elle est jouable)."""
    for motif, _ in VOCABULAIRE_RE:
        m = motif.match(texte)
        if not m:
            continue
        problemes = []
        portee = _portee(parcours, pid)
        for type_, valeur in m.groupdict().items():
            if type_ == "ecran":
                ecrans = [p["ecran"] for p in parcours.values()]
                if valeur not in ecrans:
                    problemes.append(f"page inconnue « {valeur} »")
            elif type_ in OU_CHERCHER:
                connus = [x for cle in OU_CHERCHER[type_] for x in portee.get(cle, [])]
                if type_ == "texte":
                    ok = any(_motif_texte(c, portee.get("valeurs", [])).match(valeur) for c in connus)
                else:
                    ok = valeur in connus
                if not ok:
                    problemes.append(f"{type_} « {valeur} » absent du parcours « {pid} »")
        return problemes
    return [f"étape hors vocabulaire « {texte} »"]


def verifier_liens(f: Fonctionnalite, parcours: dict, rapport: Rapport) -> None:
    pid = f.parcours
    if pid is None:
        return
    if pid not in parcours:
        rapport.erreur(f"{f.fichier}:1", f"parcours inconnu « {pid} » (voir docs/app/parcours.json)")
        return
    for e in f.contexte:
        for pb in resoudre_etape(e.texte, parcours, pid):
            rapport.erreur(f"{f.fichier}:{e.ligne}", pb)
    for s in f.scenarios:
        for e in s.etapes:
            for pb in resoudre_etape(e.texte, parcours, pid):
                if s.attendu == "passe":
                    rapport.erreur(f"{f.fichier}:{e.ligne}", pb)
                else:
                    # Attendu : c'est le piège que l'agent doit signaler.
                    rapport.note(f"{f.fichier}:{e.ligne}", f"[{s.attendu}] {pb}")


# ---------------------------------------------------------------- point d'entrée

def valider(dossier_features: Path, dossier_app: Path) -> tuple[list[Fonctionnalite], Rapport]:
    rapport = Rapport()
    parcours = charger_parcours(dossier_app)
    verifier_parcours_dans_appli(parcours, dossier_app, rapport)
    fonctionnalites = []
    fichiers = sorted(dossier_features.glob("*.feature"))
    if not fichiers:
        rapport.erreur(str(dossier_features), "aucun fichier .feature")
    for chemin in fichiers:
        nom = chemin.relative_to(dossier_features.parent).as_posix() if dossier_features.parent in chemin.parents else chemin.name
        f = analyser(chemin.read_text(encoding="utf-8"), nom, rapport)
        verifier_liens(f, parcours, rapport)
        fonctionnalites.append(f)
    return fonctionnalites, rapport


def main(argv: list[str]) -> int:
    features = Path(argv[1]) if len(argv) > 1 else RACINE / "features"
    app = Path(argv[2]) if len(argv) > 2 else RACINE / "docs" / "app"
    fonctionnalites, rapport = valider(features, app)
    total = sum(len(f.scenarios) for f in fonctionnalites)
    par_attendu = {a: sum(1 for f in fonctionnalites for s in f.scenarios if s.attendu == a) for a in ATTENDUS}
    print(f"{len(fonctionnalites)} fonctionnalités, {total} scénarios "
          f"(passe {par_attendu['passe']}, echec {par_attendu['echec']}, ambigu {par_attendu['ambigu']})")
    for n in rapport.notes:
        print("  piège attendu ·", n)
    for e in rapport.erreurs:
        print("  ERREUR ·", e)
    print("OK" if not rapport.erreurs else f"{len(rapport.erreurs)} erreur(s)")
    return 1 if rapport.erreurs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
