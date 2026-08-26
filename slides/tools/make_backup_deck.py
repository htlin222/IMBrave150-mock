#!/usr/bin/env python3
"""Build deck-backup.md: the talk deck with a recorded frame after each signpost.

The talk runs a live agent session. When that will not cooperate — no network,
a rate limit, a wedged terminal — the presenter switches to this deck, which
carries a still frame from an actual recorded session at each of the five
signposts. The frames come from `slides/img/`, extracted from the VHS
recordings by `record_segments.sh`.

Do not hand-edit deck-backup.md; edit deck.md and rerun this.

    python3 tools/make_backup_deck.py
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent.parent

# Each signpost heading in deck.md, and what its recorded frame shows.
SEGMENTS = [
    ("## Ten Hospitals, Three Dialects",
     "Ten hospitals, three dialects",
     "It built the comparison table itself and found the trap: <strong>dialect B "
     "stores albumin in g/L and bilirubin in µmol/L</strong>."),
    ("## The Unadjusted Answer Is Lying",
     "The unadjusted answer",
     "<strong>HR 0.505</strong> — then the balance table. Every serious "
     "imbalance leans the same way, toward the treated arm."),
    ("## Make the Two Arms Comparable",
     "Matching, and what it costs",
     "<strong>706 pairs, 256 treated left unmatched.</strong> It separates the "
     "124 who could never match from the 132 caliper failures."),
    ("## Try to Break Your Own Result",
     "120 analytic paths",
     "It found its own outlier: the 0.822 run matches on a near-degenerate "
     "score that reuses one control <strong>212 times</strong>."),
    ("## Let It Review Its Own Manuscript",
     "Four reviewers, blind to each other",
     "<strong>Four background agents launched</strong> from one message, each "
     "reading the manuscript and the output files, none seeing the others."),
]


def main():
    deck = (HERE / "deck.md").read_text()
    missing = [img for i in range(1, len(SEGMENTS) + 1)
               if not (img := HERE / "img" / f"seg{i}.png").exists()]
    if missing:
        sys.exit("missing frames: " + ", ".join(str(m.name) for m in missing)
                 + "\n  run tools/record_segments.sh first")

    out, used = [], 0
    for slide in deck.split("\n---\n"):
        out.append(slide)
        for i, (heading, title, caption) in enumerate(SEGMENTS, start=1):
            if heading in slide:
                out.append(
                    f'\n<!-- _class: shot -->\n<!-- _footer: "" -->\n\n'
                    f'## <span class="tag">recorded</span>{title}\n\n'
                    f'![]({"img/seg%d.png" % i})\n\n'
                    f'<p class="caption">{caption}</p>\n')
                used += 1
                break

    if used != len(SEGMENTS):
        sys.exit(f"matched {used} of {len(SEGMENTS)} signposts in deck.md — "
                 "a heading was renamed; update SEGMENTS in this script")

    text = "\n---\n".join(out)
    text = text.replace('title: "Mission by Mission"',
                        'title: "Mission by Mission — Backup"', 1)
    text = text.replace(
        'description: "A live demonstration of driving an AI coding agent '
        'from ten messy hospital exports to an auditable result."',
        'description: "Backup edition: the talk with a still frame from a '
        'recorded agent session after each signpost."', 1)
    text = text.replace(
        '<p class="subtitle">Driving an AI coding agent, live — from ten messy '
        'hospital exports to a result you can audit.</p>',
        '<p class="subtitle">Driving an AI coding agent, live — from ten messy '
        'hospital exports to a result you can audit.'
        '<br><em>Backup edition: every step shown as recorded session.</em></p>',
        1)

    (HERE / "deck-backup.md").write_text(text)
    print(f"deck-backup.md: {len(text.split(chr(10) + '---' + chr(10)))} slides, "
          f"{used} recorded frames")


if __name__ == "__main__":
    main()
