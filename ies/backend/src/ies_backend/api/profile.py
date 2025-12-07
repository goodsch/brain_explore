"""Profile API endpoints."""

from fastapi import APIRouter, HTTPException

from ies_backend.schemas.profile import (
    CapacityCheckIn,
    ProfileObservation,
    ProfileUpdate,
    UserProfile,
)
from ies_backend.services.profile_service import ProfileService

router = APIRouter()
profile_service = ProfileService()


@router.post("/login", response_model=UserProfile)
async def login(user_id: str, display_name: str | None = None) -> UserProfile:
    """Get or create profile for user (upsert behavior).

    This is the primary entry point for frontend auth flow. Accepts any user_id
    format (Supabase UUID, device ID, username, etc.) and ensures a profile exists.

    Frontends should call this on initialization and use the returned user_id
    for all subsequent API calls.
    """
    return await profile_service.get_or_create_profile(user_id, display_name)


@router.get("/{user_id}", response_model=UserProfile)
async def get_profile(user_id: str) -> UserProfile:
    """Get user profile by ID."""
    profile = await profile_service.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found: {user_id}")
    return profile


@router.post("/{user_id}", response_model=UserProfile)
async def create_profile(user_id: str, display_name: str | None = None) -> UserProfile:
    """Create a new user profile with defaults."""
    profile = await profile_service.create_profile(user_id, display_name)
    return profile


@router.patch("/{user_id}", response_model=UserProfile)
async def update_profile(user_id: str, update: ProfileUpdate) -> UserProfile:
    """Update user profile dimensions."""
    profile = await profile_service.update_profile(user_id, update)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found: {user_id}")
    return profile


@router.post("/{user_id}/capacity", response_model=UserProfile)
async def check_in_capacity(user_id: str, check_in: CapacityCheckIn) -> UserProfile:
    """Record session capacity check-in."""
    profile = await profile_service.record_capacity(user_id, check_in)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found: {user_id}")
    return profile


@router.post("/{user_id}/observe", response_model=UserProfile)
async def observe_session(user_id: str, observation: ProfileObservation) -> UserProfile:
    """Update profile based on session observations."""
    profile = await profile_service.apply_observation(user_id, observation)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found: {user_id}")
    return profile


@router.get("/{user_id}/summary")
async def get_profile_summary(user_id: str) -> dict:
    """Get a condensed profile summary for session context."""
    summary = await profile_service.get_profile_summary(user_id)
    if not summary:
        raise HTTPException(status_code=404, detail=f"Profile not found: {user_id}")
    return summary


@router.post("/{user_id}/sync-siyuan")
async def sync_to_siyuan(user_id: str, notebook_id: str | None = None) -> dict:
    """Sync profile to SiYuan as a human-readable page.

    Args:
        user_id: User ID
        notebook_id: Optional SiYuan notebook ID override
    """
    from ies_backend.services.siyuan_profile_service import SiYuanProfileService

    profile = await profile_service.get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found: {user_id}")

    siyuan_service = SiYuanProfileService(notebook_id)
    try:
        doc_id = await siyuan_service.create_or_update_profile_page(profile)
        return {"status": "synced", "doc_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SiYuan sync failed: {str(e)}")
