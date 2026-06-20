from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: Path) -> None:
    print(f"\n> {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def main() -> int:
    run([sys.executable, "-m", "pytest", "-q"], ROOT / "backend")
    run([sys.executable, str(ROOT / "scripts" / "run_evaluation.py")], ROOT)
    print("\nBackend verification: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

