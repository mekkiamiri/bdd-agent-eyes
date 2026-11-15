// Généré par outils/construire_page.py à partir de features/*.feature : ne pas modifier.
window.SCENARIOS = [
 {
  "id": "connexion.feature:Connexion réussie",
  "fonctionnalite": "Connexion",
  "parcours": "connexion",
  "nom": "Connexion réussie",
  "attendu": "passe",
  "piege": "",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Connexion\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "je saisis \"demo@exemple.org\" dans le champ \"Email\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je saisis \"bonjour123\" dans le champ \"Mot de passe\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Se connecter\"",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "je vois \"Bonjour demo@exemple.org\"",
    "contexte": false
   }
  ]
 },
 {
  "id": "connexion.feature:Mauvais mot de passe",
  "fonctionnalite": "Connexion",
  "parcours": "connexion",
  "nom": "Mauvais mot de passe",
  "attendu": "passe",
  "piege": "",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Connexion\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "je saisis \"demo@exemple.org\" dans le champ \"Email\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je saisis \"mauvais\" dans le champ \"Mot de passe\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Se connecter\"",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "je vois \"Email ou mot de passe incorrect.\"",
    "contexte": false
   }
  ]
 },
 {
  "id": "connexion.feature:Compte bloqué après trois échecs",
  "fonctionnalite": "Connexion",
  "parcours": "connexion",
  "nom": "Compte bloqué après trois échecs",
  "attendu": "passe",
  "piege": "",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Connexion\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "je saisis \"demo@exemple.org\" dans le champ \"Email\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je saisis \"mauvais\" dans le champ \"Mot de passe\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Se connecter\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Se connecter\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Se connecter\"",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "je vois \"Compte bloqué après 3 essais. Réessayez plus tard.\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "le bouton \"Se connecter\" est désactivé",
    "contexte": false
   }
  ]
 },
 {
  "id": "connexion.feature:Message d'accueil personnalisé",
  "fonctionnalite": "Connexion",
  "parcours": "connexion",
  "nom": "Message d'accueil personnalisé",
  "attendu": "echec",
  "piege": "l'appli affiche « Bonjour demo@exemple.org », jamais « Bienvenue, Demo ». Le scénario est faux, l'appli est juste.",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Connexion\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "je saisis \"demo@exemple.org\" dans le champ \"Email\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je saisis \"bonjour123\" dans le champ \"Mot de passe\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Se connecter\"",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "je vois \"Bienvenue, Demo\"",
    "contexte": false
   }
  ]
 },
 {
  "id": "connexion.feature:Connexion rapide",
  "fonctionnalite": "Connexion",
  "parcours": "connexion",
  "nom": "Connexion rapide",
  "attendu": "ambigu",
  "piege": "« Connexion » est un lien du bandeau, pas un bouton, et « je suis connecté » ne dit pas ce qu'il faut voir à l'écran.",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Connexion\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "je clique sur \"Connexion\"",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "je suis connecté",
    "contexte": false
   }
  ]
 },
 {
  "id": "livraison.feature:Commande valide",
  "fonctionnalite": "Livraison",
  "parcours": "livraison",
  "nom": "Commande valide",
  "attendu": "passe",
  "piege": "",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Catalogue\"",
    "contexte": true
   },
   {
    "mot": "Et",
    "texte": "j'ajoute \"Marteau\" au panier",
    "contexte": true
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Commander\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "je saisis \"Camille Martin\" dans le champ \"Nom\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je saisis \"12 rue des Lilas\" dans le champ \"Adresse\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je saisis \"69003\" dans le champ \"Code postal\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je coche \"J'accepte les conditions de vente\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Valider la commande\"",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "je vois \"Commande confirmée\"",
    "contexte": false
   }
  ]
 },
 {
  "id": "livraison.feature:Code postal invalide",
  "fonctionnalite": "Livraison",
  "parcours": "livraison",
  "nom": "Code postal invalide",
  "attendu": "passe",
  "piege": "",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Catalogue\"",
    "contexte": true
   },
   {
    "mot": "Et",
    "texte": "j'ajoute \"Marteau\" au panier",
    "contexte": true
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Commander\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "je saisis \"Camille Martin\" dans le champ \"Nom\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je saisis \"6900\" dans le champ \"Code postal\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Enregistrer l'adresse\"",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "je vois \"Le code postal doit contenir 5 chiffres.\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je ne vois pas \"Adresse enregistrée.\"",
    "contexte": false
   }
  ]
 },
 {
  "id": "livraison.feature:Conditions de vente non acceptées",
  "fonctionnalite": "Livraison",
  "parcours": "livraison",
  "nom": "Conditions de vente non acceptées",
  "attendu": "passe",
  "piege": "",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Catalogue\"",
    "contexte": true
   },
   {
    "mot": "Et",
    "texte": "j'ajoute \"Marteau\" au panier",
    "contexte": true
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Commander\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "je saisis \"Camille Martin\" dans le champ \"Nom\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je saisis \"69003\" dans le champ \"Code postal\"",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "le bouton \"Valider la commande\" est désactivé",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je ne vois pas \"Commande confirmée\"",
    "contexte": false
   }
  ]
 },
 {
  "id": "livraison.feature:Message quand les conditions ne sont pas cochées",
  "fonctionnalite": "Livraison",
  "parcours": "livraison",
  "nom": "Message quand les conditions ne sont pas cochées",
  "attendu": "echec",
  "piege": "le bouton est désactivé et l'appli n'affiche aucun message. Le scénario décrit un comportement qui n'existe pas.",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Catalogue\"",
    "contexte": true
   },
   {
    "mot": "Et",
    "texte": "j'ajoute \"Marteau\" au panier",
    "contexte": true
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Commander\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "je saisis \"Camille Martin\" dans le champ \"Nom\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je saisis \"69003\" dans le champ \"Code postal\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Valider la commande\"",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "je vois \"Veuillez accepter les conditions de vente\"",
    "contexte": false
   }
  ]
 },
 {
  "id": "livraison.feature:La commande est enregistrée",
  "fonctionnalite": "Livraison",
  "parcours": "livraison",
  "nom": "La commande est enregistrée",
  "attendu": "ambigu",
  "piege": "« je valide » peut viser « Enregistrer l'adresse » ou « Valider la commande », et « la commande est enregistrée » n'a aucun critère visible.",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Catalogue\"",
    "contexte": true
   },
   {
    "mot": "Et",
    "texte": "j'ajoute \"Marteau\" au panier",
    "contexte": true
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Commander\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "je saisis \"Camille Martin\" dans le champ \"Nom\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je saisis \"69003\" dans le champ \"Code postal\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je valide",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "la commande est enregistrée",
    "contexte": false
   }
  ]
 },
 {
  "id": "panier.feature:Ajouter un produit",
  "fonctionnalite": "Panier",
  "parcours": "panier",
  "nom": "Ajouter un produit",
  "attendu": "passe",
  "piege": "",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Catalogue\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "j'ajoute \"Marteau\" au panier",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "le panier contient 1 article",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "le total est \"12,00 €\"",
    "contexte": false
   }
  ]
 },
 {
  "id": "panier.feature:Code promo de bienvenue",
  "fonctionnalite": "Panier",
  "parcours": "panier",
  "nom": "Code promo de bienvenue",
  "attendu": "passe",
  "piege": "",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Catalogue\"",
    "contexte": true
   },
   {
    "mot": "Soit",
    "texte": "j'ajoute \"Marteau\" au panier",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "j'ajoute \"Mètre ruban\" au panier",
    "contexte": false
   },
   {
    "mot": "Quand",
    "texte": "je saisis \"BIENVENUE\" dans le champ \"Code promo\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "je clique sur \"Appliquer\"",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "je vois \"Code BIENVENUE appliqué : -10 %\"",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "le total est \"19,71 €\"",
    "contexte": false
   }
  ]
 },
 {
  "id": "panier.feature:Panier vide, commande impossible",
  "fonctionnalite": "Panier",
  "parcours": "panier",
  "nom": "Panier vide, commande impossible",
  "attendu": "passe",
  "piege": "",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Catalogue\"",
    "contexte": true
   },
   {
    "mot": "Alors",
    "texte": "le panier contient 0 article",
    "contexte": false
   },
   {
    "mot": "Et",
    "texte": "le bouton \"Commander\" est désactivé",
    "contexte": false
   }
  ]
 },
 {
  "id": "panier.feature:Ajouter un produit épuisé",
  "fonctionnalite": "Panier",
  "parcours": "panier",
  "nom": "Ajouter un produit épuisé",
  "attendu": "echec",
  "piege": "« Tournevis » est épuisé et son bouton « Ajouter » est désactivé. Il ne faut ni forcer le clic ni conclure que le scénario passe.",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Catalogue\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "j'ajoute \"Tournevis\" au panier",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "le panier contient 1 article",
    "contexte": false
   }
  ]
 },
 {
  "id": "panier.feature:Ajouter au panier",
  "fonctionnalite": "Panier",
  "parcours": "panier",
  "nom": "Ajouter au panier",
  "attendu": "ambigu",
  "piege": "trois boutons affichent « Ajouter » et le scénario ne dit pas lequel. Le total laisse deviner « Marteau », mais deviner n'est pas tester.",
  "etapes": [
   {
    "mot": "Soit",
    "texte": "je suis sur la page \"Catalogue\"",
    "contexte": true
   },
   {
    "mot": "Quand",
    "texte": "je clique sur \"Ajouter\"",
    "contexte": false
   },
   {
    "mot": "Alors",
    "texte": "le total est \"12,00 €\"",
    "contexte": false
   }
  ]
 }
];
