# Layer 0 – Ingestion & External Metadata

## Inputs

- New sources (books, articles, PDFs, transcripts, web clips, etc.).

## Operations

1. **Extract cheap metadata** (from files/APIs):
   - Title
   - Authors
   - Publication year
   - Type (book, article, video transcript, etc.)
   - Publisher / journal / site
   - Identifiers (ISBN, DOI, URL)
   - Language
   - Optional: table of contents / section structure.

2. **Create a minimal Source record**:
   - `id`
   - `title`, `authors`, `year`, `type`
   - `metadata` (raw)
   - `structure` (chapters, headings if available)
   - `processing_status` flags for each pipeline layer.

## Outputs

- A unified source catalog with enough information for:
  - listing,
  - simple search,
  - and prioritization before heavy NLP work begins.
