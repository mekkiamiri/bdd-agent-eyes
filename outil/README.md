# gherkin-eyes

**Un agent qui regarde l'écran joue vos scénarios Gherkin, sans step definitions, et rend un verdict expliqué :
`passe`, `échec`, ou `refus` quand le scénario est ambigu.** Sortie : un rapport HTML (verdict, explication,
capture de l'écran final) et un fichier JUnit XML que votre CI sait lire.

À quoi ça sert : garder Cucumber en CI, et lancer `gherkin-eyes` là où les step definitions ne suivent pas :
après une refonte d'écran (savoir si l'appli marche pendant qu'on répare la colle), sur un écran qui n'a pas encore
de colle, ou pour relire des scénarios neufs (il refuse ceux qu'on ne peut pas jouer sans deviner).

## Trois commandes

```sh
pipx install "git+https://github.com/mekkiamiri/bdd-agent-eyes#subdirectory=outil"   # ou : pip install ./outil
gherkin-eyes features/ --url http://localhost:8080                                   # Chrome avec fenêtre
gherkin-eyes features/ --url docs/app/index.html --sans-fenetre -j 4                 # WebKit sans fenêtre, 4 en parallèle
```

Sans installation, depuis ce dépôt : `PYTHONPATH=outil python3 -m gherkin_eyes features/ --url docs/app/index.html --sans-fenetre`.

Prérequis : Python 3.10+, Node.js (pour `npx @playwright/mcp`), et une CLI d'agent qui lit une invite sur son
entrée standard. Par défaut : `claude -p` avec le modèle `claude-sonnet-5-5` (option `--modele`) ; toute autre
commande se branche avec `--commande` (`{mcp}` et `{modele}` y sont remplacés). Chaque passage coûte des jetons :
voir le coût dans le rapport.

## Sortie réelle (exemple du dépôt, 28/11/2026)

`gherkin-eyes features/ --url docs/app/index.html --sans-fenetre -j 4` sur les 17 scénarios de l'appli de démo
(11 justes, 3 faux, 3 ambigus, étiquetés `@attendu:…`) :

```
  panier.feature:Ajouter un produit épuisé · passage 1 · echec · 31.76 s
  panier.feature:Ajouter au panier · passage 1 · refus · 32.96 s
  panier.feature:Un code inconnu retire la remise · passage 1 · passe · 40.29 s
17 passages : 11 passe, 3 échec, 3 refus, 0 erreur · 473.1 s · 1.98 $ · conformes à l'attendu : 17/17
rapport : gherkin-eyes-rapport/rapport.html · JUnit : gherkin-eyes-rapport/junit.xml
```

Durée réelle de la série : 2 min 24 s avec 4 passages en parallèle (473 s cumulés). Fichiers complets :
[`exemple/rapport.html`](exemple/rapport.html), [`exemple/junit.xml`](exemple/junit.xml),
[`exemple/resultats.json`](exemple/resultats.json), captures dans `exemple/passages/`.
Ce qu'il répond sur le produit épuisé (mot pour mot) : « Le bouton « Ajouter » de « Tournevis » est désactivé et le
produit est marqué « Épuisé ». Je n'ai donc pas pu l'ajouter au panier, et le panier reste à 0 article au lieu de 1.
Je n'ai pas forcé le clic sur le bouton désactivé. »

## Ce qu'il fait

1. Lit vos `.feature` (français ou anglais : Contexte/Background, Plan du scénario/Scenario Outline développé,
   tableaux, doc strings, filtre `--tags` façon Cucumber). Les tags, descriptions et commentaires ne sont **jamais**
   envoyés à l'agent : ils peuvent contenir la réponse.
2. Pour chaque scénario, ouvre un navigateur neuf piloté par [Playwright MCP](https://github.com/microsoft/playwright-mcp)
   (`@playwright/mcp` 0.0.85) et envoie la consigne et le scénario à l'agent. Consigne : regarder avant d'agir,
   ne rien forcer (pas de script, pas de clic sur un bouton grisé), refuser plutôt que deviner, ne dire `passe` que
   si chaque résultat attendu est vu à l'écran, capturer l'écran final.
3. Lit le verdict JSON, relance les passages où le navigateur ou le modèle n'a pas répondu (`--relances`, défaut 2),
   et écrit `rapport.html`, `junit.xml` et `resultats.json` dans `--sortie` (défaut `gherkin-eyes-rapport/`).

| Option | Rôle |
|---|---|
| `--url` | `http://…`, `file://…` ou chemin d'un fichier HTML |
| `--sans-fenetre` | WebKit de Playwright en mode headless (sinon Chrome avec fenêtre) |
| `--vue arbre\|capture\|les-deux` | ce que voit l'agent : arbre d'accessibilité, capture d'écran, ou les deux (défaut) |
| `--passages N`, `-j N` | passages par scénario, passages en parallèle |
| `--tags`, `--scenario` | filtres |
| `--attendu @attendu:` | préfixe d'un tag de vérité terrain (`@attendu:passe\|echec\|ambigu`) : le rapport compte les verdicts conformes |

JUnit : un `testsuite` par fichier, un `testcase` par passage ; `échec` → `<failure type="echec">`, `refus` →
`<failure type="refus">` (le scénario est à réécrire), agent sans réponse → `<error>`. Code de sortie : 0 si tout
passe, 1 si un scénario échoue ou est refusé, 2 si l'agent n'a pas pu répondre, 3 si la commande est mal écrite.

## Briques open source

- [Playwright MCP](https://github.com/microsoft/playwright-mcp) (Microsoft, Apache-2.0) : pilote le navigateur, donne
  à l'agent l'arbre d'accessibilité et les captures.
- [Gherkin](https://cucumber.io/docs/gherkin/reference/) (Cucumber) : la syntaxe lue ; `gherkin-eyes` n'en remplace
  pas l'exécution en CI, il la complète.
- Python, bibliothèque standard seulement (aucune dépendance à installer).

## Limites (honnêtes)

- Lent et payant : 14 à 40 s et 6 à 16 centimes par scénario sur l'exemple, contre 1,4 s et aucune facture pour
  Cucumber. Ce n'est pas un remplaçant de la CI.
- Mesuré sur une petite appli de démo écrite par l'auteur, avec un seul modèle (voir `../resultats/LISEZMOI.md`).
- Un verdict n'est pas une preuve : la capture de l'écran final et l'explication sont là pour qu'un humain vérifie.
  Une revue à l'aveugle de 10 passages (juge distinct, grille écrite avant) est décrite dans `../revue/`.

## Tests

```sh
python3 -m unittest discover -s outil/tests -v    # faux agent : aucun modèle, aucun navigateur
```

Licence : Apache-2.0 (voir `../LICENSE`).
