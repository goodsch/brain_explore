"""Pydantic schemas for API request/response models."""

from ies_backend.schemas.context import (
    AreaOfExploration,
    Context,
    ContextCreate,
    ContextCreateRequest,
    ContextCreateResponse,
    ContextJourneyEntry,
    ContextListResponse,
    ContextNoteParseRequest,
    ContextNoteParseResponse,
    ContextSearchRequest,
    ContextSearchResponse,
    ContextSearchResult,
    ContextStatus,
    ContextType,
    ContextUpdate,
    JourneyClassification,
    JourneyEntryCreateRequest,
    JourneyListResponse,
    Question,
    QuestionCreateRequest,
    QuestionListResponse,
    QuestionStatus,
)
from ies_backend.schemas.extraction import (
    ExtractionProfile,
    ExtractionProfileCreate,
    ExtractionResult,
    ExtractionRunRequest,
    ExtractionRunResponse,
    QuestionExtractionProfile,
)
from ies_backend.schemas.visit_tracking import (
    VisitScope,
    VisitRecord,
    RecordVisitRequest,
    RecordVisitResponse,
    NewItemsSummary,
    NewItemsDetailRequest,
    NewItemsDetailResponse,
    NewEntity,
    NewHighlight,
    NewQuestion,
    NewRelationship,
    GlobalActivitySummary,
)
from ies_backend.schemas.passage import (
    PassageRankingRequest,
    PassageRankingResponse,
    RankedPassage,
)

__all__ = [
    # Context types
    "Context",
    "ContextType",
    "ContextStatus",
    "ContextCreate",
    "ContextUpdate",
    "ContextCreateRequest",
    "ContextCreateResponse",
    "ContextListResponse",
    # Question types
    "Question",
    "QuestionStatus",
    "QuestionCreateRequest",
    "QuestionListResponse",
    # Area types
    "AreaOfExploration",
    # Journey types
    "ContextJourneyEntry",
    "JourneyClassification",
    "JourneyEntryCreateRequest",
    "JourneyListResponse",
    # Context Note parsing
    "ContextNoteParseRequest",
    "ContextNoteParseResponse",
    # Context Search
    "ContextSearchRequest",
    "ContextSearchResponse",
    "ContextSearchResult",
    # Extraction types
    "ExtractionProfile",
    "ExtractionProfileCreate",
    "ExtractionResult",
    "ExtractionRunRequest",
    "ExtractionRunResponse",
    "QuestionExtractionProfile",
    # Visit tracking types
    "VisitScope",
    "VisitRecord",
    "RecordVisitRequest",
    "RecordVisitResponse",
    "NewItemsSummary",
    "NewItemsDetailRequest",
    "NewItemsDetailResponse",
    "NewEntity",
    "NewHighlight",
    "NewQuestion",
    "NewRelationship",
    "GlobalActivitySummary",
    # Passage ranking types
    "PassageRankingRequest",
    "PassageRankingResponse",
    "RankedPassage",
]
