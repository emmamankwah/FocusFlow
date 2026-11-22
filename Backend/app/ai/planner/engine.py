from typing import Dict, Any
from .schemas import PlannerInput, PlannerOutput

class BasePlanner:
    """Abstract planner interface."""
    def generate(self, data: PlannerInput) -> Dict[str, Any]:
        raise NotImplementedError

class SimplePlanner(BasePlanner):
    """A minimal placeholder that returns a static plan.
    Future implementations can replace this class.
    """
    def generate(self, data: PlannerInput) -> Dict[str, Any]:
        # Simple echo of received tasks with dummy schedule
        return {
            "tasks": [
                {"id": t.id, "title": t.title, "deadline": t.deadline, "priority": t.priority, "scheduled_time": "2026-12-01T09:00:00"}
                for t in data.tasks
            ],
            "message": "Generated simple static plan",
        }
