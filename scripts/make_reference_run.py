#!/usr/bin/env python3
"""Snapshot live-demo/workspace/ into live-demo/reference-run/.

`live-demo/workspace/` is git-ignored on purpose: it is the sandbox the demo
writes into, and it must start empty on every clone. That leaves a reader with
no way to tell whether their own run went somewhere sensible. This script
copies the small result tables out of a finished run, plus a manifest of
everything else (size, checksum, shape), so a later run can be diffed against
a known-good one.

Run it after a full pass of Chapters 00-07:

    python3 scripts/make_reference_run.py

It refuses to overwrite the snapshot from an incomplete run.
"""
from __future__ import annotations

import csv
import hashlib
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WS = ROOT / "live-demo" / "workspace"
OUT = ROOT / "live-demo" / "reference-run"

# Small enough to commit, and these are the numbers anyone would want to
# compare against. pooled.csv and matched.csv are deliberately not copied:
# they are ~280 KB each and fully determined by the committed inputs, so the
# manifest's checksum is the useful part.
COPY = [
    "naive_hr.json",
    "km_summary.json",
    "tmle.json",
    "balance.csv",
    "baseline_table1.csv",
    "site_profile.csv",
    "subgroups.csv",
    "multiverse.csv",
]

# Without these the run did not finish, and a half-run snapshot is worse than
# none — it looks authoritative and is not.
REQUIRED = ["pooled.csv", "matched.csv", "km_summary.json", "tmle.json"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def shape(p: Path) -> str:
    """rows x cols for a CSV, blank for anything else."""
    if p.suffix != ".csv":
        return ""
    with p.open(newline="") as fh:
        rows = list(csv.reader(fh))
    return f"{len(rows) - 1}x{len(rows[0])}" if rows else ""


def walk() -> list[Path]:
    skip = {"__pycache__", ".git"}
    return sorted(
        p for p in WS.rglob("*")
        if p.is_file()
        and not any(part in skip for part in p.parts)
        and p.name not in {".gitignore", ".DS_Store"}
    )


def main() -> int:
    if not WS.exists():
        print("no live-demo/workspace — nothing to snapshot", file=sys.stderr)
        return 1
    missing = [f for f in REQUIRED if not (WS / f).exists()]
    if missing:
        print(f"workspace looks incomplete, missing: {', '.join(missing)}",
              file=sys.stderr)
        return 1

    (OUT / "results").mkdir(parents=True, exist_ok=True)
    for name in COPY:
        src = WS / name
        if src.exists():
            shutil.copy2(src, OUT / "results" / Path(name).name)
        else:
            print(f"  note: {name} not in the workspace, skipped")

    files = walk()
    with (OUT / "MANIFEST.tsv").open("w", newline="") as fh:
        # lineterminator: csv defaults to CRLF, which turns every checksum
        # in this file into "<sha>\r" for anyone comparing with shell tools.
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["path", "bytes", "shape", "sha256"])
        for p in files:
            w.writerow([p.relative_to(WS).as_posix(), p.stat().st_size,
                        shape(p), sha256(p)])

    total = sum(p.stat().st_size for p in files)
    print(f"snapshotted {len(files)} files ({total // 1024} KB) "
          f"-> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
