from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCANNER = ROOT / "nba2k_integrated_scanner.py"
GENERATED = ROOT / "claim_selectors.py"
NBA2KMOBILE = ROOT / "nba2kmobile.py"

START = "# --- AUTO-GENERATED SELECTORS START ---"
END = "# --- AUTO-GENERATED SELECTORS END ---"

candidates = [ROOT / "claimselectors.py", ROOT / "claim_selectors.py"]
generated_path = next((p for p in candidates if p.exists()), None)
if not generated_path:
    raise FileNotFoundError("Cannot find claimselectors.py / claim_selectors.py after scanner run")

generated_text = generated_path.read_text(encoding="utf-8")


def run_scanner() -> None:
    # Scanner prompts: "Enter choice 1 or 2 (default 2)".
    # Sending just newline picks default "2".
    subprocess.run(
        [sys.executable, str(SCANNER)],
        input="\n",
        text=True,
        cwd=str(ROOT),
        check=True,
    )


def extract_generated_block(text: str) -> str:
    lines = text.splitlines(True)
    for i, line in enumerate(lines):
        if line.lstrip().startswith("CLAIM_SELECTORS"):
            return "".join(lines[i:]).rstrip() + "\n"
    raise RuntimeError("Could not find 'CLAIM_SELECTORS' in claimselectors.py")


def patch_nba2kmobile(new_block: str) -> None:
    src = NBA2KMOBILE.read_text(encoding="utf-8")

    pattern = re.compile(
        re.escape(START) + r".*?" + re.escape(END),
        flags=re.DOTALL,
    )

    if not pattern.search(src):
        raise RuntimeError(
            "Markers not found. Add START/END markers around the selector block in nba2kmobile.py."
        )

    replacement = f"{START}\n{new_block}{END}"
    out = pattern.sub(replacement, src, count=1)
    NBA2KMOBILE.write_text(out, encoding="utf-8")


def main() -> None:
    run_scanner()
    generated_text = GENERATED.read_text(encoding="utf-8")
    new_block = extract_generated_block(generated_text)
    patch_nba2kmobile(new_block)


if __name__ == "__main__":
    main()
