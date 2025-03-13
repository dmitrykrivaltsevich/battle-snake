#!/bin/bash

# Install dependencies using uv if needed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with uv..."
    uv venv
fi

echo "Installing dependencies with uv..."
uv pip install -r requirements.txt

echo "Running tests..."
./.venv/bin/python -m pytest test_battle_snake.py -v

echo "Tests completed!"