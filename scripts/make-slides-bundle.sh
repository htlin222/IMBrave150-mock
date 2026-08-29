#!/usr/bin/env bash
# 把上台需要的東西打包成一個 zip：一份走位表、一個離線播放器、三份 PDF。
#
#   scripts/make-slides-bundle.sh [version]
#
# 產出 dist/imbrave150-slides-<version>.zip，解開後是 imbrave150-slides/。
# 講者在會場只需要這一包 —— 不需要 clone、不需要網路、不需要 node。
#
# 打包前會斷言 PDF 與播放器真的建好了，因為「zip 發出去才發現裡面是空的」
# 是這種包最常見也最難救的失敗。
set -euo pipefail

VERSION="${1:-dev}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="imbrave150-slides"
OUT="$ROOT/dist"
STAGE="$(mktemp -d)/$NAME"

SLIDES="$ROOT/slides"
REQUIRED=(
  "$SLIDES/dist/imbrave150-deck.pdf"
  "$SLIDES/dist/imbrave150-deck-backup.pdf"
  "$SLIDES/dist/imbrave150-deck-full.pdf"
  "$SLIDES/cast/walk.html"
  "$SLIDES/cast/walk.cast"
  "$SLIDES/SCRIPT.md"
  "$SLIDES/SPEAKER-NOTES.md"
)
for f in "${REQUIRED[@]}"; do
  [ -s "$f" ] || { echo "missing or empty: ${f#"$ROOT"/}"; echo "run: cd slides && make check && make cast-html"; exit 1; }
done

mkdir -p "$STAGE" "$OUT"

# ---- 上台當天真的會用到的三樣 ----
cp "$SLIDES/SCRIPT.md" "$SLIDES/STRATEGY.md" "$SLIDES/SPEAKER-NOTES.md" "$STAGE/"
cp "$SLIDES/cast/walk.html"   "$STAGE/talk.html"
cp "$SLIDES/dist/imbrave150-deck.pdf"        "$STAGE/deck.pdf"
cp "$SLIDES/dist/imbrave150-deck-backup.pdf" "$STAGE/deck-backup.pdf"
cp "$SLIDES/dist/imbrave150-deck-full.pdf"   "$STAGE/deck-reference.pdf"

# ---- 來源，給想重建或引用的人 ----
mkdir -p "$STAGE/source"
cp "$SLIDES/cast/walk.cast"         "$STAGE/source/"
cp "$SLIDES/cast/walk-markers.tsv"  "$STAGE/source/"
cp "$SLIDES/cast/RUNNING-ORDER.md"  "$STAGE/source/"
# The long version: the same study with the methodological arguments in it.
[ -f "$SLIDES/cast/talk-full.html" ] && cp "$SLIDES/cast/talk-full.html" "$STAGE/talk-long.html"

cat > "$STAGE/START-HERE.md" <<'EOF'
# Mission by Mission — presenter bundle

A talk about doing a whole study — ten messy hospital exports to a written-up
manuscript — by asking an AI agent in plain sentences, and checking everything
it hands back.

Everything needed to give it is in this folder. No clone, no network, no
toolchain: it runs on a borrowed laptop.

## On the day

1. **Rehearse from `SCRIPT.md`** (Chinese). It is verbatim, with stage
   directions, and it reads to length: 19-22 minutes of speaking plus the
   22-minute recording. `SPEAKER-NOTES.md` is the same talk as notes if you
   would rather not read from a script.
2. **Present the first five slides of `deck.pdf`** — about ten minutes. The
   fourth explains what a terminal is. Do not skip it if the room has never
   seen one.
3. **Open `talk.html` and play.** It opens at 1.5x, where the recording runs
   22 minutes. Stop five times, roughly a minute each, where the notes mark.
4. **Close on the last two slides of `deck.pdf`** — about ten minutes with
   discussion.

A 45-minute slot: 10 speaking, 25 playing and stopping, 10 closing.

## While it is playing

The bar across the top has speed (1x to 3x), a chapter dropdown, play/pause and
fullscreen. Three things are there for the room:

- **A chapter side pane** — the hamburger button, or `c`. All twenty-two
  chapters listed, the current one highlighted, click to jump. The page shifts
  left so it never covers the terminal. Use `f` for fullscreen: that expands the
  whole page, so the pane survives it. The player's own fullscreen button
  expands only the terminal.
- **Click anywhere to pause.** No hunting for a button.
- **Select terminal text, then the enlarge button.** A popover appears above the
  selection and the chosen lines fill the window at the largest size that fits.
  `Esc` or the close button returns. This is for the back row.

Drop to 1x for anything you want the room to read; push to 2x through the parts
where the agent is thinking rather than printing.

If someone asks something the walkthrough does not cover — how the matching
works, what happens when a prompt is ambiguous, the 120 analytic paths, the
four reviewers — `talk-long.html` is the hour-long version with all of it in.

If the browser fails, `deck-backup.pdf` carries a still frame from the
recording after each signpost, so you can finish from the PDF.

## The files

| file | what it is |
|---|---|
| `STRATEGY.md` | **Read this last, three minutes before going on.** What to cut, what never to cut, how to read the room, what to say when challenged. |
| `SCRIPT.md` | **The rehearsal script.** Every word you say, in Chinese, with stage directions — （停頓）, （慢）, where to press play. Reading it aloud takes about as long as the talk. |
| `SPEAKER-NOTES.md` | The same talk as notes rather than verbatim, if you would rather not read from a script. |
| `talk.html` | The recording. 32:55, or 22 minutes at the default 1.5x. Double-click it; any browser, no internet. |
| `deck.pdf` | The slides you present around it. |
| `talk-long.html` | The hour-long version, with the methodological arguments in it. For questions, and for handing out. |
| `deck-backup.pdf` | The same slides with a still frame from a recorded session after each signpost, for when the browser will not cooperate. |
| `deck-reference.pdf` | The 43-slide reference edition, for handing out afterwards. |
| `source/` | The raw `.cast`, the marker log, and the running order for the long version. |

## Everything on screen is synthetic

The cohort is simulated from the published summaries of a phase 3 trial. No
real patient is represented, and nothing in the talk is evidence about
atezolizumab, bevacizumab or sorafenib.

Source, and the mission-by-mission guide the recording follows:
https://github.com/htlin222/IMBrave150-mock
EOF

ZIP="$OUT/$NAME-$VERSION.zip"
/bin/rm -f "$ZIP"
( cd "$(dirname "$STAGE")" && zip -qr "$ZIP" "$NAME" -x '*.DS_Store' )

# 從解開後的成品再驗一次：講者拿到的東西真的不是空的。
VERIFY="$(mktemp -d)"
unzip -q "$ZIP" -d "$VERIFY"
for f in START-HERE.md SCRIPT.md SPEAKER-NOTES.md talk.html deck.pdf deck-backup.pdf deck-reference.pdf; do
  [ -s "$VERIFY/$NAME/$f" ] || { echo "bundle is missing $f"; exit 1; }
done
grep -q "asciinema" "$VERIFY/$NAME/talk.html" || { echo "talk.html has no player in it"; exit 1; }
# The speed buttons and chapter dropdown are injected after the player is
# generated, so a page can look complete and still have no way to change speed.
grep -q 'id="talkbar"' "$VERIFY/$NAME/talk.html" || { echo "talk.html has no control bar; run: cd slides && make cast-html"; exit 1; }
/bin/rm -rf "$VERIFY" "$(dirname "$STAGE")"

echo "$ZIP"
du -h "$ZIP" | cut -f1
