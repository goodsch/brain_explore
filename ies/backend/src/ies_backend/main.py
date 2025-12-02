"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ies_backend.api import profile, question_engine, session

app = FastAPI(
    title="IES Backend",
    description="Intelligent Exploration System - Entity extraction and knowledge management",
    version="0.1.0",
)

# Configure CORS for SiYuan plugin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # SiYuan can run on various ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(profile.router, prefix="/profile", tags=["profile"])
app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(question_engine.router, prefix="/question-engine", tags=["question-engine"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
