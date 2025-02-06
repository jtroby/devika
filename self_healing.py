# self_healing.py
import time
import subprocess
import requests
import logging
import threading
import os

from fastapi import FastAPI
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# Global variable to store the uvicorn process handle for the main API
uvicorn_process = None

# Global flag to signal exit of the monitor loop
exit_triggered = False

# Health check URL for the API component (adjust as needed)
HEALTH_CHECK_URL = "http://127.0.0.1:8000/health"

MAX_RETRIES = 5
INITIAL_BACKOFF = 2  # seconds

# --- Exit Trigger Server Setup ---
# We'll run a small FastAPI app on port 9000 to trigger an exit.
exit_app = FastAPI()

@exit_app.post("/trigger_exit")
def trigger_exit():
    global exit_triggered
    exit_triggered = True
    return {"status": "exit triggered"}

def run_exit_server():
    # Run the exit trigger server quietly on port 9000.
    uvicorn.run(exit_app, host="127.0.0.1", port=9000, log_level="error", access_log=False)

# --- Main API (Uvicorn) Functions ---
def start_uvicorn():
    """
    Starts the uvicorn server (for your main API) and saves the process handle globally.
    """
    global uvicorn_process
    if uvicorn_process and uvicorn_process.poll() is None:
        logging.info("Uvicorn is already running.")
        return uvicorn_process
    try:
        # Suppress access logs with --no-access-log
        uvicorn_process = subprocess.Popen(["uvicorn", "api:app", "--reload", "--no-access-log"])
        logging.info(f"Started uvicorn with PID: {uvicorn_process.pid}")
        return uvicorn_process
    except Exception as e:
        logging.error(f"Failed to start uvicorn: {str(e)}")
        return None

def stop_uvicorn():
    """
    Stops the currently running uvicorn server using its process handle.
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
    """
    logging.info("Restarting the component...")
    stop_uvicorn() 
    time.sleep(5)  # Optional delay to ensure port release
    start_uvicorn()

def is_component_healthy():
    """
    Check the health of the component by sending a GET request to the health endpoint.
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
    Logs state changes only when health status changes.
    Exits gracefully if the exit_triggered flag is set (via the REST endpoint).
    """
    retry_count = 0
    backoff = INITIAL_BACKOFF
    prev_healthy = None  # Track previous health status

    while True:
        # Check if exit was triggered by the REST endpoint
        if exit_triggered:
            logging.info("Exit triggered via REST endpoint. Exiting monitoring loop gracefully.")
            break

        logging.info("Performing health check...")
        current_healthy = is_component_healthy()
        
        # Log state change only
        if current_healthy and prev_healthy != True:
            logging.info("Component is healthy.")
        elif not current_healthy and prev_healthy != False:
            logging.warning("Component is unhealthy.")
        
        if current_healthy:
            retry_count = 0  # Reset counters on healthy status
            backoff = INITIAL_BACKOFF
        else:
            retry_count += 1
            if retry_count > MAX_RETRIES:
                logging.error("Maximum retries exceeded. Manual intervention may be required.")
            else:
                restart_component()
                logging.info(f"Waiting {backoff} seconds before next check.")
                time.sleep(backoff)
                backoff *= 2
        
        prev_healthy = current_healthy

        # Sleep in small increments to check for exit trigger
        for _ in range(10):
            if exit_triggered:
                logging.info("Exit triggered during sleep. Exiting monitoring loop gracefully.")
                return
            time.sleep(1)

if __name__ == "__main__":
    logging.info("Starting self-healing monitor.")
    # Start the main API (uvicorn) server
    start_uvicorn()

    # Start the exit trigger server in a separate daemon thread
    exit_server_thread = threading.Thread(target=run_exit_server, daemon=True)
    exit_server_thread.start()

    # Start monitoring
    monitor_and_recover()
    logging.info("Self-healing monitor has exited.")


