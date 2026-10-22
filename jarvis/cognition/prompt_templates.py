"""
================================================================================
                    JARVIS META-PROMPT & COGNITIVE TEMPLATES
================================================================================
Domain-specialized system instruction templates engineered for targeted LLM tasks:
  - Deep Code Refactoring & Security Audit
  - Software Architecture Review
  - Scientific & Mathematical Step-by-Step Derivation
  - High-Speed Hinglish Conversational Banter
================================================================================
"""

from typing import Dict, Any, Optional

PROMPT_TEMPLATES: Dict[str, str] = {
    "code_refactor": (
        "You are J.A.R.V.I.S., an elite Principal Software Engineer. "
        "Review the following code in {language}.\n"
        "Identify:\n"
        "1. Performance bottlenecks (Big-O analysis)\n"
        "2. Security vulnerabilities\n"
        "3. Clean Architecture refactoring\n\n"
        "CODE:\n{code}\n\n"
        "Provide direct, production-ready optimized code with concise commentary."
    ),
    "security_audit": (
        "You are J.A.R.V.I.S. Tactical Security Intelligence. "
        "Conduct a comprehensive threat model for target: {target}.\n"
        "Evaluate potential attack vectors, privilege escalation risks, and mitigation strategies."
    ),
    "architecture_review": (
        "You are J.A.R.V.I.S. Cloud & System Architect. "
        "Evaluate the following system specification:\n{system_spec}\n\n"
        "Recommend optimal microservice topology, message bus protocols, and data persistence layers."
    ),
    "scientific_explanation": (
        "Explain the scientific principle of '{topic}' to the user ({user_name}). "
        "Use intuitive analogies, state the core equations, and explain practical modern applications."
    )
}


class PromptEngine:
    """Manages prompt template interpolation."""

    @classmethod
    def format_template(cls, template_key: str, **kwargs) -> str:
        raw = PROMPT_TEMPLATES.get(template_key)
        if not raw:
            return kwargs.get("fallback", "")
        try:
            return raw.format(**kwargs)
        except KeyError:
            return raw


def get_prompt_engine() -> type[PromptEngine]:
    return PromptEngine
