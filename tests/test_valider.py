"""Tests du validateur, du générateur de page et du comparateur (unittest, bibliothèque standard)."""

import json
import re
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
        for f in fonctionnalites:
            self.assertTrue(any(s.attendu != "passe" for s in f.scenarios), f.fichier)

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

    def test_libelle_du_parcours_absent_de_l_appli(self):
        with tempfile.TemporaryDirectory() as tmp:
            app = Path(tmp)
            for nom in ("index.html", "app.js"):
                shutil.copy(APP / nom, app / nom)
            carte = json.loads((APP / "parcours.json").read_text(encoding="utf-8"))
            carte["parcours"]["panier"]["boutons"].append("Payer maintenant")
            (app / "parcours.json").write_text(json.dumps(carte), encoding="utf-8")
            r = valider.Rapport()
            valider.verifier_parcours_dans_appli(valider.charger_parcours(app), app, r)
            self.assertEqual(len(r.erreurs), 1)
            self.assertIn("Payer maintenant", r.erreurs[0])


class VocabulaireJava(unittest.TestCase):
    def test_meme_vocabulaire_que_les_step_definitions(self):
        java = (RACINE / "src/test/java/io/github/mekkiamiri/bddagent/Etapes.java").read_text(encoding="utf-8")
        expressions_java = set(re.findall(r'@(?:Soit|Quand|Alors)\("([^"]+)"\)', java))
        expressions_python = {expr for _, expr in valider.VOCABULAIRE}
        self.assertEqual(expressions_java, expressions_python)


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

    def test_refus_d_un_scenario_juste(self):
        m = comparer.mesurer({"scenarios": [{"id": "a:passe", "verdict": "refus"}]}, self.VERITE)
        self.assertEqual((m["faux_negatifs"], m["refus_injustes"], m["joues"]), (1, 1, 1))

    def test_verdict_invalide(self):
        with self.assertRaises(ValueError):
            comparer.mesurer({"scenarios": [{"id": "a:passe", "verdict": "peut-être"}]}, self.VERITE)

    def test_scenario_inconnu(self):
        with self.assertRaises(ValueError):
            comparer.mesurer({"scenarios": [{"id": "z:z", "verdict": "passe"}]}, self.VERITE)

    def test_verite_terrain_du_depot(self):
        verite = comparer.verite_terrain()
        self.assertEqual(verite["panier.feature:Ajouter au panier"], "ambigu")


if __name__ == "__main__":
    unittest.main()
