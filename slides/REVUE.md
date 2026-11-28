# Revue du deck « L'écran change : mes step definitions cassent, pas l'agent »

# Deck v3 (branche `deck-v3`) : cadre départ → problème → cible → comment, et l'outil gherkin-eyes

Constat de départ (relecture de Mekki sur deck-v2) : on ne comprenait ni le point de départ, ni le point cible, ni
le problème, ni comment faire ; et aucun outil à installer. Réponse : le deck suit 4 étapes affichées en surtitre,
et la partie « comment » livre un outil open source, `gherkin-eyes` (dossier `outil/`).

## Nom de l'outil

| Nom | GitHub (`gh search repos`) | PyPI (`pypi.org/pypi/<nom>/json`) | Choix |
|---|---|---|---|
| **gherkin-eyes** | aucun dépôt | 404 (libre) | **retenu** : dit ce qu'il fait (des yeux pour le Gherkin), rime avec le dépôt `bdd-agent-eyes` |
| screen-cuke | aucun dépôt | 404 (libre) | plus drôle, mais « cuke » est un surnom de Cucumber : laisse croire à un plugin Cucumber |
| cuke-sight | aucun dépôt | 404 (libre) | même réserve |
| gherkin-witness (écarté) | aucun dépôt de ce nom, mais un outil BDD existant se décrit par « witness what your tests actually did » | 404 | trop proche d'un projet existant |

Vérifié le 28/11/2026.

## Mesures de l'outil (28/11/2026, Sonnet 5.5, WebKit headless, 4 passages en parallèle)

| Série | Commande | Résultat | Durée réelle | Coût |
|---|---|---|---|---|
| v1, essai 0 (version d'avant les corrections) | `gherkin-eyes features/ --url docs/app/index.html --sans-fenetre -j 4` | 11/17 conformes : 4 passages où le serveur Playwright n'a pas démarré (CONNECT_TIMEOUT, 4 lancés en même temps) rendus en « refus » par l'agent, 2 réponses au JSON mal formé non lues, 1 vrai écart (« Ajouter un produit épuisé » : refus au lieu d'échec) | 2 min 04 s | 1,90 $ |
| **v1 (série publiée, `outil/exemple/`)** | même commande, après 3 corrections : règle 7 de la consigne (navigateur absent → `erreur`, relancé), départs espacés de 3 s, lecture tolérante du JSON mal formé | **17/17 conformes** (11 passe, 3 échec, 3 refus, 0 erreur, aucune relance) ; 2 réponses lues en mode tolérant (toutes deux des refus) | 2 min 24 s (473 s cumulés) | 1,98 $ |
| v2 (interface refondue, `outil/exemple-v2/`) | `gherkin-eyes features/ --url docs/app-v2/index.html --sans-fenetre -j 4` | **17/17 conformes** (11 passe, 3 échec, 3 refus, 0 erreur) ; 10 passages relancés une fois : 9 où le navigateur piloté ne répondait plus (l'agent a répondu `erreur`, comme le demande la règle 7) et 1 délai de 600 s dépassé ; tous justes à la relance | 12 min 7 s (dont 10 min d'attente du délai dépassé ; 389 s cumulés hors relances) | 2,22 $ + 0,70 $ de relances |

L'essai 0 est gardé ici parce qu'il est instructif : sans règle explicite, l'agent transforme une panne d'outil en
« refus » (un faux signal sur le scénario). La série publiée est la première série complète après correction ; aucun
verdict n'a été corrigé à la main. Les corrections de la revue de code (plus bas) sont venues après ces séries :
elles ne changent ni la consigne ni le parcours du navigateur, seulement la lecture des réponses, les dossiers et les codes de sortie.

## Revue de code croisée

