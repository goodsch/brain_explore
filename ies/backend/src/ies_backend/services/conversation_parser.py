"""Utilities for parsing AI chat exports into normalized turns."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Optional


@dataclass
class ParsedTurn:
    """Normalized conversation turn."""

    role: str
    text: str
    timestamp: Optional[datetime] = None


class ConversationParser:
    """Parse various conversation export formats into turns."""

    @staticmethod
    def parse(content: str, source: str) -> List[ParsedTurn]:
        """Dispatch to a specific parser based on source."""
        if source == "claude":
            return ConversationParser._parse_claude_json(content)
        if source == "chatgpt":
            return ConversationParser._parse_chatgpt_export(content)
        # Plain text / markdown fallback
        return ConversationParser._parse_plaintext(content)

    @staticmethod
    def _parse_claude_json(content: str) -> List[ParsedTurn]:
        """Parse Claude conversation export JSON."""
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return ConversationParser._parse_plaintext(content)

        messages: Iterable[dict] = data.get("chat_messages") or data.get("messages") or []
        turns: List[ParsedTurn] = []
        for msg in messages:
            role = msg.get("role") or msg.get("author") or "assistant"
            text = ConversationParser._extract_text(msg.get("content"))
            ts = msg.get("date") or msg.get("created_at")
            timestamp = ConversationParser._parse_timestamp(ts)
            if text:
                turns.append(ParsedTurn(role=role, text=text, timestamp=timestamp))
        return turns or ConversationParser._parse_plaintext(content)

    @staticmethod
    def _parse_chatgpt_export(content: str) -> List[ParsedTurn]:
        """Parse ChatGPT data export conversations.json entry."""
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            return ConversationParser._parse_plaintext(content)

        # ChatGPT export can be a list or a single conversation object
        convo = None
        if isinstance(data, list) and data:
            convo = data[0]
        elif isinstance(data, dict):
            convo = data

        if not convo:
            return ConversationParser._parse_plaintext(content)

        mapping = convo.get("mapping", {})
        turns: List[ParsedTurn] = []
        # Items are keyed; sort by create_time if available
        ordered = sorted(
            mapping.values(),
            key=lambda v: (v.get("message", {}).get("create_time") or 0),
        )
        for node in ordered:
            message = node.get("message") or {}
            author = message.get("author", {}) or {}
            role = author.get("role") or "assistant"
            msg_content = message.get("content") or {}
            parts = msg_content.get("parts") or []
            text = "\n".join(p for p in parts if isinstance(p, str)).strip()
            ts = message.get("create_time")
            timestamp = None
            if ts:
                try:
                    timestamp = datetime.fromtimestamp(float(ts))
                except Exception:
                    timestamp = None
            if text:
                turns.append(ParsedTurn(role=role, text=text, timestamp=timestamp))

        return turns or ConversationParser._parse_plaintext(content)

    @staticmethod
    def _parse_plaintext(content: str) -> List[ParsedTurn]:
        """Parse plain text or markdown with role cues or separators.

        Supports:
        - user:/assistant:/system: prefixes
        - Human:/Assistant: prefixes (Claude format)
        - --- separators (ChatGPT markdown exports) - alternates roles
        """
        turns: List[ParsedTurn] = []
        current_role = "user"
        buffer: list[str] = []

        def flush():
            nonlocal buffer
            text = "\n".join(buffer).strip()
            if text:
                turns.append(ParsedTurn(role=current_role, text=text))
            buffer = []

        def alternate_role() -> str:
            return "assistant" if current_role == "user" else "user"

        # Pattern for explicit role markers
        role_pattern = re.compile(
            r"^(user|assistant|system|human)[:>-]\s*", re.IGNORECASE
        )
        # Pattern for --- separators (at least 3 dashes on their own line)
        separator_pattern = re.compile(r"^-{3,}$")

        for line in content.splitlines():
            stripped = line.strip()

            # Skip empty lines but preserve them in buffer for formatting
            if not stripped:
                if buffer:  # Only add if we have content
                    buffer.append("")
                continue

            # Check for --- separator (ChatGPT markdown format)
            if separator_pattern.match(stripped):
                flush()
                current_role = alternate_role()
                continue

            # Check for explicit role marker
            role_match = role_pattern.match(stripped)
            if role_match:
                flush()
                matched_role = role_match.group(1).lower()
                # Normalize "human" to "user"
                current_role = "user" if matched_role == "human" else matched_role
                remainder = role_pattern.sub("", stripped)
                if remainder:
                    buffer.append(remainder)
                continue

            buffer.append(stripped)

        flush()

        if not turns:
            # Single block fallback
            turns.append(ParsedTurn(role="user", text=content.strip()))
        return turns

    @staticmethod
    def _extract_text(content: str | list | dict | None) -> str:
        """Extract text from Claude content variants."""
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])
        if isinstance(content, dict):
            if "text" in content:
                return str(content.get("text"))
            if "content" in content:
                return str(content.get("content"))
        return ""

    @staticmethod
    def _parse_timestamp(raw: str | int | float | None) -> Optional[datetime]:
        """Parse timestamp from common formats."""
        if raw is None:
            return None
        try:
            if isinstance(raw, (int, float)):
                return datetime.fromtimestamp(float(raw))
            # ISO strings
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except Exception:
            return None
