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

Limites : l'appli est petite et écrite par l'auteur du protocole (les pièges sont connus d'avance) ; un seul modèle ; WebKit et non Chrome ; la robustesse quand l'interface change n'est pas encore mesurée (voir PROTOCOLE.md).

## Référence Cucumber + Playwright

Mesurée en CI : 17/17 conformes à l'attendu, 6 pièges sur 6 font bien échouer Cucumber (`outils/verifier_pieges.py`).
