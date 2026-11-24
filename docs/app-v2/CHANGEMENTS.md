# Appli v2 : refonte d'interface sans changement de comportement

`docs/app-v2/` est une copie de `docs/app/` passée par le genre de refonte qu'une équipe front fait sans
prévenir les testeurs : nouvelle convention de nommage, nouvelle mise en page en grille, composants « carte ».
Elle sert à la mesure de robustesse (PROTOCOLE.md, section « Robustesse ») : on rejoue les mêmes scénarios,
les mêmes step definitions et la même consigne d'agent, et on regarde ce qui casse.

Elle reste autonome : `docs/app-v2/index.html` s'ouvre en `file://`, sans serveur ni dépendance.

## Ce qui ne change pas

- Le comportement : mêmes règles (compte de démo, blocage après 3 essais, produit épuisé, code promo,
  panier vide, conditions de vente, confirmation cachée dans le DOM). Le JavaScript est le même, seuls les
  sélecteurs qu'il utilise ont été renommés.
- Tous les textes visibles cités dans les scénarios : titres, libellés des champs, textes des boutons,
  messages. `parcours.json` est copié tel quel.
- Les adresses des écrans (`#connexion`, `#catalogue`, `#livraison`) et les liens du bandeau.
- Les pièges : trois boutons « Ajouter », bouton désactivé presque aussi visible qu'un bouton actif,
  « Commande confirmée » présent dans le DOM mais caché.

Vérifié avant la mesure : les 11 scénarios justes rejoués avec des localisateurs par rôle, libellé et texte
donnent le même résultat sur v1 et v2 (script ponctuel WebKit headless, non versionné).
`python3 outils/valider.py features docs/app-v2` ne signale qu'une seule différence : l'attribut `data-ecran`
renommé (changement n° 3) ; avec cet attribut remis, il répond `OK`, donc tous les libellés sont présents.

## Les changements

| N° | Changement | Ce qu'un vrai refactoring de front ferait | Sélecteurs concernés |
|---|---|---|---|
| 1 | Tous les `id` renommés avec le préfixe `qc-` et le parcours : `email` → `qc-connexion-email`, `mdp` → `qc-connexion-mdp`, `btn-connexion` → `qc-connexion-envoyer`, `total` → `qc-panier-total`, `panier-compte` → `qc-panier-nb`, `btn-commander` → `qc-panier-commander`, `cgv` → `qc-livraison-cgv`, `confirmation` → `qc-livraison-confirmation`, etc. | Nouvelle convention de nommage pour éviter les collisions quand l'appli est intégrée dans un portail. | sélecteurs `#id` (CSS, XPath, `page.locator("#total")`) |
| 2 | Classes CSS renommées à la BEM avec le préfixe `qc-` : `.produits` → `.qc-catalogue`, `.panier` → `.qc-panier`, `.erreur` → `.qc-message--erreur`, `.info` → `.qc-message--info`, `.epuise` → `.qc-carte__badge`, `.bonjour` → `.qc-entete__salut`, `.confirmation` → `.qc-confirmation`. | Adoption d'une méthode de nommage CSS (BEM) et d'un préfixe d'appli. | sélecteurs `.classe` |
| 3 | Attributs de données renommés : `data-ecran` → `data-vue`, `data-produit` → `data-article`. | Même harmonisation du vocabulaire du code. | `[data-ecran=…]`, `[data-produit=…]` |
| 4 | `data-testid` passés à la convention anglaise du reste du code : `panier-compte` → `cart-count`, `total` → `cart-total`. | Harmonisation des attributs de test avec une bibliothèque de composants partagée (cas fréquent quand le front et les tests ne sont pas écrits par la même équipe). | `getByTestId("panier-compte")`, `getByTestId("total")` |
| 5 | Nom accessible des boutons « Ajouter » : `aria-label` « Ajouter Marteau au panier » → « Ajouter au panier : Marteau » (idem Tournevis, Mètre ruban). Le texte visible reste « Ajouter ». | Recommandation d'un audit d'accessibilité (action d'abord, objet ensuite, nom qui commence toujours par le texte visible). Changement cité par PROTOCOLE.md. | `getByRole(BUTTON, name="Ajouter Marteau au panier")` |
| 6 | Structure : `div.panier` → `section.qc-panier` ; `div#confirmation` → `section` ; chaque champ enveloppé dans un `div.qc-champ` ; la case à cocher passe de `p.choix` à `div.qc-case` ; chaque produit devient une carte (`li.qc-carte` avec des `p` au lieu de `span`). | Passage à des composants « champ », « carte » et à des balises de section. | sélecteurs structurels (`.panier > button`, `li span:first-child`, XPath par position) |
| 7 | Boutons regroupés dans une barre d'actions (`div.qc-barre-actions`) : « Se connecter » ; « Valider la commande » et « Enregistrer l'adresse ». | Composant « barre d'actions » commun à tous les formulaires. | sélecteurs structurels |
| 8 | Ordre changé : dans la barre de livraison, « Valider la commande » passe avant « Enregistrer l'adresse » ; messages d'erreur et d'information (connexion, livraison) déplacés au-dessus du formulaire ; aide « Compte de démo » sous le formulaire ; dans une carte produit, le bouton passe avant le prix ; dans le bandeau, le message « Bonjour … » passe entre le nom de la boutique et la navigation. | Mise en page revue : action principale en premier, messages en haut du formulaire. | sélecteurs par position (`nth`, `first`, XPath `[2]`) |
| 9 | Bouton déplacé : « Commander » quitte le bas du panier pour son en-tête, à côté du titre « Panier ». Le panier passe avant la liste des produits dans le DOM et s'affiche en colonne à droite (grille à deux colonnes). | Action principale toujours visible, panier en colonne latérale. | sélecteurs structurels ou par position |
| 10 | Feuille de style réécrite (grille, cartes, bouton secondaire en blanc pour « Appliquer » et « Enregistrer l'adresse »). Règle `[hidden]{display:none!important}` ajoutée pour que les classes de mise en page ne réaffichent pas un élément caché. | Nouvelle charte. | aucun (sauf tests visuels par capture) |

## Ce que la référence Cucumber utilise, pour lire le résultat

Les step definitions (`src/test/java/.../Etapes.java`) visent déjà des localisateurs « orientés utilisateur » :
titre par rôle, champ par libellé, bouton par rôle et nom accessible, texte exact. Les changements 1, 2, 3,
6 à 10 ne les touchent donc pas. Seuls deux changements touchent leurs localisateurs :

- n° 4 (`data-testid`) : étapes « le panier contient N article(s) » et « le total est … » ;
- n° 5 (nom accessible des boutons « Ajouter ») : étape « j'ajoute … au panier ».

Le résultat mesuré en CI (job `reference-cucumber-v2`) est dans `resultats/LISEZMOI.md`.
