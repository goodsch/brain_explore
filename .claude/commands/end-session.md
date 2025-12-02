# End Exploration Session (Phase 4)

You are ending an exploration session. This triggers entity extraction and creates session documentation.

## 1. Generate Session Summary

Before calling the backend, create a brief summary of what was explored:
- Main topic(s) discussed
- Key insights that emerged
- Any entities (ideas, questions, tensions) that were developed
- Open questions to carry forward

## 2. Prepare Transcript

Gather the conversation transcript from this session. Include:
- All user messages
- All assistant responses
- Focus on the exploration content (not meta-discussion about the system)

## 3. Call Session Processing Endpoint

```
POST http://localhost:8081/session/process
Content-Type: application/json

{
  "user_id": "chris",
  "transcript": "<full session transcript>",
  "session_title": "<main topic explored>",
  "session_date": "<today's date YYYY-MM-DD>"
}
```

This endpoint:
1. Extracts entities via Claude API
2. Creates session document in SiYuan
3. Stores entities in Neo4j
4. Stores session metadata for future context loading

## 4. Show Results

Display what was captured:

```
Session captured!

Entities created: [list new entities]
Entities updated: [list updated entities]

Key insights:
- [insight 1]
- [insight 2]

Open questions for next time:
- [question 1]
- [question 2]

Session document: [SiYuan doc ID or path]
```

## 5. Suggest Next Steps

Based on the session:
- If there are open questions: "Next session could pick up: [question]"
- If entity needs development: "[Entity] could use more exploration"
- If natural pause: "Good stopping point. Rest well!"

## Error Handling

**If backend unavailable:**
1. Save session summary to `sessions/YYYY-MM-DD-topic.md` locally
2. Note that entities weren't extracted
3. Suggest running extraction later when backend is up

**If extraction fails:**
1. Still save the transcript locally
2. Show error message
3. Can retry later

## Do NOT:
- Skip the extraction step (that's the whole point)
- Leave without showing what was captured
- Forget to mention open questions for continuity

## Backend Endpoint Reference

```
POST http://localhost:8081/session/process

Request body:
{
  "user_id": string,
  "transcript": string,
  "session_title": string | null,
  "session_date": string | null  // YYYY-MM-DD format
}

Response:
{
  "session_doc_id": string | null,
  "entities_created": string[],
  "entities_updated": string[],
  "summary": {
    "key_insights": string[],
    "open_questions": string[],
    "threads_explored": string[]
  }
}
```

Begin by summarizing what was explored in this session.
