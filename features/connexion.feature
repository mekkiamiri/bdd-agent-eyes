# language: fr
@parcours:connexion
Fonctionnalité: Connexion
  Pour retrouver mon panier, je me connecte avec mon compte.

  Contexte:
    Soit je suis sur la page "Connexion"

  @attendu:passe
  Scénario: Connexion réussie
    Quand je saisis "demo@exemple.org" dans le champ "Email"
    Et je saisis "bonjour123" dans le champ "Mot de passe"
    Et je clique sur "Se connecter"
    Alors je vois "Bonjour demo@exemple.org"

  @attendu:passe
  Scénario: Mauvais mot de passe
    Quand je saisis "demo@exemple.org" dans le champ "Email"
    Et je saisis "mauvais" dans le champ "Mot de passe"
    Et je clique sur "Se connecter"
    Alors je vois "Email ou mot de passe incorrect."

  @attendu:passe
  Scénario: Compte bloqué après trois échecs
    Quand je saisis "demo@exemple.org" dans le champ "Email"
    Et je saisis "mauvais" dans le champ "Mot de passe"
    Et je clique sur "Se connecter"
    Et je clique sur "Se connecter"
    Et je clique sur "Se connecter"
    Alors je vois "Compte bloqué après 3 essais. Réessayez plus tard."
    Et le bouton "Se connecter" est désactivé

  @attendu:echec
  Scénario: Message d'accueil personnalisé
    Piège : l'appli affiche « Bonjour demo@exemple.org », jamais « Bienvenue, Demo ». Le scénario est faux, l'appli est juste.
    Quand je saisis "demo@exemple.org" dans le champ "Email"
    Et je saisis "bonjour123" dans le champ "Mot de passe"
    Et je clique sur "Se connecter"
    Alors je vois "Bienvenue, Demo"

  @attendu:ambigu
  Scénario: Connexion rapide
    Piège : « Connexion » est un lien du bandeau, pas un bouton, et « je suis connecté » ne dit pas ce qu'il faut voir à l'écran.
    Quand je clique sur "Connexion"
    Alors je suis connecté
