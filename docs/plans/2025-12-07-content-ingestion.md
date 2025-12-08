# Content Ingestion System for Reader

Date: 2025-12-07
Owner: Claude
Scope: Enable importing diverse content types (web, video, podcast, text, PDF) into the IES reader system.

## Goals
- Support multiple content sources beyond ebooks
- Extract clean, readable text from various formats
- Integrate with existing SourceService and rendering pipeline
- Keep dependencies reasonable (avoid heavy ML unless needed)

## Content Types

| Type | Input | Extraction Method | Dependencies |
|------|-------|-------------------|--------------|
| **Web articles** | URL | Readability extraction | `trafilatura` |
| **YouTube** | URL/video ID | Transcript API | `yt-dlp` |
| **Podcasts** | URL | Existing transcript or Whisper | `yt-dlp`, optional `faster-whisper` |
| **Plain text** | Raw text | None (store as-is) | None |
| **PDF** | File/URL | Text extraction | `pypdf2` or `pdfplumber` |
| **arXiv** | arxiv ID | Abstract + PDF extraction | `httpx` + PDF extractor |

## Architecture

### Content Extractors (new module)
```
ies/backend/src/ies_backend/extractors/
├── __init__.py
├── base.py          # BaseExtractor protocol
├── web.py           # WebExtractor (trafilatura)
├── youtube.py       # YouTubeExtractor (yt-dlp)
├── podcast.py       # PodcastExtractor
├── pdf.py           # PDFExtractor
└── arxiv.py         # ArxivExtractor
```

Each extractor:
- Takes raw input (URL, file path, or ID)
- Returns `ExtractedContent(title, content, metadata)`
- Handles errors gracefully

### Updated SourceService Flow
```
import_source(request)
    ↓
Detect content type from URL/input
    ↓
Route to appropriate extractor
    ↓
Get clean text + metadata
    ↓
Extract entities (existing)
    ↓
Persist to Neo4j (existing)
    ↓
Available for reader view + EPUB export
```

### API Changes
- Extend `/sources/import` to auto-detect source type from URL
- Add `/sources/import/url` for URL-only imports with auto-detection
- Existing `/sources/{id}/read` and `/sources/{id}/epub` work unchanged

## Implementation Plan

### Phase 1: Core Extractors (priority)
1. **Web extraction** - Most common use case
   - Add `trafilatura` dependency
   - Create `WebExtractor` with readability extraction
   - Test on diverse sites (news, blogs, docs)

2. **Plain text** - Already works, verify

### Phase 2: Media Transcripts
3. **YouTube** - High value, common request
   - Add `yt-dlp` dependency
   - Fetch auto-generated or manual captions
   - Handle videos without transcripts

4. **Podcasts** - Similar to YouTube
   - Check for existing RSS transcript links
   - Fallback to audio transcription if Whisper available

### Phase 3: Documents
5. **PDF extraction**
   - Add `pypdf2` or `pdfplumber`
   - Handle multi-page documents
   - Extract text while preserving structure

6. **arXiv** - Specialty use case
   - Parse arxiv URLs/IDs
   - Fetch abstract via API
   - Optionally extract PDF text

## Dependencies to Add
```toml
dependencies = [
    # ... existing ...
    "trafilatura>=1.6.0",      # Web article extraction
    "yt-dlp>=2023.12.0",       # YouTube/podcast transcripts
    "pypdf>=3.0.0",            # PDF text extraction
]
```

## Reader Integration
- Add "Import Content" UI in reader
- URL input field with auto-detection
- File upload for PDFs
- Paste area for plain text
- Source library browser

## Non-Goals (this phase)
- Real-time audio transcription (too heavy)
- OCR for scanned documents
- Paywalled content bypass
- Full-text search across sources

## Success Criteria
- Import web article → renders in reader with clean text
- Import YouTube URL → transcript available in reader
- Import PDF → text extracted and readable
- All content types exportable to EPUB
