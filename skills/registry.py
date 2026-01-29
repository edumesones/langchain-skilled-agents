"""
Skill Registry - Discovery Layer

This module implements the first layer of the progressive disclosure architecture.
It maintains a registry of all available skills with their brief descriptions,
which are injected into the system prompt.

The agent doesn't know HOW to execute skills yet, only that they EXIST
and WHEN to call them based on the brief descriptions.
"""

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from config.settings import get_settings


@dataclass
class SkillMetadata:
    """Metadata extracted from a skill's YAML front matter."""

    skill_id: str
    version: str
    brief: str  # Short description for system prompt (max ~100 chars)
    category: str
    domain: str
    agents: list[str]
    capabilities: list[str]
    limitations: list[str]
    dependencies: dict[str, list[str]]
    references: list[dict[str, str]]
    has_forms: bool = False
    forms_path: str | None = None
    last_updated: str = ""
    author: str = ""

    @property
    def can_be_used_by(self) -> set[str]:
        """Get set of agents that can use this skill."""
        return set(self.agents)

    def to_brief_description(self) -> str:
        """Generate brief description for system prompt."""
        return f"- **{self.skill_id}**: {self.brief}"


@dataclass
class SkillRegistry:
    """
    Central registry of all available skills.

    Implements the Discovery Layer of progressive disclosure:
    - Scans skills directory on initialization
    - Extracts brief descriptions from YAML front matter
    - Provides skills list for system prompt injection
    """

    skills_path: Path
    skills: dict[str, SkillMetadata] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Load all skills on initialization."""
        self._scan_skills()

    def _scan_skills(self) -> None:
        """Scan skills directory and load metadata."""
        if not self.skills_path.exists():
            return

        for skill_dir in self.skills_path.iterdir():
            if not skill_dir.is_dir():
                continue
            if skill_dir.name.startswith("_") or skill_dir.name.startswith("."):
                continue

            skill_file = skill_dir / "skill.md"
            if skill_file.exists():
                try:
                    metadata = self._load_skill_metadata(skill_file)
                    if metadata:
                        self.skills[metadata.skill_id] = metadata
                except Exception as e:
                    print(f"Error loading skill {skill_dir.name}: {e}")

    def _load_skill_metadata(self, skill_file: Path) -> SkillMetadata | None:
        """Load skill metadata from YAML front matter."""
        content = skill_file.read_text(encoding="utf-8")

        # Extract YAML front matter
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return None

        try:
            yaml_content = yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return None

        if not yaml_content:
            return None

        # Check for forms.md
        forms_path = skill_file.parent / "forms.md"
        has_forms = forms_path.exists()

        return SkillMetadata(
            skill_id=yaml_content.get("skill_id", skill_file.parent.name),
            version=yaml_content.get("version", "1.0.0"),
            brief=yaml_content.get("brief", ""),
            category=yaml_content.get("category", "general"),
            domain=yaml_content.get("domain", "general"),
            agents=yaml_content.get("agents", ["orchestrator"]),
            capabilities=yaml_content.get("capabilities", []),
            limitations=yaml_content.get("limitations", []),
            dependencies=yaml_content.get("dependencies", {}),
            references=yaml_content.get("references", []),
            has_forms=has_forms,
            forms_path=str(forms_path) if has_forms else None,
            last_updated=yaml_content.get("last_updated", ""),
            author=yaml_content.get("author", ""),
        )

    def get_skill(self, skill_id: str) -> SkillMetadata | None:
        """Get skill metadata by ID."""
        return self.skills.get(skill_id)

    def get_skills_for_agent(self, agent: str) -> list[SkillMetadata]:
        """Get all skills available to a specific agent."""
        return [
            skill for skill in self.skills.values()
            if agent in skill.can_be_used_by
        ]

    def get_skills_by_category(self, category: str) -> list[SkillMetadata]:
        """Get all skills in a category."""
        return [
            skill for skill in self.skills.values()
            if skill.category == category
        ]

    def get_skills_by_domain(self, domain: str) -> list[SkillMetadata]:
        """Get all skills in a domain."""
        return [
            skill for skill in self.skills.values()
            if skill.domain == domain
        ]

    def generate_system_prompt_skills_section(
        self,
        agent: str | None = None,
    ) -> str:
        """
        Generate the skills section for a system prompt.

        This is the core of the Discovery Layer - it provides the agent
        with a list of available skills and their brief descriptions.

        Args:
            agent: Optional agent filter. If provided, only skills
                   available to that agent are included.

        Returns:
            Formatted string for system prompt injection.
        """
        if agent:
            skills = self.get_skills_for_agent(agent)
        else:
            skills = list(self.skills.values())

        if not skills:
            return "No skills available."

        # Group by category
        by_category: dict[str, list[SkillMetadata]] = {}
        for skill in skills:
            cat = skill.category
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(skill)

        lines = ["## Available Skills", ""]
        lines.append("You have access to the following skills. Use the `load_skill` tool ")
        lines.append("to load detailed instructions when you need to use a skill.")
        lines.append("")

        for category, cat_skills in sorted(by_category.items()):
            lines.append(f"### {category.title()}")
            for skill in sorted(cat_skills, key=lambda s: s.skill_id):
                lines.append(skill.to_brief_description())
            lines.append("")

        lines.append("---")
        lines.append("**Important**: Only load skills when needed. Each skill contains ")
        lines.append("detailed instructions that will be added to the conversation context.")

        return "\n".join(lines)

    def get_all_skill_ids(self) -> list[str]:
        """Get list of all skill IDs."""
        return list(self.skills.keys())

    def get_skill_path(self, skill_id: str) -> Path | None:
        """Get the path to a skill's directory."""
        skill = self.skills.get(skill_id)
        if not skill:
            return None
        return self.skills_path / skill_id

    def get_skill_file_path(self, skill_id: str) -> Path | None:
        """Get the path to a skill's main file."""
        skill_dir = self.get_skill_path(skill_id)
        if not skill_dir:
            return None
        return skill_dir / "skill.md"

    def get_reference_path(self, skill_id: str, reference_id: str) -> Path | None:
        """Get the path to a skill's reference file."""
        skill = self.skills.get(skill_id)
        if not skill:
            return None

        for ref in skill.references:
            if ref.get("id") == reference_id:
                ref_path = ref.get("path")
                if ref_path:
                    return self.skills_path / skill_id / ref_path

        return None

    def get_forms_path(self, skill_id: str) -> Path | None:
        """Get the path to a skill's forms file."""
        skill = self.skills.get(skill_id)
        if not skill or not skill.has_forms:
            return None
        return self.skills_path / skill_id / "forms.md"

    def to_dict(self) -> dict[str, Any]:
        """Export registry as dictionary."""
        return {
            skill_id: {
                "brief": skill.brief,
                "category": skill.category,
                "domain": skill.domain,
                "agents": skill.agents,
                "has_forms": skill.has_forms,
            }
            for skill_id, skill in self.skills.items()
        }


# Global registry instance
_registry: SkillRegistry | None = None


def get_skill_registry() -> SkillRegistry:
    """Get the global skill registry instance."""
    global _registry
    if _registry is None:
        settings = get_settings()
        _registry = SkillRegistry(skills_path=settings.skills_path)
    return _registry


def reset_skill_registry() -> None:
    """Reset the global skill registry (for testing)."""
    global _registry
    _registry = None
