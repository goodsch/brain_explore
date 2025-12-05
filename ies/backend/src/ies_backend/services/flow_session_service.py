"""Service for Flow session lifecycle and synthesis."""

import json
import uuid
from datetime import datetime, timezone
from typing import Any

from anthropic import AsyncAnthropic

from ies_backend.config import settings
from ies_backend.schemas.flow_session import (
    FlowInitialView,
    FlowOpenRequest,
    FlowOpenResponse,
    FlowOrigin,
    FlowOriginType,
    FlowSession,
    FlowSynthesisResponse,
    FlowStepRequest,
    GraphEdge,
    GraphNode,
    RecommendedPath,
)
from ies_backend.schemas.thinking import Breadcrumb
from ies_backend.services.neo4j_client import Neo4jClient
from ies_backend.services.thinking_service import ThinkingService


class FlowSessionService:
    """Manage Flow Mode sessions tied to thinking sessions or sparks."""

    _anthropic_client: AsyncAnthropic | None = None

    # ------------------------------------------------------------------
    # Session lifecycle
    # ------------------------------------------------------------------
    @classmethod
    async def open_from_thinking_session(
        cls, request: FlowOpenRequest
    ) -> FlowOpenResponse:
        """Open a flow session based on a thinking session."""
        thinking = await ThinkingService.get_session(request.thinking_session_id)
        if not thinking:
            raise ValueError(f"Thinking session not found: {request.thinking_session_id}")

        await cls._ensure_schema()

        center_node = thinking.entities[0] if thinking.entities else thinking.capture_id
        graph_view = await cls._fetch_graph_view(center_node)

        flow_session_id = f"flow_{uuid.uuid4().hex[:12]}"
        origin = FlowOrigin(
            type=FlowOriginType.THINKING_SESSION_NOTE,
            siyuan_note_id=thinking.siyuan_note_id,
            capture_id=thinking.capture_id,
        )
        breadcrumbs: list[Breadcrumb] = []

        await Neo4jClient.execute_write(
            """
            MERGE (f:FlowSession {id: $id})
            SET f.origin = $origin,
                f.visited_nodes = $visited_nodes,
                f.visited_edges = $visited_edges,
                f.breadcrumbs_json = $breadcrumbs_json,
                f.insights = $insights,
                f.created_at = $created_at
            WITH f
            MATCH (t:ThinkingSession {id: $thinking_session_id})
            MERGE (f)-[:FROM_THINKING]->(t)
            """,
            {
                "id": flow_session_id,
                "origin": json.dumps(origin.model_dump(by_alias=True)),
                "visited_nodes": [center_node] if center_node else [],
                "visited_edges": [],
                "breadcrumbs_json": json.dumps([]),
                "insights": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "thinking_session_id": thinking.id,
            },
        )

        flow_session = FlowSession(
            id=flow_session_id,
            origin=origin,
            visited_nodes=[center_node] if center_node else [],
            visited_edges=[],
            breadcrumbs=breadcrumbs,
            insights=[],
        )

        initial_view = cls._build_initial_view(center_node, graph_view)

        return FlowOpenResponse(flow_session=flow_session, initial_view=initial_view)

    @classmethod
    async def get_session(cls, session_id: str) -> FlowSession | None:
        """Get flow session by ID."""
        await cls._ensure_schema()
        results = await Neo4jClient.execute_query(
            """
            MATCH (f:FlowSession {id: $id})
            RETURN f
            """,
            {"id": session_id},
        )
        if not results:
            return None
        record = results[0]
        node = record.get("f") if isinstance(record, dict) else record
        return cls._record_to_session(node)

    @classmethod
    async def record_step(cls, session_id: str, request: FlowStepRequest) -> FlowSession | None:
        """Record a breadcrumb during flow exploration."""
        session = await cls.get_session(session_id)
        if not session:
            return None

        breadcrumb = Breadcrumb(
            id=f"breadcrumb_{uuid.uuid4().hex[:10]}",
            timestamp=datetime.now(timezone.utc),
            node_id=request.node_id,
            edge_id=request.edge_id,
            from_spark=request.from_spark,
            user_note=request.user_note,
            summary=request.summary,
        )

        breadcrumbs = list(session.breadcrumbs) + [breadcrumb]
        visited_nodes = list(session.visited_nodes)
        visited_edges = list(session.visited_edges)
        if request.node_id:
            visited_nodes.append(request.node_id)
        if request.edge_id:
            visited_edges.append(request.edge_id)

        await Neo4jClient.execute_write(
            """
            MATCH (f:FlowSession {id: $id})
            SET f.breadcrumbs_json = $breadcrumbs_json,
                f.visited_nodes = $visited_nodes,
                f.visited_edges = $visited_edges,
                f.updated_at = $updated_at
            """,
            {
                "id": session_id,
                "breadcrumbs_json": json.dumps([b.model_dump(mode="json") for b in breadcrumbs]),
                "visited_nodes": visited_nodes,
                "visited_edges": visited_edges,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        if request.from_spark:
            try:
                from ies_backend.services.personal_graph_service import PersonalGraphService
                await PersonalGraphService.visit_spark(request.from_spark)
            except Exception:
                pass

        session.breadcrumbs = breadcrumbs
        session.visited_nodes = visited_nodes
        session.visited_edges = visited_edges
        return session

    @classmethod
    async def generate_synthesis(cls, session_id: str) -> FlowSynthesisResponse | None:
        """Generate synthesis text from the flow journey."""
        session = await cls.get_session(session_id)
        if not session:
            return None

        summary = await cls._summarize_session(session)
        return FlowSynthesisResponse(synthesis=summary, flowSession=session)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @classmethod
    async def _ensure_schema(cls) -> None:
        constraints = [
            "CREATE CONSTRAINT flow_id IF NOT EXISTS FOR (f:FlowSession) REQUIRE f.id IS UNIQUE",
            "CREATE INDEX flow_origin IF NOT EXISTS FOR (f:FlowSession) ON (f.origin)",
        ]
        for query in constraints:
            try:
                await Neo4jClient.execute_write(query)
            except Exception:
                continue

    @classmethod
    def _get_anthropic_client(cls) -> AsyncAnthropic | None:
        if cls._anthropic_client is None and settings.anthropic_api_key:
            cls._anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        return cls._anthropic_client

    @classmethod
    async def _fetch_graph_view(cls, center_node: str | None) -> dict[str, Any]:
        """Use knowledge graph to gather neighbors."""
        if not center_node:
            return {}
        try:
            # Query for neighbors within 1 hop
            results = await Neo4jClient.execute_query(
                """
                MATCH (n)-[r]-(neighbor)
                WHERE n.name = $name OR n.id = $name
                RETURN n, r, neighbor
                LIMIT 50
                """,
                {"name": center_node},
            )
            nodes = []
            relationships = []
            seen_nodes = set()
            for record in results or []:
                if isinstance(record, dict):
                    neighbor = record.get("neighbor")
                    rel = record.get("r")
                    if neighbor:
                        node_name = neighbor.get("name") or neighbor.get("id", "")
                        if node_name and node_name not in seen_nodes:
                            seen_nodes.add(node_name)
                            nodes.append({
                                "name": node_name,
                                "title": neighbor.get("title") or node_name,
                            })
                    if rel:
                        relationships.append({
                            "start": rel.start_node.get("name") if hasattr(rel, "start_node") else center_node,
                            "end": rel.end_node.get("name") if hasattr(rel, "end_node") else "",
                            "type": rel.type if hasattr(rel, "type") else "RELATED",
                        })
            return {"nodes": nodes, "relationships": relationships}
        except Exception:
            return {}

    @staticmethod
    def _build_initial_view(center_node: str | None, graph_view: dict[str, Any]) -> FlowInitialView:
        nodes = graph_view.get("nodes", []) if graph_view else []
        relationships = graph_view.get("relationships", []) if graph_view else []

        neighbor_nodes = []
        for node in nodes:
            name = node.get("name") if isinstance(node, dict) else None
            if name and name != center_node:
                neighbor_nodes.append(GraphNode(id=name, label=node.get("title") or name))

        edges = []
        for rel in relationships:
            start = rel.get("start")
            end = rel.get("end")
            if start and end:
                edges.append(
                    GraphEdge(
                        id=rel.get("type", f"{start}->{end}"),
                        source=start,
                        target=end,
                        type=rel.get("type"),
                    )
                )

        recommended_paths = []
        if center_node and neighbor_nodes:
            recommended_paths.append(
                RecommendedPath(
                    id=f"path_{uuid.uuid4().hex[:8]}",
                    name="Neighbor path",
                    nodes=[center_node, neighbor_nodes[0].id],
                )
            )

        return FlowInitialView(
            center_node=center_node,
            neighbor_nodes=neighbor_nodes,
            edges=edges,
            recommended_paths=recommended_paths,
        )

    @classmethod
    async def _summarize_session(cls, session: FlowSession) -> str:
        """Use LLM (or fallback) to summarize the journey."""
        client = cls._get_anthropic_client()
        breadcrumb_texts = []
        for crumb in session.breadcrumbs:
            parts = [crumb.summary or "", crumb.user_note or ""]
            breadcrumb_texts.append(" ".join([p for p in parts if p]).strip())
        journey_text = "; ".join([p for p in breadcrumb_texts if p]) or "No breadcrumbs recorded."

        if not client:
            return f"Flow journey summary for {session.origin.type.value}: {journey_text}"

        prompt = f"""Summarize this flow journey in 3-5 bullet insights.
Visited nodes: {', '.join(session.visited_nodes)}
Journey: {journey_text}

Return plain text bullets."""
        try:
            message = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            text = message.content[0].text if message and message.content else ""
            if text:
                return text
        except Exception:
            pass
        return f"Flow journey summary for {session.origin.type.value}: {journey_text}"

    @staticmethod
    def _record_to_session(node: Any) -> FlowSession:
        data = dict(node)
        origin_raw = data.get("origin")
        origin: FlowOrigin
        if origin_raw:
            try:
                payload = origin_raw if isinstance(origin_raw, dict) else json.loads(str(origin_raw))
                origin = FlowOrigin.model_validate(payload)
            except Exception:
                origin = FlowOrigin(type=FlowOriginType.CONCEPT, siyuan_note_id=None, capture_id=None, concept_id=None)
        else:
            origin = FlowOrigin(type=FlowOriginType.CONCEPT, siyuan_note_id=None, capture_id=None, concept_id=None)

        breadcrumbs_json = data.get("breadcrumbs_json") or "[]"
        if not isinstance(breadcrumbs_json, str):
            breadcrumbs_json = json.dumps(breadcrumbs_json or [])
        try:
            breadcrumbs = [Breadcrumb.model_validate(b) for b in json.loads(breadcrumbs_json)]
        except Exception:
            breadcrumbs = []

        return FlowSession(
            id=data.get("id", ""),
            origin=origin,
            visited_nodes=data.get("visited_nodes", []),
            visited_edges=data.get("visited_edges", []),
            breadcrumbs=breadcrumbs,
            insights=data.get("insights", []),
        )
