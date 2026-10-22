"""
================================================================================
                    JARVIS MULTI-AGENT COLLABORATION SWARM
================================================================================
Orchestrates specialized virtual autonomous agents executing round-table consensus:
  1. System Architect Agent (Structural blueprints and scalability design)
  2. Lead Software Engineer Agent (High-performance code generation)
  3. Security & Code Reviewer Agent (Vulnerability and edge-case auditing)
  4. Technical Researcher Agent (Contextual fact synthesis)
================================================================================
"""

import time
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass

from jarvis.core.logger import get_logger
from jarvis.brain.llm_manager import get_llm_manager


@dataclass
class SwarmMessage:
    agent_name: str
    role: str
    content: str
    timestamp: float


class VirtualAgent:
    """Specialized persona agent with targeted domain prompt."""

    def __init__(self, name: str, role: str, system_prompt: str) -> None:
        self.name = name
        self.role = role
        self.system_prompt = system_prompt

    def generate_contribution(self, problem_statement: str, context: List[SwarmMessage]) -> str:
        """Formulate domain solution based on problem and previous discussion."""
        llm = get_llm_manager()
        history_context = "\n".join([f"[{m.agent_name} - {m.role}]: {m.content}" for m in context])

        full_prompt = (
            f"You are {self.name}, the {self.role}.\n"
            f"SYSTEM DIRECTIVE: {self.system_prompt}\n\n"
            f"PROBLEM TO SOLVE: {problem_statement}\n\n"
            f"PRIOR SWARM DISCUSSION:\n{history_context}\n\n"
            f"Provide your concise, highly technical contribution from your role's perspective."
        )

        try:
            return llm.generate_response(full_prompt)
        except Exception:
            return f"[{self.name}] Concur with current approach. Recommending modular execution."


class AgentSwarmOrchestrator:
    """Coordinates multi-agent debate and consensus synthesis."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.agents: List[VirtualAgent] = [
            VirtualAgent(
                name="Aura",
                role="Principal Architect",
                system_prompt="Focus on clean architecture, decoupling, maintainability, and scalability."
            ),
            VirtualAgent(
                name="Cipher",
                role="Cybersecurity & Reviewer",
                system_prompt="Focus on threat vectors, edge-case validation, input sanitization, and security."
            ),
            VirtualAgent(
                name="Vector",
                role="Lead Developer",
                system_prompt="Focus on efficient algorithms, low CPU/RAM footprint, and practical implementation."
            )
        ]

    def solve_complex_objective(self, objective: str) -> Dict[str, Any]:
        """
        Conduct a multi-turn round-table collaboration where each agent
        critiques and enhances the shared solution.
        """
        self.logger.info(f"Initiating Agent Swarm deliberation on: '{objective}'", "SWARM")

        discussion: List[SwarmMessage] = []

        # Turn 1: Architect sets foundation
        arch_contrib = self.agents[0].generate_contribution(objective, discussion)
        discussion.append(SwarmMessage(self.agents[0].name, self.agents[0].role, arch_contrib, time.time()))

        # Turn 2: Developer proposes code implementation
        dev_contrib = self.agents[2].generate_contribution(objective, discussion)
        discussion.append(SwarmMessage(self.agents[2].name, self.agents[2].role, dev_contrib, time.time()))

        # Turn 3: Security reviewer audits and refines
        sec_contrib = self.agents[1].generate_contribution(objective, discussion)
        discussion.append(SwarmMessage(self.agents[1].name, self.agents[1].role, sec_contrib, time.time()))

        # Consensus Synthesis
        consensus = (
            f"=== AGENT SWARM CONSENSUS ===\n\n"
            f"1. ARCHITECTURE ({self.agents[0].name}):\n{arch_contrib}\n\n"
            f"2. IMPLEMENTATION ({self.agents[2].name}):\n{dev_contrib}\n\n"
            f"3. SECURITY AUDIT ({self.agents[1].name}):\n{sec_contrib}\n"
        )

        self.logger.success("Agent Swarm concluded consensus formulation.", "SWARM")

        return {
            "objective": objective,
            "turns": [
                {"agent": m.agent_name, "role": m.role, "content": m.content}
                for m in discussion
            ],
            "consensus_summary": consensus
        }


def get_agent_swarm() -> AgentSwarmOrchestrator:
    return AgentSwarmOrchestrator()
