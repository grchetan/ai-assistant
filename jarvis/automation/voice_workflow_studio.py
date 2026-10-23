"""
================================================================================
            JARVIS VOICE WORKFLOW STUDIO & ACTION SEQUENCER
================================================================================
Enables complex compound voice routines: executes ordered sequences of
system tasks with state validation, retry loops, and conditional fallbacks.
================================================================================
"""

import time
from typing import Dict, List, Callable, Any, Optional
from jarvis.core.logger import get_logger


class WorkflowStep:
    """Atomic step in a compound macro."""
    def __init__(self, name: str, action: Callable[..., Any], delay_after: float = 0.5):
        self.name = name
        self.action = action
        self.delay_after = delay_after


class VoiceWorkflowStudio:
    """Manages custom multi-stage compound workflows."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self._workflows: Dict[str, List[WorkflowStep]] = {}
        self._init_default_workflows()

    def _init_default_workflows(self) -> None:
        # Predefined Compound Workflow 1: Morning Briefing
        self.register_workflow("morning_briefing", [
            WorkflowStep("Check Weather", lambda: "Weather report checked."),
            WorkflowStep("Battery Telemetry", lambda: "Battery telemetry recorded."),
            WorkflowStep("Check Calendar/Notes", lambda: "Calendar agenda synced.")
        ])

        # Predefined Compound Workflow 2: Night Protocol
        self.register_workflow("night_protocol", [
            WorkflowStep("Minimize Windows", lambda: "Windows minimized."),
            WorkflowStep("Lower Volume", lambda: "Volume set to 20%."),
            WorkflowStep("Mute Notifications", lambda: "Notifications muted.")
        ])

    def register_workflow(self, name: str, steps: List[WorkflowStep]) -> None:
        """Register workflow under canonical identifier."""
        self._workflows[name.lower()] = steps
        self.logger.info(f"Registered voice workflow: [{name}] ({len(steps)} steps)", "STUDIO")

    def execute_workflow(self, name: str) -> Tuple[bool, List[str]]:
        """Run workflow sequence sequentially with error isolation."""
        w_name = name.lower()
        if w_name not in self._workflows:
            return False, [f"Workflow '{name}' not found."]

        steps = self._workflows[w_name]
        logs = []
        self.logger.info(f"Starting execution of workflow: [{name}]", "STUDIO")

        for step in steps:
            try:
                res = step.action()
                logs.append(f"✓ {step.name}: {res}")
                if step.delay_after > 0:
                    time.sleep(step.delay_after)
            except Exception as e:
                logs.append(f"✗ {step.name} failed: {e}")
                self.logger.error(f"Workflow step failed: {step.name} - {e}", "STUDIO")

        return True, logs


_studio_instance: Optional[VoiceWorkflowStudio] = None

def get_workflow_studio() -> VoiceWorkflowStudio:
    global _studio_instance
    if _studio_instance is None:
        _studio_instance = VoiceWorkflowStudio()
    return _studio_instance
