"""
================================================================================
                UNIT TESTS: COGNITION & INTERACTIVE MULTIMEDIA
================================================================================
Verifies Vector Semantic Memory RAG search, Knowledge Graph BFS pathfinding,
Prompt Engineering templating, Cyberpunk RPG logic, and Habit Tracking.
================================================================================
"""

import sys
import os
import unittest
from pathlib import Path

# Ensure root workspace is in sys.path
WORKSPACE_DIR = Path(__file__).resolve().parent.parent
if str(WORKSPACE_DIR) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_DIR))

from jarvis.cognition.vector_memory import get_vector_memory
from jarvis.cognition.knowledge_graph import get_knowledge_graph
from jarvis.cognition.prompt_templates import get_prompt_engine

from jarvis.interactive.interactive_rpg import get_rpg_game
from jarvis.interactive.pomodoro_timer import get_pomodoro_coach
from jarvis.interactive.habit_tracker import get_habit_tracker


class TestCognitionAndInteractive(unittest.TestCase):
    """Unit tests for Cognitive RAG and Interactive subsystems."""

    def test_vector_semantic_search(self):
        vm = get_vector_memory()
        vm.add_document("doc1", "Python programming language for machine learning and artificial intelligence", "tech")
        vm.add_document("doc2", "Delicious Italian pizza and pasta recipes with tomatoes and cheese", "food")
        vm.add_document("doc3", "Cyberpunk futuristic flying cars and neon city lights", "scifi")

        # Query semantic relevance
        res = vm.search_semantic("neural networks AI python code", top_k=1)
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0]["id"], "doc1")

    def test_knowledge_graph_traversal(self):
        kg = get_knowledge_graph()
        kg.add_relation("Tony Stark", "CREATED", "JARVIS")
        kg.add_relation("JARVIS", "CONTROLS", "Arc Reactor")

        relations = kg.get_related_entities("Tony Stark")
        self.assertTrue(len(relations) >= 1)

        path = kg.find_path("Tony Stark", "Arc Reactor")
        self.assertIsNotNone(path)
        self.assertEqual(path, ["Tony Stark", "JARVIS", "Arc Reactor"])

    def test_prompt_templating(self):
        engine = get_prompt_engine()
        formatted = engine.format_template(
            "scientific_explanation",
            topic="Quantum Superposition",
            user_name="Master"
        )
        self.assertIn("Quantum Superposition", formatted)
        self.assertIn("Master", formatted)

    def test_cyberpunk_rpg_engine(self):
        rpg = get_rpg_game()
        intro = rpg.start_game()
        self.assertIn("Neo-Tokyo", intro)
        self.assertTrue(rpg.is_active)

        res = rpg.process_player_action("hack terminal")
        self.assertIsInstance(res, str)

        rpg.process_player_action("quit")
        self.assertFalse(rpg.is_active)

    def test_habit_tracker_logging(self):
        ht = get_habit_tracker()
        msg = ht.log_water(0.5)
        self.assertIn("0.5L water logged", msg)


if __name__ == "__main__":
    unittest.main()
