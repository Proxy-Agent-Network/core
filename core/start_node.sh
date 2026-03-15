#!/bin/bash

# Start the LangGraph MCP Server in the background (Unbuffered)
echo "Starting MCP Server (Port 8000)..."
python -u mcp_server.py &

# Start the Flask Dashboard in the foreground (Unbuffered)
echo "Starting Dashboard (Port 5000)..."
python -u app.py