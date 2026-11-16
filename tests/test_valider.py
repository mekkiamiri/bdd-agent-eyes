"""Tests du validateur, du générateur de page et du comparateur (unittest, bibliothèque standard)."""

import json
import re
import shlex
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "outils"))

import comparer  # noqa: E402
import construire_page  # noqa: E402
import valider  # noqa: E402
import verifier_pieges  # noqa: E402

sys.path.insert(0, str(RACINE / "agent"))
import lancer  # noqa: E402

APP = RACINE / "docs" / "app"
ENTETE = "# language: fr\n@parcours:panier\nFonctionnalité: Essai\n\n  Contexte:\n    Soit je suis sur la page \"Catalogue\"\n\n"


def analyser(texte):
    rapport = valider.Rapport()
    f = valider.analyser(texte, "essai.feature", rapport)
    valider.verifier_liens(f, valider.charger_parcours(APP), rapport)
    return f, rapport


class DepotReel(unittest.TestCase):
    def test_les_features_du_depot_sont_valides(self):
        fonctionnalites, rapport = valider.valider(RACINE / "features", APP)
        self.assertEqual(rapport.erreurs, [])
        self.assertEqual({f.parcours for f in fonctionnalites}, {"connexion", "panier", "livraison"})

    def test_chaque_parcours_a_des_scenarios_faux_ou_ambigus(self):
        fonctionnalites, _ = valider.valider(RACINE / "features", APP)
        attendus = {s.attendu for f in fonctionnalites for s in f.scenarios}
        self.assertEqual(attendus, {"passe", "echec", "ambigu"})
        for pid in ("connexion", "panier", "livraison"):
            self.assertTrue(any(s.attendu != "passe" for f in fonctionnalites if f.parcours == pid
                                for s in f.scenarios), pid)

    def test_les_pieges_sont_signales_en_notes(self):
        _, rapport = valider.valider(RACINE / "features", APP)
        self.assertTrue(any("je valide" in n for n in rapport.notes))

    def test_la_page_est_a_jour(self):
        self.assertEqual(construire_page.main(["construire_page.py", "--check"]), 0)


class Syntaxe(unittest.TestCase):
    def test_scenario_correct(self):
        _, r = analyser(ENTETE + "  @attendu:passe\n  Scénario: Ajout\n    Quand j'ajoute \"Marteau\" au panier\n"
                                 "    Alors le panier contient 1 article\n")
        self.assertEqual(r.erreurs, [])

    def test_langue_obligatoire(self):
        _, r = analyser(ENTETE.replace("# language: fr\n", "") + "  @attendu:passe\n  Scénario: A\n"
                        "    Alors le panier contient 0 article\n")
        self.assertTrue(any("language" in e for e in r.erreurs))

    def test_scenario_sans_alors(self):
        _, r = analyser(ENTETE + "  @attendu:passe\n  Scénario: A\n    Quand j'ajoute \"Marteau\" au panier\n")
        self.assertTrue(any("sans « Alors »" in e for e in r.erreurs))

    def test_ordre_soit_quand_alors(self):
        _, r = analyser(ENTETE + "  @attendu:passe\n  Scénario: A\n    Alors le panier contient 0 article\n"
                                 "    Quand j'ajoute \"Marteau\" au panier\n")
        self.assertTrue(any("ordre" in e for e in r.erreurs))

    def test_commence_par_et(self):
        _, r = analyser(ENTETE + "  @attendu:passe\n  Scénario: A\n    Et le panier contient 0 article\n"
                                 "    Alors le panier contient 0 article\n")
        self.assertTrue(any("commence par" in e for e in r.erreurs))

    def test_nom_en_double(self):
        bloc = "  @attendu:passe\n  Scénario: A\n    Alors le panier contient 0 article\n"
        _, r = analyser(ENTETE + bloc + bloc)
        self.assertTrue(any("double" in e for e in r.erreurs))

    def test_plan_du_scenario_non_pris_en_charge(self):
        _, r = analyser(ENTETE + "  Plan du scénario: A\n")
        self.assertTrue(any("pas pris en charge" in e for e in r.erreurs))


