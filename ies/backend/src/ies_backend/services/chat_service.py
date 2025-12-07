"""Chat service for IES plugin conversations."""

import uuid
from typing import AsyncGenerator

import anthropic

from ies_backend.config import settings
from ies_backend.schemas.entity import ChatMessage, SessionContext
from ies_backend.services.profile_service import ProfileService
from ies_backend.services.session_context_service import session_context_service
from ies_backend.services.session_store import session_store
from ies_backend.services.state_detection_service import StateDetectionService
from ies_backend.services.approach_selection_service import ApproachSelectionService

# Initialize services
profile_service = ProfileService()
state_detection_service = StateDetectionService()
approach_selection_service = ApproachSelectionService()


class ChatService:
    """Service for handling IES chat conversations.

    Uses Redis-backed session store for persistent session management.
    Sessions survive server restarts with 24-hour TTL.
    """

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    async def start_session(self, user_id: str) -> dict:
        """Start a new IES session.

        Loads user context and generates a personalized greeting.

        Args:
            user_id: The user ID

        Returns:
            dict with session_id, profile_summary, recent_context, greeting
        """
        # Generate session ID
        session_id = str(uuid.uuid4())

        # Load context
        context = await session_context_service.get_context(user_id)

        # Build recent context summary
        recent_context = None
        if context.recent_sessions:
            recent = context.recent_sessions[0]
            recent_context = f"Last session: {recent.topic}"
            if recent.hanging_question:
                recent_context += f"\nOpen question: {recent.hanging_question}"

        # Generate greeting based on context
        greeting = self._generate_greeting(context)

        # Serialize context for Redis storage
        context_data = {
            "profile_summary": context.profile_summary,
            "recent_sessions": [
                {
                    "topic": s.topic,
                    "entities": s.entities,
                    "hanging_question": s.hanging_question,
                }
                for s in (context.recent_sessions or [])
            ],
        }

        # Store session in Redis with 24-hour TTL
        await session_store.create(
            session_id=session_id,
            user_id=user_id,
            context_data=context_data,
        )

        return {
            "session_id": session_id,
            "profile_summary": context.profile_summary,
            "recent_context": recent_context,
            "greeting": greeting,
        }

    def _generate_greeting(self, context: SessionContext) -> str:
        """Generate a personalized greeting based on context."""
        parts = ["Welcome to your exploration session."]

        if context.recent_sessions:
            recent = context.recent_sessions[0]
            if recent.hanging_question:
                parts.append(f"\nLast time you were exploring: \"{recent.hanging_question}\"")
                parts.append("\nWould you like to continue that thread, or explore something new?")
            else:
                parts.append(f"\nYour last session explored {recent.topic}.")
                parts.append("\nWhat would you like to explore today?")
        else:
            parts.append("\nWhat's on your mind today? What would you like to explore?")

        return "".join(parts)

    async def chat_stream(
        self,
        session_id: str,
        message: str,
        messages: list[ChatMessage],
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response.

        Args:
            session_id: The session ID
            message: The user's message
            messages: Full conversation history

        Yields:
            str chunks of the assistant's response
        """
        session = await session_store.get(session_id)
        if not session:
            yield "Session not found. Please start a new session."
            return

        # Reconstruct context from stored data
        context_data = session.get("context", {})

        # Build system prompt with IES context
        system_prompt = self._build_system_prompt_from_data(context_data)

        # Convert messages to Claude format
        claude_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # Add current message
        claude_messages.append({"role": "user", "content": message})

        # Get recent messages for state detection
        recent_user_messages = [
            msg.content for msg in messages[-5:]
            if msg.role == "user"
        ] + [message]

        # Detect state and select approach
        profile = await profile_service.get_profile(session["user_id"])
        state = state_detection_service.detect_state(
            recent_messages=recent_user_messages,
            profile=profile,
        )
        approach = approach_selection_service.select_approach(
            state=state,
            profile=profile,
        )

        # Add approach guidance to system prompt
        approach_guidance = self._get_approach_guidance(approach)
        full_system = f"{system_prompt}\n\n{approach_guidance}"

        # Stream response from Claude
        full_response = ""
        with self.client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=full_system,
            messages=claude_messages,
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                yield text

        # Store messages in session history
        await session_store.add_message(session_id, "user", message)
        await session_store.add_message(session_id, "assistant", full_response)

    def _build_system_prompt_from_data(self, context_data: dict) -> str:
        """Build the system prompt from stored context data."""
        profile_summary = context_data.get("profile_summary", "No profile available.")
        recent_sessions = context_data.get("recent_sessions", [])

        return f"""You are an IES (Intelligent Exploration System) guide helping a user explore ideas through Socratic dialogue.

USER PROFILE:
{profile_summary}

YOUR ROLE:
- Guide exploration through thoughtful questions
- Help the user discover their own insights
- Adapt your pacing and style to their cognitive profile
- Be curious and non-judgmental
- Mirror back what you hear to ensure understanding
- Gently challenge assumptions when appropriate

GUIDELINES:
- Keep responses concise (2-4 sentences typically)
- End with a question that deepens exploration
- Don't lecture or provide answers - help them discover
- If they seem stuck, offer a different angle
- If they seem overwhelmed, slow down and ground

RECENT CONTEXT:
{self._format_recent_sessions(recent_sessions)}"""

    def _format_recent_sessions(self, sessions: list[dict]) -> str:
        """Format recent sessions for the system prompt."""
        if not sessions:
            return "This is a new user with no previous sessions."

        parts = []
        for session in sessions[:3]:
            part = f"- {session.get('topic', 'Unknown topic')}"
            entities = session.get("entities", [])
            if entities:
                part += f" (explored: {', '.join(entities[:3])})"
            hanging = session.get("hanging_question")
            if hanging:
                part += f" [open: {hanging}]"
            parts.append(part)

        return "\n".join(parts) if parts else "No recent sessions."

    def _get_approach_guidance(self, approach) -> str:
        """Get guidance based on selected approach."""
        approach_name = approach.selected_approach.value

        guidance_map = {
            "socratic": """CURRENT APPROACH: Socratic
- Use open-ended questions
- Help them examine their assumptions
- Build on their answers with follow-up questions""",

            "solution_focused": """CURRENT APPROACH: Solution-Focused
- Focus on what's working, not problems
- Ask about desired outcomes
- Highlight strengths and resources""",

            "phenomenological": """CURRENT APPROACH: Phenomenological
- Focus on their direct experience
- Ask "what is that like for you?"
- Stay with the felt sense""",

            "narrative": """CURRENT APPROACH: Narrative
- Help them tell their story
- Look for themes and patterns
- Explore the meaning they make""",

            "integrative": """CURRENT APPROACH: Integrative
- Connect different threads
- Help them see patterns
- Synthesize insights""",
        }

        base = guidance_map.get(approach_name, "")

        # Add adaptations
        if approach.pacing == "slower":
            base += "\nPACING: Slow - give them time, shorter responses"
        elif approach.pacing == "faster":
            base += "\nPACING: Quick - they're in flow, keep momentum"

        if approach.directness == "gentle":
            base += "\nSTYLE: Gentle - softer questions, more support"
        elif approach.directness == "direct":
            base += "\nSTYLE: Direct - clear, focused questions"

        return base

    async def get_session(self, session_id: str) -> dict | None:
        """Get session data from Redis."""
        return await session_store.get(session_id)

    async def end_session(self, session_id: str) -> bool:
        """End and cleanup a session."""
        return await session_store.delete(session_id)

    async def list_sessions(self, user_id: str) -> list[dict]:
        """List all active sessions for a user.

        Args:
            user_id: User whose sessions to list

        Returns:
            List of session summaries
        """
        return await session_store.list_user_sessions(user_id)

    async def resume_session(self, session_id: str) -> dict | None:
        """Resume an existing session.

        Args:
            session_id: Session to resume

        Returns:
            Session data with context for resumption, or None if not found
        """
        session = await session_store.get(session_id)
        if not session:
            return None

        # Return resumption context
        return {
            "session_id": session["session_id"],
            "user_id": session["user_id"],
            "started_at": session.get("started_at"),
            "last_activity": session.get("last_activity"),
            "message_count": len(session.get("messages", [])),
            "messages": session.get("messages", []),
        }

    async def get_full_session(self, session_id: str) -> dict | None:
        """Get full session state including ForgeMode data.

        Used by MCP server to retrieve complete session state.

        Args:
            session_id: Session to retrieve

        Returns:
            Full session data or None if not found
        """
        return await session_store.get(session_id)

    async def update_session_state(
        self, session_id: str, updates: dict
    ) -> dict | None:
        """Update session state with arbitrary data.

        Used by MCP server to store ForgeMode progress.

        Args:
            session_id: Session to update
            updates: Fields to merge into session

        Returns:
            Updated session data or None if not found
        """
        return await session_store.update(session_id, updates)


# Singleton instance
chat_service = ChatService()
