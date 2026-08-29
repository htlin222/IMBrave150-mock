#!/usr/bin/env python3
"""Regenerate docs/FILE-TREE.md from `git ls-files` plus the notes below.

A tree written by hand goes stale the first time someone adds a file, and a
stale map of a repository is actively misleading. This one is generated from
what git actually tracks, and CI asserts it is current:

    python3 scripts/gen_file_tree.py --check

Add a file to the repository and this fails until you regenerate; add a file
without a NOTES entry and it appears unannotated, which is a visible nudge
rather than a hard error.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "FILE-TREE.md"

# Directories rendered as a single summary line. The alternative is 26 lines of
# `chNN.py` that say nothing a one-liner does not.
COLLAPSE = {
    "hospitals": "10 per-hospital exports · 1,800 patients in 3 EHR schemas · **the only input**",
    "live-demo/verify": "one acceptance script per chapter + `preflight.py`, `run_all.py`, `_common.py`",
    "live-demo/reference-run/results": "the eight result tables from the reference run",
    "claude-demo/figures": "figures embedded in the animated deck",
    "slides/img": "still frames from the recording, one per signpost",
    "slides/recordings": "the older per-segment MP4s, superseded by the `.cast`",
    "slides/talk": "presenterm decks shown between prompts in the long recording",
    "slides/walkthrough": "presenterm decks shown between prompts in the walkthrough",
}

NOTES: dict[str, str] = {
    # --- the study -------------------------------------------------------
    "README.md": "start here",
    "LICENSE": "MIT, plus the note that every dataset is synthetic",
    "CITATION.cff": "how to cite this repository",
    "CONTRIBUTING.md": "what a useful contribution looks like here",
    "CODE_OF_CONDUCT.md": "",
    "CLAUDE.md": "instructions for an agent opening this repo — the stage protocol",
    "Makefile": "`setup` · `data` · `analyze` · `figure`",
    "requirements.txt": "pinned hard; `lifelines==0.30.0` is load-bearing",
    "DATA_DICTIONARY.md": "every column of the randomised dataset: type, units, encoding",
    "MULTIHOSPITAL_PSM.md": "the real-world layer: what mess was injected, and why",
    "imbrave150_simulated.csv": "501 patients, randomised — teaching layer 1",
    "hospitals_meta.csv": "site catalogue: type, region, EHR vendor, size. **Not** in the patient files.",
    "search_seed.py": "how `SEED=48` was chosen",
    "generate_imbrave150.py": "the simulator for the randomised trial",
    "generate_multihospital.py": "confounds it, splits it into 10 sites, dialect-ises it",
    "harmonize_hospitals.py": "reference solution · 10 dialects → one table",
    "analyze_imbrave150.py": "reference solution · KM, log-rank, Cox (Python)",
    "analyze_imbrave150.R": "the same in R",
    "psm_imbrave150.py": "reference solution · matching, balance, matched survival",
    "psm_imbrave150.R": "the same in R",
    "robustness_multiverse.py": "reference solution · 120 specifications",
    "robustness_multiverse.png": "the specification curve",
    "tmle_demo.py": "reference solution · G-comp, IPTW, AIPW, TMLE vs the true DGP",
    ".gitignore": "ignores the sandbox, the credentials and everything regenerable",
    ".env.example": "template for Cloudflare credentials; the real `.env` is never committed",

    # --- docs ------------------------------------------------------------
    "docs/PROMPTS.md": "**the prompt list** — generated from the recorders",
    "docs/PIPELINE.md": "what consumes what, and what it produces",
    "docs/FILE-TREE.md": "this file",

    # --- the guided course ----------------------------------------------
    "live-demo/README.md": "**agent entry point** — pacing protocol, hard constraints, chapter index",
    "live-demo/RUNBOOK.md": "the presenter's runbook",
    "live-demo/00-setup.md": "Mission 0.1 — sandbox, and look at the raw files",
    "live-demo/01-aggregate.md": "1.1–1.3 — three dialects → 1,800 patients",
    "live-demo/02-deconfound.md": "2.1–2.4 — the unadjusted HR lies; matching fixes it",
    "live-demo/03-survival.md": "3.1–3.2 — Kaplan–Meier, log-rank, Cox, publishable curves",
    "live-demo/04-subgroup.md": "4.1–4.2 — forest plot: consistency, not winners",
    "live-demo/05-robustness.md": "5.1–5.3 — 120 analytic paths, then a different estimand",
    "live-demo/06-manuscript.md": "6.1–6.9 — Methods first, Title last, every citation Crossref-verified",
    "live-demo/07-review.md": "7.1–7.4 — four blind reviewers, then revise",
    "live-demo/08-release.md": "8.1–8.4 — pandoc/LaTeX → PDF, DOCX, preprint bundle",
    "live-demo/reference-run/README.md": "what one complete run produced, and how close yours should be",
    "live-demo/reference-run/MANIFEST.tsv": "every output file: bytes, shape, SHA-256",
    "live-demo/workspace/.gitignore": "the sandbox ignores itself — it starts empty on every clone",

    # --- the talk --------------------------------------------------------
    "slides/README.md": "how to build and present the deck",
    "slides/SCRIPT.md": "verbatim rehearsal script with stage directions",
    "slides/SPEAKER-NOTES.md": "the same, as notes",
    "slides/STRATEGY.md": "on-stage briefing: what is uncuttable, what to cut first",
    "slides/Makefile": "deck and recording targets",
    "slides/.marprc.yml": "Marp configuration",
    "slides/deck.md": "the 12-slide talk deck",
    "slides/deck-backup.md": "the same with recorded frames, for presenting without a browser",
    "slides/deck-full.md": "the 43-slide reference edition",
    "slides/theme.css": "`mono-academic` — monochrome, 18 px floor, Lucide icons",
    "slides/cast/walk.cast": "**the walkthrough recording** · 33 min · 22 chapters · 2.6 MB",
    "slides/cast/walk.html": "self-contained offline player for it",
    "slides/cast/talk-full.cast": "the 64-minute version with the methodology kept in",
    "slides/cast/talk-full.html": "its player",
    "slides/cast/talk.cast": "an earlier short take",
    "slides/cast/talk.html": "its player",
    "slides/cast/walk-markers.tsv": "chapter marks, written while recording",
    "slides/cast/talk-markers.tsv": "the same for the long version",
    "slides/cast/chapters.tsv": "chapter titles",
    "slides/cast/RUNNING-ORDER.md": "what happens when, minute by minute",
    "slides/site/index.html": "landing page; the rest of `site/` is assembled, not tracked",
    "slides/stage/README.md": "what to put in place before presenting",
    "slides/stage/manuscript.md": "**the manuscript the recorded run wrote**",
    "slides/stage/review_log.csv": "the four reviewers' findings and what was done about them",
    "slides/stage/stage.sh": "copies them into the workspace so Chapter 07 runs standalone",
    "slides/tools/record_walkthrough.sh": "**records the walkthrough** — the prompt list lives here",
    "slides/tools/record_talk.sh": "records the long version",
    "slides/tools/record_cast.sh": "the earlier five-prompt take",
    "slides/tools/record_segments.sh": "the per-segment recorder behind `slides/recordings/`",
    "slides/tools/add_markers.py": "splices chapter markers into a `.cast`",
    "slides/tools/trim_cast.py": "trims dead air off the front, shifting markers",
    "slides/tools/add_player_controls.py": "the projector UI: speed, chapters, click-to-pause, text zoom",
    "slides/tools/build_site.sh": "assembles `slides/site/`",
    "slides/tools/build_notes.py": "renders the script and strategy card into the site",
    "slides/tools/deploy_site.sh": "deploys to Cloudflare Pages",
    "slides/tools/check_overflow.py": "rasterises the PDFs and fails if a slide was clipped",
    "slides/tools/make_backup_deck.py": "builds the backup deck from stills",
    "slides/tools/script_timing.py": "measures how long the script takes to read aloud",

    # --- packaging -------------------------------------------------------
    "scripts/extract_prompts.py": "regenerates `docs/PROMPTS.md` from the recorders",
    "scripts/gen_file_tree.py": "regenerates `docs/FILE-TREE.md`",
    "scripts/make_reference_run.py": "snapshots a finished run into `live-demo/reference-run/`",
    "scripts/make-live-demo-bundle.sh": "the student download bundle",
    "scripts/make-slides-bundle.sh": "the offline presenter zip",
    "scripts/bundle-START-HERE.md": "the first thing in that bundle",

    # --- the animated deck ------------------------------------------------
    "claude-demo/index.html": "the animated HTML deck (predates the recording)",
    "claude-demo/README.md": "how to open and present it",
    "claude-demo/assets/deck.css": "its styling",
    "claude-demo/assets/deck.js": "slide navigation and animation",
    "claude-demo/assets/storyboard.js": "the six acts, as data",
    "claude-demo/assets/studio.css": "the presenter view",

    # --- infrastructure ---------------------------------------------------
    ".github/workflows/slides.yml": "rebuild the decks, verify, release on a tag",
    ".github/workflows/deploy-talk.yml": "deploy the talk site to Cloudflare Pages",
    ".github/workflows/deploy.yml": "deploy the animated deck",
    ".github/workflows/release-live-demo.yml": "package and release the course bundle",
    ".github/workflows/docs.yml": "assert the generated docs are current",
    ".github/ISSUE_TEMPLATE/reproduction-report.yml": "for a run whose numbers came out elsewhere",
    ".github/ISSUE_TEMPLATE/config.yml": "links shown above the issue form",
    ".claude/hooks/log-live-demo-read.sh": "logs which chapter the agent opened, and when",
}

# Directories that exist only after something runs. Tracked files cannot show
# them, and a map that omits them is not a map of the repository you will
# actually have on disk.
GENERATED = [
    ("live-demo/workspace/", "the sandbox the guided run writes into — **git-ignored, starts empty**"),
    ("live-demo/workspace/figures/", "KM curves, Love plot, PS overlap, forest, specification curve"),
    ("live-demo/workspace/manuscript/", "`manuscript.md`, `refs.bib`, `review_log.csv`"),
    ("live-demo/workspace/dist/", "the preprint PDF/DOCX from Chapter 08"),
    ("slides/dist/", "the built PDFs"),
    ("slides/site/", "the assembled site (only `index.html` is tracked)"),
    ("dist/", "the release zips"),
    (".venv/", "`make setup`"),
    ("imbrave150_pooled.csv", "`harmonize_hospitals.py`"),
    ("_answer_key_pooled.csv", "`generate_multihospital.py` — the truth, kept out of the way"),
    ("robustness_multiverse_results.csv", "`robustness_multiverse.py`"),
]


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout
    return sorted(line for line in out.splitlines() if line)


def build_tree(paths: list[str]) -> dict:
    root: dict = {}
    for p in paths:
        node = root
        parts = p.split("/")
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = None
    return root


def render(node: dict, prefix: str, path: str, lines: list[str]) -> None:
    items = sorted(node.items(), key=lambda kv: (kv[1] is None, kv[0].lower()))
    for i, (name, child) in enumerate(items):
        last = i == len(items) - 1
        stem = "└── " if last else "├── "
        here = f"{path}/{name}" if path else name

        if child is not None and here in COLLAPSE:
            n = count_files(child)
            lines.append(row(prefix + stem + name + "/",
                             f"{COLLAPSE[here]} ({n} files)"))
            continue

        label = name + "/" if child is not None else name
        lines.append(row(prefix + stem + label, NOTES.get(here, "")))
        if child is not None:
            render(child, prefix + ("    " if last else "│   "), here, lines)


WIDTH = 46


def row(tree: str, note: str) -> str:
    if not note:
        return f"| `{tree}` | |"
    return f"| `{tree}` | {note} |"


def count_files(node: dict) -> int:
    return sum(1 if v is None else count_files(v) for v in node.values())


HEADER = """<!-- GENERATED by scripts/gen_file_tree.py — do not edit by hand.
     The tree comes from `git ls-files`; the annotations from NOTES in that
     script. Add a file, then regenerate. -->

