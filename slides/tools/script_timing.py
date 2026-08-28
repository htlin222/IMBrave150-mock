#!/usr/bin/env python3
"""Estimate how long SCRIPT.md takes to deliver.

Counts the words actually spoken — stage directions in （）, headings and
checklists are not — and adds the pauses those directions ask for. Reports a
range, because delivery rate is personal: 170 characters a minute is a careful
report to seniors, 200 is a brisk one.

    python3 tools/script_timing.py            # the whole thing
    python3 tools/script_timing.py --sections # per section
"""
import pathlib
import re
import sys

SLOW, FAST = 170, 200          # spoken Chinese characters per minute
PAUSE = {"停頓兩秒": 2.0, "停頓": 1.5, "停一下": 1.0, "停住": 2.0, "停": 1.0}

HERE = pathlib.Path(__file__).resolve().parent.parent


def measure(text):
    directions = re.findall(r"（([^）]*)）", text)
    silence = 0.0
    for d in directions:
        for key, secs in PAUSE.items():        # longest key first
            if key in d:
                silence += secs
                break
    spoken = re.sub(r"（[^）]*）", "", text)
    spoken = re.sub(r"^#.*$", "", spoken, flags=re.M)
    spoken = re.sub(r"^\s*[-*|].*$", "", spoken, flags=re.M)
    han = len(re.findall(r"[\u4e00-\u9fff]", spoken))
    return han, silence, len(directions)


def fmt(m):
    return f"{int(m)}:{int(round((m - int(m)) * 60)):02d}"


def main():
    path = HERE / "SCRIPT.md"
    if not path.exists():
        sys.exit(f"no script at {path}")
    text = path.read_text()

    # Sections headed 可選 or 備用 are not in the running order — they are
    # played only if there is time or a question asks for them — so counting
    # them would overstate the talk.
    main, optional = [], 0
    for block in re.split(r"(?m)^(?=# )", text):
        head = block.split("\n", 1)[0]
        if re.match(r"#\s*(可選|備用)", head):
            optional += 1
            continue
        main.append(block)
    text = "".join(main)

    # Everything before the first slide heading is a note to the presenter —
    # timings, how to use the file — not lines to be spoken.
    first = text.find("\n## ")
    if first != -1:
        text = text[first:]

    if "--sections" in sys.argv:
        parts = re.split(r"^## ", text, flags=re.M)[1:]
        print(f"{'section':38} {'chars':>6} {'pause':>7} {'slow':>7} {'fast':>7}")
        for p in parts:
            title = p.split("\n", 1)[0].strip()
            han, sil, _ = measure(p)
            lo = han / SLOW + sil / 60
            hi = han / FAST + sil / 60
            print(f"{title[:38]:38} {han:>6} {sil:>6.0f}s {fmt(lo):>7} {fmt(hi):>7}")
        print()

    han, sil, n = measure(text)
    lo, hi = han / SLOW + sil / 60, han / FAST + sil / 60
    if optional:
        print(f"(excluding {optional} optional section(s) not in the running order)")
    print(f"spoken characters : {han}")
    print(f"stage directions  : {n}, asking for {sil:.0f}s of silence")
    print(f"delivery          : {fmt(hi)} brisk  \u2013  {fmt(lo)} careful")
    print(f"plus 22:00 of recording  \u2192  "
          f"{fmt(hi + 22)} \u2013 {fmt(lo + 22)} total")


if __name__ == "__main__":
    main()
