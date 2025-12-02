# IES Backend

Intelligent Exploration System Backend - FastAPI service for entity extraction and knowledge management.

## Setup

```bash
cd ies-backend
pip install -e ".[dev]"
```

## Run

```bash
uvicorn ies_backend.main:app --reload
```

## Test

```bash
pytest
```

## API Endpoints

### Profile

- `GET /profile/{user_id}` - Get user profile
- `POST /profile/{user_id}` - Create new profile
- `PATCH /profile/{user_id}` - Update profile dimensions
- `POST /profile/{user_id}/capacity` - Record capacity check-in
- `POST /profile/{user_id}/observe` - Update profile from session observations
- `GET /profile/{user_id}/summary` - Get condensed profile summary

### Session (Phase 2)

- `POST /session/process` - Process session transcript

### Health

- `GET /health` - Health check
