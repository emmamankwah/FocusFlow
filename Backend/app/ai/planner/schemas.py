from pydantic import BaseModel, Field
from typing import List, Optional

class TaskItem(BaseModel):
    id: int = Field(..., description="Task identifier")
    title: str = Field(..., description="Task title")
    deadline: Optional[str] = Field(None, description="ISO‑8601 deadline timestamp")
    priority: Optional[int] = Field(None, description="Optional priority level")
    scheduled_time: Optional[str] = Field(None, description="Planned execution time (ISO‑8601)")

class PlannerInput(BaseModel):
    tasks: List[TaskItem]
    user_id: Optional[int] = None

class PlannerOutput(BaseModel):
    tasks: List[TaskItem]
    message: str
