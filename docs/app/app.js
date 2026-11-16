// Appli de démo « La Quincaillerie » : HTML et JavaScript sans dépendance.
// Elle fonctionne en file:// (référence Cucumber + Playwright) comme sur GitHub Pages.
// Quand elle est dans un cadre (page de démo), elle envoie à la page parente ce que l'utilisateur
// fait et ce qui est visible à l'écran, pour suivre le scénario Gherkin en cours.
"use strict";

const COMPTE = { email: "demo@exemple.org", mdp: "bonjour123" };
const PRIX = { "Marteau": 1200, "Tournevis": 650, "Mètre ruban": 990 }; // en centimes
const CODE_PROMO = "BIENVENUE";

const etat = { echecs: 0, connecte: null, panier: {}, promo: false };

const $ = (sel) => document.querySelector(sel);
const euros = (c) => (c / 100).toFixed(2).replace(".", ",") + " €";

// ---------- Suivi par la page parente ----------
function visible(el) {
  return el && !el.closest("[hidden]") && el.textContent.trim() !== "";
}
function textesVisibles() {
  const sel = "h1, h2, [role=alert], [role=alert] li, [role=status], #bonjour, #total, #panier-compte, #lignes-panier li, " +
    ".produits li span, .confirmation p";
  return [...document.querySelectorAll(sel)].filter(visible).map((el) => el.textContent.trim());
}
function signaler(type, libelle) {
  if (window.parent === window) return;
  const desactives = [...document.querySelectorAll("button:disabled")].filter((b) => !b.closest("[hidden]"))
    .map((b) => b.textContent.trim());
  // Même origine que la page de démo (GitHub Pages ou serveur local). En file://, l'origine est opaque
  // (« null ») et ne peut pas servir de cible : seul ce cas utilise "*".
  const cible = location.origin === "null" ? "*" : location.origin;
  window.parent.postMessage({ source: "quincaillerie", type, libelle, textes: textesVisibles(), desactives,
    ecran: location.hash.slice(1) || "connexion" }, cible);
}

// ---------- Navigation ----------
function afficher() {
  const ecran = (location.hash.slice(1) || "connexion");
  document.querySelectorAll("[data-ecran]").forEach((s) => { s.hidden = s.dataset.ecran !== ecran; });
  signaler("ecran", ecran);
}
window.addEventListener("hashchange", afficher);

// ---------- Connexion ----------
$("#form-connexion").addEventListener("submit", (e) => {
  e.preventDefault();
  const email = $("#email").value.trim();
  const ok = email === COMPTE.email && $("#mdp").value === COMPTE.mdp;
  if (ok) {
    etat.connecte = email;
    etat.echecs = 0;
    $("#erreur-connexion").textContent = "";
    $("#bonjour").textContent = "Bonjour " + email;
  } else {
    etat.echecs += 1;
    if (etat.echecs >= 3) {
      $("#btn-connexion").disabled = true;
      $("#erreur-connexion").textContent = "Compte bloqué après 3 essais. Réessayez plus tard.";
    } else {
      $("#erreur-connexion").textContent = "Email ou mot de passe incorrect.";
    }
  }
  signaler("action", "Se connecter");
});

// ---------- Panier ----------
function nbArticles() {
  return Object.values(etat.panier).reduce((a, b) => a + b, 0);
}
function rendrePanier() {
  const lignes = $("#lignes-panier");
  lignes.innerHTML = "";
  let total = 0;
  for (const [produit, qte] of Object.entries(etat.panier)) {
    total += PRIX[produit] * qte;
    const li = document.createElement("li");
    li.textContent = `${produit} × ${qte}`;
    lignes.appendChild(li);
  }
  if (etat.promo) total = Math.round(total * 0.9);
  const n = nbArticles();
  $("#panier-compte").textContent = n + (n > 1 ? " articles" : " article");
  $("#total").textContent = euros(total);
  $("#btn-commander").disabled = n === 0;
}
document.querySelectorAll("[data-produit]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const p = btn.dataset.produit;
    etat.panier[p] = (etat.panier[p] || 0) + 1;
    rendrePanier();
    signaler("action", btn.getAttribute("aria-label"));
  });
});
$("#btn-promo").addEventListener("click", () => {
  const code = $("#promo").value.trim().toUpperCase();
  if (code === CODE_PROMO) {
    etat.promo = true;
    $("#message-promo").textContent = "Code BIENVENUE appliqué : -10 %";
  } else {
    etat.promo = false; // un code inconnu retire la remise déjà appliquée
    $("#message-promo").textContent = "Code promo inconnu.";
  }
  rendrePanier();
  signaler("action", "Appliquer");
});
$("#btn-commander").addEventListener("click", () => {
  signaler("action", "Commander");
  location.hash = "#livraison";
});

// ---------- Livraison ----------
function erreursLivraison() {
  const erreurs = [];
  // On peut arriver ici par le lien « Livraison » du bandeau, panier vide : la commande est refusée.
  if (nbArticles() === 0) erreurs.push("Votre panier est vide.");
  if ($("#nom").value.trim() === "") erreurs.push("Le nom est obligatoire.");
  if (!/^\d{5}$/.test($("#cp").value.trim())) erreurs.push("Le code postal doit contenir 5 chiffres.");
  const ul = $("#erreurs-livraison");
  ul.innerHTML = "";
  for (const m of erreurs) {
    const li = document.createElement("li");
    li.textContent = m;
    ul.appendChild(li);
  }
  return erreurs;
}
$("#cgv").addEventListener("change", () => {
  // Piège : le bouton « Valider la commande » reste désactivé tant que la case n'est pas cochée,
  // et aucun message ne l'explique.
  $("#btn-valider").disabled = !$("#cgv").checked;
  signaler("action", "J'accepte les conditions de vente");
});
$("#btn-enregistrer").addEventListener("click", () => {
  $("#info-livraison").textContent = erreursLivraison().length ? "" : "Adresse enregistrée.";
  signaler("action", "Enregistrer l'adresse");
});
$("#form-livraison").addEventListener("submit", (e) => {
  e.preventDefault();
  if (erreursLivraison().length === 0 && $("#cgv").checked) {
    $("#form-livraison").hidden = true;
    $("#info-livraison").textContent = "";
    $("#confirmation").hidden = false;
  }
  signaler("action", "Valider la commande");
});

// Saisie : signalée à la page parente (libellé du champ + valeur).
document.querySelectorAll("input:not([type=checkbox])").forEach((input) => {
  input.addEventListener("change", () => {
    const label = document.querySelector(`label[for="${input.id}"]`);
    signaler("saisie", (label ? label.textContent : input.id) + "=" + input.value);
  });
});


rendrePanier();
afficher();
