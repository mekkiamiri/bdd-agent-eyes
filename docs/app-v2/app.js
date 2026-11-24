// Appli de démo « La Quincaillerie », version 2 (interface refondue, même comportement : voir CHANGEMENTS.md).
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
  const sel = "h1, h2, [role=alert], [role=alert] li, [role=status], #qc-salut, #qc-panier-total, #qc-panier-nb, " +
    "#qc-panier-lignes li, .qc-carte p, .qc-confirmation p";
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
  document.querySelectorAll("[data-vue]").forEach((s) => { s.hidden = s.dataset.vue !== ecran; });
  signaler("ecran", ecran);
}
window.addEventListener("hashchange", afficher);

// ---------- Connexion ----------
$("#qc-connexion-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const email = $("#qc-connexion-email").value.trim();
  const ok = email === COMPTE.email && $("#qc-connexion-mdp").value === COMPTE.mdp;
  if (ok) {
    etat.connecte = email;
    etat.echecs = 0;
    $("#qc-connexion-erreur").textContent = "";
    $("#qc-salut").textContent = "Bonjour " + email;
  } else {
    etat.echecs += 1;
    if (etat.echecs >= 3) {
      $("#qc-connexion-envoyer").disabled = true;
      $("#qc-connexion-erreur").textContent = "Compte bloqué après 3 essais. Réessayez plus tard.";
    } else {
      $("#qc-connexion-erreur").textContent = "Email ou mot de passe incorrect.";
    }
  }
  signaler("action", "Se connecter");
});

// ---------- Panier ----------
function nbArticles() {
  return Object.values(etat.panier).reduce((a, b) => a + b, 0);
}
function rendrePanier() {
  const lignes = $("#qc-panier-lignes");
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
  $("#qc-panier-nb").textContent = n + (n > 1 ? " articles" : " article");
  $("#qc-panier-total").textContent = euros(total);
  $("#qc-panier-commander").disabled = n === 0;
}
document.querySelectorAll("[data-article]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const p = btn.dataset.article;
    etat.panier[p] = (etat.panier[p] || 0) + 1;
    rendrePanier();
    signaler("action", btn.getAttribute("aria-label"));
  });
});
$("#qc-promo-appliquer").addEventListener("click", () => {
  const code = $("#qc-promo-code").value.trim().toUpperCase();
  if (code === CODE_PROMO) {
    etat.promo = true;
    $("#qc-promo-message").textContent = "Code BIENVENUE appliqué : -10 %";
  } else {
    etat.promo = false; // un code inconnu retire la remise déjà appliquée
    $("#qc-promo-message").textContent = "Code promo inconnu.";
  }
  rendrePanier();
  signaler("action", "Appliquer");
});
$("#qc-panier-commander").addEventListener("click", () => {
  signaler("action", "Commander");
  location.hash = "#livraison";
});

// ---------- Livraison ----------
function erreursLivraison() {
  const erreurs = [];
  // On peut arriver ici par le lien « Livraison » du bandeau, panier vide : la commande est refusée.
  if (nbArticles() === 0) erreurs.push("Votre panier est vide.");
  if ($("#qc-livraison-nom").value.trim() === "") erreurs.push("Le nom est obligatoire.");
  if (!/^\d{5}$/.test($("#qc-livraison-cp").value.trim())) erreurs.push("Le code postal doit contenir 5 chiffres.");
  const ul = $("#qc-livraison-erreurs");
  ul.innerHTML = "";
  for (const m of erreurs) {
    const li = document.createElement("li");
    li.textContent = m;
    ul.appendChild(li);
  }
  return erreurs;
}
$("#qc-livraison-cgv").addEventListener("change", () => {
  // Piège : le bouton « Valider la commande » reste désactivé tant que la case n'est pas cochée,
  // et aucun message ne l'explique.
  $("#qc-livraison-valider").disabled = !$("#qc-livraison-cgv").checked;
  signaler("action", "J'accepte les conditions de vente");
});
$("#qc-livraison-enregistrer").addEventListener("click", () => {
  $("#qc-livraison-info").textContent = erreursLivraison().length ? "" : "Adresse enregistrée.";
  signaler("action", "Enregistrer l'adresse");
});
$("#qc-livraison-form").addEventListener("submit", (e) => {
  e.preventDefault();
  if (erreursLivraison().length === 0 && $("#qc-livraison-cgv").checked) {
    $("#qc-livraison-form").hidden = true;
    $("#qc-livraison-info").textContent = "";
    $("#qc-livraison-confirmation").hidden = false;
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
