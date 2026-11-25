# Résultats

## Agent qui voit l'appli (24/11/2026, 153 passages valides)

Modèle : Sonnet 5.5, en mode non interactif. Navigateur : WebKit de Playwright en mode headless (`agent/lancer.py --sans-fenetre`), parce que Chrome headless est interdit par la politique du poste de mesure. 17 scénarios (11 justes, 3 faux, 3 ambigus) × 3 façons de voir l'écran × 3 passages.

| Ce que voit l'agent | Passages | Verdicts justes | Faux positifs | Durée moyenne | Coût moyen |
|---|---|---|---|---|---|
| arbre d'accessibilité seul | 51 | **51** | 0 | 13,9 s | 0,069 $ |
| capture d'écran seule | 51 | **51** | 0 | 13,4 s | 0,062 $ |
| les deux | 51 | **51** | 0 | 13,4 s | 0,059 $ |

Verdict juste = « passe » sur un scénario juste, « echec » sur un scénario faux, « refus » sur un scénario ambigu.
Données : `agent-<config>/resultats.json` ; synthèse : `synthese-agent.json`.

Passages écartés puis relancés (champ `erreurs_ecartees`) : 31, dont 23 erreurs d'accès au modèle (identifiants expirés, coupure du proxy) et 8 réponses dont le JSON était mal échappé par l'agent (`\'`, `\"`) ; le lecteur tolère désormais ces échappements. Aucun verdict n'a été corrigé à la main.

