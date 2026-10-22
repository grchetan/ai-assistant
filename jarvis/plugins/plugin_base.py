"""
================================================================================
                    JARVIS PLUGIN ARCHITECTURE BASE
================================================================================
Defines the standard interface and lifecycle contract for modular JARVIS plugins.
================================================================================
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple


class JarvisPlugin(ABC):
    """Abstract base class representing an extensible feature plugin."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable explanation of plugin capability."""
        pass

    def on_load(self) -> bool:
        """Lifecycle hook invoked when plugin is loaded into memory."""
        return True

    def on_unload(self) -> None:
        """Lifecycle hook invoked during clean shutdown."""
        pass

    @abstractmethod
    def can_handle(self, text: str) -> bool:
        """Inspect user utterance to determine if plugin should execute."""
        pass

    @abstractmethod
    def execute(self, text: str, payload: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Execute plugin logic.
        Returns: (success_boolean, spoken_response_string)
        """
        pass
