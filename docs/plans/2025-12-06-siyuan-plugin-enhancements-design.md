# SiYuan Plugin Enhancements Design

**Date:** 2025-12-06
**Status:** Design Complete
**Purpose:** Quick plan generation and external transcript import for SiYuan plugin

## Overview

Two new features for the SiYuan plugin:
1. **Quick Plan Generation** — One-shot implementation plans from a prompt
2. **Transcript Upload** — Import external AI chat transcripts as full sessions

## 1. Quick Plan Generation

### Purpose

Generate structured implementation plans instantly from a single prompt, without going through full ForgeMode dialogue.

### User Flow

1. User clicks "Quick Plan" button (Dashboard or ForgeMode toolbar)
2. Modal appears with text input
3. User enters prompt: "add user authentication with OAuth"
4. Backend generates structured plan
5. New document created in `/Sessions/Planning/`

### Output Format

```markdown
# Plan: Add User Authentication with OAuth

**Generated:** 2025-12-06
**Prompt:** add user authentication with OAuth

## Overview
Brief description of what this plan accomplishes.

## Tasks

### 1. Setup OAuth Provider Configuration
- [ ] Create OAuth config schema
- [ ] Add environment variables for client ID/secret
- [ ] Implement provider abstraction (Google, GitHub, etc.)

### 2. Implement Auth Flow
- [ ] Create /auth/login endpoint
- [ ] Handle OAuth callback
- [ ] Generate and store session tokens

### 3. Protect Routes
- [ ] Create auth middleware
- [ ] Apply to protected endpoints
- [ ] Handle unauthorized responses

## Success Criteria
- [ ] User can log in via OAuth provider
- [ ] Session persists across page reloads
- [ ] Protected routes reject unauthenticated requests

## Related Entities
- [[Authentication]] (if exists in graph)
- [[OAuth]] (if exists in graph)
```

### Backend Endpoint

```
POST /session/quick-plan
Content-Type: application/json

{
  "prompt": "add user authentication with OAuth",
  "user_id": "default"
}

Response:
{
  "plan_markdown": "# Plan: ...",
  "detected_entities": ["Authentication", "OAuth", "Session"],
  "suggested_mode": "planning"
}
```

### UI Component

Location: Dashboard toolbar + ForgeMode header

```svelte
<button on:click={openQuickPlanModal}>
  Quick Plan
</button>
```

## 2. Transcript Upload

### Purpose

Import external AI chat transcripts (ChatGPT, Claude.ai, etc.) and process them as full IES sessions with entity extraction and graph integration.

### Input Methods

1. **Drag & drop** — Drop .md file onto upload zone
2. **File picker** — Button opens file dialog
3. **Paste** — Paste markdown text into textarea

### Processing Flow

1. User provides markdown transcript
2. Plugin sends to backend
3. Backend:
   - Parses conversation turns (User/Assistant pattern)
   - Detects likely thinking mode from content
   - Extracts entities and relationships
   - Generates session summary
4. Plugin creates session document in `/Sessions/{detected-mode}/`
5. Entities added to knowledge graph with session links

### Markdown Parsing

Supported formats:

| Format | Pattern |
|--------|---------|
| ChatGPT | `**User:**` / `**Assistant:**` |
| Claude | `Human:` / `Assistant:` |
| Generic | `User:` / `AI:` or `Bot:` |

Parser attempts auto-detection, falls back to line-by-line if unclear.

### Backend Endpoint

```
POST /session/import
Content-Type: application/json

{
  "markdown": "**User:** What is...\n\n**Assistant:** ...",
  "source": "chatgpt",
  "user_id": "default"
}

Response:
{
  "session_id": "abc123",
  "detected_mode": "learning",
  "turn_count": 12,
  "entities_extracted": ["Executive Function", "Prefrontal Cortex"],
  "summary": "Discussion about executive function and self-regulation..."
}
```

### UI Component

Location: Dashboard (dedicated upload zone)

```svelte
<div
  class="upload-zone"
  on:drop={handleDrop}
  on:dragover={handleDragOver}
>
  <p>Drop transcript here, paste, or</p>
  <button on:click={openFilePicker}>Choose File</button>

  <textarea
    placeholder="Or paste transcript here..."
    bind:value={pastedContent}
  />

  <button on:click={processTranscript}>Import</button>
</div>
```

## Success Criteria

### Quick Plan
- [ ] Button accessible from Dashboard and ForgeMode
- [ ] Plan generated in < 5 seconds
- [ ] Document created in correct folder with proper frontmatter
- [ ] Related entities linked if they exist in graph

### Transcript Upload
- [ ] All three input methods work (drag/drop, file, paste)
- [ ] ChatGPT and Claude formats parsed correctly
- [ ] Mode auto-detected from content
- [ ] Entities extracted and added to graph
- [ ] Session document created with full transcript

## Implementation Notes

### Backend Changes Required

1. **New endpoint:** `POST /session/quick-plan`
   - Uses Claude Sonnet for plan generation
   - Returns structured markdown + detected entities

2. **New endpoint:** `POST /session/import`
   - Markdown parser for conversation turns
   - Mode detection heuristics
   - Entity extraction (reuse existing extraction service)

### Plugin Changes Required

1. **QuickPlanModal.svelte** — Modal component for prompt input
2. **TranscriptUpload.svelte** — Upload zone with drag/drop/paste
3. **Dashboard.svelte** — Add Quick Plan button and upload zone
4. **ForgeMode.svelte** — Add Quick Plan button to toolbar

## Future Extensions

- Support more transcript formats (Gemini, local LLM logs)
- Batch import multiple transcripts
- Merge related transcripts into single session
- Export sessions as shareable transcripts
