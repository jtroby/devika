import os
import shutil
import time
from pathlib import Path
import platform

# Detect if running in GitHub Actions
if "GITHUB_ACTIONS" in os.environ:
    BACKUP_DIR = Path(os.getenv("GITHUB_WORKSPACE", "/home/runner/work/devika/devika")) / "backups"
else:
    BACKUP_DIR = Path("/mnt/d/Backups")  # Local WSL2 path

# Debugging: Print the chosen backup directory
print(f"🔍 Using BACKUP_DIR: {BACKUP_DIR}")

# Ensure the directory exists
os.makedirs(BACKUP_DIR, exist_ok=True)

# Define directories
BASE_DIR = Path.home() / "control_center"
LOG_DIR = Path.home() / "automation_logs"
if "GITHUB_ACTIONS" in os.environ:
    BACKUP_DIR = Path(os.getenv("GITHUB_WORKSPACE", "/home/runner/work/devika/devika")) / "backups"
else:
    if "GITHUB_ACTIONS" in os.environ:
        BACKUP_DIR = Path(os.getenv("GITHUB_WORKSPACE", "/home/runner/work/devika/devika")) / "backups"
    else:
        BACKUP_DIR = Path("/mnt/d/Backups")  # Local WSL2 path


# Set cleanup thresholds
DAYS_OLD = 30
NOW = time.time()

def move_old_files(directory, destination, days_old):
    """ Move files older than specified days to a backup folder. """
    if not os.path.exists(destination):
        print(f"🚨 ERROR: Directory '{directory}' does not exist. Creating it now...")
        os.makedirs(directory, exist_ok=True)
    
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            file_age = NOW - os.path.getmtime(file_path)
            if file_age > (days_old * 86400):  # Convert days to seconds
                shutil.move(file_path, os.path.join(destination, file))
                print(f"📁 Moved {file} to {destination}")

def cleanup():
    print("🧹 Running File Cleanup...")

    # Move old logs & backups
    move_old_files(LOG_DIR, BACKUP_DIR / "logs", DAYS_OLD)
    move_old_files(BASE_DIR, BACKUP_DIR / "scripts", DAYS_OLD)

    print("✅ Cleanup Completed.")

if __name__ == "__main__":
    cleanup()