Limites : l'appli est petite et écrite par l'auteur du protocole (les pièges sont connus d'avance) ; un seul modèle ; WebKit et non Chrome. Robustesse quand l'interface change : voir la section suivante.

## Robustesse (interface v2)

Question : l'interface change, le comportement non. Qu'est-ce qui casse ?
`docs/app-v2/` est une copie de l'appli avec une refonte d'interface réaliste (10 changements décrits dans
`docs/app-v2/CHANGEMENTS.md`) : `id`, classes, attributs `data-*` et `data-testid` renommés, `aria-label` des
trois boutons « Ajouter » reformulé (texte visible inchangé), `div` → `section`, boutons regroupés dans une barre,
ordre changé, bouton « Commander » déplacé. Mêmes textes visibles, mêmes règles, mêmes scénarios.
Ni les scénarios, ni les step definitions, ni la consigne de l'agent n'ont été touchés.

### Cucumber + Playwright sur v2 (CI, job `reference-cucumber-v2`, run 45566605569, 25/11/2026)

Le job joue les 17 scénarios sur `docs/app` puis sur `docs/app-v2`, dans le même lancement, et compare
(`outils/rapport_robustesse.py`, rapport dans le résumé du run et l'artefact `robustesse-v2`).

| | Appli d'origine (même job) | Appli v2 |
|---|---|---|
| Scénarios conformes à la vérité terrain | 17/17 | 10/17 |
| Scénarios justes qui passent | 11/11 | **4/11** (7 cassés) |
| Pièges qui échouent pour la raison prévue | 6/6 | **3/6** (3 échouent ailleurs) |
| Durée de la suite (Surefire) | 23,9 s | 35,1 s (chaque étape cassée attend le délai de 2 s) |

Cassés (7) : tous les scénarios qui passent par l'une de ces deux étapes, et seulement eux.
- « j'ajoute … au panier » cherche le bouton par son nom accessible « Ajouter Marteau au panier » ;
  v2 l'appelle « Ajouter au panier : Marteau » (changement n° 5) : Panier · Ajouter un produit, Code promo de
  bienvenue, Un code inconnu retire la remise ; Livraison · Commande valide, Code postal invalide, Conditions de
  vente non acceptées (le Contexte de livraison ajoute un Marteau).
- « le panier contient N article(s) » lit `data-testid="panier-compte"`, devenu `cart-count` (changement n° 4) :
  Panier · Panier vide, commande impossible.

Les 4 scénarios justes qui passent encore (connexion ×3, livraison panier vide) n'utilisent que titres, libellés
de champs, boutons par leur texte et textes exacts : les renommages d'`id` et de classes, les changements de
structure, d'ordre et la place du bouton ne les touchent pas.

Pièges qui échouent toujours, mais plus pour la bonne raison (3) : un vert trompeur, la suite dit « conforme »
alors qu'elle ne teste plus le piège.
- Livraison · Message quand les conditions ne sont pas cochées : échouait sur « je clique sur "Valider la
  commande" » (bouton désactivé) ; échoue désormais dans le Contexte, sur « j'ajoute "Marteau" au panier ».
- Livraison · La commande est enregistrée : échouait sur l'étape non définie « je valide » ; échoue désormais
  dans le Contexte, sur « j'ajoute "Marteau" au panier ».
- Panier · Ajouter un produit épuisé : même étape, autre cause. Sur l'appli d'origine, Playwright trouvait le
  bouton et attendait qu'il soit activé ; sur v2, il ne trouve plus aucun bouton de ce nom (journal Playwright
  de l'artefact). Ce cas n'est pas détecté par le script, qui compare l'étape en échec, pas la cause.

Les pièges toujours bien attrapés (3) : Message d'accueil personnalisé, Connexion rapide, Ajouter au panier.

### Agent sur v2 (25/11/2026, 51 passages)

`python3 -I agent/lancer.py --config les-deux --passages 3 --sans-fenetre --url <file:// de docs/app-v2/index.html>
--sortie resultats/robustesse-v2`. Même modèle (Sonnet 5.5), même consigne, WebKit headless, capture et arbre
d'accessibilité. Données : `robustesse-v2/agent-les-deux/resultats.json`.

| | Passages | Verdicts justes | Faux positifs | Faux négatifs | Refus justes | Stables | Durée moyenne | Coût moyen | Coût total |
|---|---|---|---|---|---|---|---|---|---|
| Agent, appli d'origine (24/11) | 51 | 51 | 0 | 0 | 9/9 | 17/17 | 13,4 s | 0,059 $ | 3,02 $ |
| Agent, appli v2 (25/11) | 51 | **51** | 0 | 0 | 9/9 | 17/17 | 14,3 s | 0,087 $ | 4,44 $ |

Aucun passage en erreur sur v2 : rien n'a été écarté ni relancé (`erreurs_ecartees` absent). Durée réelle de la
série : 12 min 8 s pour les 51 passages. Les 3 scénarios faux sont refusés en `echec` et les 3 ambigus en `refus`,
à chaque passage. Sur « Ajouter un produit épuisé », l'agent cite le nouveau nom du bouton (« Ajouter au panier :
Tournevis », grisé) : il a lu l'interface v2, pas un souvenir de v1.

### Comparaison

| | Cucumber + Playwright | Agent (capture + arbre) |
|---|---|---|
| Verdicts justes sur v1 | 17/17 | 51/51 passages |
| Verdicts justes sur v2 | 10/17, dont 3 pièges « conformes » pour une mauvaise raison | 51/51 passages |
| Ce qu'il a fallu changer pour v2 | 2 step definitions à réécrire (nom accessible du bouton produit, `data-testid` du compteur) ; le `data-testid` du total, renommé aussi, n'a pas été atteint car les scénarios qui le lisent cassent avant | rien |
| Durée | 35,1 s pour les 17 scénarios (un seul passage, CI) | 14,3 s par passage, 12 min 8 s pour 51 passages |
| Coût | minutes de CI GitHub (pas de facture au scénario) | 0,087 $ par passage, 4,44 $ la série |

Lecture : Cucumber casse sur les deux changements qui touchent ses localisateurs, et seulement sur eux. Les step
definitions de ce dépôt sont déjà écrites « à la Testing Library » (rôles, libellés, textes) : des sélecteurs CSS
ou XPath auraient aussi cassé sur les changements 1, 2, 6 à 9. Cela n'a pas été mesuré ici.

Coût : +47 % par passage sur v2 par rapport à la mesure de la veille, sur 16 scénarios sur 17. La cause n'est pas
établie : le résultat ne garde que le coût, pas le nombre de jetons (pistes non vérifiées : page plus longue dans
l'arbre d'accessibilité, cache de l'invite moins utilisé sur une série unique).

Limites : une seule refonte, écrite par l'auteur du protocole, qui savait quelles étapes Cucumber utilise (le
changement d'`aria-label` vient de PROTOCOLE.md ; le renommage des `data-testid` est un choix de l'auteur,
documenté dans CHANGEMENTS.md : sans lui, seul le changement d'`aria-label` toucherait les localisateurs de Cucumber) ; une seule
configuration d'agent (les deux) sur v2 ; un seul modèle ; 3 passages ; WebKit pour l'agent, Chromium pour
Cucumber ; mesures de l'agent sur v1 et v2 à un jour d'écart.

## Référence Cucumber + Playwright

Mesurée en CI : 17/17 conformes à l'attendu, 6 pièges sur 6 font bien échouer Cucumber (`outils/verifier_pieges.py`).
