# Plan du deck : Tools-in-Action 30 min (variante Quickie 20 min)

Titre : **L'écran change : mes step definitions cassent, pas l'agent** (choix et autres options : `slides/REVUE.md`, revue 1).

**Objectif du talk** (ce que le public fera lundi) : chacun sait où un agent qui voit l'écran remplace ses step definitions, et où il ne faut surtout pas le mettre ; il peut refaire la mesure sur ses propres scénarios avec le banc du dépôt.

**Promesse** (« vous repartirez avec ») :
1. Les chiffres : 204 verdicts justes sur 204 passages de l'agent, et une refonte d'interface qui casse 7 scénarios Cucumber sur 17 mais aucun verdict de l'agent.
2. Une règle de placement : Cucumber en CI ; l'agent pour relire les scénarios, jouer un écran qui n'a pas encore de colle, et dire si l'appli marche pendant qu'on répare la colle après une refonte.
3. Trois règles pour écrire du Gherkin qu'un agent (et un humain) peut jouer, et le banc pour refaire la mesure chez vous.

**Le message en une phrase** : quand l'interface change sans que le comportement change, ce sont les step definitions qui cassent ; un agent qui regarde l'écran joue les mêmes scénarios Gherkin sans elles (204 verdicts justes sur 204), mais il est lent et payant : voici où le mettre.

Public : développeurs et testeurs qui écrivent ou maintiennent du Gherkin (Cucumber, Playwright), niveau intermédiaire.

Arc : situation (1) · complication : la colle casse au moindre changement d'écran (2) · résolution : l'agent joue sans colle, refuse quand il faut, et tient la refonte (3-8) · revers honnête : le faux vert de Cucumber, puis le prix et les limites (9-10) · recommandation, ancrée sur la complication (11-12) · fin (13).

| n° | titre-phrase | objectif : le public doit penser… | preuve | durée |
|---|---|---|---|---|
| 1 | L'écran change : mes step definitions cassent, pas l'agent | « C'est ma douleur, et il annonce des chiffres. » | annonce de la mesure (détail aux slides 7 et 8) | 1 min |
| 2 | Deux lignes de Gherkin ; derrière, du code qui casse au premier changement d'écran | « C'est mon quotidien : la colle me coûte. » | un vrai scénario + sa step definition (`Etapes.java`, simplifiée) | 2 min |
| 3 | Un agent lit le scénario, regarde l'écran, clique et rend un verdict | « J'ai compris l'idée en 10 secondes. » | schéma en 3 verbes, consigne `agent/CONSIGNE.md` | 2 min |
| 4 | Démo : l'agent joue « Commande valide » en une vingtaine de secondes, sans une ligne de colle | « Ça marche vraiment. » | démo live (plan B : vidéo) ; passages réels de 19 à 25 s | 4 min |
| 5 | J'ai piégé mon appli trois fois ; il ne tombe dans aucun piège | « Il ne clique pas au hasard, et l'auteur ne cache pas que l'appli est la sienne. » | bouton grisé, 3 « Ajouter », texte caché : verdicts réels | 2 min |
| 6 | Devant un scénario ambigu, il refuse, et il dit pourquoi | « Il fait ce qu'un bon testeur fait, et Cucumber ne fait pas. » | un vrai refus tiré des résultats ; 27 refus sur 27 passages ambigus | 2 min |
| 7 | 153 verdicts justes sur 153, jamais un « passe » à tort, quoi qu'il voie | « Ce n'est pas un coup de chance, et je n'ai pas à choisir finement ce qu'il voit. » | 17 scénarios × 3 vues × 3 passages, tableau par vue (durée, coût) | 2 min |
| 8 | Démo : je refonds l'interface ; Cucumber casse 7 scénarios sur 17, l'agent aucun | « C'est exactement ma douleur, et elle disparaît. » | tableau v1 / v2 (CI run 45566605569 + 51 passages agent sur v2), un passage live sur v2 | 5 min 30 |
| 9 | Pire que le rouge : 3 tests échouent encore, mais plus pour la bonne raison | « Mes tests verts peuvent mentir après une refonte. » | les 3 pièges qui échouent ailleurs (`resultats/LISEZMOI.md`) | 2 min |
| 10 | Le prix : 14 s et 6 à 9 centimes par scénario, contre 1,4 s et aucune facture | « Il ne remplacera pas ma CI. » | durées et coûts mesurés + limites | 2 min |
| 11 | Gardez Cucumber en CI ; envoyez l'agent là où la colle ne suit pas | « Je sais où l'essayer lundi. » | les 3 usages, chacun relié à un résultat | 2 min |
| 12 | Ses refus donnent 3 règles : nommez l'objet, le bouton, et ce qu'on voit | « Mes scénarios vont devenir meilleurs, même sans agent. » | les refus regroupés | 1 min 30 |
| 13 | Un bon testeur sait dire non. Et il ne casse pas quand l'écran change. | La phrase à retenir. | dépôt, questions | 2 min (+ questions) |

Total : 30 min. L'ancienne slide 8 (« Capture, arbre ou les deux ») est fondue dans la 7 ; sa minute et demie va à la démo 2.

## Variante Quickie 20 min (9 slides gardées)

Garder **1, 2, 3, 6, 7, 8, 10, 11, 13**. On retire la démo 1 (4) : elle coûte 4 minutes et un risque technique, alors que la démo 2 porte le message (la refonte) et que la slide 6 montre déjà une vraie réponse de l'agent. On retire aussi les pièges (5), le faux vert (9) et les règles d'écriture (12).
À dire en plus, pour ne rien perdre d'honnête : sur la 3, qu'il joue « Commande valide » en une vingtaine de secondes ; sur la 7, que l'appli et ses pièges sont écrits par moi ; à la fin de la 8, le faux vert en une phrase ; sur la 13, les 3 règles d'écriture en une phrase.
Minutage : 1 · 2 · 2 · 2 · 2 · 4 (démo 2 sans passage live, tableau seul) · 2 · 2 · 1,5 = 18 min 30, plus une minute et demie de marge.

## Variante Tools-in-Action 30 min (13 slides gardées)

Toutes : 1 à 13, minutage du tableau ci-dessus.

## Skim test (titres seuls)

Mes step definitions cassent quand l'écran change, pas l'agent → derrière deux lignes de Gherkin, du code qui casse au premier changement d'écran → un agent lit, regarde, clique et juge → il joue un vrai scénario en une vingtaine de secondes → il évite les pièges que j'ai posés dans mon appli → il refuse l'ambigu et explique → 153 sur 153 sans faux « passe », quoi qu'il voie → la refonte casse 7 Cucumber sur 17 et aucun agent → et 3 Cucumber « conformes » ne testent plus rien → mais il coûte 14 s et quelques centimes → donc Cucumber en CI, l'agent là où la colle ne suit pas → écrivez pour qu'il puisse jouer → un bon testeur sait dire non. L'argument et la recommandation tiennent sans le corps des slides.

## Sources des chiffres

`resultats/LISEZMOI.md`, `resultats/synthese-agent.json`, `resultats/agent-*/resultats.json`, `resultats/robustesse-v2/agent-les-deux/resultats.json`, `docs/app-v2/CHANGEMENTS.md`, CI run 45566605569 (job `reference-cucumber-v2`). Chaque note de slide cite le sien.
