from ast import main
import requests
import json
import logging

# Set API Endpoints
DEVIKA_API = "http://127.0.0.1:8000/task"
AUTOGPT_API = "http://127.0.0.1:5000/task"

logging.basicConfig(level=logging.INFO)

def route_task(task, priority="devika"):
    """ Routes task to the correct AI agent """
    if priority == "devika":
        response = requests.post(DEVIKA_API, json={"task": task})
        if response.status_code == 200:
            return response.json()
        else:
            logging.warning("⚠️ Devika AI failed, switching to AutoGPT...")
    
    # AutoGPT as fallback
    response = requests.post(AUTOGPT_API, json={"task": task})
    return response.json()

if __name__ == "__main__":
    task = "Analyze market volatility for SPX"
    result = route_task(task)
    print("🔹 Task Result:", result)
    main()