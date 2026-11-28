"""Tests de gherkin-eyes, sans modèle ni navigateur (faux agent). Lancer : python3 -m unittest discover -s outil/tests"""

import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

OUTIL = Path(__file__).resolve().parent.parent
DEPOT = OUTIL.parent
sys.path.insert(0, str(OUTIL))

from gherkin_eyes import cli  # noqa: E402
from gherkin_eyes.agent import config_mcp, lire_reponse  # noqa: E402
from gherkin_eyes.gherkin import ErreurGherkin, filtre_tags, lire  # noqa: E402
from gherkin_eyes.rapport import ecrire_junit  # noqa: E402
from unittest import mock  # noqa: E402

FAUX = f'"{sys.executable}" "{OUTIL / "tests" / "faux_agent.py"}" --mcp-config {{mcp}}'

FEATURE_EN = """@shop
Feature: Cart
  Free text that must never reach the agent.

  Background:
    Given I am on the "Catalogue" page

  @wip
  Scenario: Add
    The answer is hidden here.
    When I add "Hammer" to the cart
    Then I see:
      | product | qty |
      | Hammer  | 1   |

  Scenario Outline: Promo <code>
    When I type "<code>" in "Promo"
    Then I see "<message>"
    Examples:
      | code      | message       |
      | WELCOME   | -10 %         |
      | WRONG     | Unknown code. |
"""


