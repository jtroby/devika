#!/usr/bin/env bash
# =============================================================================
# Name: full_setup_cuda_minikube_ollama.sh
# -----------------------------------------------------------------------------
# Description:
#   This is a comprehensive "all-in-one" installation script designed for
#   Ubuntu 22.04 on WSL2. It reinstalls or upgrades CUDA for GPU pass-through,
#   sets up Docker and Minikube, installs Python + virtual environment
#   dependencies (Devika, Ollama, LangChain, etc.), configures Ollama to store
#   large models on /mnt/d/AI/Models/Ollama, and creates self-healing scripts.
#
# Usage:
#   1. Make sure you have WSL2 with enough resources allocated (in .wslconfig).
#   2. Save this script, e.g., as "full_setup_cuda_minikube_ollama.sh".
#   3. Make it executable:
#       chmod +x full_setup_cuda_minikube_ollama.sh
#   4. Run it (with sudo if system-level changes are needed):
#       sudo ./full_setup_cuda_minikube_ollama.sh
#
# Important Notes:
#   - This script is tailored for WSL2 with a NVIDIA GPU. It expects that:
#       (a) Your Windows host has the latest NVIDIA drivers installed.
#       (b) You want to store Ollama models in /mnt/d/AI/Models/Ollama.
#   - Adjust paths or remove sections you don't need (e.g., Tailscale).
#   - The script logs all output to a file: ./full_setup_cuda_minikube_ollama.log
#   - If you already have partial installations, this may overwrite configurations.
#   - The Docker/Minikube steps assume you want to run Docker-based containers
#     in WSL2 using the "docker" driver.
#
# Functional Description (Phases):
#   1) Remove partial/old CUDA packages, reinstall the correct CUDA version.
#   2) Install Docker if missing, check Docker readiness.
#   3) Install Minikube + kubectl, attempt to start a local cluster.
#   4) (Optional) Install Tailscale for secure overlay networking.
#   5) Set up Python environment (venv), and install Devika, Ollama + dependencies.
#   6) Configure Ollama for storing models in /mnt/d/AI/Models/Ollama.
#   7) Pull the Mistral model with updated Ollama CLI usage.
#   8) Test-run Ollama with the "ollama run mistral -p 'Hello'" command.
#   9) Clone Devika if missing, install Devika's own dependencies.
#   10) Create self-healing scripts (ollama_status.py, check_system_health.py).
#
# How-Tos:
#   - Check the log file for errors: cat ./full_setup_cuda_minikube_ollama.log
#   - If Minikube fails to start, run "minikube logs" or
#     "minikube start --driver=docker --alsologtostderr -v=5" for more details.
#   - If CUDA is not working, confirm "nvidia-smi" and "nvcc --version" in WSL2.
#   - For Ollama, use "ollama serve" to run the server in the foreground, or
#     implement a systemd/cron-based approach to run it in the background.
#
# -----------------------------------------------------------------------------
# License: Public Domain / CC0 — Use, modify, and share freely.
# =============================================================================

LOG_FILE="./full_setup_cuda_minikube_ollama.log"
touch "$LOG_FILE"

###############################################################################
# Helper Functions for Logging and Phase Indication
###############################################################################
function log() {
  echo "[INFO] $1" | tee -a "$LOG_FILE"
}

function warn() {
  echo "[WARN] $1" | tee -a "$LOG_FILE"
}

function error_msg() {
  echo "[ERROR] $1" | tee -a "$LOG_FILE"
}

function phase_start() {
  echo "" | tee -a "$LOG_FILE"
  echo "===================================================================" | tee -a "$LOG_FILE"
  echo "PHASE: $1" | tee -a "$LOG_FILE"
  echo "===================================================================" | tee -a "$LOG_FILE"
}

###############################################################################
# PHASE 1: Remove existing CUDA packages, reinstall the correct version
# -----------------------------------------------------------------------------
# Why? We want a fresh or updated CUDA that matches your GPU driver
# to enable GPU pass-through in WSL2. This sets up "nvcc" & "nvidia-smi".
###############################################################################
phase_start "Remove existing CUDA packages and reinstall the correct version"

