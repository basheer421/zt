from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
from database import init_db, close_db
from ml_engine import load_models

# Security
security = HTTPBearer()

# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    init_db()
    load_models()
    yield
    # Shutdown
    print("Shutting down...")
    close_db()

# Initialize FastAPI app
app = FastAPI(
    title="FastAPI Backend",
    description="Backend API with ML capabilities",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "FastAPI Backend is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Example protected endpoint
@app.get("/api/protected")
async def protected_route(credentials: HTTPBearer = Depends(security)):
    return {"message": "This is a protected route", "token": credentials.credentials}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
