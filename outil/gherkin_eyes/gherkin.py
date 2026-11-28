"""Lecture minimale de fichiers Gherkin (.feature), en français et en anglais, sans dépendance.

On garde ce qu'il faut pour envoyer un scénario à un agent : la fonctionnalité, le Contexte, les étapes
(avec tableaux et doc strings), les tags pour filtrer. Les descriptions libres et les commentaires ne
sont jamais envoyés (ils peuvent contenir la réponse attendue). Les plans de scénario sont développés,
une ligne d'exemples donnant un scénario.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

MOTS = {
    "fonctionnalite": ("Fonctionnalité", "Feature", "Business Need", "Ability"),
    "regle": ("Règle", "Rule"),
    "contexte": ("Contexte", "Background"),
    "plan": ("Plan du scénario", "Plan du Scénario", "Plan du scenario", "Scenario Outline", "Scenario Template"),
    "scenario": ("Scénario", "Scenario", "Exemple", "Example"),
    "exemples": ("Exemples", "Examples", "Scenarios"),
}
ETAPES = (
    # français, d'après gherkin-languages.json (les formes longues d'abord ; l'apostrophe ’ est ramenée à ')
    "Étant donné que ", "Étant donné qu'", "Etant donné que ", "Etant donné qu'", "Étant donnée que ",
    "Étant donnée qu'", "Etant donnée que ", "Etant donnée qu'", "Étant donnés que ", "Étant donnés qu'",
    "Etant donnés que ", "Etant donnés qu'", "Étant données que ", "Étant données qu'", "Etant données que ",
    "Etant données qu'", "Étant donnés ", "Étant données ", "Étant donnée ", "Étant donné ", "Etant donnés ",
    "Etant données ", "Etant donnée ", "Etant donné ", "Sachant que ", "Sachant qu'", "Sachant ", "Soit ",
    "Lorsque ", "Lorsqu'", "Quand ", "Alors ", "Donc ", "Et que ", "Et qu'", "Et ", "Mais que ", "Mais qu'", "Mais ",
    # anglais
    "Given ", "When ", "Then ", "And ", "But ", "* ",
)


@dataclass
class Etape:
    texte: str                      # ligne complète, mot-clé compris : « Quand j'ajoute "Marteau" au panier »
    suite: list[str] = field(default_factory=list)  # lignes de tableau ou de doc string, déjà indentées


@dataclass
class Scenario:
    fichier: str
    fonctionnalite: str
    mot_fonctionnalite: str
    langue: str
    mot: str
    nom: str
    tags: list[str]
    contexte: list[Etape]
    mot_contexte: str
    etapes: list[Etape]
    ligne: int

    @property
    def ident(self) -> str:
        return f"{Path(self.fichier).name}:{self.nom}"

    def gherkin(self) -> str:
        """Texte envoyé à l'agent : sans tags, sans descriptions, sans commentaires."""
        lignes = [f"# language: {self.langue}", f"{self.mot_fonctionnalite}: {self.fonctionnalite}", ""]
        if self.contexte:
            lignes.append(f"  {self.mot_contexte}:")
            for e in self.contexte:
                lignes += [f"    {e.texte}"] + [f"      {s}" for s in e.suite]
            lignes.append("")
        lignes.append(f"  {self.mot}: {self.nom}")
        for e in self.etapes:
            lignes += [f"    {e.texte}"] + [f"      {s}" for s in e.suite]
        return "\n".join(lignes) + "\n"


def _mot(ligne: str, genre: str) -> str | None:
    for m in MOTS[genre]:
        if ligne.startswith(m + ":") or ligne.startswith(m + " :"):
            return m
    return None


def _est_etape(ligne: str) -> bool:
    return ligne.replace("’", "'").startswith(ETAPES)


class ErreurGherkin(ValueError):
    pass


def _cellules(ligne: str) -> list[str]:
    return [c.strip() for c in ligne.strip().strip("|").split("|")]


