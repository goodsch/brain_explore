"""Plan/Checklist/Spark builder for Quick Add prompt-to-create."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from ies_backend.schemas.entity import ExtractionResult
from ies_backend.schemas.plan import Checklist, ChecklistItem, Plan, PlanStep, Spark
from ies_backend.services.extraction_service import ExtractionService
from ies_backend.services.neo4j_client import Neo4jClient
from ies_backend.schemas.plan import BuildPlanResponse

# Optional Anthropic
ANTHROPIC_AVAILABLE = False
try:
    import anthropic

    from ies_backend.config import settings

    ANTHROPIC_AVAILABLE = bool(settings.anthropic_api_key)
except Exception:
    pass


class PlanBuilderService:
    """Generate plans, checklists, and sparks from a prompt."""

    @staticmethod
    async def build(prompt: str, intents: list[str], duration: Optional[int], due: Optional[str], user_id: str, source_id: Optional[str] = None) -> BuildPlanResponse:
        """Orchestrate plan/checklist/spark generation and entity linking."""
        extraction = await PlanBuilderService._extract_entities(prompt)

        plan = None
        checklist = None
        spark = None

        if "plan" in intents:
            plan = await PlanBuilderService.build_plan(prompt, duration, due)
            await PlanBuilderService._link_entities(plan.id, user_id, "Plan", extraction)

        if "checklist" in intents:
            checklist = await PlanBuilderService.build_checklist(prompt)
            await PlanBuilderService._link_entities(checklist.id, user_id, "Checklist", extraction)

        if "spark" in intents or ("plan" not in intents and "checklist" not in intents):
            spark = await PlanBuilderService.create_spark(prompt)
            await PlanBuilderService._link_entities(spark.id, user_id, "Spark", extraction)

        return BuildPlanResponse(plan=plan, checklist=checklist, spark=spark, extraction=extraction)

    # ---- Builders ----
    @staticmethod
    async def build_plan(prompt: str, duration: Optional[int], due: Optional[str]) -> Plan:
        """Build an ADHD-friendly plan."""
        if ANTHROPIC_AVAILABLE:
            try:
                plan = await PlanBuilderService._llm_build_plan(prompt, duration, due)
                if plan:
                    return plan
            except Exception:
                pass
        return PlanBuilderService._fallback_plan(prompt, duration, due)

    @staticmethod
    async def build_checklist(prompt: str) -> Checklist:
        """Build a checklist."""
        if ANTHROPIC_AVAILABLE:
            try:
                cl = await PlanBuilderService._llm_build_checklist(prompt)
                if cl:
                    return cl
            except Exception:
                pass
        return PlanBuilderService._fallback_checklist(prompt)

    @staticmethod
    async def create_spark(prompt: str) -> Spark:
        """Create a concise spark/insight."""
        if ANTHROPIC_AVAILABLE:
            try:
                sp = await PlanBuilderService._llm_build_spark(prompt)
                if sp:
                    return sp
            except Exception:
                pass
        return PlanBuilderService._fallback_spark(prompt)

    # ---- LLM helpers ----
    @staticmethod
    async def _llm_build_plan(prompt: str, duration: Optional[int], due: Optional[str]) -> Optional[Plan]:
        client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        target = f"{duration} minutes" if duration else "60-90 minutes"
        system_prompt = (
            "You generate ADHD-friendly timeboxed plans. Return JSON with keys: "
            "micro_start (string), steps (array of {description, timebox_minutes, done_criteria, friction_reducer}). "
            "Steps should be 5-15 minutes. Include clear done criteria and friction reducers."
        )
        user_prompt = f"Goal: {prompt}\nTarget time: {target}\nDue: {due or 'unspecified'}\nRespond with JSON only."
        msg = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = msg.content[0].text
        import json
        try:
            data = json.loads(text.strip().split("```json")[-1].split("```")[0] if "```" in text else text)
            steps = []
            for s in data.get("steps", []):
                steps.append(
                    PlanStep(
                        description=s.get("description", ""),
                        timebox_minutes=int(s.get("timebox_minutes", 10)),
                        done_criteria=s.get("done_criteria"),
                        friction_reducer=s.get("friction_reducer"),
                    )
                )
            return Plan(
                id=f"plan_{uuid.uuid4().hex[:10]}",
                title=prompt[:80],
                micro_start=data.get("micro_start", "Start the first tiny piece."),
                steps=steps,
                total_minutes=sum(s.timebox_minutes for s in steps) if steps else duration,
                due=due,
                created_at=datetime.now(timezone.utc),
            )
        except Exception:
            return None

    @staticmethod
    async def _llm_build_checklist(prompt: str) -> Optional[Checklist]:
        client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        system_prompt = (
            "You generate actionable checklists. Return JSON with items: [{description, done_criteria}]. "
            "Make 3-7 concise items."
        )
        msg = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            system=system_prompt,
            messages=[{"role": "user", "content": f"Create a checklist for: {prompt}"}],
        )
        text = msg.content[0].text
        import json
        try:
            data = json.loads(text.strip().split("```json")[-1].split("```")[0] if "```" in text else text)
            items = []
            for item in data.get("items", []):
                items.append(ChecklistItem(description=item.get("description", ""), done_criteria=item.get("done_criteria")))
            return Checklist(
                id=f"chk_{uuid.uuid4().hex[:10]}",
                title=prompt[:80],
                items=items,
                created_at=datetime.now(timezone.utc),
            )
        except Exception:
            return None

    @staticmethod
    async def _llm_build_spark(prompt: str) -> Optional[Spark]:
        client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        system_prompt = "You write one-sentence insights with 2-4 short tags. Return JSON {content, tags}."
        msg = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            system=system_prompt,
            messages=[{"role": "user", "content": f"Synthesize the key insight from: {prompt}"}],
        )
        text = msg.content[0].text
        import json
        try:
            data = json.loads(text.strip().split("```json")[-1].split("```")[0] if "```" in text else text)
            return Spark(
                id=f"spark_{uuid.uuid4().hex[:10]}",
                content=data.get("content", prompt[:140]),
                tags=data.get("tags", []),
                created_at=datetime.now(timezone.utc),
            )
        except Exception:
            return None

    # ---- Fallbacks ----
    @staticmethod
    def _fallback_plan(prompt: str, duration: Optional[int], due: Optional[str]) -> Plan:
        steps = [
            PlanStep(
                description="Write the smallest first deliverable (5-10 min).",
                timebox_minutes=10,
                done_criteria="A draft or outline exists.",
                friction_reducer="Open editor and create the file before starting timer.",
            ),
            PlanStep(
                description="Refine and check for completeness.",
                timebox_minutes=10,
                done_criteria="All sections touched once.",
                friction_reducer="Set a 10-minute timer; stop when it rings.",
            ),
        ]
        return Plan(
            id=f"plan_{uuid.uuid4().hex[:10]}",
            title=prompt[:80],
            micro_start="Open your editor and create a blank doc with the title.",
            steps=steps,
            total_minutes=sum(s.timebox_minutes for s in steps),
            due=due,
            created_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _fallback_checklist(prompt: str) -> Checklist:
        items = [
            ChecklistItem(description="Clarify the exact outcome", done_criteria="A one-line success definition exists."),
            ChecklistItem(description="List blockers and quick mitigations", done_criteria="At least one mitigation per blocker."),
            ChecklistItem(description="Pick the first micro-step", done_criteria="A 5-minute action identified."),
        ]
        return Checklist(
            id=f"chk_{uuid.uuid4().hex[:10]}",
            title=prompt[:80],
            items=items,
            created_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _fallback_spark(prompt: str) -> Spark:
        return Spark(
            id=f"spark_{uuid.uuid4().hex[:10]}",
            content=prompt[:200],
            tags=[],
            created_at=datetime.now(timezone.utc),
        )

    # ---- Extraction & linking ----
    @staticmethod
    async def _extract_entities(prompt: str) -> ExtractionResult:
        extractor = ExtractionService()
        try:
            return await extractor.extract_entities(prompt)
        except Exception:
            return ExtractionResult(entities=[])

    @staticmethod
    async def _link_entities(item_id: str, user_id: str, item_type: str, extraction: ExtractionResult):
        """Persist a lightweight item node and link entities."""
        if not extraction or not extraction.entities:
            return
        now = datetime.now(timezone.utc).isoformat()
        names = [e.name for e in extraction.entities]
        query = """
        MERGE (n:QuickAddItem {id: $id})
        SET n.user_id = $user_id,
            n.type = $item_type,
            n.created_at = $now
        """
        await Neo4jClient.execute_write(
            query,
            {"id": item_id, "user_id": user_id, "item_type": item_type, "now": now},
        )
        rel_query = """
        UNWIND $entities AS name
        MERGE (e:Entity {user_id: $user_id, name: name})
        ON CREATE SET e.created_at = $now, e.status = 'seed'
        SET e.updated_at = $now
        WITH e
        MATCH (n:QuickAddItem {id: $id})
        MERGE (n)-[:MENTIONS]->(e)
        """
        await Neo4jClient.execute_write(
            rel_query,
            {"entities": names, "user_id": user_id, "id": item_id, "now": now},
        )
