import os
import shutil
import time
from pathlib import Path

# Define directories
BASE_DIR = Path.home() / "control_center"
LOG_DIR = Path.home() / "automation_logs"
BACKUP_DIR = Path("/mnt/d/Backups")

# Set cleanup thresholds
DAYS_OLD = 30
NOW = time.time()

def move_old_files(directory, destination, days_old):
    """ Move files older than specified days to a backup folder. """
    if not os.path.exists(destination):
        os.makedirs(destination)
    
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
