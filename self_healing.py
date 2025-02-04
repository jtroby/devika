# self_healing.py
import time
import subprocess
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Global variable to store the uvicorn process handle
uvicorn_process = None

# Health check URL for the API component; we will revisit endpoint debugging later.
HEALTH_CHECK_URL = "http://127.0.0.1:8000/task_status/agent_a_id"

MAX_RETRIES = 5
INITIAL_BACKOFF = 2  # seconds
MAX_CONSECUTIVE_FAILURES = 1  # Failsafe threshold

def start_uvicorn():
    """
    Starts the uvicorn server and saves the process handle globally.
    """
    global uvicorn_process
    if uvicorn_process and uvicorn_process.poll() is None:
        logging.info("Uvicorn is already running.")
        return uvicorn_process
    try:
        uvicorn_process = subprocess.Popen(["uvicorn", "api:app", "--reload"])
        logging.info(f"Started uvicorn with PID: {uvicorn_process.pid}")
        return uvicorn_process
    except Exception as e:
        logging.error(f"Failed to start uvicorn: {str(e)}")
        return None

def stop_uvicorn():
    """
    Stops the currently running uvicorn process using its process handle.
    """
    global uvicorn_process
    if uvicorn_process and uvicorn_process.poll() is None:
        try:
            logging.info(f"Terminating uvicorn with PID: {uvicorn_process.pid}")
            uvicorn_process.terminate()
            uvicorn_process.wait(timeout=10)
            logging.info("Uvicorn terminated successfully.")
        except Exception as e:
            logging.error(f"Failed to terminate uvicorn: {str(e)}")
    else:
        logging.info("No active uvicorn process found.")

def restart_component():
    """
    Restarts the uvicorn component by stopping the current instance and starting a new one.
    Note: We're using an in-memory process handle for simplicity.
          If this approach does not work as needed in the future,
          consider using a PID file or another process management strategy.
    """
    logging.info("Restarting the component...")
    stop_uvicorn()  # Kill the running instance
    time.sleep(2)   # Optional delay to ensure port release
    start_uvicorn()  # Start a new instance

def is_component_healthy():
    """
    Check the health of the component by sending a GET request to a health endpoint.
    Returns True if healthy, False otherwise.
    """
    try:
        response = requests.get(HEALTH_CHECK_URL, timeout=5)
        if response.status_code == 200:
            return True
        else:
            logging.error(f"Health check failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Health check exception: {str(e)}")
        return False

def monitor_and_recover():
    """
    Monitor the component's health and attempt a restart with exponential backoff if needed.
    If MAX_CONSECUTIVE_FAILURES is reached, break the loop.
    """
    retry_count = 0
    backoff = INITIAL_BACKOFF

    while True:
        logging.info("Performing health check...")
        if is_component_healthy():
            logging.info("Component is healthy.")
            retry_count = 0  # Reset on success
            backoff = INITIAL_BACKOFF
        else:
            retry_count += 1
            logging.warning(f"Component is unhealthy. Retry {retry_count} of {MAX_RETRIES}.")
            if retry_count > MAX_RETRIES:
                logging.error("Maximum retries exceeded. Manual intervention may be required.")
                # Optionally, you can break here or continue trying
                # break
                retry_count = 0  # For now, reset and continue
            else:
                restart_component()
                logging.info(f"Waiting {backoff} seconds before next check.")
                time.sleep(backoff)
                backoff *= 2

        # Failsafe: Exit if too many consecutive failures
        if retry_count >= MAX_CONSECUTIVE_FAILURES:
            logging.error("Exceeded maximum consecutive failures. Exiting monitoring loop.")
            break

        # Fixed wait before next health check
        time.sleep(10)

if __name__ == "__main__":
    logging.info("Starting self-healing monitor.")
    start_uvicorn()  # Start the server initially
    monitor_and_recover()
