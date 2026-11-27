# Plan du deck : Tools-in-Action 30 min (variante Quickie 20 min)

**Le message en une phrase** : vos step definitions sont le code le plus fragile de votre projet ; un agent qui regarde l'écran joue vos scénarios Gherkin sans elles (204 verdicts justes sur 204) et survit à une refonte d'interface qui casse 7 scénarios Cucumber sur 17, mais il est lent et payant : voici où le mettre.

Public : développeurs et testeurs qui écrivent ou maintiennent du Gherkin. Ce qu'ils emportent : où mettre un agent (et où ne pas le mettre) et trois règles pour écrire du Gherkin qu'il peut jouer.

Arc : situation (1) · complication : la colle casse au moindre changement d'écran (2) · résolution : l'agent joue sans colle, refuse quand il faut, et tient la refonte (3-9) · revers honnête : le faux vert de Cucumber, puis le prix et les limites (10-11) · recommandation, ancrée sur la complication (12-13) · fin (14).

| n° | titre-phrase | ce que je veux dire | durée |
|---|---|---|---|
| 1 | Vos scénarios Gherkin se jouent sans step definitions | La promesse du talk, et qu'elle sera chiffrée. | 1 min |
| 2 | Deux lignes de Gherkin ; derrière, du code qui casse au premier changement d'écran | Le scénario se lit, la colle dépend d'un détail invisible (aria-label). | 2 min |
| 3 | Un agent lit le scénario, regarde l'écran, clique et rend un verdict | L'idée en trois verbes, avec le droit de refuser. | 2 min |
| 4 | Démo : l'agent joue « Commande valide » en 20 secondes, sans une ligne de colle | Ça marche pour de vrai (plan B : vidéo enregistrée la veille). | 4 min |
| 5 | Trois pièges : un bouton grisé, trois « Ajouter », un texte caché | L'appli est piégée exprès ; l'agent ne tombe dans aucun. | 2 min |
| 6 | Devant un scénario ambigu, il refuse, et il dit pourquoi | Un vrai refus tiré des résultats ; Cucumber, lui, échoue sans expliquer. | 2 min |
| 7 | 153 verdicts justes sur 153, et jamais un « passe » à tort | La mesure : 17 scénarios × 3 façons de voir × 3 passages, 0 faux positif. | 2 min |
| 8 | Capture, arbre ou les deux : même résultat, presque même prix | Ce qu'il voit change peu ; durée et coût comparés. | 1,5 min |
| 9 | Démo : je refonds l'interface ; Cucumber casse 7 scénarios sur 17, l'agent aucun | Le cœur : même comportement, nouvelle interface, tableau côte à côte. | 4 min |
| 10 | Pire que le rouge : 3 tests échouent encore, mais plus pour la bonne raison | Le faux « conforme » : les pièges ne sont plus testés. | 2 min |
| 11 | Le prix : 14 s et 6 à 9 centimes par scénario, contre 1,4 s et aucune facture | Lent et payant, et les limites de la mesure dites franchement. | 2 min |
| 12 | Gardez Cucumber en CI ; envoyez l'agent là où la colle ne suit pas | Relire les scénarios, explorer un nouvel écran, rattraper une refonte. | 2 min |
| 13 | Ses refus donnent 3 règles : nommez l'objet, le bouton, et ce qu'on voit | Du Gherkin qu'un agent (et un humain) peut jouer. | 1,5 min |
| 14 | Un bon testeur sait dire non. Et il ne casse pas quand l'écran change. | La phrase à retenir, le dépôt, questions. | 2 min (+ questions) |

Total : 30 min.

## Variante Quickie 20 min (9 slides)

Garder 1, 2, 3, 6, 7, 9, 11, 12, 14. Parmi les 10 proposées (1, 2, 3, 4, 6, 7, 9, 11, 12, 14), on retire la démo 1 (slide 4) : elle coûte 4 minutes et un risque technique, alors que la démo 2 porte le message (la refonte) et que la slide 6 montre déjà une vraie réponse de l'agent. Sur la slide 3, dire en une phrase qu'il joue « Commande valide » en 20 secondes. Minutage : 1 · 2 · 2 · 2 · 2 · 4 · 2 · 2 · 2 = 19 min, plus une minute de marge.

## Skim test

Lus seuls, les titres racontent : on peut jouer du Gherkin sans step definitions → la colle casse au premier changement d'écran → un agent lit, regarde, clique et juge → il joue un vrai scénario → il évite les pièges → il refuse l'ambigu et explique → 153 sur 153 sans faux « passe » → ce qu'il voit change peu → la refonte casse 7 Cucumber sur 17 et aucun agent → et 3 Cucumber « conformes » ne testent plus rien → mais il coûte 14 s et quelques centimes → donc Cucumber en CI, l'agent là où la colle ne suit pas → écrivez pour qu'il puisse jouer → un bon testeur sait dire non. L'argument et la recommandation tiennent sans le corps des slides.

## Sources des chiffres

`resultats/LISEZMOI.md`, `resultats/synthese-agent.json`, `resultats/agent-*/resultats.json`, `resultats/robustesse-v2/agent-les-deux/resultats.json`, `docs/app-v2/CHANGEMENTS.md`, CI run 45566605569 (job `reference-cucumber-v2`). Chaque note de slide cite le sien.