class Gherkin(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.tmp = Path(d.name)

    def ecrire(self, texte, nom="a.feature"):
        f = self.tmp / nom
        f.write_text(texte, encoding="utf-8")
        return f

    def test_depot_francais(self):
        scen = [s for f in sorted((DEPOT / "features").glob("*.feature")) for s in lire(f)]
        self.assertEqual(len(scen), 17)
        epuise = next(s for s in scen if s.nom == "Ajouter un produit épuisé")
        texte = epuise.gherkin()
        self.assertNotIn("Piège", texte)
        self.assertNotIn("@attendu", texte)
        self.assertIn("Soit je suis sur la page \"Catalogue\"", texte)
        self.assertIn("@attendu:echec", epuise.tags)
        self.assertIn("@parcours:panier", epuise.tags)

    def test_anglais_description_tableau_plan(self):
        scen = lire(self.ecrire(FEATURE_EN))
        self.assertEqual([s.nom for s in scen], ["Add", "Promo WELCOME #1", "Promo WRONG #2"])
        texte = scen[0].gherkin()
        self.assertNotIn("Free text", texte)
        self.assertNotIn("hidden", texte)
        self.assertIn("| Hammer  | 1   |", texte)
        self.assertIn('Then I see "Unknown code."', scen[2].gherkin())
        self.assertEqual(scen[0].tags, ["@shop", "@wip"])

    def test_doc_string(self):
        scen = lire(self.ecrire('Feature: F\n  Scenario: S\n    Then I see\n      """\n      # pas un commentaire\n      """\n'))
        self.assertIn("# pas un commentaire", scen[0].gherkin())

    def test_mots_cles_francais_et_apostrophe(self):
        scen = lire(self.ecrire('Fonctionnalité: F\n  Scénario: S\n    Sachant je suis connecté\n'
                                '    Etant données les commandes\n    Lorsqu’il clique sur "B"\n    Alors je vois "C"\n'))
        self.assertEqual(len(scen[0].etapes), 4)
        self.assertTrue(scen[0].gherkin().startswith("# language: fr"))

    def test_ligne_inconnue_apres_une_etape(self):
        with self.assertRaises(ErreurGherkin):
            lire(self.ecrire("Feature: F\n  Scenario: S\n    Given a\n    Puis b\n"))

    def test_doc_string_non_ferme(self):
        with self.assertRaises(ErreurGherkin):
            lire(self.ecrire('Feature: F\n  Scenario: S1\n    Given a\n      """\n  Scenario: S2\n    Given b\n'))

    def test_tags_de_regle(self):
        scen = lire(self.ecrire("Feature: F\n  @lent\n  Rule: R\n    Scenario: S\n      Given a\n"))
        self.assertEqual(scen[0].tags, ["@lent"])

    def test_exemples_mal_formes(self):
        with self.assertRaises(ErreurGherkin):
            lire(self.ecrire("Feature: F\n  Scenario Outline: S\n    Given <a>\n    Examples:\n"
                             "      | a | b |\n      | 1 |\n"))

    def test_tags(self):
        f = filtre_tags("@a and not (@b or @c)")
        self.assertTrue(f(["@a"]))
        self.assertFalse(f(["@a", "@c"]))
        self.assertTrue(filtre_tags(None)([]))
        with self.assertRaises(ValueError):
            filtre_tags("@a and")
        with self.assertRaises(ValueError):
            filtre_tags("a")


class Agent(unittest.TestCase):
    def test_reponse_cli_json(self):
        v, cout = lire_reponse(json.dumps({"result": 'ok {"verdict": "refus", "etape": 2}', "total_cost_usd": 0.05}))
        self.assertEqual((v["verdict"], cout), ("refus", 0.05))

    def test_reponse_echappements(self):
        v, _ = lire_reponse('{"verdict": "echec", "explication": "l\\\'appli"}')
        self.assertEqual(v["verdict"], "echec")

    def test_reponse_illisible(self):
        self.assertEqual(lire_reponse("rien")[0], None)

    def test_verdict_imbrique_ignore(self):
        v, _ = lire_reponse('{"verdict": "echec", "etapes": [{"n": 1, "verdict": "passe"}]}')
        self.assertEqual(v["verdict"], "echec")

    def test_passe_en_prose_jamais_lu(self):
        self.assertIsNone(lire_reponse('si tout allait bien je mettrais "verdict": "passe". Mais non.')[0])

    def test_verdicts_contradictoires(self):
        self.assertIsNone(lire_reponse('{"verdict": "passe"} puis finalement {"verdict": "echec"}')[0])

    def test_enveloppe_en_erreur(self):
        self.assertIsNone(lire_reponse(json.dumps({"result": '{"verdict": "passe"}', "is_error": True}))[0])

    def test_config_mcp(self):
        args = config_mcp("arbre", Path("/c"), True, True)["mcpServers"]["playwright"]["args"]
        self.assertIn("--allow-unrestricted-file-access", args)
        self.assertEqual(args[-3:], ["--browser", "webkit", "--headless"])
        self.assertIn("omit", args)
        self.assertNotIn("--headless", config_mcp("les-deux", Path("/c"), False, False)["mcpServers"]["playwright"]["args"])


class Rapport(unittest.TestCase):
    def test_junit_sans_caracteres_de_controle(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "j.xml"
            ecrire_junit(f, [dict(fichier="a.feature", scenario="S", passage=1, verdict="echec", duree_s=1,
                                  explication="rouge \x1b[31m", preuve="nul \x00")])
            racine = ET.parse(f).getroot()
            self.assertEqual((racine.get("tests"), racine.get("failures")), ("1", "1"))


class Commande(unittest.TestCase):
    def setUp(self):
        patch = mock.patch.object(cli, "ESPACEMENT_S", 0)
        patch.start()
        self.addCleanup(patch.stop)

    def lancer(self, *extra):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        sortie = Path(d.name) / "rapport"
        code = cli.main([str(DEPOT / "features" / "panier.feature"), "--url", str(DEPOT / "docs" / "app" / "index.html"),
                         "--sortie", str(sortie), "--commande", FAUX, *extra])
        return code, sortie

    def test_bout_en_bout(self):
        code, sortie = self.lancer("-j", "3")
        self.assertEqual(code, 1)  # un échec et un refus
        donnees = json.loads((sortie / "resultats.json").read_text(encoding="utf-8"))
        b = donnees["bilan"]
        self.assertEqual((b["passages"], b["passe"], b["echec"], b["refus"], b["erreur"]), (6, 4, 1, 1, 0))
        self.assertEqual(b["conformes"], 6)
        p = donnees["passages"][0]
        self.assertTrue((sortie / p["capture"]).exists())
        for f in ("resultats.json", "junit.xml", "rapport.html"):
            self.assertNotIn(str(Path.home()), (sortie / f).read_text(encoding="utf-8"))
        self.assertEqual(len({p["capture"] for p in donnees["passages"]}), 6)  # un dossier par passage
        self.assertEqual(list(sortie.rglob("mcp.json")), [])
        junit = ET.parse(sortie / "junit.xml").getroot()
        suite = junit.find("testsuite")
        self.assertEqual((suite.get("tests"), suite.get("failures"), suite.get("errors")), ("6", "2", "0"))
        types = sorted(f.get("type") for f in junit.iter("failure"))
        self.assertEqual(types, ["echec", "refus"])
        page = (sortie / "rapport.html").read_text(encoding="utf-8")
        self.assertIn("conformes à l'attendu", page)
        self.assertIn("<img", page)

    def test_filtre_et_tout_passe(self):
        code, sortie = self.lancer("--tags", "@attendu:passe", "--passages", "2")
        self.assertEqual(code, 0)
        donnees = json.loads((sortie / "resultats.json").read_text(encoding="utf-8"))
        self.assertEqual(donnees["bilan"]["passages"], 8)
        self.assertIn("[passage 2]", (sortie / "junit.xml").read_text(encoding="utf-8"))

    def test_reponse_illisible_donne_erreur(self):
        code, sortie = self.lancer("--commande", FAUX + " illisible", "--scenario", "Ajouter un produit")
        self.assertEqual(code, 2)
        self.assertIn("<error", (sortie / "junit.xml").read_text(encoding="utf-8"))

    def test_navigateur_absent_relance_puis_erreur(self):
        code, sortie = self.lancer("--commande", FAUX + " navigateur-absent", "--scenario", "Ajouter un produit")
        self.assertEqual(code, 2)
        donnees = json.loads((sortie / "resultats.json").read_text(encoding="utf-8"))
        self.assertEqual(len(donnees["erreurs_relancees"]), 2)
        self.assertIn("navigateur indisponible", donnees["passages"][0]["erreur"])

    def test_json_presque_valide(self):
        code, sortie = self.lancer("--commande", FAUX + " presque-json", "--scenario", "Ajouter au panier")
        p = json.loads((sortie / "resultats.json").read_text(encoding="utf-8"))["passages"][0]
        self.assertEqual((p["verdict"], p["etape"], p["lecture"]), ("refus", 1, "tolerante"))
        self.assertIn('"Ajouter"', p["explication"])

    def test_aucun_scenario(self):
        self.assertEqual(self.lancer("--tags", "@inexistant")[0], 2)

    def test_erreurs_d_usage_code_3(self):
        self.assertEqual(cli.main([str(DEPOT / "features"), "--url", "nulle/part.html"]), 3)
        self.assertEqual(self.lancer("--tags", "@a and")[0], 3)
        self.assertEqual(cli.main(["absent/", "--url", "http://x"]), 3)
        self.assertEqual(cli.main([str(DEPOT / "features"), "--url", "http://x", "--passages", "0"]), 3)


if __name__ == "__main__":
    unittest.main()
