"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ies_backend.api import (
    book_entities,
    books,
    context,
    conversations,
    inbox,
    flow_session,
    graph,
    journey,
    personal,
    profile,
    question_engine,
    reframe,
    quick_add,
    sources,
    session,
    template,
    thinking,
)

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
app.include_router(graph.router, prefix="/graph", tags=["graph"])
app.include_router(book_entities.router, prefix="/graph", tags=["graph"])
app.include_router(journey.router, tags=["journeys"])
# Conversation imports
app.include_router(conversations.router, tags=["conversations"])
# Inbox router mounted at both paths for migration
app.include_router(inbox.router, prefix="/inbox", tags=["inbox"])  # New canonical path
app.include_router(inbox.router, prefix="/capture", tags=["inbox"])  # Backward compatibility
app.include_router(thinking.router, tags=["thinking"])
app.include_router(flow_session.router, tags=["flow"])
app.include_router(context.router, tags=["context"])
app.include_router(reframe.router, prefix="/reframes", tags=["reframes"])
app.include_router(personal.router, tags=["personal"])
app.include_router(books.router, tags=["books"])
app.include_router(sources.router, tags=["sources"])
app.include_router(quick_add.router, tags=["quick-add"])
app.include_router(template.router, tags=["templates"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
