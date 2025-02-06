#!/bin/bash
# setup_ollama_api.sh
# This script configures and starts the Ollama API.
# It stops any existing instance, ensures the configuration file exists,
# and then starts Ollama in API mode with detailed logging.

# Define paths and configuration
CONFIG_DIR="$HOME/.ollama"
CONFIG_FILE="$CONFIG_DIR/config.json"
MODEL_DIR="D:/AI/Models/Ollama"  # Adjust if needed
LOG_FILE="$HOME/control_center/ollama_api_setup.log"

# Create log file directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🔧 Starting Ollama API setup..."

# Ensure the configuration directory exists
if [ ! -d "$CONFIG_DIR" ]; then
    log "Configuration directory not found at $CONFIG_DIR. Creating it..."
    mkdir -p "$CONFIG_DIR" || { log "❌ Failed to create $CONFIG_DIR."; exit 1; }
fi

# Create or update the configuration file if it doesn't exist or is empty
if [ ! -s "$CONFIG_FILE" ]; then
    log "Configuration file not found or empty. Creating default configuration..."
    cat <<EOL > "$CONFIG_FILE"
{
  "model_dir": "$MODEL_DIR",
  "port": 11434
}
EOL
    if [ $? -eq 0 ]; then
        log "✅ Configuration file created at $CONFIG_FILE."
    else
        log "❌ Failed to create configuration file."
        exit 1
    fi
else
    log "✅ Configuration file exists at $CONFIG_FILE."
fi

# Stop any existing Ollama processes
log "Stopping any existing Ollama processes..."
sudo pkill -f "ollama serve" 2>/dev/null
sleep 2

# Start Ollama in API mode
log "Starting Ollama API..."
ollama serve &
sleep 2

# Verify if the API is now listening on the expected port
if lsof -i :11434 | grep -q "LISTEN"; then
    log "✅ Ollama API is now running on port 11434."
else
    log "❌ Ollama API failed to start or bind to port 11434."
fi
