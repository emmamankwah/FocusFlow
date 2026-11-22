from fastapi import APIRouter, HTTPException
from .engine import SimplePlanner
from .schemas import PlannerInput, PlannerOutput

router = APIRouter()

_planner = SimplePlanner()

@router.post("/generate", response_model=PlannerOutput)
async def generate_plan(payload: PlannerInput):
    try:
        plan = _planner.generate(payload)
        return PlannerOutput(**plan)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
