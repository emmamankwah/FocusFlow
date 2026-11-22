import sys, os
sys.path.append(r'C:\Users\emman\Desktop\FocusFlow\Backend')
from main import app
from fastapi.testclient import TestClient

client = TestClient(app)
payload = {
    "tasks": [
        {"id": 1, "title": "Task One", "deadline": None, "priority": 1},
        {"id": 2, "title": "Task Two", "deadline": None, "priority": 2},
    ]
}
resp = client.post('/ai/planner/generate', json=payload)
print('Status:', resp.status_code)
print('Response JSON:', resp.json())
