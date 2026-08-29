#!/usr/bin/env bash
# Assemble the public site: the two recordings, the three PDFs, and a landing
# page. Everything is copied in, so the directory is self-contained and can be
# handed to `wrangler pages deploy` with no build step.
#
# The speaker script and notes are deliberately NOT published — they are the
# presenter's own lines, not part of the demo.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SITE="$HERE/site"

for f in "$HERE/cast/walk.html" "$HERE/cast/talk-full.html" \
         "$HERE/dist/imbrave150-deck.pdf" "$HERE/dist/imbrave150-deck-full.pdf" \
         "$HERE/dist/imbrave150-deck-backup.pdf"; do
  [ -s "$f" ] || { echo "missing: ${f#"$HERE"/}"; echo "run: make check && make cast-html"; exit 1; }
done

cp "$HERE/cast/walk.html"                 "$SITE/talk.html"
cp "$HERE/cast/talk-full.html"            "$SITE/talk-long.html"
cp "$HERE/dist/imbrave150-deck.pdf"       "$SITE/deck.pdf"
cp "$HERE/dist/imbrave150-deck-full.pdf"  "$SITE/deck-reference.pdf"
cp "$HERE/dist/imbrave150-deck-backup.pdf" "$SITE/deck-backup.pdf"

# Cloudflare Pages serves these at /talk and /talk-long and 308s the .html
# form, so index.html links the extensionless paths.
grep -q "talkpane" "$SITE/talk.html" || { echo "talk.html has no control bar"; exit 1; }
# The speaker notes are not linked from the landing page — public site, the
# presenter's own lines — but they are served, so they can be opened from a
# phone at the lectern.
python3 "$HERE/tools/build_notes.py"

grep -q 'href="talk"' "$SITE/index.html" || { echo "index.html links the .html form; Pages will redirect"; exit 1; }
echo "site assembled: $(du -sh "$SITE" | cut -f1)"
ls -1 "$SITE"
