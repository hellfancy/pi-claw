from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Skill:
    name: str
    description: str
    content: str
    path: Path


def parse_skill_file(path: Path) -> Skill:
    raw = path.read_text(encoding="utf-8").strip()

    name = path.stem
    description = ""

    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            frontmatter = parts[1]
            raw = parts[2].strip()

            for line in frontmatter.splitlines():
                line = line.strip()
                if line.startswith("name:"):
                    name = line.removeprefix("name:").strip()
                elif line.startswith("description:"):
                    description = line.removeprefix("description:").strip()

    return Skill(
        name=name,
        description=description,
        content=raw,
        path=path,
    )


def load_skills(cwd: Path, skills_dir: str = ".openclaw/skills") -> dict[str, Skill]:
    skills_path = cwd / skills_dir

    if not skills_path.exists() or not skills_path.is_dir():
        return {}

    skills: dict[str, Skill] = {}

    for path in sorted(skills_path.glob("*.md")):
        skill = parse_skill_file(path)
        skills[skill.name] = skill

    return skills


def expand_skill_invocation(text: str, skills: dict[str, Skill]) -> str:
    stripped = text.strip()

    if not stripped.startswith("/"):
        return text

    command, _, args = stripped[1:].partition(" ")

    skill = skills.get(command)
    if not skill:
        return text

    return (
        f"请根据下面的技能说明执行任务。\n\n"
        f"# Skill: {skill.name}\n\n"
        f"{skill.content}\n\n"
        f"# User Request\n\n"
        f"{args.strip()}"
    )