class VeriteTerrain(unittest.TestCase):
    def test_tag_attendu_obligatoire(self):
        _, r = analyser(ENTETE + "  Scénario: A\n    Alors le panier contient 0 article\n")
        self.assertTrue(any("@attendu" in e for e in r.erreurs))

    def test_deux_tags_attendus_refuses(self):
        _, r = analyser(ENTETE + "  @attendu:passe @attendu:echec\n  Scénario: A\n    Alors le panier contient 0 article\n")
        self.assertTrue(any("exactement un tag" in e for e in r.erreurs))

    def test_piege_obligatoire_pour_un_scenario_faux(self):
        _, r = analyser(ENTETE + "  @attendu:echec\n  Scénario: A\n    Alors le panier contient 3 articles\n")
        self.assertTrue(any("Piège" in e for e in r.erreurs))

    def test_piege_lu_dans_la_description(self):
        f, r = analyser(ENTETE + "  @attendu:ambigu\n  Scénario: A\n    Piège : lequel ?\n"
                                 "    Quand je clique sur \"Ajouter\"\n    Alors le total est \"12,00 €\"\n")
        self.assertEqual(r.erreurs, [])
        self.assertEqual(f.scenarios[0].piege, "lequel ?")


class LienParcours(unittest.TestCase):
    def test_parcours_inconnu(self):
        _, r = analyser(ENTETE.replace("@parcours:panier", "@parcours:paiement")
                        + "  @attendu:passe\n  Scénario: A\n    Alors le panier contient 0 article\n")
        self.assertTrue(any("parcours inconnu" in e for e in r.erreurs))

    def test_etape_hors_vocabulaire_dans_un_scenario_passe(self):
        _, r = analyser(ENTETE + "  @attendu:passe\n  Scénario: A\n    Quand je valide\n"
                                 "    Alors le panier contient 0 article\n")
        self.assertTrue(any("hors vocabulaire" in e for e in r.erreurs))

    def test_libelle_absent_du_parcours(self):
        _, r = analyser(ENTETE + "  @attendu:passe\n  Scénario: A\n    Quand je clique sur \"Payer\"\n"
                                 "    Alors le panier contient 0 article\n")
        self.assertTrue(any("bouton « Payer »" in e for e in r.erreurs))

    def test_libelle_d_un_parcours_dont_on_depend(self):
        texte = ENTETE.replace("@parcours:panier", "@parcours:livraison") + (
            "  @attendu:passe\n  Scénario: A\n    Quand j'ajoute \"Marteau\" au panier\n"
            "    Alors le bouton \"Valider la commande\" est désactivé\n")
        _, r = analyser(texte)
        self.assertEqual(r.erreurs, [])

    def test_texte_avec_valeur(self):
        self.assertEqual(valider.resoudre_etape('je vois "Bonjour demo@exemple.org"',
                                                valider.charger_parcours(APP), "connexion"), [])
        self.assertNotEqual(valider.resoudre_etape('je vois "Bonjour pirate@exemple.org"',
                                                   valider.charger_parcours(APP), "connexion"), [])

    def test_piege_hors_vocabulaire_note_pas_erreur(self):
        _, r = analyser(ENTETE + "  @attendu:ambigu\n  Scénario: A\n    Piège : flou.\n    Quand je valide\n"
                                 "    Alors c'est bon\n")
        self.assertEqual(r.erreurs, [])
        self.assertEqual(len(r.notes), 2)


class VocabulaireJava(unittest.TestCase):
    def test_meme_vocabulaire_que_les_step_definitions(self):
        java = (RACINE / "src/test/java/io/github/mekkiamiri/bddagent/Etapes.java").read_text(encoding="utf-8")
        expressions_java = set(re.findall(r'@(?:Soit|Quand|Alors)\("([^"]+)"\)', java))
        expressions_python = {expr for _, expr in valider.VOCABULAIRE}
        self.assertEqual(expressions_java, expressions_python)


