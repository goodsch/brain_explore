# Suggested Commands

## Docker Services

```bash
# Start services
docker compose up -d

# Check status
docker compose ps

# Stop services
docker compose down

# View logs
docker compose logs -f neo4j
docker compose logs -f qdrant
```

## Library Ingestion

```bash
# Ingest all books to vector store
python scripts/ingest_library.py

# Check Neo4j stats
python scripts/extract_entities.py --stats
```

## Entity Extraction

```bash
# Extract from single book
python scripts/extract_single.py "books/SomeBook.pdf"

# Batch extract (parallel)
python scripts/batch_extract.py

# Monitor progress
./scripts/check_progress.sh
```

## Search

```bash
# Test hybrid search
python scripts/test_hybrid_search.py
```

## Neo4j Queries (via browser at localhost:7474)

```cypher
-- Count entities
MATCH (n) RETURN labels(n) as type, count(*) as count

-- Find concepts
MATCH (c:Concept) RETURN c.name, c.description LIMIT 20

-- Find relationships
MATCH (a)-[r]->(b) RETURN type(r), count(*) as count
```

## Python Environment

```bash
# Install dependencies
uv pip install -e .

# Install dev dependencies
uv pip install -e ".[dev]"
```
