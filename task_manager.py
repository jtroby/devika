import random
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Migration ratio: 0.0 routes all tasks to AutoGPT; 1.0 routes all tasks to Devika.
MIGRATION_RATIO = 1.0

# Endpoints for each system
AUTO_GPT_URL = "http://127.0.0.1:8001"  # Example endpoint for AutoGPT (adjust as needed)
DEVIKA_URL = "http://127.0.0.1:8000"      # Our Devika API endpoint

def register_agent():
    """
    Registers the agent and returns the agent_id.
    """
    try:
        response = requests.post(f"{DEVIKA_URL}/register_agent", json={"name": "Agent_A"})
        if response.status_code == 200:
            agent_info = response.json()
            logging.info("Registered Agent: %s", agent_info)
            return agent_info.get("agent_id")
        else:
            logging.error("Failed to register agent: HTTP %s", response.status_code)
            return None
    except Exception as e:
        logging.error("Exception during agent registration: %s", str(e))
        return None

def send_task_to_devika(task, agent_id):
    """
    Send the task to Devika by posting to the custom Research Agent API.
    """
    try:
        response = requests.post(f"{DEVIKA_URL}/assign_task/{agent_id}", json={"description": task})
        if response.status_code == 200:
            logging.info("Task successfully assigned to Devika.")
            return response.json()
        else:
            logging.error("Failed to assign task to Devika: HTTP %s", response.status_code)
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        logging.error("Exception when sending task to Devika: %s", str(e))
        return {"error": str(e)}

def send_task_to_autogpt(task):
    """
    Simulate sending the task to the AutoGPT system.
    """
    logging.info("Simulating task assignment to AutoGPT.")
    return {"status": "success", "system": "AutoGPT", "task": task}

def route_task(task, agent_id):
    """
    Route the task to either AutoGPT or Devika based on the migration ratio.
    """
    if random.random() < MIGRATION_RATIO:
        logging.info("Routing task to Devika (custom Research Agent).")
        return send_task_to_devika(task, agent_id)
    else:
        logging.info("Routing task to AutoGPT prototype.")
        return send_task_to_autogpt(task)

def main():
    """
    Main function for testing the task manager.
    """
    # Register the agent and obtain the agent_id.
    registered_agent_id = register_agent()
    if not registered_agent_id:
        logging.error("Agent registration failed. Exiting.")
        exit(1)
    
    # Route a sample task using the registered agent ID.
    test_task = "Explain SPX volatility smile dynamics"
    result = route_task(test_task, registered_agent_id)
    logging.info("Task routing result: %s", result)

if __name__ == "__main__":
    main()

