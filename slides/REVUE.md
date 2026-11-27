# Revue du deck « L'écran change : mes step definitions cassent, pas l'agent »

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
