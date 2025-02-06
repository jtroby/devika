#!/bin/bash
# self_healing_recovery.sh
# This script detects failures in core services and attempts to automatically recover them.
# All actions are logged for troubleshooting.

LOG_DIR="$HOME/automation_logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/self_healing_$(date +"%Y-%m-%d_%H-%M-%S").log"

echo "🔍 Starting Self-Healing Recovery..." | tee -a "$LOG_FILE"

# Function to log messages
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Function to attempt to restart a service
restart_service() {
    local service=$1
    log "[⚠️] $service is not running! Restarting..."
    sudo systemctl restart "$service" && log "[✅] $service restarted successfully." || log "[❌] Failed to restart $service!"
}

# Check and restart services if needed
if ! systemctl is-active --quiet docker; then
    restart_service docker
else
    log "[✅] Docker is running."
fi

if ! systemctl is-active --quiet ollama; then
    restart_service ollama
else
    log "[✅] Ollama is running."
fi

if ! minikube status | grep -q "Running"; then
    log "[⚠️] Minikube is not running! Restarting..."
    minikube start --driver=docker && log "[✅] Minikube restarted successfully." || log "[❌] Failed to restart Minikube!"
else
    log "[✅] Minikube is running."
fi

log "✅ Self-Healing Recovery complete. Logs available in $LOG_FILE"
