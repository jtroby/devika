#!/usr/bin/env python3
"""
control_center.py

A centralized script to orchestrate key components of the custom Research Agent system,
including task management, self-healing, and diagnostics. This control center serves as a
starting point for integrating modules and will eventually be extended with a web dashboard
for real-time monitoring and control.

Usage:
    python3 control_center.py --self-healing    # Launch the self-healing monitor
    python3 control_center.py --task-manager    # Launch the task manager test
    python3 control_center.py --diagnostics     # Run a one-time diagnostics test
    python3 control_center.py --all             # Launch all components (for testing)
"""

import argparse
import threading
import time
import subprocess
import logging

# Import modules from your project.
# Assuming these modules are in the same directory:
import task_manager  # For task routing
import self_healing  # For self-healing monitor
import performance_tests  # For diagnostics/performance tests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("control_center")

def launch_self_healing():
    logger.info("Launching self-healing monitor...")
    # Run self-healing monitor in its own thread.
    thread = threading.Thread(target=self_healing.monitor_and_recover, daemon=True)
    thread.start()
    return thread

def launch_task_manager():
    logger.info("Launching task manager test...")
    # For demonstration, run the task manager's main function.
    # In production, you might integrate this differently.
    thread = threading.Thread(target=task_manager.main, daemon=True)
    thread.start()
    return thread

def run_diagnostics():
    logger.info("Running one-time diagnostics (performance tests)...")
    # For example, run all benchmarks once.
    results = performance_tests.run_all_benchmarks()
    logger.info("Diagnostics results: %s", results)
    return results

def main():
    parser = argparse.ArgumentParser(description="Control Center for the Research Agent System")
    parser.add_argument("--self-healing", action="store_true", help="Launch the self-healing monitor")
    parser.add_argument("--task-manager", action="store_true", help="Launch the task manager")
    parser.add_argument("--diagnostics", action="store_true", help="Run one-time diagnostics")
    parser.add_argument("--all", action="store_true", help="Launch all components")
    
    args = parser.parse_args()
    
    threads = []
    
    if args.all:
        threads.append(launch_self_healing())
        threads.append(launch_task_manager())
        run_diagnostics()
    else:
        if args.self_healing:
            threads.append(launch_self_healing())
        if args.task_manager:
            threads.append(launch_task_manager())
        if args.diagnostics:
            run_diagnostics()
    
    # Keep the main thread alive if any background threads are running.
    if threads:
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            logger.info("Control center shutting down.")
    else:
        logger.info("No components were selected to run. Exiting.")

if __name__ == "__main__":
    main()
