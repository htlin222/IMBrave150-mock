#!/usr/bin/env python3
"""Insert chapter markers into a .cast at the moments the recorder logged.

asciinema 2.4 cannot drop a marker while recording unattended, but the
asciicast v2 format carries them as ordinary events — [time, "m", "label"] —
and asciinema-player draws them on the timeline and jumps between them. The
recorder logs a wall-clock epoch every time it puts a slide up, runs a command
on screen, or submits a prompt; this converts those to offsets and splices them
in.

Markers sit slightly BEFORE the logged moment, so jumping to one shows the
prompt being typed rather than starting mid-answer.

    python3 tools/add_markers.py                       # the full talk
    python3 tools/add_markers.py talk.cast chapters.tsv # anything else
"""
import csv
import json
import pathlib
import sys

LEAD_IN = 3.0
GLYPH = {"slide": "▮", "shell": "$", "prompt": "▸"}

HERE = pathlib.Path(__file__).resolve().parent.parent


def load(cast_path):
    lines = cast_path.read_text().splitlines()
    header = json.loads(lines[0])
    events = []
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if len(ev) >= 2 and ev[1] == "m":   # drop old markers: stay idempotent
            continue
        events.append(ev)
    return header, events


def main():
    cast = HERE / "cast" / (sys.argv[1] if len(sys.argv) > 1 else "talk-full.cast")
    log = HERE / "cast" / (sys.argv[2] if len(sys.argv) > 2 else "talk-markers.tsv")
    if not cast.exists():
        sys.exit(f"no recording at {cast}")
    if not log.exists():
        sys.exit(f"no marker log at {log}")

    header, events = load(cast)
    start = header.get("timestamp")
    if not start:
        sys.exit("cast header has no timestamp; cannot place markers")
    if not events:
        sys.exit("cast has no events")
    duration = events[-1][0]

    rows = list(csv.DictReader(log.read_text().splitlines(), delimiter="\t"))
    if not rows:
        sys.exit("marker log is empty")

    # Offset from the recording's start is exact as long as the -i idle cap did
    # not actually remove time. It only bites during dead air, of which an agent
    # session has little — but check rather than assume, and scale to fit if it
    # did.
    offsets = [int(r["epoch"]) - start for r in rows]
    if offsets[-1] >= duration:
        scale = (duration * 0.97) / offsets[-1]
        offsets = [o * scale for o in offsets]
        print(f"note: idle capping removed time; offsets scaled by {scale:.3f}")

    markers = []
    for r, o in zip(rows, offsets):
        kind = r.get("kind", "prompt")
        label = f"{GLYPH.get(kind, '·')} {r['label']}"
        markers.append((max(0.0, o - LEAD_IN), label))

    merged = [[t, "m", label] for t, label in markers] + events
    merged.sort(key=lambda ev: (ev[0], 0 if ev[1] == "m" else 1))

    out = [json.dumps(header, separators=(",", ":"))]
    out += [json.dumps(ev, separators=(",", ":")) for ev in merged]
    cast.write_text("\n".join(out) + "\n")

    print(f"{cast.name}: {len(markers)} markers over "
          f"{int(duration)//60}:{int(duration)%60:02d}")
    for t, label in markers:
        print(f"  {int(t)//60:>3}:{int(t)%60:02d}  {label}")


if __name__ == "__main__":
    main()
