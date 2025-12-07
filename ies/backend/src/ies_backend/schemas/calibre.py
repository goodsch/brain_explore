"""Schemas for Calibre book catalog."""

from pydantic import BaseModel


class Book(BaseModel):
    """A book from the Calibre library."""

    calibre_id: int
    title: str
    author: str
    path: str
    entity_count: int = 0
    indexed: bool = False
