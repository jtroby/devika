#!/bin/bash
# update_env.sh: Export, update, and install the conda environment file.
# This script exports the current Conda environment, processes the requirements.txt
# to separate packages available via Conda vs pip (with a whitelist for pip-only packages),
# generates an updated YAML file, and optionally installs the dependencies.
#
# Usage:
#   ./update_env.sh [--install] [--env <env_name>]
#
# Note: Version pinning is assumed to be handled in requirements.txt (e.g., numpy==1.21.2).

# Parse command-line arguments
TARGET_ENV=""
INSTALL_FLAG="false"
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --install) INSTALL_FLAG="true"; shift ;;
        --env) TARGET_ENV="$2"; shift 2 ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done

# Define the output file name (in the current directory).
OUTPUT_FILE="environment_updated.yml"

# Define the requirements file.
REQUIREMENTS_FILE="requirements.txt"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Conda environment export..."

# Export the current environment to a temporary file.
conda env export > temp_env.yml
if [ $? -ne 0 ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Error: Failed to export the environment."
  exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Environment export successful."

# Filter out build-specific metadata (e.g., lines starting with "prefix:").
grep -v '^prefix:' temp_env.yml > base_env.yml
if [ $? -ne 0 ]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Error: Failed to filter the environment file."
  exit 1
fi

rm temp_env.yml

# Define a whitelist for pip-only packages.
PIP_ONLY=("netlify-py" "fastlogging" "duckduckgo-search" "curl_cffi")

# Initialize variables for dependency sections.
CONDA_DEPS=""
PIP_DEPS=""

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Processing $REQUIREMENTS_FILE for dependency categorization..."

# Check if the requirements file exists.
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Error: $REQUIREMENTS_FILE not found."
    exit 1
fi

# Process each non-comment, non-empty line in requirements.txt.
while IFS= read -r line; do
    # Skip empty lines or lines starting with #
    if [[ -z "$line" || "$line" =~ ^# ]]; then
        continue
    fi

    # Extract the package name by removing version specifiers.
    pkg_name=$(echo "$line" | sed -E 's/==.*//')

    # Check if the package is in the pip-only whitelist.
    whitelist_match="false"
    for pkg in "${PIP_ONLY[@]}"; do
        if [[ "$pkg_name" == "$pkg" ]]; then
            whitelist_match="true"
            break
        fi
    done

    if [ "$whitelist_match" == "true" ]; then
        PIP_DEPS+="- $line"$'\n'
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $line is pip-only (whitelisted)."
        continue
    fi

    # Use conda search to see if the package is available via conda.
    search_result=$(conda search "$pkg_name" 2>/dev/null)
    if [[ -n "$search_result" ]]; then
        CONDA_DEPS+="- $line"$'\n'
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Found $line in Conda."
    else
        PIP_DEPS+="- $line"$'\n'
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] $line not found in Conda; marking for pip."
    fi
done < "$REQUIREMENTS_FILE"

# Read the environment name from the base environment export.
ENV_NAME=$(grep '^name:' base_env.yml | head -n1 | sed 's/name: //')

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Generating updated environment YAML file..."

# Generate the new YAML file with categorized dependencies.
cat <<EOF > "$OUTPUT_FILE"
name: ${ENV_NAME}
channels:
  - conda-forge
  - defaults
dependencies:
$(echo "$CONDA_DEPS" | sed 's/^/  /')
  - pip
  - pip:
$(echo "$PIP_DEPS" | sed 's/^/    /')
EOF

if [ $? -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Updated environment file saved as $OUTPUT_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Error: Failed to generate updated environment file."
fi

rm base_env.yml

# Optionally update the current environment with the new YAML file and install pip-only packages.
if [ "$INSTALL_FLAG" == "true" ]; then
    if [ -n "$TARGET_ENV" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing dependencies to environment: $TARGET_ENV..."
        conda env update -n "$TARGET_ENV" --file "$OUTPUT_FILE" --prune
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing dependencies in the current environment..."
        conda env update --file "$OUTPUT_FILE" --prune
    fi
    if [ $? -eq 0 ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Conda dependencies installed successfully."
        # Now install pip-only packages via pip as a fallback.
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing pip-only packages fallback..."
        while IFS= read -r pkg_line; do
            # Remove the leading "- " from the package line.
            pkg=$(echo "$pkg_line" | sed 's/^- //')
            if [ -n "$pkg" ]; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] Installing $pkg via pip..."
                pip install "$pkg"
            fi
        done <<< "$PIP_DEPS"
    else
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Error installing conda dependencies."
    fi
fi
