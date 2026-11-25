# bdd-agent-eyes

[![ci](https://github.com/mekkiamiri/bdd-agent-eyes/actions/workflows/ci.yml/badge.svg)](https://github.com/mekkiamiri/bdd-agent-eyes/actions/workflows/ci.yml)

**La promesse du talk : un agent qui regarde l'écran peut-il jouer vos scénarios Gherkin sans step definitions, et sait-il refuser un scénario faux ou ambigu ? On le mesure face à Cucumber + Playwright.**

Talk proposé à Devoxx France 2027 (Tools-in-Action, 30 min) par Mekki Amiri.

- Page de démo (appli jouable + scénario en cours) : https://mekkiamiri.github.io/bdd-agent-eyes/
- Slides : https://mekkiamiri.github.io/bdd-agent-eyes/slides/
- Protocole de comparaison : [PROTOCOLE.md](PROTOCOLE.md)

> **État : premières mesures sur la branche `mesures`** (agent sur l'appli, robustesse quand l'interface change) : voir [resultats/LISEZMOI.md](resultats/LISEZMOI.md).

## Démarrer (une commande)

```sh
python3 outils/valider.py
```

Python 3.10 ou plus, bibliothèque standard seulement. Sortie actuelle :
`4 fonctionnalités, 17 scénarios (passe 11, echec 3, ambigu 3)`, les pièges attendus, puis `OK`.

Autres commandes :

```sh
python3 -m unittest discover -s tests -v     # tests du validateur, du générateur de page et du comparateur
python3 outils/construire_page.py            # régénère docs/scenarios.js après une modification des features
mvn verify                                   # référence Cucumber-JVM + Playwright Java (Java 21, télécharge Chromium)
python3 outils/verifier_pieges.py --lancer   # Cucumber sur les scénarios faux ou ambigus : chacun doit échouer comme étiqueté
python3 agent/lancer.py --config les-deux    # l'agent joue les scénarios (appel payant, voir agent/lancer.py)
python3 outils/comparer.py resultats/*/resultats.json   # tableau des mesures (quand il y aura des résultats)
```

Après le clone, activer le hook pre-push (termes interdits, secrets, tests) :

```sh
git config core.hooksPath .githooks
```

L'appli de démo s'ouvre sans serveur : `docs/app/index.html` dans un navigateur.

## Comment c'est fait

```
features/*.feature ──(tags @parcours, @attendu)──► outils/valider.py ◄── docs/app/parcours.json ◄── docs/app/index.html + app.js
        │                                               (syntaxe + lien feature → parcours → appli)
        ├──► Cucumber-JVM + Playwright Java (src/test/java/…/Etapes.java) ──┐
        └──► agent : capture + arbre d'accessibilité (agent/CONSIGNE.md) ───┴──► resultats/<config>/resultats.json ──► outils/comparer.py
```

| Élément | Rôle |
|---|---|
| `docs/app/` | Appli de démo « La Quincaillerie », HTML/JS sans dépendance : connexion, panier, livraison. Pièges : bouton désactivé (produit épuisé, conditions non cochées, compte bloqué), messages d'erreur, trois boutons « Ajouter », texte « Commande confirmée » présent dans le DOM mais caché. |
| `features/` | 17 scénarios en Gherkin français. Chaque scénario porte sa vérité terrain : `@attendu:passe`, `@attendu:echec` (scénario faux) ou `@attendu:ambigu` (à refuser), et une ligne `Piège :` qui l'explique. |
| `outils/valider.py` | Vérifie la syntaxe, la vérité terrain, que chaque étape d'un scénario juste appartient au vocabulaire et cite des libellés du parcours, et que chaque libellé du parcours existe dans le code de l'appli. |
| `src/test/java/` | Référence Cucumber classique : step definitions écrites à la main, Playwright Java en `file://`. Par défaut, ne joue que les scénarios `@attendu:passe`. |
| `agent/CONSIGNE.md` | La consigne envoyée à l'agent (verdict `passe`, `echec` ou `refus` en JSON). |
| `agent/lancer.py` | Envoie chaque scénario (sans tags ni pièges) à une commande d'agent configurable, par défaut `claude -p` avec le serveur MCP `@playwright/mcp` 0.0.85 (`agent/mcp-arbre.json`, `mcp-capture.json`, `mcp-les-deux.json`), et écrit `resultats/agent-<config>/resultats.json`. Testé avec un faux agent ; jamais lancé en CI. |
| `outils/verifier_pieges.py` | Lance Cucumber sur `not @attendu:passe` et vérifie, scénario par scénario, l'échec attendu (assertion, délai dépassé ou étape non définie). |
| `outils/comparer.py` | Regroupe les 3 passages de chaque scénario et calcule réussite (moyenne et variance entre passages), stabilité, faux positifs, faux négatifs, refus justes, temps et coût. |
| `docs/index.html` | Page de démo : vous jouez le scénario dans l'appli, les étapes se cochent à côté ; tableau de comparaison (colonne Cucumber tirée de la CI, colonnes agent publiées en janvier 2027). |

Versions vérifiées sur Maven Central le 16/11/2026 : Cucumber-JVM 8.1.0, JUnit 6.1.3, Playwright Java 1.65.0, Surefire 3.6.1, Compiler 3.16.0, exec-maven-plugin 3.7.0.

## État (honnête)

| Partie | État |
|---|---|
| Appli de démo jouable (3 parcours, pièges) | fait |
| 17 scénarios Gherkin dont 6 faux ou ambigus, avec vérité terrain | fait |
| Validateur, comparateur, lanceur d'agent (faux agent) : 50 tests unitaires | fait, verts en local |
| Page de démo (appli + scénario en cours) | fait |
| Référence Cucumber-JVM + Playwright Java | écrite et compilée en local ; exécution non vérifiée en local (téléchargement de Chromium bloqué sur le poste) : **la CI fait foi** |
| Vérification des pièges côté Cucumber (job CI `pieges-cucumber`) | écrite ; **la CI fait foi** (pas de Chromium en local) |
| Lanceur de l'agent (`agent/lancer.py`) | écrit et testé avec un faux agent ; jamais lancé avec un vrai modèle |
| Mesures agent contre Cucumber (réussite, faux positifs, temps, coût, robustesse) | mesurées (branche `mesures`) : [resultats/LISEZMOI.md](resultats/LISEZMOI.md) ; appli refondue pour la robustesse : `docs/app-v2/` |
| Conversion du rapport Cucumber en `resultats/cucumber/resultats.json` | à faire |

## Licence

Apache-2.0, voir [LICENSE](LICENSE).
