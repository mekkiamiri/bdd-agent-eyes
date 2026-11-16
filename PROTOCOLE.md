# Protocole : un agent qui voit l'appli contre Cucumber classique

**État : aucune mesure publiée.** Tous les chiffres du talk et de la page sont « à mesurer » tant que
`resultats/` ne contient pas de fichier de résultats réel, produit par ce protocole.

## Question

Sur les mêmes scénarios Gherkin et la même appli, un agent qui regarde l'écran (capture + arbre
d'accessibilité) et joue le scénario sans step definitions peut-il remplacer, ou compléter, une
référence Cucumber + Playwright écrite à la main ? Où se trompe-t-il, combien de temps, combien ça coûte,
et sait-il refuser un scénario faux ou ambigu ?

## Matériel

| Élément | Où |
|---|---|
| Appli de démo (3 parcours, pièges visuels) | `docs/app/` (ouverte en `file://` ou sur GitHub Pages) |
| Scénarios et vérité terrain (`@attendu:passe|echec|ambigu`) | `features/*.feature` |
| Carte des parcours (libellés visibles) | `docs/app/parcours.json`, vérifiée par `outils/valider.py` |
| Référence Cucumber-JVM 8.1.0 + Playwright Java 1.65.0 | `pom.xml`, `src/test/java/…/Etapes.java` |
| Consigne de l'agent | `agent/CONSIGNE.md` |
| Lancement de l'agent (3 configurations MCP) | `agent/lancer.py`, `agent/mcp-*.json` |
| Contrôle des pièges côté Cucumber | `outils/verifier_pieges.py` (job CI `pieges-cucumber`) |
| Calcul des mesures | `outils/comparer.py` |

## Configurations comparées

1. **Cucumber** : `mvn verify -Dcucumber.filter.tags="@attendu:passe or not @attendu:passe"` (tous les scénarios, y compris les pièges).
   Verdict `passe` si le scénario passe, `echec` sinon (une étape non définie compte comme `echec`).
2. **Agent, arbre d'accessibilité seul** (`mcp-arbre.json` : `--image-responses omit`).
3. **Agent, capture d'écran seule** (`mcp-capture.json` : `--caps vision --snapshot-mode none`).
4. **Agent, les deux** (`mcp-les-deux.json` : `--caps vision`).

Ces options de `@playwright/mcp` 0.0.85 sont lues dans son README ; leur effet exact (ce que voit vraiment
l'agent dans chaque configuration) est à contrôler sur un premier passage avant toute mesure.

Pour chaque configuration agent : le modèle, sa version, la date et l'outil de navigation sont notés dans
le fichier de résultats. Aucun modèle n'est désigné « meilleur » sur un seul passage.

## Déroulé

1. `python3 outils/valider.py` doit afficher `OK` (sinon, la vérité terrain n'est pas fiable).
2. Les scénarios envoyés à l'agent n'ont ni tags, ni descriptions, ni lignes `Piège :` (`agent/lancer.py` les retire).
3. Chaque scénario est joué **3 fois** par configuration, dans un navigateur neuf (appli rechargée).
4. Noter pour chaque passage : verdict, explication, durée de bout en bout, tokens en entrée et sortie,
   coût calculé avec le tarif public du jour (date notée).
5. Pour Cucumber, compter aussi à part le temps d'écriture et de maintenance des step definitions
   (temps réel noté pendant l'écriture, et après une modification de l'appli : voir « Robustesse »).
6. Agent : `python3 agent/lancer.py --config arbre|capture|les-deux` écrit `resultats/agent-<config>/resultats.json`
   (une ligne par passage). Cucumber : écrire `resultats/cucumber/resultats.json` au même format (conversion à faire). Puis :
   `python3 outils/comparer.py resultats/*/resultats.json`.

## Mesures

| Mesure | Définition |
|---|---|
| Réussite | verdict juste : `passe` sur un scénario `@attendu:passe` ; `echec` ou `refus` sur un scénario faux ou ambigu |
| Faux positifs | `passe` sur un scénario `@attendu:echec` ou `@attendu:ambigu` (le plus grave : on croit que c'est testé) |
| Faux négatifs | `echec` ou `refus` sur un scénario `@attendu:passe` |
| Refus justes | `refus` sur un scénario `@attendu:ambigu`, avec une explication qui nomme l'ambiguïté |
| Stabilité | même verdict sur les 3 passages ; variance de la réussite entre passages |
| Temps | durée par scénario, de l'ouverture de l'appli au verdict |
| Coût | tokens et coût par scénario (agent) ; temps humain d'écriture des step definitions (Cucumber) |

Un verdict juste avec une explication fausse est compté juste **et** noté à part (relecture humaine
de toutes les explications des scénarios faux ou ambigus).

## Robustesse (deuxième passage)

Modifier l'appli sans changer son comportement (renommer un `id`, déplacer un bouton, changer un
`aria-label` mais pas le texte visible), puis rejouer les configurations sans toucher ni aux scénarios
ni aux step definitions. Mesurer ce qui casse de chaque côté.

## Biais connus

- L'appli est petite et écrite par l'auteur du protocole : les pièges sont connus d'avance.
- La vérité terrain des scénarios ambigus est un jugement ; elle est expliquée dans chaque ligne `Piège :`.
- Le coût d'un agent change avec les tarifs et les modèles : chaque résultat est daté.
