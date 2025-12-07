#!/usr/bin/env python3
"""
Cross-agent communication helper.

Usage:
    # Post a message
    python scripts/agent_comm.py post --from claude --to codex --type task --subject "Review PR" --body "Please review..."

    # Check inbox
    python scripts/agent_comm.py inbox --agent claude

    # Update status
    python scripts/agent_comm.py status --agent claude --task "Working on tests" --status active

    # Archive processed messages
    python scripts/agent_comm.py archive --message 20251207_143022_claude_codex_task.json
"""

import argparse
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

AGENTS_DIR = Path(__file__).parent.parent / ".agents"
QUEUE_DIR = AGENTS_DIR / "queue"
ARCHIVE_DIR = AGENTS_DIR / "archive"
STATUS_FILE = AGENTS_DIR / "status.json"

VALID_AGENTS = ["claude", "codex", "gemini", "all"]
VALID_TYPES = ["task", "question", "update", "handoff", "blocker"]
VALID_PRIORITIES = ["low", "normal", "high", "urgent"]


def post_message(from_agent: str, to_agent: str, msg_type: str, subject: str,
                 body: str, priority: str = "normal", files: list = None,
                 branch: str = None):
    """Post a message to the queue."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{from_agent}_{to_agent}_{msg_type}.json"

    message = {
        "from": from_agent,
        "to": to_agent,
        "type": msg_type,
        "priority": priority,
        "subject": subject,
        "body": body,
        "context": {
            "files": files or [],
            "branch": branch,
        },
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    filepath = QUEUE_DIR / filename
    filepath.write_text(json.dumps(message, indent=2))
    print(f"Posted: {filename}")
    return filepath


def check_inbox(agent: str):
    """Check messages for an agent."""
    messages = []
    for f in QUEUE_DIR.glob(f"*_{agent}_*.json"):
        messages.append((f.name, json.loads(f.read_text())))
    for f in QUEUE_DIR.glob(f"*_all_*.json"):
        messages.append((f.name, json.loads(f.read_text())))

    if not messages:
        print(f"No messages for {agent}")
        return []

    print(f"\n=== Inbox for {agent} ({len(messages)} messages) ===\n")
    for filename, msg in sorted(messages, key=lambda x: x[1].get("created_at", "")):
        priority_marker = "!" if msg.get("priority") == "urgent" else ""
        print(f"[{msg['type'].upper()}]{priority_marker} {msg['subject']}")
        print(f"  From: {msg['from']} | {msg.get('created_at', 'unknown')[:16]}")
        print(f"  {msg['body'][:100]}...")
        print(f"  File: {filename}")
        print()

    return messages


def update_status(agent: str, task: str = None, status: str = None,
                  branch: str = None, commits: list = None):
    """Update an agent's status."""
    data = json.loads(STATUS_FILE.read_text()) if STATUS_FILE.exists() else {
        "last_updated": None,
        "agents": {}
    }

    if agent not in data["agents"]:
        data["agents"][agent] = {}

    now = datetime.now(timezone.utc).isoformat()
    data["last_updated"] = now
    data["agents"][agent]["last_active"] = now

    if task:
        data["agents"][agent]["current_task"] = task
    if status:
        data["agents"][agent]["status"] = status
    if branch:
        data["agents"][agent]["branch"] = branch
    if commits:
        data["agents"][agent]["recent_commits"] = commits

    STATUS_FILE.write_text(json.dumps(data, indent=2))
    print(f"Updated status for {agent}")


def show_status():
    """Show all agents' status."""
    if not STATUS_FILE.exists():
        print("No status file found")
        return

    data = json.loads(STATUS_FILE.read_text())
    print(f"\n=== Agent Status (updated {data.get('last_updated', 'unknown')[:16]}) ===\n")

    for agent, info in data.get("agents", {}).items():
        status_emoji = {"active": "🟢", "idle": "🟡", "completed": "✅", "blocked": "🔴"}.get(
            info.get("status"), "⚪"
        )
        print(f"{status_emoji} {agent.upper()}")
        print(f"   Task: {info.get('current_task', 'None')}")
        print(f"   Branch: {info.get('branch', 'unknown')}")
        print(f"   Last active: {info.get('last_active', 'unknown')[:16]}")
        print()


def archive_message(filename: str):
    """Move a processed message to archive."""
    src = QUEUE_DIR / filename
    if not src.exists():
        print(f"Message not found: {filename}")
        return

    dst = ARCHIVE_DIR / filename
    shutil.move(src, dst)
    print(f"Archived: {filename}")


def main():
    parser = argparse.ArgumentParser(description="Cross-agent communication")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Post command
    post_parser = subparsers.add_parser("post", help="Post a message")
    post_parser.add_argument("--from", dest="from_agent", required=True, choices=VALID_AGENTS[:3])
    post_parser.add_argument("--to", required=True, choices=VALID_AGENTS)
    post_parser.add_argument("--type", required=True, choices=VALID_TYPES)
    post_parser.add_argument("--subject", required=True)
    post_parser.add_argument("--body", required=True)
    post_parser.add_argument("--priority", default="normal", choices=VALID_PRIORITIES)
    post_parser.add_argument("--files", nargs="*")
    post_parser.add_argument("--branch")

    # Inbox command
    inbox_parser = subparsers.add_parser("inbox", help="Check inbox")
    inbox_parser.add_argument("--agent", required=True, choices=VALID_AGENTS[:3])

    # Status commands
    status_parser = subparsers.add_parser("status", help="Update/show status")
    status_parser.add_argument("--agent", choices=VALID_AGENTS[:3])
    status_parser.add_argument("--task")
    status_parser.add_argument("--status", choices=["active", "idle", "completed", "blocked"])
    status_parser.add_argument("--branch")
    status_parser.add_argument("--show", action="store_true")

    # Archive command
    archive_parser = subparsers.add_parser("archive", help="Archive a message")
    archive_parser.add_argument("--message", required=True)

    args = parser.parse_args()

    if args.command == "post":
        post_message(args.from_agent, args.to, args.type, args.subject,
                     args.body, args.priority, args.files, args.branch)
    elif args.command == "inbox":
        check_inbox(args.agent)
    elif args.command == "status":
        if args.show or not args.agent:
            show_status()
        else:
            update_status(args.agent, args.task, args.status, args.branch)
    elif args.command == "archive":
        archive_message(args.message)


if __name__ == "__main__":
    main()
