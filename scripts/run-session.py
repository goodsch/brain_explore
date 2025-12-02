#!/usr/bin/env python3
"""
IES Session Runner - Helper for Phase 1 therapy exploration sessions

Usage:
    python scripts/run-session.py --topic "Your therapy question"

    # Or interactive mode:
    python scripts/run-session.py
"""

import requests
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

BASE_URL = "http://localhost:8081"
USER_ID = "chris"
TRANSCRIPTS_DIR = Path(__file__).parent.parent / "docs" / "session-transcripts"

def ensure_transcripts_dir():
    """Ensure session transcripts directory exists."""
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

def api_post(endpoint, data):
    """Make a POST request to the IES backend."""
    try:
        url = f"{BASE_URL}{endpoint}"
        response = requests.post(url, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to backend at {BASE_URL}")
        print("   Make sure the backend is running: PYTHONPATH=./src python -m uvicorn ies_backend.main:app --host 0.0.0.0 --port 8081")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
        sys.exit(1)

def start_session():
    """Start a new IES session."""
    print("\n🔄 Starting session...")
    data = api_post("/session/start", {"user_id": USER_ID})
    return data["session_id"], data

def run_conversation(session_id, messages_so_far):
    """Interactive conversation loop."""
    messages = messages_so_far.copy()

    while True:
        print("\n(Type 'done' to end session, 'quit' to exit without saving)")
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "quit":
            return None
        if user_input.lower() == "done":
            return messages
        if not user_input:
            continue

        print("\nAssistant: ", end="", flush=True)

        try:
            response = api_post("/session/chat-sync", {
                "session_id": session_id,
                "message": user_input,
                "messages": messages
            })

            assistant_response = response["response"]
            print(assistant_response)

            messages.append({"role": "user", "content": user_input})
            messages.append({"role": "assistant", "content": assistant_response})

        except Exception as e:
            print(f"\n❌ Error: {e}")
            return None

def save_transcript(session_data, messages):
    """Save session transcript to file."""
    ensure_transcripts_dir()

    # Generate filename from current date/time
    now = datetime.now()
    filename = TRANSCRIPTS_DIR / f"session-{now.strftime('%Y%m%d-%H%M%S')}.md"

    # Build transcript content
    content = f"""# Therapy Exploration Session
**Date:** {now.strftime('%Y-%m-%d %H:%M:%S')}
**Session ID:** {session_data['session_id']}

## Profile Summary
{session_data['profile_summary']}

## Recent Context
{session_data.get('recent_context', 'N/A')}

## Conversation

"""

    for msg in messages:
        role = "**You**" if msg['role'] == "user" else "**Assistant**"
        content += f"{role}: {msg['content']}\n\n"

    content += """## Reflection
*(Add your thoughts about this session after running it)*

### Key Moments
-

### Patterns Noticed
-

### Concepts That Emerged
-

### What Worked Well
-

### What Could Be Better
-
"""

    with open(filename, 'w') as f:
        f.write(content)

    print(f"\n✅ Session saved to: {filename}")
    return filename

def main():
    parser = argparse.ArgumentParser(description="Run a therapy exploration session")
    parser.add_argument("--topic", help="Starting topic/question for the session")
    args = parser.parse_args()

    print("=" * 60)
    print("IES THERAPY EXPLORATION SESSION")
    print("=" * 60)

    # Start session
    session_id, session_data = start_session()
    print(f"✅ Session started: {session_id[:8]}...")
    print(f"\n📋 Profile: {session_data['profile_summary']}")
    print(f"\n💬 Greeting:\n{session_data['greeting']}")

    # Initialize messages with greeting
    messages = [{"role": "assistant", "content": session_data['greeting']}]

    # If topic provided, start with that
    if args.topic:
        print(f"\n🎯 Starting topic: {args.topic}")
        messages.append({"role": "user", "content": args.topic})

        response = api_post("/session/chat-sync", {
            "session_id": session_id,
            "message": args.topic,
            "messages": messages[:-1]  # Don't include the user message we just added
        })

        assistant_response = response["response"]
        print(f"\nAssistant: {assistant_response}")
        messages.append({"role": "assistant", "content": assistant_response})

    # Continue conversation
    final_messages = run_conversation(session_id, messages)

    if final_messages:
        save_transcript(session_data, final_messages)
        print("\n🎉 Session complete!")
    else:
        print("\n⚠️  Session not saved")

if __name__ == "__main__":
    main()
