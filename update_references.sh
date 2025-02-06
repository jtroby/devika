#!/bin/bash
# update_references.sh
# This script replaces all occurrences of "/home/jt-msi/control_center/" with "/home/jt-msi/control_center/"
# in files with extensions .sh, .py, .txt, and .md within the TARGET_DIR.
# Adjust TARGET_DIR if you want to limit the search to a specific folder.

TARGET_DIR="$HOME"
OLD_PATH="/home/jt-msi/control_center/"
NEW_PATH="/home/jt-msi/control_center/"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting reference update..."
echo "Replacing all occurrences of \"$OLD_PATH\" with \"$NEW_PATH\" in files under $TARGET_DIR."

# Use find with a directly embedded expression for file extensions.
find "$TARGET_DIR" -type f \( -name '*.sh' -o -name '*.py' -o -name '*.txt' -o -name '*.md' \) -exec sed -i "s|$OLD_PATH|$NEW_PATH|g" {} +

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Update complete. Please review changes."
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Error occurred during the update process."
fi


