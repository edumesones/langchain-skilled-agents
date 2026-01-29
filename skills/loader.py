"""
Skill Loader - Acquisition and Depth Layers

This module implements the second and third layers of progressive disclosure:

Acquisition Layer (load_skill):
    - When the agent decides it needs a skill, it calls load_skill
    - The tool reads the complete skill.md file
    - Returns detailed instructions to the agent's context

Depth Layer (read_reference):
    - For complex skills that need additional documentation
    - Agent can load specific reference files as needed
    - Avoids loading heavy technical details unless necessary
"""

from pathlib import Path
from typing import Any

from langchain_core.tools import tool

from config.logging_config import get_trace_logger
from skills.registry import get_skill_registry


@tool
def load_skill(skill_id: str) -> str:
    """
    Load detailed instructions for a specific skill.

    This is the Acquisition Layer of progressive disclosure. When you determine
    that you need to use a skill (based on the brief descriptions in your
    system prompt), call this tool to load the complete instructions.

    The skill instructions will include:
    - Detailed purpose and when to use
    - Required inputs and expected outputs
    - Step-by-step workflow
    - Examples and edge cases
    - Compliance considerations

    Args:
        skill_id: The ID of the skill to load (e.g., "customer_360", "alert_prioritizer")

    Returns:
        The complete skill instructions as markdown text, or an error message
        if the skill is not found.

    Example:
        >>> load_skill("customer_360")
        "# Customer 360\\n\\n## Purpose\\n..."
    """
    trace_logger = get_trace_logger()
    registry = get_skill_registry()

    # Log the skill load
    trace_logger.log_skill_load("TOOL", skill_id)

    # Check if skill exists
    skill = registry.get_skill(skill_id)
    if not skill:
        available = ", ".join(registry.get_all_skill_ids())
        return f"Error: Skill '{skill_id}' not found. Available skills: {available}"

    # Get skill file path
    skill_file = registry.get_skill_file_path(skill_id)
    if not skill_file or not skill_file.exists():
        return f"Error: Skill file not found for '{skill_id}'"

    try:
        content = skill_file.read_text(encoding="utf-8")

        # Add header with metadata
        header_lines = [
            f"# Skill Loaded: {skill_id}",
            f"**Version:** {skill.version}",
            f"**Category:** {skill.category}",
            f"**Domain:** {skill.domain}",
            "",
            "---",
            "",
        ]

        # Add info about available references
        if skill.references:
            header_lines.append("**Available References** (use `read_reference` to load):")
            for ref in skill.references:
                header_lines.append(f"- `{ref.get('id')}`: {ref.get('description', 'No description')}")
            header_lines.append("")

        # Add info about forms
        if skill.has_forms:
            header_lines.append("**Report Template Available**: Use `get_form_template` to get the downloadable report template.")
            header_lines.append("")

        header_lines.append("---")
        header_lines.append("")

        # Remove YAML front matter from content for cleaner output
        import re
        content = re.sub(r"^---\n.*?\n---\n*", "", content, flags=re.DOTALL)

        return "\n".join(header_lines) + content

    except Exception as e:
        return f"Error loading skill '{skill_id}': {str(e)}"


@tool
def read_reference(skill_id: str, reference_id: str) -> str:
    """
    Load a specific reference document for a skill.

    This is the Depth Layer of progressive disclosure. Use this when you need
    additional technical documentation that wasn't included in the main skill
    instructions.

    Reference documents contain detailed technical information like:
    - API specifications
    - Regulatory requirements
    - Decision matrices
    - Algorithm details

    Args:
        skill_id: The ID of the skill that owns the reference
        reference_id: The ID of the reference to load (shown when you load a skill)

    Returns:
        The reference document content, or an error message if not found.

    Example:
        >>> read_reference("alert_prioritizer", "severity_matrix")
        "# Severity Matrix\\n\\n| Alert Type | Low | Medium | High |..."
    """
    trace_logger = get_trace_logger()
    registry = get_skill_registry()

    trace_logger.log(
        "TOOL",
        f"Loading reference: {skill_id}/{reference_id}",
        level="INFO",
    )

    # Get reference path
    ref_path = registry.get_reference_path(skill_id, reference_id)
    if not ref_path:
        skill = registry.get_skill(skill_id)
        if not skill:
            return f"Error: Skill '{skill_id}' not found"

        available_refs = [r.get("id") for r in skill.references]
        return f"Error: Reference '{reference_id}' not found. Available: {available_refs}"

    if not ref_path.exists():
        return f"Error: Reference file not found at {ref_path}"

    try:
        content = ref_path.read_text(encoding="utf-8")
        return f"# Reference: {reference_id}\n**Skill:** {skill_id}\n\n---\n\n{content}"
    except Exception as e:
        return f"Error reading reference: {str(e)}"


@tool
def get_form_template(skill_id: str) -> str:
    """
    Get the report/form template for a skill.

    Some skills have downloadable report templates (forms.md) that can be
    used to generate formatted reports for the user.

    Args:
        skill_id: The ID of the skill

    Returns:
        The form template content, or an error message if not available.

    Example:
        >>> get_form_template("case_report_generator")
        "# SAR Report Template\\n\\n## Section 1: Subject Information..."
    """
    trace_logger = get_trace_logger()
    registry = get_skill_registry()

    trace_logger.log(
        "TOOL",
        f"Loading form template: {skill_id}",
        level="INFO",
    )

    forms_path = registry.get_forms_path(skill_id)
    if not forms_path:
        return f"Error: Skill '{skill_id}' does not have a form template"

    if not forms_path.exists():
        return f"Error: Form template file not found for '{skill_id}'"

    try:
        content = forms_path.read_text(encoding="utf-8")
        return f"# Form Template: {skill_id}\n\n---\n\n{content}"
    except Exception as e:
        return f"Error reading form template: {str(e)}"


@tool
def list_available_skills(category: str | None = None, domain: str | None = None) -> str:
    """
    List all available skills with optional filtering.

    Use this to discover what skills are available before loading them.

    Args:
        category: Optional filter by category (risk, compliance, analysis, reporting)
        domain: Optional filter by domain (aml, fraud, kyc, general)

    Returns:
        Formatted list of available skills with their brief descriptions.
    """
    registry = get_skill_registry()

    if category:
        skills = registry.get_skills_by_category(category)
    elif domain:
        skills = registry.get_skills_by_domain(domain)
    else:
        skills = list(registry.skills.values())

    if not skills:
        return "No skills found matching the criteria."

    lines = ["# Available Skills", ""]
    for skill in sorted(skills, key=lambda s: s.skill_id):
        lines.append(f"## {skill.skill_id}")
        lines.append(f"**Brief:** {skill.brief}")
        lines.append(f"**Category:** {skill.category} | **Domain:** {skill.domain}")
        lines.append(f"**Agents:** {', '.join(skill.agents)}")
        if skill.has_forms:
            lines.append("**Has Form Template:** Yes")
        lines.append("")

    return "\n".join(lines)


def get_skill_tools() -> list:
    """Get all skill-related tools for agent configuration."""
    return [load_skill, read_reference, get_form_template, list_available_skills]
