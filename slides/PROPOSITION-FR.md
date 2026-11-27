# Proposition (français)

**Format** : Tools-in-Action (30 min). Existe aussi en Quickie (20 min), voir les notes.
**Track** : pratiques de développement / tests et qualité (pas le track IA, saturé : voir `slides/REVUE.md`)
**Niveau** : intermédiaire
**Langue** : français

## Titre

L'écran change : mes step definitions cassent, pas l'agent

## Abstract

Quand l'interface change sans que le comportement change, ce sont les step definitions qui cassent : le Gherkin se lit toujours, mais le code derrière cherchait un libellé reformulé ou un attribut de test renommé, alors que l'appli marche.

En direct, un agent lit chaque scénario, regarde l'écran (capture et arbre d'accessibilité), clique, et répond passe, échec ou refus, sans step definitions. Sur ma petite appli de démo, piégée exprès, avec 17 scénarios dont 6 faux ou ambigus : 204 verdicts justes en 204 passages, chaque ambigu refusé avec sa raison, et une refonte d'interface qui casse 7 scénarios Cucumber sur 17 sans changer un seul verdict de l'agent. Le prix : 14 s et 6 à 9 centimes par scénario, contre 1,4 s pour Cucumber.

Vous repartirez avec : où le mettre (Cucumber en CI ; l'agent pour relire les scénarios, jouer un écran qui n'a pas encore de colle, tenir pendant une refonte) ; trois règles pour écrire du Gherkin qu'un agent peut jouer ; un dépôt public avec l'appli, les scénarios et les résultats bruts, pour refaire la mesure chez vous.

(1 061 caractères)

## Notes au comité

```
Pourquoi moi :
- 18 ans de software craftsmanship, BDD pratiqué au quotidien (Gherkin, Cucumber) ;
  référent IA d'un centre de développement logiciel.
- J'ai construit le banc moi-même : appli piégée, vérité terrain étiquetée sur chaque
  scénario, référence Cucumber-JVM + Playwright en CI, lanceur de l'agent.

Ce qui tourne déjà :
- Dépôt : github.com/mekkiamiri/bdd-agent-eyes — démarrage : python3 outils/valider.py
  (bibliothèque standard seule) ; CI : validateur, référence Cucumber, pièges, robustesse v2.
- Mesures publiées (resultats/LISEZMOI.md, 24-25/11/2026, Sonnet 5.5) : agent 153 passages
  sur l'appli d'origine (3 façons de voir × 3 passages), 153 justes, 0 « passe » à tort ;
  51 passages sur l'interface refondue, 51 justes. Cucumber : 17/17 avant, 10/17 après
  (7 scénarios justes cassés par deux changements de localisateurs ; 3 des 10 restants
  ne sont « conformes » que parce que le piège échoue maintenant sur une étape antérieure).
- Démo live : l'agent joue un scénario (une vingtaine de secondes), puis la refonte côte
  à côte avec un passage live sur la v2 ; plan B : vidéo enregistrée et résumé du run CI.

Plan minuté (30 min) :
- 0-5    la colle casse au premier changement d'écran ; l'idée de l'agent
- 5-13   démo 1, pièges, refus d'un scénario ambigu
- 13-15  la mesure : 153 sur 153, quoi qu'il voie
- 15-22  démo 2 : la refonte (7 Cucumber cassés sur 17, 0 pour l'agent) et le faux vert
- 22-28  le prix, les limites, où mettre l'agent, 3 règles d'écriture
- 28-30  phrase de fin + questions

Limites dites sur scène : l'appli et la refonte sont les miennes (pièges connus d'avance) ;
un seul modèle ; WebKit pour l'agent, Chromium pour Cucumber ; mes step definitions visent
déjà rôles et libellés, des sélecteurs CSS casseraient sans doute plus (non mesuré).

Pas un pitch produit : la conclusion est « gardez Cucumber en CI », l'agent ne sert
que là où la colle ne suit pas.

Expérience de scène : <à compléter par Mekki : meetups, JUG, interne, lien vidéo>
Accord employeur : <à compléter par Mekki>
Adaptable : Quickie 20 min (9 des 13 slides : sans la démo 1, la démo de la refonte reste).
```

## Bio

Mekki Amiri est Tech Lead, architecte système et référent IA d'un centre de développement logiciel. Il pratique le software craftsmanship depuis 18 ans, avec DDD, TDD et BDD au cœur de son travail. Il a proposé des contributions (pull requests ouvertes) à Google ADK Java, Spring AI A2A et AG-UI. Il aime les talks où chaque chiffre d'une slide se vérifie dans un dépôt public.
