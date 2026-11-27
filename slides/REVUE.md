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
