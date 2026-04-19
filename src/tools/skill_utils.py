"""
A simple tool for AI agents to discover and read Agent Skills.
"""
import sys
import re
import os
from pathlib import Path
from typing import Optional, Tuple
from langchain_core.tools import StructuredTool

# Add the parent directory to sys.path so we can import our models
current_file_path = os.path.abspath(__file__)
current_directory_path = os.path.dirname(current_file_path)
parent_directory_path = os.path.dirname(current_directory_path)
root_directory_path = os.path.dirname(parent_directory_path)
sys.path.insert(0, current_directory_path)
sys.path.insert(0, parent_directory_path)
sys.path.insert(0, root_directory_path)

SKILL_DIR = fr"{root_directory_path}\src\agents\skills"


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


def list_skills() -> list[dict]:
    """
    DISCOVERY PHASE — load only name + description for every skill found.

    Returns:
        List of dicts with keys: name, description, path
    """
    global skills_dir
    skills_dir = SKILL_DIR
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


def read_skill(skills_dir: str, skill_file: str) -> dict:
    """
    ACTIVATION PHASE — load the full SKILL.md for a specific skill.

    Args:
        skills_dir: Root folder that contains skill sub-folders.
        skill_file: The skill's file name.

    Returns:
        Dict with keys: name, description, metadata, body (full Markdown instructions)
    """
    skill_file = Path(skills_dir) / skill_file
    if not skill_file.exists():
        raise FileNotFoundError(f"Skill not found: {skill_file} (looked in {skill_file})")

    raw = skill_file.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(raw)

    return {
        "name":        meta.get("name", skill_file.name),
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
    for s in list_skills():
        print(s)

    print(f"\n=== FULL SKILL: {s['file name']} ===")
    skill = read_skill(skills_dir, s['file name'])
    print(json.dumps({k: v for k, v in skill.items() if k != "body"}, indent=2))
    print("\n--- BODY ---\n")
    print(skill["body"])