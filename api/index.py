from fastapi import FastAPI
from pydantic import BaseModel
from campusflow_ai import CampusFlowAI
import io
import contextlib

app = FastAPI()


class MissionRequest(BaseModel):
    prompt: str
    accessibility_mode: bool = False
    disruption: str = "none"


@app.get("/api")
def api_home():
    return {
        "status": "online",
        "project": "CampusFlow AI"
    }


@app.get("/api/health")
def health():
    return {
        "status": "online",
        "message": "CampusFlow AI backend is running"
    }


@app.post("/api/mission")
def create_mission(request: MissionRequest):

    agent = CampusFlowAI(
        accessibility_mode=request.accessibility_mode
    )

    output = io.StringIO()

    with contextlib.redirect_stdout(output):

        tasks = agent.understand(request.prompt)

        tasks = agent.plan(tasks)

        agent.act(tasks, active_step=0)

        agent.monitor()

        if request.disruption == "faculty_away":
            tasks = agent.replan_on_disruption(
                tasks,
                disruption_type="faculty_away"
            )

        elif request.disruption == "admin_queue_spike":
            tasks = agent.replan_on_disruption(
                tasks,
                disruption_type="admin_queue_spike"
            )

    task_data = []

    for task in tasks:
        task_data.append({
            "id": task.task_id,
            "title": task.title,
            "location": task.location,
            "duration": task.base_duration,
            "queue": task.queue_time,
            "open": task.window_open,
            "close": task.window_close,
            "instruction": task.instruction
        })

    return {
        "success": True,
        "project": "CampusFlow AI",
        "workflow": [
            "UNDERSTAND",
            "PLAN",
            "ACT",
            "MONITOR",
            "REPLAN"
        ],
        "tasks": task_data,
        "console_output": output.getvalue()
    }
