#!/usr/bin/env python3
"""Copy only the distributable skill into an explicitly selected skills directory."""
import argparse
from pathlib import Path
import shutil


def install(source, skills_dir):
    dest = skills_dir.expanduser().resolve() / "video-vision-summary"
    if dest.exists() or dest.is_symlink():
        raise FileExistsError(f"已存在：{dest}。请先自行备份并选择新的安装位置。")
    dest.mkdir(parents=True)
    for name in ("SKILL.md", "LICENSE"):
        shutil.copyfile(source / name, dest / name)
    for name in ("scripts", "references"):
        shutil.copytree(source / name, dest / name,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return dest


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--skills-dir", required=True, type=Path, help="例如 ~/.agents/skills 或 ~/.claude/skills")
    args = p.parse_args()
    try:
        print("已安装：" + str(install(Path(__file__).resolve().parents[1], args.skills_dir)))
    except (OSError, ValueError) as exc:
        p.exit(1, str(exc) + "\n")