def lire(fichier: Path) -> list[Scenario]:
    """Lit un fichier .feature et retourne ses scénarios (plans de scénario développés)."""
    texte = fichier.read_text(encoding="utf-8")
    langue, fonctionnalite, mot_f = "en", "", "Feature"
    tags_f: list[str] = []
    tags_attente: list[str] = []
    contexte_f: list[Etape] = []
    contexte_r: list[Etape] = []
    mot_ctx = "Background"
    sortie: list[Scenario] = []
    courant: list[Etape] | None = None     # liste d'étapes en cours de remplissage
    scen: dict | None = None               # scénario ou plan en cours
    exemples: dict | None = None           # bloc Exemples en cours
    dans_regle = False
    tags_r: list[str] = []
    docstring: str | None = None
    marge_doc, ligne_doc = 0, 0
    langue_vue = False

    def fermer_scenario() -> None:
        nonlocal scen, exemples
        if scen is None:
            return
        base = dict(fichier=str(fichier), fonctionnalite=fonctionnalite, mot_fonctionnalite=mot_f, langue=langue,
                    contexte=contexte_f + contexte_r, mot_contexte=mot_ctx)
        if not scen["plan"]:
            sortie.append(Scenario(mot=scen["mot"], nom=scen["nom"], tags=tags_f + tags_r + scen["tags"],
                                   etapes=scen["etapes"], ligne=scen["ligne"], **base))
        else:
            mot_simple = "Scénario" if langue == "fr" else "Scenario"
            for bloc in scen["exemples"]:
                if not bloc["lignes"]:
                    continue
                entete, *rangs = bloc["lignes"]
                for n, rang in enumerate(rangs, 1):
                    if len(rang) != len(entete):
                        raise ErreurGherkin(f"{fichier}:{scen['ligne']} : une ligne d'exemples n'a pas "
                                            f"{len(entete)} cellules")
                    valeurs = dict(zip(entete, rang))

                    def remplacer(s: str) -> str:
                        return re.sub(r"<([^<>]+)>", lambda m: valeurs.get(m.group(1), m.group(0)), s)

                    etapes = [Etape(remplacer(e.texte), [remplacer(x) for x in e.suite]) for e in scen["etapes"]]
                    nom = f"{remplacer(scen['nom'])} #{n}" if len(rangs) > 1 or len(scen["exemples"]) > 1 else remplacer(scen["nom"])
                    sortie.append(Scenario(mot=mot_simple, nom=nom, tags=tags_f + tags_r + scen["tags"] + bloc["tags"],
                                           etapes=etapes, ligne=scen["ligne"], **base))
        scen, exemples = None, None

    for num, brute in enumerate(texte.splitlines(), 1):
        ligne = brute.strip()
        if docstring is not None:
            if courant:  # on garde l'indentation relative au délimiteur ouvrant
                courant[-1].suite.append(ligne if ligne.startswith(docstring) else brute[marge_doc:].rstrip()
                                         if brute[:marge_doc].strip() == "" else ligne)
            if ligne.startswith(docstring):
                docstring = None
            continue
        if not ligne:
            continue
        if ligne.startswith("#"):
            m = re.match(r"#\s*language\s*:\s*([\w-]+)", ligne)
            if m and not fonctionnalite:
                langue, langue_vue = m.group(1), True
            continue
        if ligne.startswith("@"):
            tags_attente += [t for t in ligne.split() if t.startswith("@")]
            continue
        if m := _mot(ligne, "fonctionnalite"):
            mot_f, fonctionnalite = m, ligne.split(":", 1)[1].strip()
            if not langue_vue:  # pas d'en-tête « # language: » : on déduit la langue du mot-clé
                langue = "fr" if m == "Fonctionnalité" else "en"
            tags_f, tags_attente, courant = tags_attente, [], None
            continue
        if _mot(ligne, "regle"):
            fermer_scenario()
            dans_regle, contexte_r, courant, tags_r, tags_attente = True, [], None, tags_attente, []
            continue
        if m := _mot(ligne, "contexte"):
            fermer_scenario()
            mot_ctx = m
            courant = contexte_r if dans_regle else contexte_f
            tags_attente = []
            continue
        if (m := _mot(ligne, "plan")) or (m := _mot(ligne, "scenario")):
            fermer_scenario()
            scen = dict(mot=m, nom=ligne.split(":", 1)[1].strip(), tags=tags_attente, etapes=[], ligne=num,
                        plan=m in MOTS["plan"], exemples=[])
            tags_attente, courant = [], scen["etapes"]
            continue
        if _mot(ligne, "exemples"):
            if scen is not None:
                exemples = dict(tags=tags_attente, lignes=[])
                scen["exemples"].append(exemples)
            tags_attente, courant = [], None
            continue
        if ligne.startswith("|"):
            if exemples is not None and courant is None:
                exemples["lignes"].append(_cellules(ligne))
            elif courant:
                courant[-1].suite.append(ligne)
            continue
        if ligne.startswith(('"""', "```")):
            docstring, marge_doc, ligne_doc = ligne[:3], len(brute) - len(brute.lstrip()), num
            if courant:
                courant[-1].suite.append(ligne)
            continue
        if courant is not None and _est_etape(ligne):
            courant.append(Etape(ligne))
        elif courant:
            # Après la première étape, une ligne sans mot-clé n'est pas une description : Cucumber la refuse,
            # et l'ignorer ferait disparaître une vérification sans bruit.
            raise ErreurGherkin(f"{fichier}:{num} : ligne sans mot-clé d'étape reconnu : {ligne!r}")
        # sinon : description libre (avant la première étape), jamais envoyée
    if docstring is not None:
        raise ErreurGherkin(f"{fichier}:{ligne_doc} : doc string ouvert jamais fermé")
    fermer_scenario()
    return sortie