class TexteAffiche(unittest.TestCase):
    """Les libellés doivent être affichés par l'appli, pas seulement présents dans un commentaire."""

    def copie(self, tmp, html_ajout="", js_ajout="", carte_modif=None):
        app = Path(tmp)
        (app / "index.html").write_text((APP / "index.html").read_text(encoding="utf-8").replace(
            "</main>", html_ajout + "</main>"), encoding="utf-8")
        (app / "app.js").write_text((APP / "app.js").read_text(encoding="utf-8") + js_ajout, encoding="utf-8")
        carte = json.loads((APP / "parcours.json").read_text(encoding="utf-8"))
        carte["parcours"]["panier"]["boutons"].append("Payer maintenant")
        if carte_modif:
            carte_modif(carte)
        (app / "parcours.json").write_text(json.dumps(carte), encoding="utf-8")
        r = valider.Rapport()
        valider.verifier_parcours_dans_appli(valider.charger_parcours(app), app, r)
        return r.erreurs

    def test_libelle_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            erreurs = self.copie(tmp)
        self.assertEqual(len(erreurs), 1)
        self.assertIn("Payer maintenant", erreurs[0])

    def test_libelle_dans_un_commentaire_html_ne_compte_pas(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(len(self.copie(tmp, html_ajout="<!-- Payer maintenant -->")), 1)

    def test_libelle_dans_un_commentaire_js_ne_compte_pas(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(len(self.copie(tmp, js_ajout='\n// $("#x").textContent = "Payer maintenant";\n')), 1)

    def test_libelle_dans_un_selecteur_js_ne_compte_pas(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(len(self.copie(tmp, js_ajout='\nconst x = "Payer maintenant";\n')), 1)

    def test_libelle_affiche_par_le_js(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.copie(tmp, js_ajout='\n$("#x").textContent = "Payer maintenant";\n'), [])

    def test_libelle_affiche_par_le_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.copie(tmp, html_ajout="<button>Payer maintenant</button>"), [])

    def test_ecran_sans_data_ecran(self):
        def renommer(carte):
            carte["parcours"]["panier"]["ecran"] = "Boutique"
        with tempfile.TemporaryDirectory() as tmp:
            erreurs = self.copie(tmp, html_ajout="<h1>Boutique</h1><button>Payer maintenant</button>",
                                 carte_modif=renommer)
        self.assertEqual(len(erreurs), 1)
        self.assertIn("data-ecran", erreurs[0])

    def test_page_hors_du_parcours(self):
        carte = valider.charger_parcours(APP)
        self.assertEqual(valider.resoudre_etape('je suis sur la page "Catalogue"', carte, "livraison"), [])
        self.assertNotEqual(valider.resoudre_etape('je suis sur la page "Connexion"', carte, "livraison"), [])


class PageDeDemo(unittest.TestCase):
    def test_la_page_gere_tout_le_vocabulaire_genere(self):
        page = (RACINE / "docs" / "index.html").read_text(encoding="utf-8")
        bloc = page.split("const CONDITIONS = {", 1)[1].split("\n};", 1)[0]
        cles = set(re.findall(r'^\s*"([^"]+)":', bloc, re.M))
        self.assertEqual(cles, {expr for _, expr in valider.VOCABULAIRE})

    def test_le_vocabulaire_est_genere_dans_scenarios_js(self):
        js = (RACINE / "docs" / "scenarios.js").read_text(encoding="utf-8")
        vocab = json.loads(js.split("window.VOCABULAIRE = ", 1)[1].split(";\nwindow.SCENARIOS", 1)[0])
        self.assertEqual([v["expression"] for v in vocab], [e for _, e in valider.VOCABULAIRE])
        self.assertNotIn("(?P<", js)


class Comparateur(unittest.TestCase):
    # Données synthétiques de test, pas des mesures.
    VERITE = {"a:passe": "passe", "a:faux": "echec", "a:flou": "ambigu"}

    def test_mesures(self):
        res = {"config": "essai", "scenarios": [
            {"id": "a:passe", "verdict": "passe", "duree_s": 1, "cout_usd": 0.5},
            {"id": "a:faux", "verdict": "passe", "duree_s": 2, "cout_usd": 0.5},
            {"id": "a:flou", "verdict": "refus", "duree_s": 3, "cout_usd": 1}]}
        m = comparer.mesurer(res, self.VERITE)
        self.assertEqual((m["justes"], m["faux_positifs"], m["faux_negatifs"], m["refus_justes"]), (2, 1, 0, 1))
        self.assertEqual((m["duree_s"], m["cout_usd"]), (6.0, 2.0))

    def test_trois_passages_ne_s_ecrasent_pas(self):
        lignes = []
        for passage, (v1, v2) in enumerate([("passe", "echec"), ("passe", "passe"), ("passe", "refus")], 1):
            lignes += [{"id": "a:passe", "passage": passage, "verdict": v1, "duree_s": passage},
                       {"id": "a:faux", "passage": passage, "verdict": v2, "duree_s": 1}]
        m = comparer.mesurer({"scenarios": lignes}, self.VERITE)
        self.assertEqual((m["verdicts"], m["justes"], m["faux_positifs"]), (6, 5, 1))
        self.assertEqual(m["stables"], 1)  # a:passe stable, a:faux instable
        self.assertEqual(m["reussite_par_passage"], [1.0, 0.5, 1.0])
        self.assertAlmostEqual(m["reussite_moyenne"], 2.5 / 3)
        self.assertAlmostEqual(m["reussite_variance"], 1 / 18)
        self.assertAlmostEqual(m["variance_duree_s2"], (2 / 3 + 0) / 2)

    def test_passage_implicite_par_ordre(self):
        lignes = [{"id": "a:passe", "verdict": "passe"}, {"id": "a:passe", "verdict": "echec"}]
        groupes = comparer.regrouper({"scenarios": lignes}, self.VERITE)
        self.assertEqual([r["passage"] for r in groupes["a:passe"]], [1, 2])

    def test_passage_en_double(self):
        lignes = [{"id": "a:passe", "passage": 1, "verdict": "passe"},
                  {"id": "a:passe", "passage": 1, "verdict": "echec"}]
        with self.assertRaises(ValueError):
            comparer.mesurer({"scenarios": lignes}, self.VERITE)

    def test_refus_d_un_scenario_juste(self):
        m = comparer.mesurer({"scenarios": [{"id": "a:passe", "verdict": "refus"}]}, self.VERITE)
        self.assertEqual((m["faux_negatifs"], m["refus_injustes"], m["scenarios_joues"]), (1, 1, 1))

    def test_verdict_invalide(self):
        with self.assertRaises(ValueError):
            comparer.mesurer({"scenarios": [{"id": "a:passe", "verdict": "peut-être"}]}, self.VERITE)

    def test_scenario_inconnu(self):
        with self.assertRaises(ValueError):
            comparer.mesurer({"scenarios": [{"id": "z:z", "verdict": "passe"}]}, self.VERITE)

    def test_verite_terrain_du_depot(self):
        verite = comparer.verite_terrain()
        self.assertEqual(verite["panier.feature:Ajouter au panier"], "ambigu")


class LanceurAgent(unittest.TestCase):
    FAUX = f"{shlex.quote(sys.executable)} tests/faux_agent.py"
    AMBIGU = "livraison.feature:La commande est enregistrée"
    JUSTE = "panier.feature:Ajouter un produit"

    def test_l_invite_cache_la_verite_terrain(self):
        texte = lancer.invite(lancer.scenarios()[self.AMBIGU], "file:///app")
        self.assertIn("Et je valide", texte)
        self.assertIn("Contexte:", texte)
        self.assertNotIn("@attendu", texte)
        self.assertNotIn("Piège", texte)
        self.assertNotIn("@parcours", texte)

    def test_faux_agent_bout_en_bout(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = lancer.main(["--config", "essai", "--commande", self.FAUX, "--sortie", tmp, "--passages", "2",
                                "--scenario", self.AMBIGU, "--scenario", self.JUSTE])
            self.assertEqual(code, 0)
            donnees = json.loads((Path(tmp) / "agent-essai" / "resultats.json").read_text(encoding="utf-8"))
        self.assertEqual(len(donnees["scenarios"]), 4)
        self.assertEqual(donnees["erreurs"], [])
        m = comparer.mesurer(donnees, comparer.verite_terrain())
        self.assertEqual((m["verdicts"], m["justes"], m["refus_justes"], m["stables"]), (4, 4, 2, 2))

    def test_reponse_illisible_va_dans_les_erreurs(self):
        with tempfile.TemporaryDirectory() as tmp:
            lancer.main(["--config", "essai", "--commande", self.FAUX + " illisible", "--sortie", tmp,
                         "--passages", "1", "--scenario", self.JUSTE])
            donnees = json.loads((Path(tmp) / "agent-essai" / "resultats.json").read_text(encoding="utf-8"))
        self.assertEqual((len(donnees["scenarios"]), len(donnees["erreurs"])), (0, 1))

    def test_lire_reponse_texte_brut(self):
        verdict, cout = lancer.lire_reponse('blabla {"a": 1} puis {"verdict": "echec", "etape": 2}')
        self.assertEqual((verdict["verdict"], cout), ("echec", 0.0))

    def test_config_mcp_existe_pour_chaque_configuration(self):
        for config in ("arbre", "capture", "les-deux"):
            mcp = json.loads((RACINE / "agent" / f"mcp-{config}.json").read_text(encoding="utf-8"))
            self.assertEqual(mcp["mcpServers"]["playwright"]["args"][0], "@playwright/mcp@0.0.85")


RAPPORT_SUREFIRE = """<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="io.github.mekkiamiri.bddagent.RunCucumberTest">
 <testcase name="Connexion - Message d'accueil personnalisé"><failure type="org.opentest4j.AssertionFailedError" message="Locator expected to be visible"/></testcase>
 <testcase name="Connexion - Connexion rapide"><failure type="com.microsoft.playwright.TimeoutError" message="Timeout 2000ms exceeded."/></testcase>
 <testcase name="Panier - Ajouter un produit épuisé"><error type="com.microsoft.playwright.TimeoutError" message="Timeout 2000ms exceeded."/></testcase>
 <testcase name="Panier - Ajouter au panier"><failure type="com.microsoft.playwright.TimeoutError" message="Timeout"/></testcase>
 <testcase name="Livraison - Message quand les conditions ne sont pas cochées"><failure type="com.microsoft.playwright.TimeoutError" message="Timeout"/></testcase>
 <testcase name="Livraison - La commande est enregistrée"><failure type="io.cucumber.junit.platform.engine.UndefinedStepException" message="The step 'je valide' is undefined."/></testcase>
</testsuite>
"""


class PiegesCucumber(unittest.TestCase):
    def rapports(self, texte):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp)
        (Path(tmp) / "TEST-RunCucumberTest.xml").write_text(texte, encoding="utf-8")
        return verifier_pieges.lire_rapports(Path(tmp))

    def test_tous_les_pieges_echouent_comme_prevu(self):
        self.assertEqual(verifier_pieges.verifier(self.rapports(RAPPORT_SUREFIRE)), [])

    def test_un_piege_qui_passe_est_une_erreur(self):
        texte = RAPPORT_SUREFIRE.replace(
            '<failure type="org.opentest4j.AssertionFailedError" message="Locator expected to be visible"/>', "")
        erreurs = verifier_pieges.verifier(self.rapports(texte))
        self.assertEqual(len(erreurs), 1)
        self.assertIn("Message d'accueil", erreurs[0])

    def test_echec_attendu_mais_etape_non_definie(self):
        texte = RAPPORT_SUREFIRE.replace(
            'type="org.opentest4j.AssertionFailedError" message="Locator expected to be visible"',
            'type="io.cucumber.junit.platform.engine.UndefinedStepException" message="undefined"')
        self.assertEqual(len(verifier_pieges.verifier(self.rapports(texte))), 1)

    def test_erreur_d_infrastructure_n_est_pas_un_echec(self):
        texte = RAPPORT_SUREFIRE.replace(
            'type="com.microsoft.playwright.TimeoutError" message="Timeout 2000ms exceeded."/></testcase>\n <testcase name="Panier',
            'type="java.lang.RuntimeException" message="Failed to create driver"/></testcase>\n <testcase name="Panier', 1)
        self.assertEqual(len(verifier_pieges.verifier(self.rapports(texte))), 1)

    def test_scenario_absent_du_rapport(self):
        texte = "\n".join(l for l in RAPPORT_SUREFIRE.splitlines() if "Connexion rapide" not in l)
        self.assertEqual(len(verifier_pieges.verifier(self.rapports(texte))), 1)


if __name__ == "__main__":
    unittest.main()
