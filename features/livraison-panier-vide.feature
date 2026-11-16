# language: fr
@parcours:livraison
Fonctionnalité: Livraison sans panier
  Le lien « Livraison » du bandeau mène au formulaire même quand le panier est vide.

  Contexte:
    Soit je suis sur la page "Livraison"

  @attendu:passe
  Scénario: Commande refusée quand le panier est vide
    Quand je saisis "Camille Martin" dans le champ "Nom"
    Et je saisis "69003" dans le champ "Code postal"
    Et je coche "J'accepte les conditions de vente"
    Et je clique sur "Valider la commande"
    Alors je vois "Votre panier est vide."
    Et je ne vois pas "Commande confirmée"
