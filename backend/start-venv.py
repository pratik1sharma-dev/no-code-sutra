#!/usr/bin/env python3
"""
Startup script for No Code Sutra Python Backend with Virtual Environment
"""

import os
import sys
import subprocess
import uvicorn
from pathlib import Path

def main():
    """Start the FastAPI server with virtual environment"""
    
    # Check if we're in a virtual environment
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment not detected!")
        print("Please activate the virtual environment first:")
        print("  .\\venv\\Scripts\\Activate.ps1  # PowerShell")
        print("  .\\venv\\Scripts\\activate.bat  # Command Prompt")
        print()
    
    # Check if .env file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("ℹ️  Info: .env file not found")
        print("The backend will work without OpenAI API key for basic workflow generation")
        print()
    
    print("🚀 Starting No Code Sutra Backend...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print()
    
    # Start the server
    uvicorn.run(
        "main-simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 