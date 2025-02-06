#!/bin/bash
# dynamic_update_references.sh
# This script replaces all occurrences of an old directory path with a new directory path
# within files of specified types. It is designed to be flexible so that you can update
# references whenever your project structure changes.
#
# Usage:
#   ./dynamic_update_references.sh <target_dir> <old_path> <new_path>
#
# Example:
#   ./dynamic_update_references.sh /home/jt-msi/project "/home/jt-msi/automation_agent/" "/home/jt-msi/control_center/"

# Check for the required number of arguments
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <target_dir> <old_path> <new_path>"
    exit 1
fi

TARGET_DIR="$1"
OLD_PATH="$2"
NEW_PATH="$3"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting reference update in $TARGET_DIR..."
echo "Replacing all occurrences of \"$OLD_PATH\" with \"$NEW_PATH\"."

# Find files with specified extensions and perform the replacement
find "$TARGET_DIR" -type f \( -name '*.sh' -o -name '*.py' -o -name '*.txt' -o -name '*.md' \) -exec sed -i "s|$OLD_PATH|$NEW_PATH|g" {} +

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Update complete. Please review changes."
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Error occurred during the update process."
fi
