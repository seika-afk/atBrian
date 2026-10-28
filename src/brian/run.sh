#!/usr/bin/env zsh

ollama serve &
ollama_pid=$!

sleep 2

uv run Tag_waiting.py &
script_pid=$!

cleanup() {
    echo "\nStopping both processes..."
    kill $ollama_pid $script_pid 2>/dev/null
    wait $ollama_pid $script_pid 2>/dev/null
    echo "Both processes stopped."
    exit 0
}

trap cleanup INT TERM

wait
