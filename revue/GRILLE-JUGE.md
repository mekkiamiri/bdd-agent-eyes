# Grille du juge à l'aveugle (écrite avant les passages)

Question : sur un échantillon de 10 passages de `gherkin-eyes`, le verdict de l'agent correspond-il à ce
qu'affiche l'écran ? Méthode reprise du banc spec-driven du Lab (captures, juge à l'aveugle, grille écrite
avant) ; seule la méthode est reprise, aucun code ni résultat de ce banc. Pas d'écart de pixels ici : il n'y a
pas d'image cible à comparer, seulement l'écran final que l'agent a capturé.

## Échantillon

- Série : `gherkin-eyes features/ --url docs/app/index.html --sans-fenetre` (17 scénarios, 1 passage), le jour de la revue.
- 10 passages tirés par `revue/juge_aveugle.py preparer` (graine fixe 2026) : les 3 scénarios faux, les 3 ambigus,
  4 des 11 justes. Les passages en erreur ne sont pas tirés (relancés avant).
- Chaque passage reçoit un code neutre (P01 à P10, ordre mélangé). Le juge ne voit ni le nom du fichier
  `.feature`, ni les tags, ni les lignes « Piège : », ni le verdict, ni l'explication de l'agent.

## Juge

- Modèle différent de l'agent : Opus 5.5 (l'agent est Sonnet 5.5), via la CLI d'agent en mode non interactif,
  une session neuve par passage, dans un dossier vide, seul outil autorisé : lire l'image.
- Entrée : le scénario Gherkin (tel qu'envoyé à l'agent) et la capture de l'écran final.

## Étape 1 (aveugle) : le verdict que l'écran permet

Pour chaque étape « Alors / Et » du scénario : le résultat attendu est-il visible sur la capture (`oui`, `non`, `illisible`) ?
Puis un verdict :
- `passe` : chaque résultat attendu est visible sur la capture ;
- `echec` : la capture montre un état qui contredit le scénario (autre texte, autre valeur, bouton grisé qu'il fallait utiliser…) ;
- `refus` : la capture montre que le scénario est ambigu (une étape peut désigner plusieurs éléments visibles)
  ou qu'un résultat attendu ne peut pas s'observer à l'écran ;
- `indetermine` : l'écran final ne permet pas de trancher (étape antérieure non visible sur une seule capture).

## Étape 2 (après l'étape 1, session séparée) : la preuve de l'agent est-elle vraie ?

Une nouvelle session du juge reçoit le scénario, la capture et le champ « preuve » de l'agent (ce qu'il dit avoir vu à l'écran), sans son verdict.
Réponse : `oui` (tout ce qui est visible sur la capture est conforme), `partiellement` (au moins une affirmation
contredite par la capture), `non` (la preuve décrit un autre écran). Les affirmations sur des écrans antérieurs,
invisibles sur la capture finale, ne comptent pas comme contredites.

## Comptage (décidé avant)

- Accord : verdict du juge = verdict de l'agent.
- Indéterminé : compté à part, ni accord ni désaccord.
- Désaccord : tout le reste ; chaque désaccord est relu à la main, capture à l'appui, et expliqué dans `slides/REVUE.md`.
- Preuve : nombre de `oui` / `partiellement` / `non` sur 10.
- Un passage dont la capture manque est remplacé par le suivant du tirage, et compté comme « capture manquante ».
