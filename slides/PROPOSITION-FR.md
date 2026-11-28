# Proposition (français)

**Format** : Tools-in-Action (30 min). Existe aussi en Quickie (20 min), voir les notes.
**Track** : pratiques de développement / tests et qualité (pas le track IA, saturé : voir `slides/REVUE.md`)
**Niveau** : intermédiaire
**Langue** : français

## Titre

L'écran change : mes step definitions cassent, pas l'agent

## Abstract

Vous écrivez du Gherkin, et Cucumber le joue grâce à des step definitions, le code de colle qui cherche chaque bouton. Le jour où le front refait l'écran sans changer le comportement, c'est cette colle qui casse : sur mon appli de démo, une refonte casse 7 scénarios sur 17, et 3 autres restent « conformes » sans plus rien tester.

La cible : des scénarios qui survivent aux refontes, avec un verdict expliqué, sans réécrire la colle. En direct, gherkin-eyes, un outil open source que j'ai écrit sur Playwright MCP, fait lire chaque scénario à un agent qui regarde l'écran, clique, et répond passe, échec ou refus (scénario ambigu), avec la capture de l'écran. Mesuré avec le même agent : 204 verdicts justes sur 204 passages, la refonte comprise ; mais 28 s et 12 centimes par scénario.

Vous repartirez avec : gherkin-eyes (une commande, un rapport HTML et un JUnit pour la CI) ; trois gestes : garder Cucumber en CI, lancer l'agent après une refonte ou sur des scénarios neufs, écrire le Gherkin avec trois règles.

(1 018 caractères)

## Notes au comité

```
Pourquoi moi :
- 18 ans de software craftsmanship, BDD pratiqué au quotidien (Gherkin, Cucumber) ;
  référent IA d'un centre de développement logiciel.
- J'ai construit le banc moi-même : appli piégée, vérité terrain étiquetée sur chaque
  scénario, référence Cucumber-JVM + Playwright en CI, lanceur de l'agent.

Ce qui tourne déjà :
- Dépôt : github.com/mekkiamiri/bdd-agent-eyes — l'outil gherkin-eyes (dossier outil/,
  Python sans dépendance, Apache-2.0) : gherkin-eyes features/ --url <appli> → rapport HTML
  + JUnit ; sortie réelle dans outil/exemple/ (17/17 verdicts conformes, 2 min 24 s, 1,98 $).
  CI : validateur, référence Cucumber, pièges, robustesse v2.
- Verdicts vérifiés à l'aveugle : 10 passages (les 6 pièges et 4 justes tirés au hasard), un autre modèle ne voit que
  le scénario et la capture finale : 9 accords, 1 désaccord (refus contre échec, jamais sur
  un « passe »), preuve de l'agent conforme à l'écran 10 fois sur 10 (revue/).
- Mesures publiées (resultats/LISEZMOI.md, 24-25/11/2026, Sonnet 5.5) : agent 153 passages
  sur l'appli d'origine (3 façons de voir × 3 passages), 153 justes, 0 « passe » à tort ;
  51 passages sur l'interface refondue, 51 justes. Cucumber : 17/17 avant, 10/17 après
  (7 scénarios justes cassés par deux changements de localisateurs ; 3 des 10 restants
  ne sont « conformes » que parce que le piège échoue maintenant sur une étape antérieure).
- Démo live : gherkin-eyes sur un scénario (une vingtaine de secondes) et son rapport,
  puis la même commande sur l'interface refondue ; plan B : rapports déjà générés
  (outil/exemple/) et vidéo.

Plan minuté (30 min), en 4 étapes :
- 0-3    départ : Gherkin + Cucumber + step definitions (la colle)
- 3-8    problème : la refonte casse 7 scénarios sur 17 ; 3 faux verts
- 8-15   cible : verdicts qui survivent et s'expliquent ; l'agent, les pièges, les refus
- 15-28  comment : démo de gherkin-eyes (avant et après la refonte), puis 3 gestes
         (Cucumber en CI et le prix ; quand lancer l'agent ; 3 règles d'écriture)
- 28-30  phrase de fin + questions

Limites dites sur scène : l'appli et la refonte sont les miennes (pièges connus d'avance) ;
un seul modèle ; WebKit pour l'agent, Chromium pour Cucumber ; mes step definitions visent
déjà rôles et libellés, des sélecteurs CSS casseraient sans doute plus (non mesuré).

Pas un pitch produit : la conclusion est « gardez Cucumber en CI », l'agent ne sert
que là où la colle ne suit pas.

Expérience de scène : <à compléter par Mekki : meetups, JUG, interne, lien vidéo>
Accord employeur : <à compléter par Mekki>
Adaptable : Quickie 20 min (9 des 13 slides, voir slides/PLAN.md ; la démo de l'outil reste).
```

## Bio

Mekki Amiri est Tech Lead, architecte système et référent IA d'un centre de développement logiciel. Il pratique le software craftsmanship depuis 18 ans, avec DDD, TDD et BDD au cœur de son travail. Il a proposé des contributions (pull requests ouvertes) à Google ADK Java, Spring AI A2A et AG-UI. Il aime les talks où chaque chiffre d'une slide se vérifie dans un dépôt public.
