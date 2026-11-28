# Plan du deck : Tools-in-Action 30 min (variante Quickie 20 min)

Titre : **L'écran change : mes step definitions cassent, pas l'agent**

Le deck suit 4 étapes, affichées en surtitre sur chaque slide : **DÉPART → PROBLÈME → CIBLE → COMMENT**.

| Étape | En une phrase |
|---|---|
| **Départ** | Votre équipe écrit des scénarios Gherkin ; Cucumber les joue grâce à des step definitions, le code de « colle » qui cherche chaque bouton à l'écran. |
| **Problème** | Cette colle casse quand l'écran change, même sans changement de comportement : sur l'appli de démo, une refonte casse 7 scénarios sur 17 (2 step definitions à réécrire), et 3 tests restent « conformes » sans plus tester leur piège. |
| **Cible** | Des scénarios qui survivent aux refontes, avec un verdict expliqué (passe, échec, ou refus quand le scénario est ambigu), sans réécrire la colle. Atteignable : un agent qui regarde l'écran garde 51 verdicts justes sur 51 après la refonte (204 sur 204 en tout). |
| **Comment** | L'outil **gherkin-eyes** + 3 gestes : 1. garder Cucumber en CI (rapide, gratuit) ; 2. lancer gherkin-eyes après une refonte, sur des scénarios neufs ou un écran sans colle ; 3. écrire le Gherkin avec 3 règles (nommer l'objet, le bouton, ce qu'on voit). |
| **Outil** | `gherkin-eyes features/ --url <appli>` (dossier `outil/`, Python sans dépendance, Apache-2.0, sur Playwright MCP) → `rapport.html` (verdict, explication, capture de l'écran final) + `junit.xml` pour la CI. Installation : `pipx install "git+https://github.com/mekkiamiri/bdd-agent-eyes#subdirectory=outil"`. |

**Objectif du talk** (ce que le public fera lundi) : installer gherkin-eyes, le lancer sur ses propres scénarios après la prochaine refonte (ou sur ses scénarios neufs), et garder Cucumber en CI.

**Promesse** (« vous repartirez avec ») :
1. **L'outil** gherkin-eyes : une commande, un rapport HTML et un fichier JUnit ; sortie réelle sur l'exemple : 17 verdicts conformes sur 17.
2. **Les chiffres** : une refonte casse 7 scénarios Cucumber sur 17 et aucun verdict de l'agent ; mais l'agent coûte 28 s et 12 centimes par scénario, contre 1,4 s pour Cucumber.
3. **Trois gestes** : Cucumber en CI ; l'agent là où la colle ne suit pas ; trois règles d'écriture.

**Le message en une phrase** : quand l'écran change sans que le comportement change, ce sont les step definitions qui cassent ; gherkin-eyes joue les mêmes scénarios en regardant l'écran et dit pourquoi, mais il est lent et payant : gardez Cucumber en CI et lancez-le là où la colle ne suit pas.

Public : développeurs Java et testeurs qui écrivent ou maintiennent du Gherkin (Cucumber, Playwright), niveau intermédiaire.

| n° | étape | titre-phrase | objectif : le public doit penser… | preuve | durée |
|---|---|---|---|---|---|
| 1 | départ | L'écran change : mes step definitions cassent, pas l'agent | « Il va partir de mon quotidien et me donner un outil. » | annonce du chemin et de l'outil | 1 min |
| 2 | départ | Vous écrivez du Gherkin ; Cucumber le joue grâce à du code de colle | « C'est exactement ce que je fais. » | vrai scénario + sa step definition (`Etapes.java`, l. 96, simplifiée) ; banc : 17 scénarios | 2 min |
| 3 | problème | Une refonte d'écran, aucun comportement changé : Cucumber casse 7 scénarios sur 17 | « C'est ma douleur, chiffrée. » | CI run 45566605569 : 17/17 → 10/17, 11/11 → 4/11, 2 step definitions | 2 min 30 |
| 4 | problème | Pire que le rouge : 3 tests restent « conformes » mais ne testent plus rien | « Mes tests verts peuvent mentir. » | les 3 pièges qui échouent ailleurs (`resultats/LISEZMOI.md`) | 2 min |
| 5 | cible | La cible : des scénarios qui survivent aux refontes, avec un verdict expliqué | « Voilà ce que je veux. » | agent sur v2 : 51/51, 0 ligne de colle | 1 min 30 |
| 6 | cible | Un agent lit le scénario, regarde l'écran, clique : 204 verdicts justes sur 204 | « J'ai compris le mécanisme, et ce n'est pas un coup de chance. » | 153 (3 vues × 3 passages) + 51 ; 0 passe à tort | 2 min |
| 7 | cible | Bouton grisé, trois « Ajouter » : il ne force pas, il ne devine pas | « Il ne clique pas au hasard ; l'appli est la sienne, il le dit. » | capture réelle de l'écran final + citations mot pour mot (série du 28/11) ; 27 refus sur 27 | 2 min |
| 8 | comment | L'outil : gherkin-eyes. Une commande, un rapport HTML et un fichier JUnit | « Je peux l'installer en sortant. » | sortie réelle : 17/17 conformes, 2 min 24 s, 1,98 $ ; **démo live** | 4 min |
| 9 | comment | Après la refonte, même commande, rien à réparer | « Mon problème de la slide 3 est réglé. » | sortie réelle de gherkin-eyes sur v2 contre 10/17 pour Cucumber | 3 min |
| 10 | comment · geste 1 | Gardez Cucumber en CI : l'agent prend 20 fois plus de temps, et coûte | « Il ne remplacera pas ma CI. » | 1,4 s contre 28 s (13 à 43 s), 6 à 16 centimes | 2 min |
| 11 | comment · geste 2 | Lancez gherkin-eyes là où la colle ne suit pas | « Je sais quand le lancer, et je peux croire ses verdicts. » | 3 usages ; juge à l'aveugle : 9 accords sur 10, preuves conformes 10/10 | 2 min 30 |
| 12 | comment · geste 3 | Écrivez le Gherkin avec 3 règles : l'objet, le bouton, ce qu'on voit | « Mes scénarios s'améliorent, même sans agent. » | les refus réels regroupés | 1 min 30 |
| 13 | comment | Un bon testeur sait dire non. Et il ne casse pas quand l'écran change. | La phrase à retenir, et les 2 commandes. | `pipx install …` + `gherkin-eyes …` | 2 min (+ questions) |

Total : 28 min 30 + 1 min 30 de marge.

## Variante Quickie 20 min (9 slides)

Garder **1, 2, 3, 5, 6, 8, 9, 10, 11**. On retire le faux vert (4, dit en une phrase à la fin de la 3), les pièges (7, dire sur la 6 que l'appli et les pièges sont les miens et qu'il refuse les ambigus), les 3 règles (12, dites en une phrase sur la 11) et la fin (13 : afficher les 2 commandes sur la 11).
Minutage : 1 · 2 · 2 · 1 · 2 · 4 (démo) · 2 · 1,5 · 2 = 17 min 30, plus 2 min 30 de marge.

## Skim test (titres seuls)

Départ : on écrit du Gherkin, Cucumber le joue grâce à de la colle → problème : une refonte casse 7 scénarios sur 17, et 3 tests verts ne testent plus rien → cible : des verdicts qui survivent et s'expliquent ; un agent y arrive (204 sur 204), sans tomber dans les pièges → comment : l'outil gherkin-eyes, une commande ; après la refonte, rien à réparer ; geste 1 Cucumber en CI (l'agent est 20 fois plus lent) ; geste 2 l'agent là où la colle ne suit pas ; geste 3 trois règles d'écriture → un bon testeur sait dire non.

## Sources des chiffres

`resultats/LISEZMOI.md`, `resultats/synthese-agent.json`, `resultats/agent-*/resultats.json`, `resultats/robustesse-v2/agent-les-deux/resultats.json`, `docs/app-v2/CHANGEMENTS.md`, CI run 45566605569 (job `reference-cucumber-v2`), `outil/exemple/resultats.json` (série gherkin-eyes du 28/11/2026 sur `docs/app`), `revue/juge-aveugle.json` (juge à l'aveugle), `slides/REVUE.md` (série gherkin-eyes sur `docs/app-v2`, revue de code croisée). Chaque note de slide cite le sien.
