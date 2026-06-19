#!/usr/bin/env python3
"""Package a skill directory as a .skill archive for release uploads."""

import argparse
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SKILL_DIR = REPO_ROOT / "skills" / "llm-gtd"
DEFAULT_OUTPUT = REPO_ROOT / "dist" / "llm-gtd.skill"


def package_skill(skill_dir: Path = DEFAULT_SKILL_DIR, output: Path = DEFAULT_OUTPUT) -> Path:
    skill_dir = skill_dir.resolve()
    output = output.resolve()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        raise FileNotFoundError(f"Missing SKILL.md: {skill_md}")

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(skill_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(skill_dir.parent))

    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Package llm-gtd setup skill")
    parser.add_argument("--skill-dir", type=Path, default=DEFAULT_SKILL_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    output = package_skill(args.skill_dir, args.output)
    print(f"Created {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
