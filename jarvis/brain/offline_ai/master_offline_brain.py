"""
================================================================================
            JARVIS MASTER OFFLINE AI BRAIN & COGNITIVE CONTROLLER
================================================================================
Unified offline intelligence pipeline synthesizing symbolic mathematics,
knowledge graphs, code recipes, system diagnostics, macro execution, and
conversational personality without requiring any external cloud APIs.
================================================================================
"""

import re
from typing import Optional, Dict, Any

from jarvis.core.logger import get_logger
from jarvis.brain.offline_ai.knowledge_engine import get_knowledge_engine
from jarvis.brain.offline_ai.symbolic_math import get_math_engine
from jarvis.brain.offline_ai.code_generator import get_code_engine
from jarvis.brain.offline_ai.conversational_agent import get_conversational_agent
from jarvis.brain.offline_ai.semantic_engine import get_semantic_engine
from jarvis.brain.offline_ai.system_troubleshooter import get_troubleshooter
from jarvis.brain.offline_ai.macro_automator import get_macro_automator
from jarvis.neural.complete_periodic_table import get_full_periodic_table
from jarvis.neural.world_geography_dataset import get_world_geography
from jarvis.neural.astronomy_deep_catalog import get_astronomy_catalog
from jarvis.neural.math_formula_sheet import get_formula_sheet
from jarvis.neural.code_synthesis_library import get_code_library
from jarvis.neural.dialogue_matrix_pro import get_dialogue_matrix


class MasterOfflineBrain:
    """Zero-cloud autonomous cognitive core for JARVIS."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.knowledge = get_knowledge_engine()
        self.math_solver = get_math_engine()
        self.code_gen = get_code_engine()
        self.convo = get_conversational_agent()
        self.semantic = get_semantic_engine()
        self.troubleshooter = get_troubleshooter()
        self.macros = get_macro_automator()
        self.periodic_table = get_full_periodic_table()
        self.geography = get_world_geography()
        self.astronomy = get_astronomy_catalog()
        self.formula_sheet = get_formula_sheet()
        self.code_library = get_code_library()
        self.dialogue_matrix = get_dialogue_matrix()

    def process_query(self, user_query: str) -> str:
        """
        Main cognitive dispatch:
        1. Check multi-stage automated macros
        2. Check symbolic math & physics calculations & formula sheet
        3. Check code synthesis & programming recipes
        4. Check chemical periodic table elements
        5. Check world geography & sovereign nations
        6. Check astronomy & celestial catalogs
        7. Check factual science, history, CS, and general knowledge
        8. Check system error / troubleshooting diagnostics
        9. Check contextual conversation and personality banter
        10. Fallback to intelligent extractive semantic synthesis
        """
        q = user_query.strip()
        if not q:
            return "Sir, I am listening. Please tell me how I can assist you."

        self.logger.info(f"Offline AI analyzing query: '{q}'", "OFFLINE_AI")

        # 1. Macro execution
        macro_res = self.macros.try_execute_macro(q)
        if macro_res:
            return macro_res

        # 2. Math & Physics computation
        math_res = self.math_solver.try_solve(q)
        if math_res:
            return f"Sir, calculation complete: {math_res}"

        # Formula lookup
        formula_res = self.formula_sheet.search_formula(q)
        if formula_res:
            return self.formula_sheet.format_speech(formula_res)

        # 3. Code Generation (Templates & Advanced Library)
        code_recipe = self.code_gen.find_code(q)
        if code_recipe:
            return self.code_gen.format_code_response(code_recipe)

        lib_code = self.code_library.search_library(q)
        if lib_code:
            return f"Sir, here is the implementation for {lib_code['title']}:\n\n```{lib_code['lang']}\n{lib_code['code']}\n```"

        # 4. Periodic Table Element
        elem = self.periodic_table.search_element(q)
        if elem:
            return self.periodic_table.format_element_speech(elem)

        # 5. World Geography & Countries
        geo = self.geography.lookup_country(q)
        if geo:
            return self.geography.format_country_speech(geo)

        # 6. Astronomy & Celestial bodies
        astro = self.astronomy.search_body(q)
        if astro:
            return self.astronomy.format_speech(astro)

        # 7. In-House Knowledge Graph Search
        fact_answer = self.knowledge.answer_query(q)
        if fact_answer:
            return f"Sir, yahan detail information hai:\n\n{fact_answer}"

        # 8. System Troubleshooter
        diag_res = self.troubleshooter.diagnose(q)
        if diag_res:
            return diag_res

        # 9. Conversational Agent & Banter
        pro_dialogue = self.dialogue_matrix.match_dialogue(q)
        if pro_dialogue:
            return pro_dialogue

        convo_res = self.convo.chat(q)
        if convo_res:
            return convo_res

        # 10. Semantic summary or keywords
        tokens = self.semantic.tokenize(q)
        if tokens:
            kw_list = [k for k, _ in self.semantic.extract_keywords(q, top_k=3)]
            kw_str = ", ".join(kw_list) if kw_list else "general instructions"
            return (
                f"Sir, maine aapki query '{q}' analyze kar li hai (Focus areas: {kw_str}). "
                "Main aapka personal offline AI brain hoon — aap mujhse kisi bhi scientific topic, "
                "mathematical equations, programming code, ya system automation ke baare me pooch sakte hain!"
            )

        return "Sir, all neural offline registers ready hain. Please batayein agla task kya hai?"


_master_offline_brain: Optional[MasterOfflineBrain] = None

def get_offline_brain() -> MasterOfflineBrain:
    global _master_offline_brain
    if _master_offline_brain is None:
        _master_offline_brain = MasterOfflineBrain()
    return _master_offline_brain
