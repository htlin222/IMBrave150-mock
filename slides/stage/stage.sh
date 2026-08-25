#!/usr/bin/env bash
# Put the pre-built manuscript where Mission 7.1 expects it, so the four
# reviewers on slide 9 can run without first running all of Chapter 06.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dest="$here/../../live-demo/workspace/manuscript"

mkdir -p "$dest"
cp "$here/manuscript.md" "$dest/manuscript.md"
echo "staged: $dest/manuscript.md"

if [ ! -f "$here/../../live-demo/workspace/pooled.csv" ]; then
  echo
  echo "note: live-demo/workspace/ has no pooled.csv, so the reviewers will not"
  echo "      be able to check the manuscript's numbers against source files."
  echo "      Run the pipeline first if you want that part of the demo to land."
fi
