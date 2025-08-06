#!/usr/bin/env python3
"""
Simple startup script for No Code Sutra Backend
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create a simple FastAPI app for testing
app = FastAPI(title="No Code Sutra API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "No Code Sutra API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Backend is operational"}

@app.get("/api/status")
async def api_status():
    return {
        "status": "online",
        "version": "1.0.0",
        "environment": "development"
    }

if __name__ == "__main__":
    print("🚀 Starting No Code Sutra Backend...")
    print("📍 API will be available at: http://localhost:8000")
    print("📚 API docs will be available at: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print()
    
    uvicorn.run(
        "start_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )