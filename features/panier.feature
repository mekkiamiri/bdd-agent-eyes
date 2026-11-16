# language: fr
@parcours:panier
Fonctionnalité: Panier
  Je choisis des produits et je vois le total de mon panier.

  Contexte:
    Soit je suis sur la page "Catalogue"

  @attendu:passe
  Scénario: Ajouter un produit
    Quand j'ajoute "Marteau" au panier
    Alors le panier contient 1 article
    Et le total est "12,00 €"

  @attendu:passe
  Scénario: Code promo de bienvenue
    Soit j'ajoute "Marteau" au panier
    Et j'ajoute "Mètre ruban" au panier
    Quand je saisis "BIENVENUE" dans le champ "Code promo"
    Et je clique sur "Appliquer"
    Alors je vois "Code BIENVENUE appliqué : -10 %"
    Et le total est "19,71 €"

  @attendu:passe
  Scénario: Panier vide, commande impossible
    Alors le panier contient 0 article
    Et le bouton "Commander" est désactivé

  @attendu:echec
  Scénario: Ajouter un produit épuisé
    Piège : « Tournevis » est épuisé et son bouton « Ajouter » est désactivé. Il ne faut ni forcer le clic ni conclure que le scénario passe.
    Quand j'ajoute "Tournevis" au panier
    Alors le panier contient 1 article

  @attendu:ambigu
  Scénario: Ajouter au panier
    Piège : trois boutons affichent « Ajouter » et le scénario ne dit pas lequel. Le total laisse deviner « Marteau », mais deviner n'est pas tester.
    Quand je clique sur "Ajouter"
    Alors le total est "12,00 €"

  @attendu:passe
  Scénario: Un code inconnu retire la remise
    Soit j'ajoute "Marteau" au panier
    Et je saisis "BIENVENUE" dans le champ "Code promo"
    Et je clique sur "Appliquer"
    Quand je saisis "FAUX" dans le champ "Code promo"
    Et je clique sur "Appliquer"
    Alors je vois "Code promo inconnu."
    Et le total est "12,00 €"
