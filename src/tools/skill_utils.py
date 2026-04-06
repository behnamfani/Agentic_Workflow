"""
A simple tool for AI agents to discover and read Agent Skills.
"""

import re
from pathlib import Path
from typing import Optional, Tuple
from langchain_core.tools import StructuredTool

SKILL_DIR = r"..\agents\skills"


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split YAML frontmatter and Markdown body from a SKILL.md string."""
    pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    match = pattern.match(text)
    if not match:
        return {}, text

    raw_yaml = match.group(1)
    body = text[match.end():]

    # Minimal YAML key-value parser (handles simple string values + nested maps)
    meta: dict = {}
    current_key: Optional[str] = None
    for line in raw_yaml.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        # Nested value (indented)
        if line.startswith("  ") and current_key:
            sub = line.strip()
            if ":" in sub:
                k, _, v = sub.partition(":")
                if isinstance(meta.get(current_key), dict):
                    meta[current_key][k.strip()] = v.strip().strip('"')
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip('"')
            if value == "":          # nested map coming next
                meta[key] = {}
                current_key = key
            else:
                meta[key] = value
                current_key = key

    return meta, body.strip()


def list_skills(skills_dir: str = SKILL_DIR) -> list[dict]:
    """
    DISCOVERY PHASE — load only name + description for every skill found.

    Args:
        skills_dir: Root folder that contains one sub-folder per skill.

    Returns:
        List of dicts with keys: name, description, path
    """
    root = Path(skills_dir)
    if not root.exists():
        raise FileNotFoundError(f"Skills directory not found: {skills_dir}")

    skills = []
    for skill_file in sorted(root.iterdir()):
        meta, _ = _parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        skills.append({
            "file name": skill_file.name,
            "name": meta.get("name", skill_file.name),
            "description": meta.get("description", "(no description)"),
            "path":        str(skill_file),
        })

    return skills


def read_skill(skills_dir: str, skill_name: str) -> dict:
    """
    ACTIVATION PHASE — load the full SKILL.md for a specific skill.

    Args:
        skills_dir: Root folder that contains skill sub-folders.
        skill_name: The skill's directory name (e.g. 'behnam-fanitabasi').

    Returns:
        Dict with keys: name, description, metadata, body (full Markdown instructions)
    """
    skill_file = Path(skills_dir) / skill_name
    if not skill_file.exists():
        raise FileNotFoundError(f"Skill not found: {skill_name} (looked in {skill_file})")

    raw = skill_file.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(raw)

    return {
        "name":        meta.get("name", skill_name),
        "description": meta.get("description", ""),
        "metadata":    meta,
        "body":        body,
    }


def get_tools() -> tuple[StructuredTool, StructuredTool]:
    return StructuredTool.from_function(list_skills), StructuredTool.from_function(read_skill)

if __name__ == "__main__":
    import sys
    import json

    skills_dir = r"..\agents\skills"

    print("=== DISCOVERED SKILLS ===")
    for s in list_skills(skills_dir):
        print(s)

    print(f"\n=== FULL SKILL: {s['file name']} ===")
    skill = read_skill(skills_dir, s['file name'])
    print(json.dumps({k: v for k, v in skill.items() if k != "body"}, indent=2))
    print("\n--- BODY ---\n")
    print(skill["body"])