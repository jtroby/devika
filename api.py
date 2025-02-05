# api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid

app = FastAPI()

# Existing endpoints...

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Simple in-memory store for agents and tasks
agents = {}
tasks = {}

class Agent(BaseModel):
    name: str

class Task(BaseModel):
    description: str

@app.post("/register_agent")
def register_agent(agent: Agent):
    agent_id = str(uuid.uuid4())
    agents[agent_id] = agent.name
    return {"agent_id": agent_id, "agent_name": agent.name}

@app.post("/assign_task/{agent_id}")
def assign_task(agent_id: str, task: Task):
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    tasks[agent_id] = task.description
    return {"agent_id": agent_id, "task_assigned": task.description}

@app.get("/task_status/{agent_id}")
def task_status(agent_id: str):
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    task = tasks.get(agent_id, "No task assigned")
    return {"agent_id": agent_id, "current_task": task}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Devika AI Research Agent API!"}