# Attempt to purge old installations
log "Purging old CUDA packages..."
sudo apt-get remove --purge nvidia-cuda-toolkit cuda -y >> "$LOG_FILE" 2>&1
sudo apt-get autoremove -y >> "$LOG_FILE" 2>&1

# Download and install the CUDA keyring
log "Downloading CUDA keyring for Ubuntu 22.04..."
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb -O cuda-keyring.deb >> "$LOG_FILE" 2>&1
sudo dpkg -i cuda-keyring.deb >> "$LOG_FILE" 2>&1
rm -f cuda-keyring.deb

# Update repos and install CUDA
log "Installing CUDA from official repo..."
sudo apt-get update -y >> "$LOG_FILE" 2>&1
if sudo apt-get install -y cuda >> "$LOG_FILE" 2>&1; then
  log "CUDA installation completed."
else
  error_msg "CUDA installation failed."
fi

# Validate nvcc and nvidia-smi
if command -v nvcc >/dev/null 2>&1; then
  log "nvcc version information:"
  nvcc --version | tee -a "$LOG_FILE"
else
  warn "nvcc not found after installation, please check your CUDA setup."
fi

if command -v nvidia-smi >/dev/null 2>&1; then
  log "nvidia-smi output:"
  nvidia-smi | tee -a "$LOG_FILE"
else
  warn "nvidia-smi not available. GPU pass-through may not be fully configured."
fi

###############################################################################
# PHASE 2: Install Docker if missing
# -----------------------------------------------------------------------------
# Why? We need Docker for container-based operations and to run Minikube
# with the "docker" driver on WSL2.
###############################################################################
phase_start "Install Docker if missing"

if ! command -v docker &> /dev/null; then
  log "Docker not found. Installing Docker CE..."
  sudo apt-get install -y ca-certificates curl gnupg lsb-release >> "$LOG_FILE" 2>&1
  sudo mkdir -p /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg >> "$LOG_FILE" 2>&1
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list >> "$LOG_FILE"

  sudo apt-get update -y >> "$LOG_FILE" 2>&1
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin >> "$LOG_FILE" 2>&1

  # Enable Docker in systemd if possible
  sudo systemctl enable docker >> "$LOG_FILE" 2>&1 || true
  sudo systemctl start docker >> "$LOG_FILE" 2>&1 || true

  # Add current user to Docker group (may require re-login)
  sudo usermod -aG docker "$USER" >> "$LOG_FILE" 2>&1 || true

  log "Docker installation complete. Check Docker info below:"
else
  log "Docker already installed. Checking Docker info..."
fi

docker info >> "$LOG_FILE" 2>&1 || warn "Docker daemon might not be fully running."

###############################################################################
# PHASE 3: Install Minikube and kubectl
# -----------------------------------------------------------------------------
# Why? This sets up a local Kubernetes cluster. We use the "docker" driver
# in WSL2, so ensure Docker is running first.
###############################################################################
phase_start "Install Minikube and kubectl"

if ! command -v kubectl &> /dev/null; then
  log "kubectl not found, installing stable version from official source..."
  VERSION_KUBECTL="$(curl -L -s https://dl.k8s.io/release/stable.txt)"
  curl -LO "https://dl.k8s.io/release/${VERSION_KUBECTL}/bin/linux/amd64/kubectl" >> "$LOG_FILE" 2>&1
  sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
  rm -f kubectl
else
  log "kubectl already installed."
fi

if ! command -v minikube &> /dev/null; then
  log "Minikube not found, installing..."
  curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 >> "$LOG_FILE" 2>&1
  sudo install minikube-linux-amd64 /usr/local/bin/minikube
  rm -f minikube-linux-amd64
else
  log "Minikube already installed."
fi

log "Attempting to start Minikube with driver=docker..."
minikube start --driver=docker --alsologtostderr -v=5 >> "$LOG_FILE" 2>&1 || warn "Minikube start may have failed or partially succeeded."
log "Minikube status:"
minikube status >> "$LOG_FILE" 2>&1 || true

###############################################################################
# PHASE 4: Optional Tailscale installation
# -----------------------------------------------------------------------------
# Why? Tailscale can provide easy VPN overlay networking. Skip if not needed.
###############################################################################
phase_start "Optional Tailscale installation"

