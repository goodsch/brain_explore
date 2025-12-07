#!/usr/bin/env python3
"""IES MCP Server - ForgeMode thinking sessions via Claude Desktop/mobile.

A lightweight MCP server that wraps the IES backend APIs, enabling voice-driven
ForgeMode sessions. Uses Redis session persistence via the backend.
"""

import asyncio
import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configuration
BACKEND_URL = os.environ.get("IES_BACKEND_URL", "http://localhost:8081")

# Template mode mapping
MODE_TO_TEMPLATE = {
    "learning": "learning-mechanism-map",
    "articulating": "articulating-clarify-intuition",
    "planning": "planning-implementation",  # Future
    "ideating": "ideating-possibilities",  # Future
    "reflecting": "reflecting-patterns",  # Future
}

# Question class hints for cognitive guidance
QUESTION_CLASS_HINTS = {
    "schema_probe": "Try listing the main categories, components, or buckets",
    "boundary": "Consider what's NOT included, where does this end?",
    "dimensional": "Think in terms of spectra or scales",
    "causal": "What causes this? What has to happen first?",
    "counterfactual": "What if the opposite were true?",
    "anchor": "Give a specific, concrete example",
    "perspective_shift": "How would someone else see this?",
    "meta_cognitive": "What patterns do you notice in your thinking?",
    "reflective_synthesis": "What's the main insight that ties this together?",
}

server = Server("ies-forgemode")


async def _backend_get(path: str) -> dict[str, Any]:
    """Make GET request to backend."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BACKEND_URL}{path}")
        response.raise_for_status()
        return response.json()


async def _backend_post(path: str, data: dict[str, Any]) -> dict[str, Any]:
    """Make POST request to backend."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(f"{BACKEND_URL}{path}", json=data)
        response.raise_for_status()
        return response.json()


async def _load_template(template_id: str) -> dict[str, Any] | None:
    """Load template from backend."""
    try:
        return await _backend_get(f"/templates/templates/{template_id}")
    except httpx.HTTPStatusError:
        return None


async def _get_session(session_id: str) -> dict[str, Any] | None:
    """Get session state from backend."""
    try:
        result = await _backend_get(f"/session/state/{session_id}")
        return result
    except httpx.HTTPStatusError:
        return None


