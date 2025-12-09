# Pass 2 Relationship Extraction - Implementation Summary

**Date:** 2025-12-09
**Status:** Complete - Ready for Testing

## Overview

Pass 2 relationship extraction CLI script has been implemented following the established pattern from `scripts/ingest_calibre.py`. This completes the second phase of the three-pass ingestion pipeline.

## Components Created

### 1. UnifiedGraphClient Enhancement
**File:** `/home/chris/dev/projects/codex/brain_explore/library/graph/unified_client.py`

Added `add_typed_relationship()` method (lines 424-495):
- Validates relationship types (CAUSES, PART_OF, CONTRASTS_WITH)
- Adds metadata: `extracted_by='pass2'`, `extracted_at`, `confidence`, `source_book`, `source_chunk`
- Handles bidirectional CONTRASTS_WITH relationships automatically
- Prevents Cypher injection with type validation

### 2. Pass 2 CLI Script
**File:** `/home/chris/dev/projects/codex/brain_explore/scripts/pass2_relationships.py`

**Functions:**
- `get_books_for_pass2()` - Query books with status='entities_extracted'
- `get_entity_rich_chunks()` - Get chunks mentioning 2+ entities
- `get_valid_entities()` - Get all entity names for validation
- `pass2_single_book()` - Extract and store relationships for one book
- `show_status()` - Display processing statistics with Rich tables

**Features:**
- Progress bars with Rich console
- Relationship deduplication
- Validation against known entities
- Dry-run mode for preview
- Comprehensive error handling
- Detailed statistics reporting

## Usage

### Show Status
```bash
python scripts/pass2_relationships.py --status
```

Shows:
- Books by processing status
- Pass 2 relationships by type
- Top books by relationship count
- Average confidence scores

### Process All Books
```bash
python scripts/pass2_relationships.py
```

### Process Specific Book
```bash
python scripts/pass2_relationships.py --id 42
```

### Batch Processing
```bash
python scripts/pass2_relationships.py --limit 10
```

### Preview (Dry Run)
```bash
python scripts/pass2_relationships.py --dry-run
```

## Processing Pipeline

1. **Query Books** - Find books with status='entities_extracted'
2. **Get Chunks** - Retrieve chunks mentioning 2+ entities
3. **Extract Relationships** - Use RelationshipExtractor with GPT-4o-mini
4. **Deduplicate** - Merge duplicate relationships (keep highest confidence)
5. **Validate** - Check entity names exist, confidence >= 0.5, valid types
6. **Store** - Write to Neo4j with metadata
7. **Update Status** - Set book status to 'relationships_mapped'

## Relationship Types

### CAUSES (Unidirectional)
- Causal mechanisms: "dopamine deficiency CAUSES attention issues"
- Prerequisites: "executive function CAUSES self-regulation"
- Temporal sequences: "shame CAUSES metabolization blocking"

### PART_OF (Unidirectional)
- Hierarchical: "working memory PART_OF executive function"
- Taxonomic: "ADHD PART_OF neurodevelopmental disorders"
- Modular: "mindfulness PART_OF DBT"

### CONTRASTS_WITH (Bidirectional)
- Conceptual distinctions: "acceptance CONTRASTS_WITH resignation"
- Comparisons: "ADHD CONTRASTS_WITH autism"
- Theoretical opposites: "behaviorism CONTRASTS_WITH psychoanalysis"

## Current Status

**Test Run Results:**
```
Pass 2 Processing Status
┌──────────────────────┬───────┬──────────────────┐
│ Status               │ Count │ Description      │
├──────────────────────┼───────┼──────────────────┤
│ entities_extracted   │     8 │ Ready for Pass 2 │
│ relationships_mapped │     4 │ Pass 2 complete  │
│ Total                │    12 │                  │
└──────────────────────┴───────┴──────────────────┘

No Pass 2 relationships found yet
```

**Observations:**
- 8 books ready for Pass 2 processing
- 4 books already marked as 'relationships_mapped' (from previous manual processing)
- No Pass 2 relationships in graph yet (properties `extracted_by`, `source_book` not present)

## Integration Points

### With RelationshipExtractor
- Uses existing `library/graph/relationship_extractor.py`
- GPT-4o-mini model for cost efficiency
- Confidence threshold: 0.5 (configurable)
- Automatic retry with exponential backoff

### With Pass 1
- Requires books with status='entities_extracted'
- Reuses entities and chunks from Pass 1
- Maintains Book→Chunk→Entity structure

### With Pass 3
- Sets status to 'relationships_mapped' on completion
- Ready for LLM enrichment (reframes, mechanisms, patterns)

## Statistics Tracked

**Per Book:**
- chunks_processed
- relationships_extracted
- high_confidence (>= 0.8)
- relationships_stored
- relationships_rejected

**Summary:**
- Total books processed
- Success/error counts
- Overall relationship statistics
- API call counts and token usage

## Error Handling

- Neo4j connection errors → logged and continue
- OpenAI API failures → retry with exponential backoff (max 3)
- Invalid relationship types → rejected with reason
- Missing entities → rejected with warning
- Low confidence → rejected if < 0.5

## Cost Estimation

**GPT-4o-mini Pricing:**
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens

**Expected per book:**
- ~50 entity-rich chunks
- ~500 tokens per chunk (25K input tokens)
- ~100 tokens per response (5K output tokens)
- Cost: ~$0.004 per book

**For 8 books:** ~$0.03 total

## Next Steps

1. **Test on Single Book:**
   ```bash
   python scripts/pass2_relationships.py --id <calibre_id> --dry-run
   ```

2. **Process Small Batch:**
   ```bash
   python scripts/pass2_relationships.py --limit 3
   ```

3. **Verify Results:**
   ```bash
   python scripts/pass2_relationships.py --status
   ```

4. **Full Processing:**
   ```bash
   python scripts/pass2_relationships.py
   ```

## Files Modified

1. `/home/chris/dev/projects/codex/brain_explore/library/graph/unified_client.py`
   - Added `add_typed_relationship()` method

2. `/home/chris/dev/projects/codex/brain_explore/scripts/pass2_relationships.py` (NEW)
   - Complete CLI implementation (427 lines)

## Dependencies

- `library.graph.relationship_extractor` (existing)
- `library.graph.unified_client` (enhanced)
- `library.ingest.chunk` (existing)
- `rich` (for console output)
- `openai` (via RelationshipExtractor)

## Testing Recommendations

1. **Dry Run First:** Always test with `--dry-run` on new books
2. **Single Book Test:** Process one book and inspect results in Neo4j
3. **Validation:** Check relationship evidence quality manually
4. **Performance:** Monitor API latency and token usage
5. **Cost:** Track OpenAI API costs during batch processing

## Known Limitations

1. **In-Memory Storage:** RelationshipExtractor statistics stored in-memory only
2. **No Persistence:** Extraction results not saved (direct to Neo4j)
3. **No Resume:** Failed batches must restart from beginning
4. **Rate Limits:** OpenAI API rate limits may affect large batches
5. **Token Limits:** Very long chunks may exceed model context window

## Future Enhancements

1. **Persistence:** Save extraction results to JSON for analysis
2. **Resume Support:** Track progress for batch resumption
3. **Parallel Processing:** Multi-threaded extraction for speed
4. **Model Selection:** Support GPT-4o for higher quality
5. **Custom Prompts:** Domain-specific relationship extraction prompts
6. **Quality Metrics:** Track precision/recall on validation set
