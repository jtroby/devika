#!/usr/bin/env python3
"""
cleanup_files.py

🧹 This script automatically organizes logs & backups:
  ✅ Moves old logs to the backup folder
  ✅ Ensures directories exist before accessing them
  ✅ Uses correct paths inside GitHub Actions
"""

import os
import shutil
import time
from pathlib import Path

# 🛠️ Configuration
DAYS_OLD = 7  # Move files older than this

# 🔍 Detect GitHub Actions Environment
if "GITHUB_ACTIONS" in os.environ:
    BASE_DIR = Path(os.getenv("GITHUB_WORKSPACE", "/home/runner/work/devika/devika"))
else:
    BASE_DIR = Path("/home/jt-msi")

LOG_DIR = BASE_DIR / "automation_logs"
BACKUP_DIR = BASE_DIR / "backups"

# ✅ Ensure directories exist
for dir_path in [LOG_DIR, BACKUP_DIR]:
    if not dir_path.exists():
        print(f"📂 Creating directory: {dir_path}")
        os.makedirs(dir_path, exist_ok=True)

def move_old_files(directory, destination, days_old):
    """
    Moves files older than `days_old` from `directory` to `destination`
    """
    print(f"🛠️ Checking for old files in: {directory}")

    if not directory.exists():
        print(f"🚨 ERROR: Directory '{directory}' does not exist! Skipping...")
        return

    cutoff_time = time.time() - (days_old * 86400)  # Convert days to seconds
    moved_files = 0

    for file in directory.iterdir():
        if file.is_file() and file.stat().st_mtime < cutoff_time:
            target_path = destination / file.name
            print(f"📦 Moving {file} → {target_path}")
            shutil.move(str(file), str(target_path))
            moved_files += 1

    print(f"✅ Moved {moved_files} old files to {destination}")

def cleanup():
    """
    Runs the cleanup process
    """
    print(f"🔍 Using BACKUP_DIR: {BACKUP_DIR}")
    print("🧹 Running File Cleanup...")

    move_old_files(LOG_DIR, BACKUP_DIR / "logs", DAYS_OLD)

    print("✅ Cleanup Completed.")

if __name__ == "__main__":
    cleanup()

