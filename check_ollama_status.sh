#!/bin/bash

echo "🔍 Checking Ollama Status..."

if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama is running."
else
    echo "⚠️ Ollama is NOT running. Attempting to start..."
    nohup ollama serve > /mnt/d/logs/ollama.log 2>&1 &
    sleep 3
    if pgrep -x "ollama" > /dev/null; then
        echo "✅ Ollama started successfully."
    else
        echo "❌ Failed to start Ollama. Check logs."
    fi
fi
