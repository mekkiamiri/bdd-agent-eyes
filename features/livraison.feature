# language: fr
@parcours:livraison
Fonctionnalité: Livraison
  Après le panier, je donne mon adresse et je valide ma commande.

  Contexte:
    Soit je suis sur la page "Catalogue"
    Et j'ajoute "Marteau" au panier
    Et je clique sur "Commander"

  @attendu:passe
  Scénario: Commande valide
    Quand je saisis "Camille Martin" dans le champ "Nom"
    Et je saisis "12 rue des Lilas" dans le champ "Adresse"
    Et je saisis "69003" dans le champ "Code postal"
    Et je coche "J'accepte les conditions de vente"
    Et je clique sur "Valider la commande"
    Alors je vois "Commande confirmée"

  @attendu:passe
  Scénario: Code postal invalide
    Quand je saisis "Camille Martin" dans le champ "Nom"
    Et je saisis "6900" dans le champ "Code postal"
    Et je clique sur "Enregistrer l'adresse"
    Alors je vois "Le code postal doit contenir 5 chiffres."
    Et je ne vois pas "Adresse enregistrée."

  @attendu:passe
  Scénario: Conditions de vente non acceptées
    Quand je saisis "Camille Martin" dans le champ "Nom"
    Et je saisis "69003" dans le champ "Code postal"
    Alors le bouton "Valider la commande" est désactivé
    Et je ne vois pas "Commande confirmée"

  @attendu:echec
  Scénario: Message quand les conditions ne sont pas cochées
    Piège : le bouton est désactivé et l'appli n'affiche aucun message. Le scénario décrit un comportement qui n'existe pas.
    Quand je saisis "Camille Martin" dans le champ "Nom"
    Et je saisis "69003" dans le champ "Code postal"
    Et je clique sur "Valider la commande"
    Alors je vois "Veuillez accepter les conditions de vente"

  @attendu:ambigu
  Scénario: La commande est enregistrée
    Piège : « je valide » peut viser « Enregistrer l'adresse » ou « Valider la commande », et « la commande est enregistrée » n'a aucun critère visible.
    Quand je saisis "Camille Martin" dans le champ "Nom"
    Et je saisis "69003" dans le champ "Code postal"
    Et je valide
    Alors la commande est enregistrée