async def _update_session(session_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    """Update session state in backend."""
    try:
        return await _backend_post(f"/session/state/{session_id}", updates)
    except httpx.HTTPStatusError:
        return None


def _get_current_question(template: dict, section_index: int) -> dict[str, Any]:
    """Get current question from template section."""
    sections = template.get("sections", [])
    if section_index >= len(sections):
        return {"complete": True, "question": None}

    section = sections[section_index]
    return {
        "complete": False,
        "question": section.get("prompt", ""),
        "section_id": section.get("id", ""),
        "section_index": section_index,
        "total_sections": len(sections),
        "required": section.get("required", False),
        "input_type": section.get("input_type", "freeform"),
    }


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available MCP tools."""
    return [
        Tool(
            name="start_session",
            description="Start a ForgeMode thinking session with a specific mode and topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["learning", "articulating", "planning", "ideating", "reflecting"],
                        "description": "Thinking mode to use",
                    },
                    "topic": {
                        "type": "string",
                        "description": "What you want to think about",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (default: 'default')",
                        "default": "default",
                    },
                },
                "required": ["mode", "topic"],
            },
        ),
        Tool(
            name="submit_response",
            description="Submit response to current question and get the next one",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Active session identifier",
                    },
                    "response": {
                        "type": "string",
                        "description": "User's response to the current question",
                    },
                },
                "required": ["session_id", "response"],
            },
        ),
        Tool(
            name="end_session",
            description="End session and trigger entity extraction",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session to end",
                    },
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="get_question",
            description="Get current question (for context recovery after interruption)",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Active session identifier",
                    },
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="list_templates",
            description="List available thinking modes/templates",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="get_status",
            description="Get session status, progress, and history",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session to check",
                    },
                },
                "required": ["session_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""

    if name == "start_session":
        result = await _start_session(
            mode=arguments["mode"],
            topic=arguments["topic"],
            user_id=arguments.get("user_id", "default"),
        )
    elif name == "submit_response":
        result = await _submit_response(
            session_id=arguments["session_id"],
            response=arguments["response"],
        )
    elif name == "end_session":
        result = await _end_session(session_id=arguments["session_id"])
    elif name == "get_question":
        result = await _get_question(session_id=arguments["session_id"])
    elif name == "list_templates":
        result = await _list_templates()
    elif name == "get_status":
        result = await _get_status(session_id=arguments["session_id"])
    else:
        result = {"error": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def _start_session(mode: str, topic: str, user_id: str) -> dict[str, Any]:
    """Start a ForgeMode session."""
    # Validate mode
    if mode not in MODE_TO_TEMPLATE:
        return {"error": f"Invalid mode: {mode}. Available: {list(MODE_TO_TEMPLATE.keys())}"}

    template_id = MODE_TO_TEMPLATE[mode]

    # Load template
    template = await _load_template(template_id)
    if not template:
        return {"error": f"Template '{template_id}' not found. Only 'learning' and 'articulating' are available."}

    # Start session via backend
    try:
        session_result = await _backend_post("/session/start", {"user_id": user_id})
        session_id = session_result.get("session_id")
    except httpx.HTTPError as e:
        return {"error": f"Failed to start session: {e}"}

    # Store ForgeMode state in session
    forge_state = {
        "mode": mode,
        "topic": topic,
        "template_id": template_id,
        "template": template,
        "current_section": 0,
        "section_responses": {},
    }

    # Update session with ForgeMode state
    try:
        await _backend_post(f"/session/state/{session_id}", {"forge_mode": forge_state})
    except httpx.HTTPError:
        # If state endpoint doesn't exist, we'll track locally
        pass

    # Get first question
    question_info = _get_current_question(template, 0)

    return {
        "session_id": session_id,
        "mode": mode,
        "topic": topic,
        "template_name": template.get("name", template_id),
        "template_description": template.get("description", ""),
        "current_question": question_info.get("question"),
        "section_id": question_info.get("section_id"),
        "progress": f"1/{question_info.get('total_sections', 1)}",
        "hints": [
            "Take your time with each response",
            "You can skip non-required sections by saying 'skip'",
            "Say 'end session' when you want to finish and extract insights",
        ],
    }


async def _submit_response(session_id: str, response: str) -> dict[str, Any]:
    """Submit response to current question."""
    # Get session state
    session = await _get_session(session_id)
    if not session:
        # Try to recover from backend session list
        return {"error": f"Session '{session_id}' not found or expired"}

    forge_state = session.get("forge_mode", {})
    if not forge_state:
        return {"error": "Session is not a ForgeMode session"}

    template = forge_state.get("template", {})
    current_section = forge_state.get("current_section", 0)
    section_responses = forge_state.get("section_responses", {})

    # Get current section info
    sections = template.get("sections", [])
    if current_section >= len(sections):
        return {
            "complete": True,
            "message": "Session is already complete. Use 'end_session' to extract insights.",
        }

    section = sections[current_section]
    section_id = section.get("id", f"section_{current_section}")

    # Handle skip
    if response.lower().strip() == "skip":
        if section.get("required", False):
            return {
                "error": "This section is required and cannot be skipped",
                "current_question": section.get("prompt"),
            }
    else:
        # Store response
        section_responses[section_id] = response

    # Move to next section
    next_section = current_section + 1

    # Update session state
    forge_state["current_section"] = next_section
    forge_state["section_responses"] = section_responses

    try:
        await _backend_post(f"/session/state/{session_id}", {"forge_mode": forge_state})
    except httpx.HTTPError:
        pass

    # Also add message to session transcript
    try:
        await _backend_post("/session/chat", {
            "session_id": session_id,
            "message": response,
            "messages": [],  # Empty for non-streaming
        })
    except httpx.HTTPError:
        pass

    # Check if complete
    if next_section >= len(sections):
        return {
            "complete": True,
            "message": "All sections complete! Use 'end_session' to extract insights and save the session.",
            "sections_completed": len(section_responses),
        }

    # Get next question
    question_info = _get_current_question(template, next_section)

    return {
        "complete": False,
        "acknowledged": f"Recorded response for '{section_id}'",
        "next_question": question_info.get("question"),
        "section_id": question_info.get("section_id"),
        "progress": f"{next_section + 1}/{question_info.get('total_sections', 1)}",
        "required": question_info.get("required", False),
    }


async def _end_session(session_id: str) -> dict[str, Any]:
    """End session and trigger extraction."""
    # Get session state
    session = await _get_session(session_id)
    forge_state = session.get("forge_mode", {}) if session else {}

    # Build transcript from section responses
    section_responses = forge_state.get("section_responses", {})
    template = forge_state.get("template", {})
    topic = forge_state.get("topic", "Thinking session")
    mode = forge_state.get("mode", "learning")

    transcript = []
    for section in template.get("sections", []):
        section_id = section.get("id", "")
        prompt = section.get("prompt", "")
        response = section_responses.get(section_id, "")
        if response:
            transcript.append({"role": "assistant", "content": prompt})
            transcript.append({"role": "user", "content": response})

    # Call end session endpoint
    try:
        result = await _backend_post("/session/end", {
            "session_id": session_id,
            "user_id": forge_state.get("user_id", "default"),
            "session_title": f"{mode.title()} Session: {topic}",
            "transcript": transcript,
            "template_id": forge_state.get("template_id"),
            "section_responses": section_responses,
        })

        return {
            "status": "complete",
            "session_title": f"{mode.title()} Session: {topic}",
            "doc_id": result.get("doc_id"),
            "entities_extracted": result.get("entities_extracted", 0),
            "summary": result.get("summary"),
            "key_insights": result.get("key_insights", []),
            "message": "Session complete! Your thinking has been saved and entities extracted.",
        }
    except httpx.HTTPError as e:
        return {
            "status": "error",
            "error": f"Failed to end session: {e}",
            "sections_captured": len(section_responses),
        }


async def _get_question(session_id: str) -> dict[str, Any]:
    """Get current question for context recovery."""
    session = await _get_session(session_id)
    if not session:
        return {"error": f"Session '{session_id}' not found or expired"}

    forge_state = session.get("forge_mode", {})
    if not forge_state:
        return {"error": "Session is not a ForgeMode session"}

    template = forge_state.get("template", {})
    current_section = forge_state.get("current_section", 0)

    question_info = _get_current_question(template, current_section)

    if question_info.get("complete"):
        return {
            "complete": True,
            "message": "All questions answered. Use 'end_session' to complete.",
        }

    return {
        "mode": forge_state.get("mode"),
        "topic": forge_state.get("topic"),
        "current_question": question_info.get("question"),
        "section_id": question_info.get("section_id"),
        "progress": f"{current_section + 1}/{question_info.get('total_sections', 1)}",
        "required": question_info.get("required", False),
        "sections_completed": len(forge_state.get("section_responses", {})),
    }


async def _list_templates() -> dict[str, Any]:
    """List available thinking templates."""
    templates = []

    for mode, template_id in MODE_TO_TEMPLATE.items():
        template = await _load_template(template_id)
        if template:
            templates.append({
                "mode": mode,
                "template_id": template_id,
                "name": template.get("name", template_id),
                "description": template.get("description", ""),
                "section_count": len(template.get("sections", [])),
            })
        else:
            templates.append({
                "mode": mode,
                "template_id": template_id,
                "name": f"{mode.title()} (coming soon)",
                "description": "Template not yet available",
                "available": False,
            })

    return {
        "templates": templates,
        "available_modes": [t["mode"] for t in templates if t.get("available", True)],
    }


async def _get_status(session_id: str) -> dict[str, Any]:
    """Get session status and history."""
    session = await _get_session(session_id)
    if not session:
        return {"error": f"Session '{session_id}' not found or expired"}

    forge_state = session.get("forge_mode", {})
    template = forge_state.get("template", {})
    section_responses = forge_state.get("section_responses", {})

    # Build response history
    history = []
    for section in template.get("sections", []):
        section_id = section.get("id", "")
        response = section_responses.get(section_id)
        history.append({
            "section_id": section_id,
            "question": section.get("prompt", ""),
            "response": response,
            "completed": response is not None,
        })

    total_sections = len(template.get("sections", []))
    completed_sections = len(section_responses)

    return {
        "session_id": session_id,
        "mode": forge_state.get("mode"),
        "topic": forge_state.get("topic"),
        "template_name": template.get("name", ""),
        "status": "complete" if completed_sections >= total_sections else "in_progress",
        "progress": {
            "completed": completed_sections,
            "total": total_sections,
            "percentage": int((completed_sections / total_sections) * 100) if total_sections else 0,
        },
        "history": history,
        "started_at": session.get("started_at"),
        "last_activity": session.get("last_activity"),
    }


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
