"""Neo4j client for database operations."""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession

from ies_backend.config import settings


class Neo4jClient:
    """Async Neo4j client wrapper."""

    _driver: AsyncDriver | None = None

    @classmethod
    async def get_driver(cls) -> AsyncDriver:
        """Get or create the Neo4j driver."""
        if cls._driver is None:
            cls._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
        return cls._driver

    @classmethod
    async def close(cls) -> None:
        """Close the driver connection."""
        if cls._driver is not None:
            await cls._driver.close()
            cls._driver = None

    @classmethod
    @asynccontextmanager
    async def session(cls) -> AsyncGenerator[AsyncSession, None]:
        """Get a Neo4j session context manager."""
        driver = await cls.get_driver()
        session = driver.session()
        try:
            yield session
        finally:
            await session.close()

    @classmethod
    async def execute_query(
        cls,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query and return results."""
        async with cls.session() as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    @classmethod
    async def execute_write(
        cls,
        query: str,
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Execute a write query in a transaction."""
        async with cls.session() as session:

            async def _write_tx(tx: Any) -> list[dict[str, Any]]:
                result = await tx.run(query, parameters or {})
                return await result.data()

            return await session.execute_write(_write_tx)