def trouver(chemins: list[Path]) -> list[Path]:
    fichiers: list[Path] = []
    for c in chemins:
        if c.is_dir():
            fichiers += sorted(c.rglob("*.feature"))
        elif c.suffix == ".feature" and c.exists():
            fichiers.append(c)
        else:
            raise FileNotFoundError(f"ni dossier ni fichier .feature : {c}")
    return fichiers


# --- Expressions de tags (sous-ensemble de Cucumber : @tag, not, and, or, parenthèses) ---

def filtre_tags(expression: str | None):
    if not expression:
        return lambda tags: True
    jetons = re.findall(r"\(|\)|[^\s()]+", expression)
    pos = 0

    def voir() -> str | None:
        return jetons[pos] if pos < len(jetons) else None

    def prendre() -> str:
        nonlocal pos
        if pos >= len(jetons):
            raise ValueError(f"expression de tags incomplète : {expression!r}")
        pos += 1
        return jetons[pos - 1]

    def ou():
        g = et()
        while voir() == "or":
            prendre()
            d, gg = et(), g
            g = lambda t, a=gg, b=d: a(t) or b(t)
        return g

    def et():
        g = non()
        while voir() == "and":
            prendre()
            d, gg = non(), g
            g = lambda t, a=gg, b=d: a(t) and b(t)
        return g

    def non():
        if voir() == "not":
            prendre()
            f = non()
            return lambda t: not f(t)
        j = prendre()
        if j == "(":
            f = ou()
            if prendre() != ")":
                raise ValueError(f"parenthèse non fermée : {expression!r}")
            return f
        if not j.startswith("@"):
            raise ValueError(f"tag attendu (@…), reçu {j!r} dans {expression!r}")
        return lambda t: j in t

    f = ou()
    if voir() is not None:
        raise ValueError(f"expression de tags invalide : {expression!r}")
    return lambda tags: f(set(tags))