# File tree

Every tracked file, and what it is for. Generated from `git ls-files`, so it
cannot drift from the repository.

Three things live here at once — [the dataset](#the-study), [the guided
course](#the-guided-course), and [the talk](#the-talk) — and they are easier to
read separately than as one alphabetical list. The full tree is at the bottom.

## The study

The data and the reference implementations. This is the part you can use
without ever running an agent.

```
imbrave150_simulated.csv        501 patients, randomised          → teaching layer 1
hospitals/H01…H10.csv           1,800 patients, 3 EHR schemas     → teaching layer 2
hospitals_meta.csv              site catalogue — a separate file, on purpose
DATA_DICTIONARY.md              every column of layer 1
MULTIHOSPITAL_PSM.md            what mess layer 2 injects, and why
```

Generators run first, reference solutions run last; `make data && make analyze`
does both. See [`PIPELINE.md`](PIPELINE.md).

## The guided course

`live-demo/` — nine chapters, 32 missions, executed by an agent one at a time.
`README.md` there is the entry point and is written **for the agent**, not for
you. `verify/` holds the acceptance checks; `reference-run/` holds what a
finished run looked like; `workspace/` is the git-ignored sandbox.

## The talk

`slides/` — the recordings (`cast/`), the decks (`deck*.md` + `theme.css`), the
presenter's material (`SCRIPT.md`, `STRATEGY.md`) and the tooling that records,
builds and deploys all of it (`tools/`). `claude-demo/` is an older animated
deck telling the same story.

## Generated, not tracked

These appear once something runs. They are ignored by git, and listed here
because otherwise this map does not match the directory you are looking at.

"""

FOOTER = """
## Every tracked file

"""


def main() -> int:
    paths = tracked()
    lines: list[str] = []
    render(build_tree(paths), "", "", lines)

    gen = ["| Path | Produced by |", "|---|---|"]
    gen += [f"| `{p}` | {why} |" for p, why in GENERATED]

    body = [HEADER, "\n".join(gen), FOOTER,
            "| Path | What it is |", "|---|---|", "\n".join(lines),
            f"\n---\n\n{len(paths)} tracked files. "
            f"Regenerate with `python3 scripts/gen_file_tree.py`.\n"]
    text = "\n".join(body)

    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text() != text:
            print(f"{OUT.relative_to(ROOT)} is stale — run "
                  f"python3 scripts/gen_file_tree.py", file=sys.stderr)
            return 1
        print(f"{OUT.relative_to(ROOT)} is current")
        return 0

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(text)
    missing = [p for p in paths
               if p not in NOTES
               and not any(p.startswith(c + "/") for c in COLLAPSE)]
    print(f"wrote {OUT.relative_to(ROOT)} — {len(paths)} tracked files")
    if missing:
        print(f"  {len(missing)} without a note: {', '.join(missing[:8])}"
              f"{' …' if len(missing) > 8 else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
