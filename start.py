#!/usr/bin/env python3
"""
Enterprise LLMOps RAG System Startup Script

Starts both API server and Streamlit frontend automatically.
"""

import subprocess
import time
import os
import signal
import sys
from pathlib import Path

def run_command(cmd: str, name: str) -> subprocess.Popen:
    """Run a command in background."""
    print(f"🚀 Starting {name}...")
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid if hasattr(os, 'setsid') else None
    )
    return process


def main():
    print("=" * 60)
    print("🤖 Enterprise LLMOps RAG System")
    print("=" * 60)
    print()
    
    # Get project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Start API server
    api_cmd = '"{}/llmops-env/bin/python" -m uvicorn api_gateway.main:app --reload --host 0.0.0.0 --port 8000'.format(project_dir)
    api_process = run_command(api_cmd, "API Server (port 8000)")
    
    # Wait a bit for API to start
    time.sleep(3)
    
    # Start Streamlit frontend
    streamlit_cmd = '"{}/llmops-env/bin/streamlit" run frontend_streamlit/app.py --server.port 8501'.format(project_dir)
    streamlit_process = run_command(streamlit_cmd, "Streamlit Frontend (port 8501)")
    
    print()
    print("=" * 60)
    print("✓ System Started Successfully!")
    print("=" * 60)
    print()
    print("🌐 Access the system:")
    print("   Frontend:  http://localhost:8501")
    print("   API Docs:  http://localhost:8000/docs")
    print()
    print("Press Ctrl+C to stop...")
    print()
    
    try:
        # Wait for processes
        api_process.wait()
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n\n⏹️  Shutting down...")
        try:
            os.killpg(os.getpgid(api_process.pid), signal.SIGTERM)
            os.killpg(os.getpgid(streamlit_process.pid), signal.SIGTERM)
        except:
            pass
        print("✓ Shutdown complete")


if __name__ == "__main__":
    main()
