#!/bin/bash

set -e  # Exit on any error

USERNAME=$(whoami)
SUDOERS_FILE="/etc/sudoers.d/$USERNAME"

echo "🔧 Configuring passwordless sudo access for $USERNAME..."

# Ensure the sudoers file exists
if [ ! -f "$SUDOERS_FILE" ]; then
    echo "Creating sudoers file for $USERNAME..."
    sudo touch "$SUDOERS_FILE"
    sudo chmod 0440 "$SUDOERS_FILE"
fi

# Define the required commands
REQUIRED_COMMANDS=(
    "/bin/systemctl restart docker"
    "/bin/systemctl stop docker"
    "/bin/systemctl start docker"
    "/usr/bin/pkill -f ollama"
    "/usr/bin/minikube start"
    "/usr/bin/minikube stop"
    "/usr/bin/minikube delete"
)

# Add commands to the sudoers file if not already present
for CMD in "${REQUIRED_COMMANDS[@]}"; do
    if ! sudo grep -q "$CMD" "$SUDOERS_FILE"; then
        echo "$USERNAME ALL=(ALL) NOPASSWD: $CMD" | sudo tee -a "$SUDOERS_FILE" > /dev/null
        echo "✅ Added: $CMD"
    else
        echo "✔️ Already exists: $CMD"
    fi
done

echo "🔄 Reloading sudoers rules..."
sudo chmod 0440 "$SUDOERS_FILE"
sudo visudo -c  # Validate sudoers file syntax

echo "✅ Passwordless sudo access configured successfully!"
