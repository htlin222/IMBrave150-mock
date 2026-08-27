#!/usr/bin/env python3
"""Insert chapter markers into talk.cast at the moment each prompt was sent.

asciinema 2.4 has no way to drop a marker while recording unattended, but the
asciicast v2 format carries them as ordinary events — [time, "m", "label"] —
and asciinema-player renders them on the timeline and lets you jump between
them. record_cast.sh logs the wall-clock time of every prompt; this converts
those to offsets from the recording's start and splices them in.

Each marker is placed slightly BEFORE the prompt was submitted, so jumping to a
chapter shows the prompt being typed rather than starting mid-answer.

    python3 tools/add_markers.py            # cast/talk.cast + cast/chapters.tsv
"""
import csv
import json
import pathlib
import sys

LEAD_IN = 3.0          # seconds of run-up before each prompt

HERE = pathlib.Path(__file__).resolve().parent.parent
CAST = HERE / "cast" / "talk.cast"
CHAPTERS = HERE / "cast" / "chapters.tsv"


def main():
    if not CAST.exists():
        sys.exit(f"no recording at {CAST} — run tools/record_cast.sh first")
    if not CHAPTERS.exists():
        sys.exit(f"no chapter log at {CHAPTERS}")

    lines = CAST.read_text().splitlines()
    header = json.loads(lines[0])
    start = header.get("timestamp")
    if not start:
        sys.exit("cast header has no timestamp; cannot place markers")

    events = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        # Drop any markers from a previous run so this is idempotent.
        if len(ev) >= 2 and ev[1] == "m":
            continue
        events.append(ev)

    if not events:
        sys.exit("cast has no events")
    duration = events[-1][0]

    rows = list(csv.DictReader(CHAPTERS.read_text().splitlines(), delimiter="\t"))
    if not rows:
        sys.exit("chapter log is empty")

    # Wall-clock offset from the recording's start is exact, as long as the
    # -i idle cap did not actually remove time. It engages only during dead
    # air, and an agent session has very little, so check rather than assume:
    # if the last prompt's offset already exceeds the recording, idle capping
    # did bite and the offsets have to be scaled to fit instead.
    offsets = [int(r["epoch"]) - start for r in rows]
    if offsets[-1] >= duration:
        scale = (duration * 0.92) / offsets[-1]
        offsets = [o * scale for o in offsets]
        print(f"note: idle capping removed time; offsets scaled by {scale:.3f}")

    markers = [(max(0.0, o - LEAD_IN), f"{r['idx']}. {r['label']}")
               for r, o in zip(rows, offsets)]

    merged = [[t, "m", label] for t, label in markers] + events
    merged.sort(key=lambda ev: (ev[0], 0 if ev[1] == "m" else 1))

    out = [json.dumps(header, separators=(",", ":"))]
    out += [json.dumps(ev, separators=(",", ":")) for ev in merged]
    CAST.write_text("\n".join(out) + "\n")

    print(f"{CAST.name}: {len(markers)} markers over {duration:.0f}s")
    for t, label in markers:
        print(f"  {int(t)//60:02d}:{int(t)%60:02d}  {label}")


if __name__ == "__main__":
    main()
