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
  "$SLIDES/cast/talk-full.html"
  "$SLIDES/cast/talk-full.cast"
  "$SLIDES/cast/RUNNING-ORDER.md"
)
for f in "${REQUIRED[@]}"; do
  [ -s "$f" ] || { echo "missing or empty: ${f#"$ROOT"/}"; echo "run: cd slides && make check && make cast-html"; exit 1; }
done

mkdir -p "$STAGE" "$OUT"

# ---- 上台當天真的會用到的三樣 ----
cp "$SLIDES/cast/RUNNING-ORDER.md" "$STAGE/"
cp "$SLIDES/cast/talk-full.html"   "$STAGE/talk.html"
cp "$SLIDES/dist/imbrave150-deck.pdf"        "$STAGE/deck.pdf"
cp "$SLIDES/dist/imbrave150-deck-backup.pdf" "$STAGE/deck-backup.pdf"
cp "$SLIDES/dist/imbrave150-deck-full.pdf"   "$STAGE/deck-reference.pdf"

# ---- 來源，給想重建或引用的人 ----
mkdir -p "$STAGE/source"
cp "$SLIDES/cast/talk-full.cast"    "$STAGE/source/"
cp "$SLIDES/cast/talk-markers.tsv"  "$STAGE/source/"
[ -f "$SLIDES/cast/talk.html" ] && cp "$SLIDES/cast/talk.html" "$STAGE/source/talk-short.html"

cat > "$STAGE/START-HERE.md" <<'EOF'
# Mission by Mission — presenter bundle

Everything needed to give the talk, offline. No clone, no network, no toolchain.

| file | what it is |
|---|---|
| `RUNNING-ORDER.md` | **Read this first.** Three routes through the recording, and where to pause. |
| `talk.html` | The recording. Double-click it; any browser, no internet. 64 minutes, 30 markers. |
| `deck.pdf` | The 12-slide talk deck. |
| `deck-backup.pdf` | The same slides with a still frame from a recorded session after each signpost, for when a live demo will not cooperate. |
| `deck-reference.pdf` | The 43-slide reference edition, for handing out afterwards. |
| `source/` | The raw `.cast`, the marker log, and the short 8-minute recording. |

## On the day

1. Open `talk.html`. It plays offline.
2. Follow `RUNNING-ORDER.md`: play to a marker, pause, talk, carry on.
3. Markers are the dots on the progress bar — **click one to jump to it**.
   Clicking the terminal toggles play/pause. Bracket keys do not step between
   markers in this build, so use the mouse.

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
for f in START-HERE.md RUNNING-ORDER.md talk.html deck.pdf deck-backup.pdf deck-reference.pdf; do
  [ -s "$VERIFY/$NAME/$f" ] || { echo "bundle is missing $f"; exit 1; }
done
grep -q "asciinema" "$VERIFY/$NAME/talk.html" || { echo "talk.html has no player in it"; exit 1; }
/bin/rm -rf "$VERIFY" "$(dirname "$STAGE")"

echo "$ZIP"
du -h "$ZIP" | cut -f1
