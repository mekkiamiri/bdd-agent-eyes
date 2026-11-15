package io.github.mekkiamiri.bddagent;

import static com.microsoft.playwright.assertions.PlaywrightAssertions.assertThat;

import com.microsoft.playwright.Browser;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.Playwright;
import com.microsoft.playwright.options.AriaRole;
import io.cucumber.java.After;
import io.cucumber.java.Before;
import io.cucumber.java.fr.Alors;
import io.cucumber.java.fr.Quand;
import io.cucumber.java.fr.Soit;
import java.nio.file.Path;
import java.util.Locale;

/**
 * Step definitions écrites à la main : c'est exactement le code que l'agent « qui voit l'appli »
 * cherche à remplacer. Le vocabulaire doit rester identique à VOCABULAIRE dans outils/valider.py
 * (un test Python le vérifie).
 *
 * Cucumber ignore le mot-clé : une étape @Soit peut être utilisée après « Alors ».
 */
public class Etapes {

    private static final String APP = Path.of("docs/app/index.html").toAbsolutePath().toUri().toString();
    private static final double DELAI_MS = 2_000;

    private static Playwright playwright;
    private static Browser navigateur;

    private BrowserContext contexte;
    private Page page;

    @Before
    public void ouvrir() {
        if (playwright == null) {
            playwright = Playwright.create();
            navigateur = playwright.chromium().launch();
            Runtime.getRuntime().addShutdownHook(new Thread(playwright::close));
        }
        contexte = navigateur.newContext();
        page = contexte.newPage();
        page.setDefaultTimeout(DELAI_MS);
    }

    @After
    public void fermer() {
        contexte.close();
    }

    @Soit("je suis sur la page {string}")
    public void jeSuisSurLaPage(String ecran) {
        page.navigate(APP + "#" + ecran.toLowerCase(Locale.ROOT));
        assertThat(page.getByRole(AriaRole.HEADING, new Page.GetByRoleOptions().setName(ecran).setLevel(1))).isVisible();
    }

    @Soit("je suis connecté")
    public void jeSuisConnecte() {
        jeSuisSurLaPage("Connexion");
        jeSaisis("demo@exemple.org", "Email");
        jeSaisis("bonjour123", "Mot de passe");
        jeCliqueSur("Se connecter");
        jeVois("Bonjour demo@exemple.org");
    }

    @Quand("je saisis {string} dans le champ {string}")
    public void jeSaisis(String valeur, String champ) {
        page.getByLabel(champ, new Page.GetByLabelOptions().setExact(true)).fill(valeur);
    }

    @Quand("je clique sur {string}")
    public void jeCliqueSur(String libelle) {
        // Pas de setExact : « Ajouter » désigne trois boutons, Playwright refuse (mode strict).
        page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName(libelle)).click();
    }

    @Quand("j'ajoute {string} au panier")
    public void jAjouteAuPanier(String produit) {
        page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions()
                .setName("Ajouter " + produit + " au panier").setExact(true)).click();
    }

    @Quand("je coche {string}")
    public void jeCoche(String libelle) {
        page.getByLabel(libelle, new Page.GetByLabelOptions().setExact(true)).check();
    }

    @Alors("je vois {string}")
    public void jeVois(String texte) {
        assertThat(page.getByText(texte)).isVisible();
    }

    @Alors("je ne vois pas {string}")
    public void jeNeVoisPas(String texte) {
        // « Commande confirmée » est toujours dans le DOM : seul un contrôle de visibilité est juste.
        assertThat(page.getByText(texte)).isHidden();
    }

    @Alors("le panier contient {int} article(s)")
    public void lePanierContient(int n) {
        assertThat(page.getByTestId("panier-compte")).hasText(n + (n > 1 ? " articles" : " article"));
    }

    @Alors("le total est {string}")
    public void leTotalEst(String montant) {
        assertThat(page.getByTestId("total")).hasText(montant);
    }

    @Alors("le bouton {string} est désactivé")
    public void leBoutonEstDesactive(String libelle) {
        assertThat(page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName(libelle))).isDisabled();
    }
}
