import json
import sys
from pathlib import Path
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from main import app


def test_generate_plan():
    client = TestClient(app)
    payload = {
        "tasks": [
            {"id": 1, "title": "Task One", "deadline": None, "priority": 1},
            {"id": 2, "title": "Task Two", "deadline": None, "priority": 2},
        ]
    }
    response = client.post("/ai/planner/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert isinstance(data["tasks"], list)
    assert len(data["tasks"]) == 2
    for t in data["tasks"]:
        assert "scheduled_time" in t
    assert data.get("message") == "Generated simple static plan"
