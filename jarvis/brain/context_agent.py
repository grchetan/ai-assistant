"""
================================================================================
                    JARVIS AUTONOMOUS AGENT & TASK DECOMPOSITION
================================================================================
Goal-driven reasoning planner that decomposes complex user objectives into
discrete executable sub-tasks, manages intermediate working memory, and verifies
task completion state.
================================================================================
"""

import time
import json
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field

from jarvis.core.logger import get_logger
from jarvis.core.events import get_event_bus, EventType, Priority


class StepStatus:
    PENDING     = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED   = "COMPLETED"
    FAILED      = "FAILED"


@dataclass
class PlanStep:
    id: int
    description: str
    action_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    status: str = StepStatus.PENDING
    result: Optional[str] = None


class GoalPlanner:
    """Decomposes compound user requests into actionable sequences."""

    def __init__(self) -> None:
        self.logger = get_logger()
        self.bus = get_event_bus()

    def create_project_plan(self, project_name: str, framework: str) -> List[PlanStep]:
        """Construct multi-step workflow to bootstrap a new software project."""
        return [
            PlanStep(
                id=1,
                description=f"Create project directory for {project_name}",
                action_type="fs_mkdir",
                params={"dir_name": project_name}
            ),
            PlanStep(
                id=2,
                description=f"Generate {framework} boilerplate code",
                action_type="code_generate",
                params={"framework": framework, "project": project_name}
            ),
            PlanStep(
                id=3,
                description="Initialize Git repository",
                action_type="git_init",
                params={"project": project_name}
            ),
            PlanStep(
                id=4,
                description="Open workspace in Visual Studio Code",
                action_type="launch_editor",
                params={"editor": "code", "path": project_name}
            )
        ]

    def create_maintenance_plan(self) -> List[PlanStep]:
        """Construct automated PC maintenance and optimization routine."""
        return [
            PlanStep(
                id=1,
                description="Collect pre-maintenance hardware metrics",
                action_type="hardware_snapshot",
                params={}
            ),
            PlanStep(
                id=2,
                description="Empty Windows Recycle Bin",
                action_type="empty_recycle",
                params={}
            ),
            PlanStep(
                id=3,
                description="Clean temporary cache files",
                action_type="clean_temp",
                params={}
            ),
            PlanStep(
                id=4,
                description="Inspect top memory-consuming processes",
                action_type="audit_processes",
                params={}
            )
        ]


class AutonomousAgent:
    """Executes multi-step plans with status tracking and verification."""

    def __init__(self, action_dispatcher: Optional[Callable[[PlanStep], Tuple[bool, str]]] = None):
        self.logger = get_logger()
        self.planner = GoalPlanner()
        self.dispatcher = action_dispatcher
        self.active_plan: List[PlanStep] = []
        self._is_executing = False

    def execute_plan(self, plan: List[PlanStep]) -> Tuple[bool, str]:
        """Execute each step in plan sequentially."""
        self.active_plan = plan
        self._is_executing = True
        self.logger.info(f"Executing autonomous goal plan ({len(plan)} steps)...", "AGENT")

        completed_count = 0
        for step in plan:
            step.status = StepStatus.IN_PROGRESS
            self.logger.info(f"Step {step.id}: {step.description}", "AGENT")

            if self.dispatcher:
                try:
                    success, res = self.dispatcher(step)
                    step.result = res
                    step.status = StepStatus.COMPLETED if success else StepStatus.FAILED
                    if success:
                        completed_count += 1
                    else:
                        self.logger.warning(f"Step {step.id} failed: {res}", "AGENT")
                except Exception as e:
                    step.status = StepStatus.FAILED
                    step.result = str(e)
            else:
                # Simulation pass
                time.sleep(0.3)
                step.status = StepStatus.COMPLETED
                step.result = "Success"
                completed_count += 1

        self._is_executing = False
        summary = f"Plan executed: {completed_count}/{len(plan)} steps completed successfully."
        self.logger.success(summary, "AGENT")
        return completed_count == len(plan), summary


def get_autonomous_agent() -> AutonomousAgent:
    return AutonomousAgent()