if ! command -v tailscale &> /dev/null; then
  log "Installing Tailscale. This step is optional, skip if you don't need it."
  curl -fsSL https://tailscale.com/install.sh | sh >> "$LOG_FILE" 2>&1 || warn "Tailscale installation script failed."
else
  log "Tailscale already installed."
fi

###############################################################################
# PHASE 5: Install Python3 venv, Devika, and related dependencies
# -----------------------------------------------------------------------------
# Why? We want a dedicated Python environment to install Devika, Ollama bindings,
# and additional libraries (FastAPI, LangChain, etc.).
###############################################################################
phase_start "Install Python3 venv, Devika, and related dependencies"

sudo apt-get install -y python3 python3-pip python3-venv >> "$LOG_FILE" 2>&1
ENV_NAME="automation_env"

if [ ! -d "$ENV_NAME" ]; then
  log "Creating Python virtual environment: $ENV_NAME"
  python3 -m venv "$ENV_NAME" >> "$LOG_FILE" 2>&1
else
  log "Python venv '$ENV_NAME' already exists."
fi

source "$ENV_NAME/bin/activate"
log "Upgrading pip..."
pip install --upgrade pip >> "$LOG_FILE" 2>&1

log "Installing Devika, Ollama, FastAPI, LangChain, ChromaDB, pytest, rich..."
pip install devika ollama fastapi langchain chromadb pytest rich >> "$LOG_FILE" 2>&1

###############################################################################
# PHASE 6: Install Ollama if missing, configure for /mnt/d/AI/Models/Ollama
# -----------------------------------------------------------------------------
# Why? We want to store large models on the D: drive, which WSL sees as /mnt/d/.
###############################################################################
phase_start "Install Ollama if missing, configure for /mnt/d/AI/Models/Ollama"

if ! command -v ollama &> /dev/null; then
  log "Ollama not found, installing..."
  curl -fsSL https://ollama.ai/install.sh | sh >> "$LOG_FILE" 2>&1
else
  log "Ollama already installed."
fi

mkdir -p "$(dirname "$HOME/.ollama/config.json")"
cat <<EOF > "$HOME/.ollama/config.json"
{
  "model_dir": "/mnt/d/AI/Models/Ollama",
  "port": 11434
}
EOF

mkdir -p "/mnt/d/AI/Models/Ollama"

###############################################################################
# PHASE 7: Pull mistral model using new CLI usage
# -----------------------------------------------------------------------------
# Why? The older CLI used --prompt, but from Ollama 0.5.7 onward, usage changed.
###############################################################################
phase_start "Pull mistral model using new CLI usage"

ollama_version="$(ollama --version 2>&1 | grep 'client version' || true)"
log "Ollama version info: $ollama_version"

# Attempt to pull the mistral model. If it fails, the script won't exit
# but we will log a warning so you can investigate.
(ollama pull mistral) >> "$LOG_FILE" 2>&1 || warn "Could not pull mistral model or the server isn't running."

###############################################################################
# PHASE 8: Test Ollama run with updated syntax
# -----------------------------------------------------------------------------
# Why? We confirm the new CLI usage. Typically "ollama run <model> -p 'Hello'".
###############################################################################
phase_start "Test Ollama run with updated syntax"

# The new approach is "ollama run mistral -p 'Hello'" or "ollama run mistral 'Hello'".
(ollama run mistral -p "Hello") >> "$LOG_FILE" 2>&1 || warn "Ollama run mistral test failed, check if it's running or GPU config."

###############################################################################
# PHASE 9: Clone Devika if missing, install devika/requirements.txt
# -----------------------------------------------------------------------------
# Why? Devika's own repo may have additional libraries not covered above.
###############################################################################
phase_start "Clone Devika if missing, install devika/requirements.txt"

if [ ! -d "devika" ]; then
  log "Cloning Devika repo from GitHub..."
  git clone https://github.com/stitionai/devika.git >> "$LOG_FILE" 2>&1 || warn "Could not clone Devika repo."
else
  log "Devika repository folder already exists. Skipping clone."
fi

