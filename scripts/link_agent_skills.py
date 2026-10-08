"""Make the runbooks in .agents/skills visible to tools that look elsewhere.

.agents/skills is the single source of truth. Some AI tools only discover
skills in their own directory, so this script links those directories to it.
Run it with `make agent-links`. Add a line to TOOL_DIRECTORIES for a new tool.

Where symbolic links are not available (Windows without Developer Mode) the
runbooks are copied instead; re-run the script after editing them.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".agents" / "skills"

TOOL_DIRECTORIES = [
    ROOT / ".claude" / "skills",  # Claude Code
]


def link(target: Path) -> str:
    if target.is_symlink():
        return "already linked"
    if target.exists():
        # A real folder, possibly holding tool-specific files: add to it, delete nothing.
        shutil.copytree(SOURCE, target, dirs_exist_ok=True)
        return "copied into the existing folder"

    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        target.symlink_to(Path("..") / ".agents" / "skills", target_is_directory=True)
    except OSError:
        shutil.copytree(SOURCE, target)
        return "copied (symbolic links are not available here)"
    return "linked"


def main() -> None:
    for target in TOOL_DIRECTORIES:
        print(f"{target.relative_to(ROOT)} -> .agents/skills: {link(target)}")


if __name__ == "__main__":
    main()
