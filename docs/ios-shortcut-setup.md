# iOS Shortcut Setup for Inbox Capture

Capture thoughts instantly from your iPhone and have them appear in your SiYuan Inbox.

## Prerequisites

- iOS 15+ (Shortcuts app)
- Backend server accessible from your network (e.g., `http://192.168.86.60:8081`)
- Network connectivity between iPhone and server

## Quick Setup

### 1. Create the Shortcut

1. Open **Shortcuts** app on iOS
2. Tap **+** to create new shortcut
3. Name it: **"Capture Thought"** (or "Quick Capture", "Send to Inbox")

### 2. Add Actions

**Action 1: Ask for Input**
- Search for "Ask for Input"
- Prompt: `What's on your mind?`
- Input Type: Text

**Action 2: Get Contents of URL**
- Search for "Get Contents of URL"
- URL: `http://YOUR_SERVER_IP:8081/inbox`
- Method: POST
- Headers:
  - `Content-Type`: `application/json`
- Request Body: JSON
  ```json
  {
    "text": [Provided Input],
    "source": "ios_shortcut",
    "context": {
      "device": "iPhone"
    }
  }
  ```

**Action 3: Show Notification**
- Search for "Show Notification"
- Title: `Saved to Inbox`
- Body: `Your thought has been captured.`

### 3. Configure Siri

1. Tap shortcut settings (⋯)
2. Enable "Show in Share Sheet" (optional)
3. Add to Home Screen (optional)
4. Say: "Hey Siri, Capture Thought"

## Complete Shortcut JSON

Import this directly into Shortcuts:

```json
{
  "WFWorkflowName": "Capture Thought",
  "WFWorkflowActions": [
    {
      "WFWorkflowActionIdentifier": "is.workflow.actions.ask",
      "WFWorkflowActionParameters": {
        "WFAskActionPrompt": "What's on your mind?",
        "WFInputType": "Text"
      }
    },
    {
      "WFWorkflowActionIdentifier": "is.workflow.actions.downloadurl",
      "WFWorkflowActionParameters": {
        "WFURL": "http://192.168.86.60:8081/inbox",
        "WFHTTPMethod": "POST",
        "WFHTTPHeaders": {
          "Content-Type": "application/json"
        },
        "WFHTTPBodyType": "JSON",
        "WFJSONValues": {
          "text": {
            "Value": {
              "Type": "Variable",
              "VariableName": "Provided Input"
            }
          },
          "source": "ios_shortcut",
          "context": {
            "device": "iPhone"
          }
        }
      }
    },
    {
      "WFWorkflowActionIdentifier": "is.workflow.actions.notification",
      "WFWorkflowActionParameters": {
        "WFNotificationActionTitle": "Saved to Inbox",
        "WFNotificationActionBody": "Your thought has been captured."
      }
    }
  ]
}
```

## Variations

### Voice Capture

Add "Dictate Text" action before the URL request:

1. **Dictate Text** → captures voice input
2. **Get Contents of URL** → POST with `"source": "voice"`

### Link Capture (Share Sheet)

1. Enable "Show in Share Sheet"
2. Accept: URLs
3. Use `Shortcut Input` instead of "Ask for Input"
4. Set `"source": "browser"`

### With Location

Add location context:

```json
{
  "text": "[Provided Input]",
  "source": "ios_shortcut",
  "context": {
    "device": "iPhone",
    "location": "[Current Location]"
  }
}
```

## Troubleshooting

### "Could not connect to server"

- Ensure your iPhone is on the same network as the server
- Check the server IP address is correct
- Verify the backend is running: `curl http://YOUR_IP:8081/health`

### "Request failed"

- Check the JSON format is valid
- Ensure `source` is a valid value: `ios_shortcut`, `voice`, `browser`
- Check backend logs for errors

### Offline Capture

For offline support, the shortcut can save to Notes app and sync later:

1. If URL request fails → Save to Notes app
2. Create a separate "Sync Inbox" shortcut that:
   - Reads notes with a specific tag
   - POSTs each to `/inbox`
   - Deletes synced notes

## API Reference

### POST /inbox

Creates a new inbox item.

**Request:**
```json
{
  "text": "The thought or content to capture",
  "source": "ios_shortcut",
  "context": {
    "device": "iPhone",
    "location": "optional"
  }
}
```

**Response:**
```json
{
  "id": "abc123",
  "text": "The thought or content to capture",
  "source": "ios_shortcut",
  "status": "queued",
  "captured_at": "2025-12-06T12:00:00Z"
}
```

### Valid Sources

| Source | Use Case |
|--------|----------|
| `ios_shortcut` | Siri, home screen shortcut |
| `voice` | Dictated input |
| `browser` | Share sheet from Safari |
| `email` | Forwarded email (future) |
| `siyuan` | Captured within SiYuan |
| `ies_reader` | Captured from IES Reader |
