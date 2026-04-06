from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_PYTHON_VERSION = "3.13"


def discover_projects() -> list[Path]:
    return sorted(path.parent for path in ROOT.glob("lesson*/pyproject.toml"))


def run_command(command: list[str], cwd: Path) -> None:
    location = cwd.relative_to(ROOT)
    print(f"[bootstrap] {location}: {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap UV environments for one or more lesson projects.",
    )
    parser.add_argument(
        "lessons",
        nargs="*",
        help="Lesson directories to bootstrap. Defaults to all Python lessons.",
    )
    parser.add_argument(
        "--python-version",
        default=DEFAULT_PYTHON_VERSION,
        help="Python version passed to UV during environment creation.",
    )
    parser.add_argument(
        "--skip-python-install",
        action="store_true",
        help="Skip `uv python install` before syncing lesson environments.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List bootstrap-enabled lesson directories and exit.",
    )
    return parser.parse_args()


def main() -> int:
    if shutil.which("uv") is None:
        raise SystemExit("UV is required but was not found in PATH.")

    args = parse_args()
    available_projects = {project.name: project for project in discover_projects()}

    if args.list:
        for name in available_projects:
            print(name)
        return 0

    if not available_projects:
        raise SystemExit("No lesson pyproject.toml files were found.")

    requested_lessons = args.lessons or list(available_projects)
    invalid_lessons = [lesson for lesson in requested_lessons if lesson not in available_projects]
    if invalid_lessons:
        available = ", ".join(sorted(available_projects))
        invalid = ", ".join(invalid_lessons)
        raise SystemExit(f"Unknown lesson(s): {invalid}. Available lessons: {available}")

    if not args.skip_python_install:
        run_command(["uv", "python", "install", args.python_version], ROOT)

    for lesson in requested_lessons:
        run_command(["uv", "sync", "--python", args.python_version], available_projects[lesson])

    print(f"[bootstrap] Bootstrapped {len(requested_lessons)} lesson(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())