Trois regards sur le même code : l'agent de revue (`gsd-code-reviewer`, rapport complet : `revue/REVUE-CODE.md`),
la notation façon banc devkit (captures + juge à l'aveugle, grille `revue/GRILLE-JUGE.md` commitée avant les passages),
et les règles automatiques (tests, compilation, validateur du dépôt).

Le banc devkit du Lab (banc spec-driven) a été retrouvé : sa méthode est décrite dans le dépôt `lab/benchmarks`
(captures Playwright, écart de pixels, SSIM, juge à l'aveugle avec dossiers renommés, grille écrite avant) ; son code de
notation complet vit dans un dossier du travail et n'a pas été repris. Seule la méthode est reprise, réécrite dans
`revue/juge_aveugle.py`. Pas d'écart de pixels ici : il n'y a pas d'image cible, seulement l'écran final capturé par l'agent.

### 1. Agent de revue (29 constats)

| Partie | Bloquant | Important | Mineur |
|---|---|---|---|
| Step definitions Java (`Etapes.java`…) | 0 | 4 | 6 |
| Outil Python (`outil/gherkin_eyes/`) | 2 | 8 | 9 |

- **Bloquants (outil), corrigés** : un verdict « passe » imbriqué dans un objet « echec » était lu « passe » (faux vert) ;
  des mots-clés français manquants (`Sachant `, `Etant données `, apostrophe `’`) faisaient disparaître des étapes sans bruit.
- **Importants (outil), corrigés** : lecture tolérante qui pouvait lire un « passe » écrit en prose (elle n'accepte plus
  jamais « passe ») ; doc string non fermé et ligne inconnue après une étape (erreur au lieu de silence) ; tags de `Règle`
  perdus ; deux scénarios aux noms proches dans le même dossier (préfixe unique) ; capture d'une série précédente prise
  comme preuve (dossier vidé) ; processus orphelins au délai dépassé (groupe de processus tué) ; erreurs d'usage
  confondues avec un échec (code 3) ; chemins locaux dans `mcp.json` et la sortie brute (fichier temporaire, anonymisation).
  Mineurs corrigés : encodage UTF-8, caractères de contrôle dans le JUnit, totaux à la racine du JUnit, indentation des doc strings,
  lignes d'exemples mal formées, langue déduite du mot-clé, anonymisation qui cassait les `//` des URL. 10 tests de non-régression ajoutés (25 au total).
- **Importants (Java), non corrigés, et c'est voulu** : ce sont les step definitions mesurées ; les corriger changerait la
  référence. Deux d'entre eux nourrissent le talk : `je ne vois pas` reste vert si le texte n'existe pas du tout (une faute de
  frappe donne un faux vert), et `Alors je suis connecté` se connecte au lieu de vérifier. Les deux autres sont exactement les
  deux localisateurs cassés par la refonte (nom accessible du bouton, `data-testid`).

### 2. Juge à l'aveugle (10 passages de la série v1 publiée)

Tirage `revue/juge_aveugle.py preparer` (graine 2026) : les 3 scénarios faux, les 3 ambigus, 4 justes au hasard ;
codes P01 à P10. Juge : Opus 5.5 (l'agent est Sonnet 5.5), une session neuve par passage, dossier isolé, seul outil :
lire l'image. Étape 1 : scénario + capture finale, sans verdict. Étape 2 (session séparée) : la preuve écrite de l'agent est-elle conforme à la capture ?

| Code | Scénario | Agent | Juge (aveugle) | Accord | Preuve de l'agent conforme |
|---|---|---|---|---|---|
| P01 | connexion · Message d'accueil personnalisé | échec | échec | oui | oui |
| P02 | livraison · Message quand les conditions ne sont pas cochées | échec | échec | oui | oui |
| P03 | panier · Ajouter un produit épuisé | échec | échec | oui | oui |
| P04 | panier · Un code inconnu retire la remise | passe | passe | oui | oui |
| P05 | panier · Ajouter au panier | refus | refus | oui | oui |
| P06 | livraison · La commande est enregistrée | refus | **échec** | **non** | oui |
| P07 | livraison · Code postal invalide | passe | passe | oui | oui |
| P08 | connexion · Mauvais mot de passe | passe | passe | oui | oui |
| P09 | panier · Code promo de bienvenue | passe | passe | oui | oui |
| P10 | connexion · Connexion rapide | refus | refus | oui | oui |

**9 accords sur 10, 0 indéterminé, preuve conforme 10 fois sur 10.** Coût du juge : 1,93 $.
Le désaccord, relu à la main capture à l'appui : l'écran final montre le formulaire de livraison, case des conditions non
cochée, « Enregistrer l'adresse » actif et « Valider la commande » grisé. Le juge conclut « échec » (le bouton qu'il fallait
utiliser est grisé) ; l'agent conclut « refus » (« je valide » peut viser deux boutons). La vérité terrain du scénario est
« ambigu » : l'agent a raison selon l'étiquette, et la capture montre bien les deux boutons ; aucun des deux ne dit « passe ».
Limite : une seule capture finale ne montre pas les étapes intermédiaires ; le juge vérifie l'état final, pas tout le parcours.

### 3. Règles automatiques

- `python3 -m unittest discover -s outil/tests` : 25 tests OK (faux agent, sans modèle ni navigateur) ;
  `python3 -m unittest discover -s tests` : 54 tests OK ; `python3 outils/valider.py` : OK ; `construire_page.py --check` : à jour.
- `python3 -W error -m py_compile` sur l'outil et le juge : OK. Pas de pyflakes ni ruff sur le poste : contrôle maison des imports inutilisés, rien trouvé.
- `mvn -q -B -o test-compile` (lancé par l'agent de revue) : compile. Les tests Cucumber eux-mêmes tournent en CI (Chromium bloqué sur le poste).
- Installation vérifiée : `pip install ./outil` dans un environnement virtuel neuf, `gherkin-eyes --version` → `gherkin-eyes 0.1.0`.

### Ce que chaque regard voit, et pas les autres

| Regard | Voit | Ne voit pas |
|---|---|---|
| Agent de revue | les faux verts possibles **dans le code** (verdict imbriqué, `isHidden()` sur un texte absent, étapes avalées) | si les verdicts réels sont justes |
| Juge à l'aveugle | si le verdict et la preuve **correspondent à l'écran** (9/10, 10/10) | les bugs qui ne se sont pas produits sur cet échantillon (aucun des deux bloquants ne s'est produit dans la série) |
| Tests, compilation, validateur | les régressions sur les cas écrits (25 + 54 tests) | les cas que personne n'a écrits : les deux bloquants passaient les 15 premiers tests |

Lecture : les tests verts n'avaient pas vu les deux bloquants ; l'agent de revue les a trouvés en lisant le code ; le juge
confirme que sur la série réelle, ils n'ont pas joué (aucun verdict imbriqué, aucun mot-clé manquant dans nos features).

## Test de clarté

Méthode : à chaque tour, un relecteur neuf (agent sans aucun accès au dépôt) reçoit **seulement** le texte des slides
(titres et corps, sans notes ni PLAN.md) et le profil « développeur Java intermédiaire qui n'a jamais entendu parler du
sujet ». Il répond en 5 lignes : départ, problème, cible, comment, outil. On compare avec `slides/PLAN.md`.

### Tour 1

> 1. Point de départ : on écrit des scénarios Gherkin que Cucumber-JVM exécute avec Playwright en CI, grâce à du code de colle (les step definitions) qui transforme chaque phrase en clic sur un élément précis de la page.
> 2. Problème : une refonte d'écran qui ne change aucun comportement casse 7 scénarios sur 17 parce que la colle visait un nom de bouton caché ou un attribut de test qui ont changé. Pire, 3 tests qui doivent échouer restent « conformes » parce qu'ils échouent plus tôt, sur une étape commune : le piège qu'ils devaient vérifier n'est plus atteint.
> 3. Point cible : des scénarios qui survivent aux refontes sans qu'on touche à la colle, avec pour chaque scénario un verdict expliqué parmi trois (passe, échec, refus).
> 4. Comment faire : un agent (un modèle d'IA, Sonnet 5.5) lit le scénario, regarde une capture d'écran et ce que lit un lecteur d'écran, puis clique et rend son verdict. On garde Cucumber en CI parce que l'agent est environ 20 fois plus lent et coûte autour de 12 centimes par scénario. On lance l'agent après une refonte, sur des scénarios neufs ou sur un écran qui n'a pas encore de colle. On écrit le Gherkin en nommant l'objet, le bouton et ce qu'on voit à l'écran.
> 5. Outil à installer : gherkin-eyes, avec `pipx install "git+https://github.com/mekkiamiri/bdd-agent-eyes#subdirectory=outil"`, puis `gherkin-eyes features/ --url http://localhost:8080`.
>
> Ce qui m'a gêné : les chiffres se mélangent (17/17, 51/51, 204/204, 11/11, 27 refus) sans que je sache sur quoi porte chaque total, et « un juge confirme 9 verdicts sur 10 » semble contredire « 204 verdicts justes sur 204 ».
> Ce qui m'a gêné : je ne sais pas si un « refus » compte comme un résultat attendu, ni ce que veut dire au juste « conforme » à côté de « juste ». La slide 4 (les deux lignes ✘ et « le piège ») est difficile à comprendre sans l'orateur.
> Ce qui m'a gêné : du jargon sans explication (« Playwright MCP », « juge à l'aveugle », « -j 4 »), et le dépôt s'appelle bdd-agent-eyes alors que l'outil s'appelle gherkin-eyes.

Comparaison avec PLAN.md : les 5 réponses sont justes (départ, problème chiffré avec le faux vert, cible, les 3 gestes, l'outil et ses 2 commandes). Rien de faux ni de vague ; mais trois gênes, corrigées quand même avant le tour 2 :

| Gêne | Correction |
|---|---|
| Sur quoi portent 17, 51, 204 ; « 9 sur 10 » semble contredire « 204 sur 204 » | Slide 6 : « 204 = les 17 scénarios joués 12 fois : 9 avant la refonte, 3 après » ; slide 2 : « 11 justes, 6 faux ou ambigus exprès, chacun avec son verdict attendu » ; slide 11 : le juge devient « un 2e modèle, qui ne voit que cet écran et pas le verdict, arrive au même verdict 9 fois sur 10 » (une autre mesure : l'accord entre deux modèles, pas la justesse) |
| « Conforme », « juste », « refus » | Slide 3 : « conformes (= le verdict attendu) » ; slide 5 : « refus (scénario ambigu) » ; slide 6 : « juste = le verdict attendu » |
| Slide 4 illisible sans l'orateur | Réécrite : « Un scénario faux doit échouer sur son piège » / avant : échoue sur le piège / après : échoue plus tôt, sur une étape commune / « Toujours rouge comme prévu, donc conforme. Mais le piège n'est plus testé. » Les noms d'étapes passent en note. |
| Jargon (Playwright MCP, juge à l'aveugle, -j 4) ; dépôt et outil aux noms différents | Slide 8 : « -j 4 : 4 scénarios en parallèle », « le navigateur est piloté par Playwright MCP (Microsoft) » ; « juge à l'aveugle » retiré des slides (gardé en note) ; slide 13 : « Dépôt du talk (outil, appli, mesures) » |

### Tour 2 (relecteur neuf, slides corrigées)

> 1. Point de départ : on écrit des scénarios Gherkin que Cucumber exécute grâce à des step definitions (du code « de colle » qui traduit chaque phrase en clic Playwright). Banc de test : une appli de démo et 17 scénarios, dont 6 volontairement faux ou ambigus.
> 2. Problème : une refonte d'écran sans aucun changement de comportement fait échouer 7 scénarios justes sur 11, et il faut réécrire 2 step definitions. Pire, 3 scénarios faux restent rouges « comme prévu », mais ils échouent avant leur piège, donc ils ne testent plus rien.
> 3. Point cible : des scénarios qui survivent aux refontes sans toucher à la colle, avec un verdict expliqué (passe, échec ou refus si le scénario est ambigu). Un agent lit le scénario, regarde l'écran, clique, et ne force ni ne devine.
> 4. Comment faire : garder Cucumber en CI (20 fois plus rapide, gratuit). Lancer gherkin-eyes sur le dossier features avec l'URL de l'appli après une refonte, sur des scénarios neufs ou avant d'avoir écrit la colle. Écrire le Gherkin avec 3 règles : nommer l'objet, nommer le bouton, dire ce qu'on voit.
> 5. Outil à installer : gherkin-eyes, avec `pipx install "git+https://github.com/mekkiamiri/bdd-agent-eyes#subdirectory=outil"`, puis `gherkin-eyes features/ --url http://localhost:8080`.
>
> Ce qui m'a gêné : trop de totaux différents (17/17, 51/51, 204/204, 9+3 passages, 27 passages). Je ne sais pas d'où vient 51, et je dois refaire le calcul pour comprendre comment « 7 cassés » et « 3 encore conformes » donnent 10/17.
> Ce qui m'a gêné : « l'agent » apparaît dans le titre mais n'est présenté qu'à la slide 6. On voit un coût en $ et « Sonnet 5.5 », mais rien ne dit quel modèle ou quelle clé d'API configurer pour lancer l'outil. Et « sans dépendance » me semble contredire « piloté par Playwright MCP ».
> Ce qui m'a gêné : le dépôt s'appelle bdd-agent-eyes et l'outil gherkin-eyes. Les mots « colle », « refus » et « un 2e modèle » demandent un temps d'adaptation.

Comparaison avec PLAN.md : **réussi**. Les 5 réponses sont justes et précises, plus précises qu'au tour 1 : le problème
est chiffré sur les bons totaux (7 justes sur 11, 2 step definitions), le faux vert est compris sans l'orateur, et les 3 gestes
sont donnés dans l'ordre du plan avec l'outil et ses 2 commandes. On s'arrête au tour 2 (3 tours au plus).
Deux gênes corrigées après coup, sans nouveau tour (ajouts d'une ligne, aucun changement de sens) : slide 5, « 51 / 51 … (17 scénarios × 3) » ;
slide 8, prérequis dits (Python, Node.js pour Playwright MCP, une CLI d'agent avec sa clé, modèle par défaut Sonnet 5.5) à la place de
« sans dépendance ». Laissées : l'agent n'est présenté qu'à la slide 6 (le titre l'annonce, la cible vient d'abord, c'est voulu),
et le nom du dépôt (`bdd-agent-eyes`, déjà publié et cité) différent de celui de l'outil.

## Grille du comité (deck v3 et propositions mises à jour)

| Critère | v2 | v3 | Pourquoi |
|---|---|---|---|
| Unicité | 4 | 4 | « Agent + tests » sera vu souvent en 2027 ; mesuré contre Cucumber, avec une refonte, le faux vert et un juge à l'aveugle, beaucoup moins. |
| Légitimité | 3 | 3 | 18 ans de BDD, un banc et un outil construits soi-même ; toujours aucune contribution BDD publique ni retour de production. |
| Promesse | 4 | **5** | On repart avec un outil installable en une commande (sortie réelle montrée), plus 3 gestes concrets. |
| Concret | 5 | 5 | Démo de l'outil, deux séries réelles (avant et après la refonte), run CI citable, rapports publiés. |
| Actualité | 4 | 4 | Agents de test et MCP navigateur, vus sous l'angle « où ne pas le mettre ». |
| Clarté | 4 | **5** | Départ → problème → cible → comment en surtitre ; un relecteur neuf retrouve les 5 réponses du plan au 2e tour. |
| Risque speaker | 3 | 3 | Dépôt soigné, CI, rapports prêts en plan B ; aucune vidéo ni meetup cité. |
| Format | 5 | 5 | Tools-in-Action : un outil livré, démontré en direct ; variante Quickie listée. |
| **Total** | 32/40 | **34/40** | Aucun critère sous 3. Les deux 3 ne se règlent pas dans le deck (voir ci-dessous). |

## Ce qui reste à Mekki

1. **Valider le nom** `gherkin-eyes` (libre sur GitHub et PyPI au 28/11/2026 ; autres options libres : `screen-cuke`, `cuke-sight`).
2. **Fusionner `deck-v3` dans `main`** avant de soumettre : la commande `pipx install "git+…#subdirectory=outil"` affichée sur les slides
   et dans `outil/README.md` ne marche qu'une fois `outil/` sur la branche par défaut. Publier sur PyPI : optionnel.
3. **Expérience de scène et accord employeur** dans les notes au comité (c'est ce qui bloque Légitimité et Risque speaker à 3).
4. **Vidéo de plan B** de la démo (gherkin-eyes sur un scénario, puis sur la v2) ; les rapports `outil/exemple*/` servent déjà de plan B statique.
5. **Contrôle visuel du deck** dans un navigateur (non fait : aucun navigateur avec fenêtre pendant ce travail), en particulier la slide 7 (capture + tableau côte à côte) et la slide 8 (6 lignes de terminal).
6. **Constats Java de la revue de code** (`revue/REVUE-CODE.md`) : laissés tels quels parce que ce sont les step definitions mesurées ; à décider si on les corrige après la soumission (l'étape `je ne vois pas` qui reste verte sur un texte absent ferait un bon exemple de faux vert sur scène).

# Historique : revues du deck v2 (branche `deck-v2`)

Trois revues successives avant la relecture de Mekki, sur la branche `deck-v2`. Gravité : 🔴 casse dans la salle ou devant le comité · 🟡 coûte de la force · ⚪ goût, à prendre ou à laisser.
Méthode : titres-phrases et skim test (deck-outline-first), arc situation → complication → résolution (deck-narrative-arc), grille argument / preuves / densité / arc / honnêteté (deck-review-rubric), grille du comité du coach CFP.

## Revue 1 : l'argument

Objectif et promesse écrits en tête de `slides/PLAN.md`, table slide par slide (titre-phrase, objectif, preuve, durée).

### Titre : trois options

| Option | Caractères | Pour | Contre |
|---|---|---|---|
| A. « Quand l'écran change, mes step definitions cassent. Pas l'agent. » | 64 | La formulation proposée, rythme oral | Dépasse 60 |
| **B. « L'écran change : mes step definitions cassent, pas l'agent »** | 58 | Même idée, ≤ 60, la tension en premier | Un peu plus sec |
| C. « Gherkin joué par un agent qui voit l'écran : 204 verdicts sur 204 » | 65 | Chiffré | Promet la performance, pas la leçon ; le talk conclut « gardez Cucumber en CI » |

**Choisi : B.** Il dit la douleur (la colle casse), le contraste (pas l'agent), et ne promet pas « sans step definitions » : il reste compatible avec la conclusion « Cucumber en CI ». « Mes » assume que c'est une mesure personnelle, sur une appli à moi. Titre court du pied de slide : « Mes step definitions cassent, pas l'agent ». Anglais : « The screen changes: my step definitions break, the agent doesn't ».

### Problèmes trouvés

| Gravité | Slide | Problème | Correction |
|---|---|---|---|
| 🔴 | 1 + proposition | Le titre « Vos scénarios Gherkin se jouent sans step definitions » promet ce que le talk dément à la fin (« gardez Cucumber en CI ») : le comité et la salle se sentent trompés. | Titre B, slide 1, PLAN, `PROPOSITION-EN.md`. |
| 🔴 | 5 | « L'appli est la mienne » n'arrivait qu'à la slide du prix (11) : pendant six slides, le public croit à une appli neutre ; un sceptique le découvre et ne croit plus rien. | Slide 5 retitrée « J'ai piégé mon appli trois fois. Il ne tombe dans aucun piège. » + ligne « L'appli et ses pièges sont écrits par moi : je les connaissais d'avance. » + note. En Quickie (slide 5 retirée) : le dire sur la 7. |
| 🟡 | 8 | « Capture, arbre ou les deux » ne sert pas l'objectif (où mettre l'agent) et retarde la démo 2, le cœur du talk. | Fondue dans la 7 (tableau par vue, colonne « passe à tort », durée, coût) ; la minute et demie va à la démo 2 (5 min 30, avec un passage live sur v2, `--sortie /tmp/demo`). Deck : 14 → 13 slides. |
| 🟡 | 5 | Titre-thème (« Trois pièges : un bouton grisé… ») : liste, pas conclusion. | Titre-phrase (ci-dessus). |
| 🟡 | PLAN | Ni objectif « lundi », ni promesse en 3 points, ni colonne preuve : le plan ne permettait pas de vérifier que chaque slide sert l'objectif. | En-tête et table refaits. |
| ⚪ | 7 | Le titre « 153 sur 153 » répété avec la 13 (« 204 ») peut sembler deux chiffres concurrents. | Note de la 13 : « 153 + 51 = 204 » (déjà là). Laissé. |

### Skim test

Titres seuls (voir `PLAN.md`) : la tension arrive à la slide 2, la résolution est annoncée dès le titre et prouvée en 7-8, le revers (9-10) arrive avant la recommandation, qui répond à la complication (11 : « là où la colle ne suit pas »). L'argument tient sans le corps. Seul accroc : la 3 est descriptive plus que conclusive ; gardée, parce qu'elle installe le mécanisme en 10 secondes.

### Reste après la revue 1

- La démo 2 en live sur v2 ajoute un risque : plan B inchangé (capture du run CI, vidéo).
- Vérification des chiffres et citations : revue 2.

## Revue 2 : les preuves et l'honnêteté

Revérifié dans le dépôt : chaque chiffre des slides, des notes et de la proposition anglaise, recalculé depuis `resultats/agent-*/resultats.json` et `resultats/robustesse-v2/agent-les-deux/resultats.json` (passages, verdicts par vérité terrain, durées et coûts moyens, coûts totaux), `resultats/synthese-agent.json`, `docs/app-v2/CHANGEMENTS.md`, `src/test/java/…/Etapes.java`, et le journal du job `reference-cucumber-v2` du run CI 45566605569 (lu avec `gh run view --log`) : v1 « Tests run: 17, Failures: 1, Errors: 5 » en 23,93 s (les 6 pièges), v2 « Failures: 2, Errors: 11 » en 35,13 s (6 pièges + 7 cassés).

Justes : 153/153 (33 passe, 9 echec, 9 refus par vue), 51/51 sur v2, 0 faux positif ; 27 refus sur les 27 passages ambigus (v1) ; « Conditions de vente non acceptées » juste 9 fois sur 9 ; 13,9 / 13,4 / 13,4 s et 0,069 / 0,062 / 0,059 $ ; v2 14,3 s, 0,087 $, 4,44 $ ; 1,4 s = 23,9 s / 17 ; 17 × 0,059 à 0,087 $ = 1,00 à 1,48 $ ; citations des slides 5, 6, 12 présentes dans les explications des passages cités.

### Problèmes trouvés

| Gravité | Où | Problème | Correction |
|---|---|---|---|
| 🔴 | Slide 4 | La réponse affichée « preuve : Après le clic sur « Valider la commande », la page Livraison affiche le titre « Commande confirmée »… » n'existe dans aucun passage : le champ s'appelle `explication`, et le texte du passage 1 cité est autre. Une citation reformulée présentée comme réelle. | Remplacée par l'explication mot pour mot du passage 3 (19 s, 0,056 $) ; note corrigée. |
| 🔴 | Slide 4 (démo live) | La commande de la démo écrit par défaut dans `resultats/agent-les-deux/resultats.json` (`agent/lancer.py`, `--sortie` vaut `resultats`) : le passage live s'ajoutait aux résultats mesurés et changeait leur date. | `--sortie /tmp/demo` dans la commande (slide 4 et démo 2), expliqué en note. |
| 🟡 | Slide 4 | « en 20 secondes » : les passages durent 19 à 25 s. | « en une vingtaine de secondes ». |
| 🟡 | Slide 6 | Citation coupée sans le signaler (prix, fin « par exemple « Ajouter le Marteau » »). « Cucumber ne dit pas pourquoi » : son message dit ce qu'il cherchait. | Coupes marquées « […] » ; note nuancée (délai de 2 s, message qui dit ce qu'il cherchait, pas ce qui manque au scénario). |
| 🟡 | Slide 10 | « 1,4 s par scénario » est une moyenne qui inclut l'attente de 2 s des 6 pièges. | Dit en note. |
| 🟡 | Slide 11 | « Nouvel écran » présenté comme tiré d'un résultat : aucune mesure dédiée. | Note : c'est une déduction (tous les passages se font sans colle), pas une mesure. Promesse 2 gardée, formulée « jouer un écran qui n'a pas encore de colle ». |
| 🟡 | Proposition EN | « On 17 trapped scenarios it gave 204 correct verdicts » mélange scénarios et passages, et tait que l'appli est celle de l'auteur ; « 10/17 … plus 3 traps » laisse croire 10 + 3. | « On my own small demo app… 204 correct verdicts in 204 runs » ; « 3 of the 10 that still match only because… » ; mesure datée. |
| 🟡 | « C'était avant » | Mesure de novembre 2026 avec Sonnet 5.5, talk en avril 2027 : le modèle aura changé. | Date et modèle sur la slide 10 ; note : le banc permet de refaire la mesure avec le modèle du jour. |
| 🟡 | Jargon | « Contexte » (slide 9) et « data-testid » (slide 8) non expliqués. | Expliqués dans les notes (à dire à l'oral). |
| 🟡 | `PROTOCOLE.md` | En-tête périmée « aucune mesure agent publiée ». | Remplacée par l'état réel (mesures du 24-25/11, chiffres, run CI ; temps humain d'écriture des step definitions absent de `resultats/`). README : « (quand il y aura des résultats) » retiré. |

Densité : une idée par slide ; la slide 7 fusionnée tient (titre 2 lignes, une ligne, tableau de 3 lignes) ; aucune slide n'a plus de 4 lignes de corps hors code. Non vérifié dans un navigateur (consigne : aucun navigateur) : contrôle visuel à faire par Mekki.

### Reste après la revue 2

- La vidéo de plan B citée en note (slides 4 et 8) n'existe pas encore dans le dépôt : à enregistrer.
- Le dépôt public ne montre les résultats que sur les branches `mesures` / `deck-v2` : `main` (et donc GitHub Pages, si Pages sert `main`) est encore à l'état d'avant les mesures. La proposition cite le dépôt comme preuve : décision de Mekki (fusion avant soumission).
- Le surcoût de +47 % sur v2 reste inexpliqué (le résultat ne garde pas les jetons) : dit en note, sans nouvelle mesure.

## Revue 3 : le comité

Nouvelle `slides/PROPOSITION-FR.md` (titre, abstract de 1 061 caractères en 3 paragraphes avec « Vous repartirez avec : », notes au comité au format du coach, bio à la 3e personne de 377 caractères, format, track) ; `PROPOSITION-EN.md` alignée.

### Test des 30 secondes

Titre + 1re phrase : « L'écran change : mes step definitions cassent, pas l'agent » / « Quand l'interface change sans que le comportement change, ce sont les step definitions qui cassent… ». On comprend le problème (la colle casse sur une refonte) et la piste (un agent qui voit l'écran) sans lire la suite. Avant correction, la 1re phrase anglaise parlait de « code le plus fragile » sans lien avec le titre : réalignée sur la refonte.

### Le débutant comprend-il chaque slide ?

| Slide | Obstacle | Correction |
|---|---|---|
| 2 | « step definition » expliqué, mais le mot « colle », utilisé dès la 4 et jusqu'à la 11, n'était jamais défini | Commentaire du code : « step definition, la « colle » » + note |
| 7 | « Arbre d'accessibilité » dans le tableau | Lignes renommées « Ce que lit un lecteur d'écran » / « Une capture d'écran », les mots de la slide 3 |
| 9 | « le Contexte » (mot Gherkin) | « le Contexte (étapes communes) » sur la slide + note |
| 10 | « WebKit, Chromium » | « deux navigateurs différents (WebKit, Chromium) » |
| 3, 6, 8, 11 | « agent », « refus », « data-testid », « CI » | Agent et refus définis à la 3 ; data-testid en note de la 8 ; CI connu du public visé. Laissé. |

### Grille du comité (après corrections)

| Critère | Note | Pourquoi |
|---|---|---|
| Unicité | 4 | « Agent + tests » sera vu souvent en 2027 ; mesuré contre Cucumber, avec une refonte et le faux vert, beaucoup moins. |
| Légitimité | 3 | 18 ans de BDD et un banc construit soi-même, mais aucune contribution BDD publique ni retour de production. |
| Promesse | 4 | 3 éléments concrets (où le mettre, 3 règles, le banc) ; « où le mettre » reste une recommandation, pas une mesure en équipe. |
| Concret | 5 | Deux démos live, chiffres datés, dépôt public, run CI citable. |
| Actualité | 4 | Agents de test et MCP navigateur : sujet chaud, vu sous l'angle mûr « où ne pas le mettre ». |
| Clarté | 4 | Titre + 1re phrase compris en 30 s ; « step definitions » suppose de connaître Cucumber, ce qui est le public visé. |
| Risque speaker | 3 | Slides en ligne, dépôt soigné, CI verte ; aucune vidéo ni meetup cité (à compléter dans les notes). |
| Format | 5 | Tools-in-Action : un outil, deux démos, minutage qui tombe à 30 min ; variante Quickie listée. |
| **Total** | **32/40** | Seuil atteint de justesse, aucun critère sous 3. |

### Trois membres du comité, en réunion

- **L'expert blasé** : « Encore un agent qui clique ; mais il a mis Cucumber en face, une refonte et le faux vert, et il dit lui-même de garder Cucumber en CI. Je prends si l'appli à lui ne cache pas tout : il le dit dès les pièges. »
- **Le généraliste** : « Je comprends le titre sans connaître l'outil : la refonte casse les tests, pas l'agent. Le prix au scénario me dit qu'il ne vend rien. »
- **Le défenseur de la diversité des sujets** : « Un talk sur le BDD et la maintenance des tests, pas un énième talk IA : je le pousse, surtout s'il n'est pas rangé dans le track IA. »

### Problèmes trouvés

| Gravité | Où | Problème | Correction |
|---|---|---|---|
| 🔴 | Proposition FR | Absente. | Écrite (format du coach, chiffres repris de la revue 2). |
| 🟡 | Slides 2 → 11 | « Colle » jamais défini. | Défini à la slide 2. |
| 🟡 | Proposition EN | 1re phrase décalée du titre ; « You leave with » sans les deux-points ni les 3 éléments séparés. | Réécrite. |
| 🟡 | Track | « Development practices » sans dire pourquoi ; le track IA serait le plus évident et le plus saturé. | Track tests et qualité recommandé, raison notée. |
| 🟡 | Légitimité et risque speaker à 3 | Rien de citable sur la scène ni sur le BDD en public. | Non réparable sans Mekki : champs « à compléter » dans les notes au comité. |

### Ce qui reste, et pourquoi

- Pas de nouvelle mesure : la cause du +47 % de coût sur v2, l'effet de sélecteurs CSS, le temps humain d'écriture des step definitions restent non mesurés et sont dits comme tels.
- Rendu visuel non contrôlé (aucun navigateur pendant la revue).

## Points qui demandent une décision de Mekki

1. **Titre** : B retenu (« L'écran change : mes step definitions cassent, pas l'agent », 58 caractères) ; A (64 caractères, plus oral) reste possible.
2. **Fusionner `mesures` / `deck-v2` dans `main` avant de soumettre** : la proposition cite le dépôt comme preuve, et `main` n'a pas encore les résultats.
3. **Expérience de scène et accord employeur** : à remplir dans les notes au comité ; c'est le levier pour passer Risque speaker et Légitimité au-dessus de 3 (un passage en meetup ou JUG avant le CFP).
4. **Passage live sur v2 dans la démo 2** (ajouté pour utiliser la minute et demie gagnée) : le garder, ou montrer seulement le tableau et le résumé du run CI.
5. **Vidéo de plan B** : à enregistrer (démo 1 et démo 2).
6. **Track** : vérifier les noms des tracks du CFP visé et choisir celui des tests et de la qualité plutôt que celui de l'IA.
