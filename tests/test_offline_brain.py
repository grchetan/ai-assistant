"""
================================================================================
            TEST SUITE: OFFLINE AI & NEURAL SUBSYSTEMS
================================================================================
Comprehensive verification for in-house offline intelligence:
  • MasterOfflineBrain dispatch logic
  • Symbolic math, calculus & quadratic solver
  • Neural NLP parser & sentiment analyzer
  • Entity recognition
  • Periodic table & scientific encyclopedia
  • System troubleshooter expert system
================================================================================
"""

import unittest
from jarvis.brain.offline_ai.master_offline_brain import get_offline_brain
from jarvis.brain.offline_ai.symbolic_math import get_math_engine
from jarvis.neural.nlp_parser import get_neural_parser
from jarvis.neural.entity_recognizer import get_entity_recognizer
from jarvis.neural.complete_periodic_table import get_full_periodic_table
from jarvis.neural.world_geography_dataset import get_world_geography
from jarvis.neural.astronomy_deep_catalog import get_astronomy_catalog
from jarvis.neural.math_formula_sheet import get_formula_sheet
from jarvis.security.security_suite_pro import get_security_suite


class TestOfflineBrainSubsystem(unittest.TestCase):
    """Test suite verifying all offline cognitive components."""

    def setUp(self):
        self.brain = get_offline_brain()
        self.math = get_math_engine()
        self.parser = get_neural_parser()
        self.ner = get_entity_recognizer()

    def test_quadratic_solver(self):
        msg, roots = self.math.solve_quadratic(1, -5, 6)
        self.assertIn("Two real distinct roots", msg)
        self.assertEqual(len(roots), 2)
        self.assertAlmostEqual(roots[0].real, 3.0)
        self.assertAlmostEqual(roots[1].real, 2.0)

    def test_differentiation(self):
        deriv = self.math.differentiate_polynomial("3x^2 + 4x - 5")
        self.assertIn("6x + 4", deriv)

    def test_unit_conversion(self):
        res = self.math.convert_units(100, "C", "F")
        self.assertIn("212.00°F", res)

    def test_sentiment_analysis(self):
        pos = self.parser.analyze_sentiment("Jarvis is amazing, excellent and brilliant!")
        self.assertEqual(pos["label"], "POSITIVE")
        neg = self.parser.analyze_sentiment("System is slow, horrible, broken and lagging.")
        self.assertEqual(neg["label"], "NEGATIVE")

    def test_entity_recognition(self):
        text = "Download 15.5 MB from 192.168.1.1 in 30 seconds for ₹500"
        entities = self.ner.extract_entities(text)
        self.assertIn("192.168.1.1", entities["ipv4"])
        self.assertTrue(len(entities["durations"]) > 0)
        self.assertEqual(entities["durations"][0]["value"], 30)

    def test_periodic_table(self):
        pt = get_full_periodic_table()
        gold = pt.search_element("gold")
        self.assertIsNotNone(gold)
        self.assertEqual(gold["z"], 79)
        self.assertEqual(gold["sym"], "Au")

    def test_world_geography(self):
        geo = get_world_geography()
        india = geo.lookup_country("India")
        self.assertIsNotNone(india)
        self.assertEqual(india["capital"], "New Delhi")

    def test_master_brain_integration(self):
        ans_math = self.brain.process_query("solve quadratic 1 x^2 - 5 x + 6")
        self.assertIn("distinct roots", ans_math)

        ans_geo = self.brain.process_query("what is the capital of Japan")
        self.assertIn("Tokyo", ans_geo)

        ans_code = self.brain.process_query("code quicksort")
        self.assertIn("quicksort", ans_code)

    def test_password_entropy(self):
        sec = get_security_suite()
        res = sec.calculate_password_entropy("P@ssw0rd1234!#$")
        self.assertGreater(res["bits"], 50)


if __name__ == "__main__":
    unittest.main()
