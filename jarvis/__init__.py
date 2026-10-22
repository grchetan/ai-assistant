"""
================================================================================
                    J.A.R.V.I.S. / A.R.I.A. NEXT-GEN AI
            ADVANCED COGNITIVE VOICE & DESKTOP AUTOMATION PLATFORM
================================================================================
Version     : 4.0.0 Enterprise Quantum
Author      : AI Engineering Team
Platform    : Windows 10 / 11 (64-bit Optimized)
Architecture: Decoupled Asynchronous Micro-Kernel with Real-time Neural Bridge
================================================================================
"""

__title__       = "JARVIS Next-Gen OS"
__version__     = "4.0.0"
__author__      = "AI Engineering Team"
__license__     = "MIT"
__description__ = "High-Intelligence Voice Assistant & Desktop Automation Platform"

import sys
import os

# Ensure the root workspace is always in Python's path
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT_DIR not in sys.path:
    sys.path.insert(0, _ROOT_DIR)

from jarvis.core.config import get_config
from jarvis.core.events import EventBus, Event
from jarvis.core.state import StateManager
from jarvis.core.logger import get_logger

__all__ = [
    "get_config",
    "EventBus",
    "Event",
    "StateManager",
    "get_logger",
    "__version__",
]
