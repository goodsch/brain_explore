"""SiYuan profile page service - creates human-readable profile pages."""

from ies_backend.schemas.profile import UserProfile
from ies_backend.services.siyuan_client import SiYuanClient


class SiYuanProfileService:
    """Service for managing profile pages in SiYuan."""

    # Default notebook for IES profiles
    DEFAULT_NOTEBOOK = "20241201000000-ies"  # Will be configured

    def __init__(self, notebook_id: str | None = None):
        """Initialize with optional notebook override."""
        self.notebook_id = notebook_id or self.DEFAULT_NOTEBOOK

    async def create_or_update_profile_page(self, profile: UserProfile) -> str:
        """Create or update a profile page in SiYuan.

        Args:
            profile: User profile to render

        Returns:
            Document ID
        """
        markdown = self._render_profile_markdown(profile)
        path = f"/Profiles/{profile.user_id}"

        # Check if page exists
        existing = await SiYuanClient.find_doc_by_path(self.notebook_id, path)

        if existing:
            # Update existing page
            await SiYuanClient.update_block(existing["id"], markdown)
            return existing["id"]
        else:
            # Create new page
            result = await SiYuanClient.create_doc(
                self.notebook_id, path, markdown
            )
            return result.get("id", "")

    def _render_profile_markdown(self, profile: UserProfile) -> str:
        """Render profile as human-readable markdown."""
        lines = [
            f"# {profile.display_name or profile.user_id}'s Profile",
            "",
            f"*Last updated: {profile.last_updated or 'Never'}*",
            "",
        ]

        # Processing Style
        lines.extend([
            "## Processing Style",
            "",
            f"- **Information processing**: {self._format_style(profile.processing.style.value)}",
            f"- **Decision making**: {self._format_style(profile.processing.decision_style.value)}",
            f"- **Habituation speed**: {self._format_scale(profile.processing.habituation_speed, 'slow to habituate', 'quick to habituate')}",
            f"- **Abstraction preference**: {self._format_scale(profile.processing.abstraction_preference, 'concrete examples', 'theoretical frameworks')}",
            "",
        ])

        # Attention & Energy
        lines.extend([
            "## Attention & Energy",
            "",
            f"- **Current capacity**: {profile.attention.current_capacity}/10",
            f"- **Optimal session length**: {profile.attention.optimal_session_length} minutes",
            "",
        ])

        if profile.attention.hyperfocus_triggers:
            lines.append("**Hyperfocus triggers:**")
            for trigger in profile.attention.hyperfocus_triggers:
                lines.append(f"- {trigger}")
            lines.append("")

        if profile.attention.distraction_vulnerabilities:
            lines.append("**Distraction vulnerabilities:**")
            for vuln in profile.attention.distraction_vulnerabilities:
                lines.append(f"- {vuln}")
            lines.append("")

        if profile.attention.recovery_patterns:
            lines.append("**Recovery patterns:**")
            for pattern in profile.attention.recovery_patterns:
                lines.append(f"- {pattern}")
            lines.append("")

        # Communication
        lines.extend([
            "## Communication Preferences",
            "",
            f"- **Verbal fluency**: {self._format_scale(profile.communication.verbal_fluency, 'searching for words', 'easy flow')}",
            f"- **Pace preference**: {profile.communication.pace.value}",
            f"- **Directness**: {self._format_scale(profile.communication.directness_preference, 'gentle', 'direct')}",
            f"- **Wait time needed**: {self._format_scale(profile.communication.wait_time_needed, 'thinks while speaking', 'needs processing time')}",
            "",
        ])

        # Executive Functioning
        lines.extend([
            "## Executive Functioning",
            "",
            f"- **Task initiation**: {self._format_scale(profile.executive.task_initiation, 'hard to start', 'easy to start')}",
            f"- **Transition cost**: {self._format_scale(profile.executive.transition_cost, 'easy switches', 'high switching cost')}",
            f"- **Time perception**: {self._format_scale(profile.executive.time_perception, 'time aware', 'time blind')}",
            f"- **Structure need**: {profile.executive.structure_need.value}",
            f"- **Working memory**: {self._format_scale(profile.executive.working_memory, 'limited', 'strong')}",
            "",
        ])

        # Sensory
        lines.extend([
            "## Sensory & Environment",
            "",
            f"- **Environment preference**: {self._format_scale(profile.sensory.environment_preference, 'quiet', 'stimulating')}",
            "",
        ])

        if profile.sensory.overwhelm_signals:
            lines.append("**Overwhelm signals:**")
            for signal in profile.sensory.overwhelm_signals:
                lines.append(f"- {signal}")
            lines.append("")

        if profile.sensory.regulation_tools:
            lines.append("**Regulation tools:**")
            for tool in profile.sensory.regulation_tools:
                lines.append(f"- {tool}")
            lines.append("")

        # Metadata
        lines.extend([
            "---",
            "",
            "## Session History",
            "",
            f"- **Sessions completed**: {profile.sessions_completed}",
            f"- **Onboarding complete**: {'Yes' if profile.onboarding_complete else 'No'}",
        ])

        return "\n".join(lines)

    def _format_style(self, value: str) -> str:
        """Format enum style values for display."""
        return value.replace("_", " ").title()

    def _format_scale(self, value: int, low_label: str, high_label: str) -> str:
        """Format a 1-10 scale value with labels."""
        if value <= 3:
            return f"{value}/10 ({low_label})"
        elif value >= 8:
            return f"{value}/10 ({high_label})"
        else:
            return f"{value}/10 (moderate)"
