#!/bin/bash
# core_automation_logic.sh
# This script manages core automation tasks including health checks and scheduled task execution.
# It logs all activity to a timestamped log file.

LOG_DIR="$HOME/automation_logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/core_automation_$(date +"%Y-%m-%d_%H-%M-%S").log"

echo "🚀 Starting Core Automation Agent..." | tee -a "$LOG_FILE"

# Function to log messages
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Function to check if a service is running; if not, attempt restart.
check_service() {
    local service=$1
    log "[🔍] Checking $service..."
    if systemctl is-active --quiet "$service"; then
        log "[✅] $service is running."
    else
        log "[⚠️] $service is NOT running. Attempting restart..."
        sudo systemctl restart "$service"
        if systemctl is-active --quiet "$service"; then
            log "[✅] $service restarted successfully."
        else
            log "[❌] Failed to restart $service!"
        fi
    fi
}

# Check core services
check_service docker
check_service minikube
check_service ollama

# Run any scheduled tasks (if available)
if [ -f "$HOME/automation_agent/scripts/scheduled_tasks.sh" ]; then
    log "[🔍] Running scheduled tasks..."
    bash "$HOME/automation_agent/scripts/scheduled_tasks.sh" | tee -a "$LOG_FILE"
else
    log "[⚠️] Scheduled tasks script not found."
fi

log "🎯 All core automation tasks completed. Logs saved to $LOG_FILE"
