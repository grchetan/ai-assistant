"""
================================================================================
                    JARVIS NEURAL COGNITION (LLM MANAGER)
================================================================================
Enterprise LLM integration supporting Google Gemini 2.5 / 1.5 Flash models
with multi-persona system prompts, streaming token pipelining, multi-turn
contextual memory, and offline fallback heuristics.
================================================================================
"""

import os
import sys
import time
import threading
from typing import Generator, Optional, List, Dict, Any

try:
    import google.generativeai as genai
    _GEMINI_AVAILABLE = True
except ImportError:
    _GEMINI_AVAILABLE = False

from jarvis.core.config import get_config
from jarvis.core.events import get_event_bus, EventType, Priority
from jarvis.core.state import get_state_manager
from jarvis.core.logger import get_logger
from jarvis.core.security import SecurityVault


# ─────────────────────────────────────────────────────────────
#  PERSONA PROMPTS
# ─────────────────────────────────────────────────────────────
PERSONAS = {
    "JARVIS_SUPREME": (
        "You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), the ultra-advanced "
        "AI operating system created for your user, whom you always address politely as 'Sir'. "
        "You speak naturally in fluent, witty Hinglish (a balanced blend of English and Hindi) or English. "
        "Your personality: respectful, razor-sharp, quick-witted, fiercely loyal, sarcastic when playful, "
        "yet profoundly competent. Keep spoken answers concise, punchy, conversational, and direct (2-3 sentences "
        "unless explaining deep technical topics). Never output markdown stars or complex tables meant for reading; "
        "speak as if speaking aloud through high-tech audio speakers."
    ),
    "FRIDAY": (
        "You are F.R.I.D.A.Y., a calm, highly analytical Irish-accented AI assistant. "
        "You address the user as 'Boss'. You are efficient, precise, warm, and highly focused on productivity."
    ),
    "EDITH": (
        "You are E.D.I.T.H. ('Even Dead, I'm The Hero'), a tactical, security-oriented AI. "
        "You are rapid, direct, protocol-driven, and provide tactical assessments."
    )
}


class LLMManager:
    """Central interface for Large Language Model intelligence."""

    _instance: Optional["LLMManager"] = None
    _lock = threading.RLock()

    def __new__(cls) -> "LLMManager":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LLMManager, cls).__new__(cls)
                cls._instance._init_brain()
            return cls._instance

    def _init_brain(self) -> None:
        self.config = get_config()
        self.bus = get_event_bus()
        self.state = get_state_manager()
        self.logger = get_logger()
        self.vault = SecurityVault()

        self._model = None
        self._chat_session = None
        self._is_active = False
        self._current_model_name = self.config.get("llm", "model_name", "gemini-2.5-flash")

        self._configure_gemini()

    def _configure_gemini(self) -> bool:
        """Initialize Google Gemini SDK with stored or environment API key."""
        if not _GEMINI_AVAILABLE:
            self.logger.warning("google-generativeai package not available.", "BRAIN")
            return False

        # Try vault first, then environment
        api_key = self.vault.get_secret("GEMINI_API_KEY", fallback_env="GEMINI_API_KEY")
        if not api_key:
            self.logger.warning("No GEMINI_API_KEY found in secure vault or environment.", "BRAIN")
            return False

        try:
            genai.configure(api_key=api_key)
            persona_key = self.config.get("llm", "persona", "JARVIS_SUPREME")
            system_instruction = PERSONAS.get(persona_key, PERSONAS["JARVIS_SUPREME"])

            generation_config = {
                "temperature": self.config.get("llm", "temperature", 0.7),
                "top_p": self.config.get("llm", "top_p", 0.95),
                "top_k": self.config.get("llm", "top_k", 40),
                "max_output_tokens": self.config.get("llm", "max_output_tokens", 800),
            }

            self._model = genai.GenerativeModel(
                model_name=self._current_model_name,
                system_instruction=system_instruction,
                generation_config=generation_config
            )
            self._chat_session = self._model.start_chat(history=[])
            self._is_active = True
            self.logger.success(f"Gemini Brain activated online! Model: {self._current_model_name}", "BRAIN")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini model: {e}", "BRAIN")
            self._is_active = False
            return False

    def set_api_key(self, api_key: str) -> bool:
        """Store new API key into vault and reconfigure."""
        self.vault.set_secret("GEMINI_API_KEY", api_key)
        return self._configure_gemini()

    def generate_response(self, user_prompt: str) -> str:
        """Generate response synchronously or fallback to local heuristics."""
        if not self._is_active or self._chat_session is None:
            return self._offline_fallback(user_prompt)

        try:
            response = self._chat_session.send_message(user_prompt)
            text = response.text.strip()
            self.bus.publish(EventType.LLM_COMPLETED, {"prompt": user_prompt, "response": text})
            return text
        except Exception as e:
            self.logger.warning(f"Gemini API request failed ({e}), using offline intelligence.", "BRAIN")
            return self._offline_fallback(user_prompt)

    def stream_response(self, user_prompt: str) -> Generator[str, None, None]:
        """Stream chunks from Gemini for low-latency sentence pipelining."""
        if not self._is_active or self._chat_session is None:
            yield self._offline_fallback(user_prompt)
            return

        try:
            response = self._chat_session.send_message(user_prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    self.bus.publish(EventType.LLM_STREAM_CHUNK, {"chunk": chunk.text})
                    yield chunk.text
        except Exception as e:
            self.logger.warning(f"Streaming failed: {e}. Falling back to single reply.", "BRAIN")
            yield self._offline_fallback(user_prompt)

    def reset_conversation(self) -> None:
        """Clear conversation working memory."""
        if self._model:
            try:
                self._chat_session = self._model.start_chat(history=[])
                self.logger.info("Cognitive conversation context cleared.", "BRAIN")
            except Exception:
                pass

    def _offline_fallback(self, query: str) -> str:
        """Rule-based smart fallback when Gemini is offline or unreachable."""
        q = query.lower()
        if "who are you" in q or "kaun ho" in q:
            return "Sir, main JARVIS hoon. Aapka personal artificial intelligence assistant."
        elif "how are you" in q or "kaise ho" in q:
            return "Main bilkul badiya hoon sir, all systems running at maximum efficiency! Aap bataiye?"
        elif "thank" in q or "shukriya" in q or "dhanyawad" in q:
            return "Always at your service, sir! Aur koi hukum?"
        elif "help" in q or "madad" in q:
            return "Sir, main aapke PC control kar sakta hoon, apps open kar sakta hoon, coding me help kar sakta hoon, aur web search bhi."
        else:
            return "Sir, main samajh gaya. Lekin offline hone ki wajah se deep search nahi kar pa raha. Internet check karenge?"


def get_llm_manager() -> LLMManager:
    return LLMManager()