if [ -d "devika" ]; then
  cd devika
  if [ -f requirements.txt ]; then
    log "Installing Devika-specific requirements..."
    pip install -r requirements.txt >> "$LOG_FILE" 2>&1 || warn "Could not install Devika requirements."
  else
    warn "No requirements.txt found in devika/."
  fi
  cd ..
fi

###############################################################################
# PHASE 10: Create self-healing scripts (ollama_status.py, check_system_health.py)
# -----------------------------------------------------------------------------
# Why? We automate checks for Ollama and system health. If Ollama is down, we
# can attempt to restart it. If Docker or Minikube fail, we log the error.
###############################################################################
phase_start "Create self-healing scripts (ollama_status.py, check_system_health.py)"

cat <<'EOS' > ollama_status.py
#!/usr/bin/env python3
"""
ollama_status.py - Self-healing script for Ollama

DESCRIPTION:
    This script checks the Ollama API on http://localhost:11434/api.
    If Ollama is unreachable or returns an unexpected status, we kill
    any existing 'ollama' process and relaunch 'ollama serve' with the
    'mistral' model. The script logs events to ollama_status.log.

USAGE:
    1. Make this file executable: chmod +x ollama_status.py
    2. Run manually: ./ollama_status.py
    3. (Optional) Automate with cron or systemd to run regularly or continuously.
"""

import requests
import subprocess
import time
import logging

logging.basicConfig(filename='ollama_status.log', level=logging.INFO)

def check_ollama():
    """Checks if the Ollama API is responding with a 200 status."""
    try:
        response = requests.post(
            "http://localhost:11434/api",
            json={"model": "mistral", "prompt": "ping"},
            timeout=5
        )
        if response.status_code == 200:
            logging.info("Ollama is healthy.")
            return True
    except Exception as e:
        logging.error(f"Ollama check error: {e}")
    return False

def restart_ollama():
    """Kills any running ollama process and restarts it in serve mode."""
    logging.info("Attempting to restart Ollama process...")
    try:
        subprocess.run(["pkill", "ollama"], check=False)
        time.sleep(3)
        subprocess.Popen(["ollama", "serve", "--model", "mistral"])
        logging.info("Restarted Ollama in serve mode with 'mistral'.")
    except Exception as e:
        logging.error(f"Failed to restart Ollama: {e}")

if __name__ == "__main__":
    while True:
        if not check_ollama():
            restart_ollama()
        time.sleep(60)
EOS

cat <<'EOS' > check_system_health.py
#!/usr/bin/env python3
"""
check_system_health.py - Self-healing or Monitoring for Docker & Minikube

DESCRIPTION:
    This script checks Docker and Minikube statuses, logging any issues.
    You can extend it to check GPU usage, memory, or other system resources.

USAGE:
    1. Make executable: chmod +x check_system_health.py
    2. Optionally run with cron or systemd to verify system health periodically.
"""

import logging
import subprocess

logging.basicConfig(filename='system_health.log', level=logging.INFO)

def check_docker():
    """Runs 'docker info' to verify Docker is up and running."""
    try:
        subprocess.run(["docker", "info"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("Docker is running.")
    except subprocess.CalledProcessError:
        logging.error("Docker check failed.")

def check_minikube():
    """Runs 'minikube status' to see if all Minikube components are 'Running'."""
    try:
        out = subprocess.check_output(["minikube", "status"])
        if b"Running" in out:
            logging.info("Minikube is running.")
        else:
            logging.error("Minikube is not fully running.")
    except Exception as e:
        logging.error(f"Minikube check error: {e}")

if __name__ == "__main__":
    check_docker()
    check_minikube()
EOS

chmod +x ollama_status.py check_system_health.py

###############################################################################
# FINAL MESSAGE
###############################################################################
log "Setup complete. All phases have been attempted. Please review $LOG_FILE for details."
log "You can now test or refine each phase as needed. For example:"
log "  - Run 'nvidia-smi' or 'nvcc --version' to confirm CUDA is correct."
log "  - 'minikube status' or 'minikube kubectl -- get pods -A' to confirm K8s is up."
log "  - 'ollama run mistral -p \"Hello\"' to test local LLM inference."
log "  - './ollama_status.py' to continuously monitor Ollama in a separate shell."
