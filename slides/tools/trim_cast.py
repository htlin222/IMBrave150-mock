#!/usr/bin/env python3
"""Trim dead air off the front of a .cast, shifting markers with it.

A recording made by attaching to tmux opens on whatever the shell was showing —
here, the agent's splash screen and the command that launches the slides. The
talk should open on the first slide instead.

Cutting is safe only where the terminal is about to be repainted in full, which
is what `clear` plus a full-screen program does. The new first event is prefixed
with a clear-and-home sequence so the trimmed recording starts from a known
blank screen rather than inheriting state from the events that were dropped.

    python3 tools/trim_cast.py cast/talk-full.cast 6.2
    python3 tools/trim_cast.py cast/talk-full.cast --at-marker 1
"""
import json
import pathlib
import sys

CLEAR = "\x1b[H\x1b[2J\x1b[3J"


def main():
    args = list(sys.argv[1:])
    if not args:
        sys.exit(__doc__)
    path = pathlib.Path(args[0])
    if not path.exists():
        sys.exit(f"no recording at {path}")

    lines = path.read_text().splitlines()
    header = json.loads(lines[0])
    events = []
    for line in lines[1:]:
        line = line.strip()
        if line:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    if not events:
        sys.exit("no events")

    if "--at-marker" in args:
        n = int(args[args.index("--at-marker") + 1])
        marks = [e[0] for e in events if e[1] == "m"]
        if n < 1 or n > len(marks):
            sys.exit(f"marker {n} out of range (1..{len(marks)})")
        cut = marks[n - 1]
    else:
        cut = float(args[1])

    kept = [e for e in events if e[0] >= cut]
    if not kept:
        sys.exit(f"cutting at {cut}s would leave nothing")

    # A marker that names the section being cut into still belongs to the
    # recording — dropping it would silently lose a chapter — so carry the last
    # one from before the cut over to the very start.
    before = [e for e in events if e[0] < cut and e[1] == "m"]
    if before and not (kept and kept[0][1] == "m" and kept[0][0] <= cut + 0.01):
        kept = [[cut, "m", before[-1][2]]] + kept

    dropped = len(events) - len(kept)

    shifted = []
    for e in kept:
        e = list(e)
        e[0] = round(e[0] - cut, 6)
        shifted.append(e)

    # Start from a known blank screen: the dropped events set up state this one
    # no longer inherits.
    first_out = next((i for i, e in enumerate(shifted) if e[1] == "o"), None)
    if first_out is not None:
        shifted[first_out][2] = CLEAR + shifted[first_out][2]

    out = [json.dumps(header, separators=(",", ":"))]
    out += [json.dumps(e, separators=(",", ":")) for e in shifted]
    path.write_text("\n".join(out) + "\n")

    d = shifted[-1][0]
    print(f"{path.name}: cut {cut:.1f}s off the front "
          f"({dropped} events), now {int(d)//60}:{int(d)%60:02d}, "
          f"{sum(1 for e in shifted if e[1] == 'm')} markers")


if __name__ == "__main__":
    main()
