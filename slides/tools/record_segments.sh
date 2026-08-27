#!/usr/bin/env bash
# Record the five demo segments as real Claude Code sessions, then extract one
# still frame from each into slides/img/ for deck-backup.md.
#
# Requires: vhs, ffmpeg (brew install vhs ffmpeg) and the agent-demo-recorder
# skill for its Stop hook, which prints the sentinel VHS waits on.
#
# Three things this script encodes, each of which cost an hour to find:
#
#  1. RECORD ONE SEGMENT AT A TIME. Four concurrent runs drove load average
#     past 70, and Claude Code's startup then took longer than the tape's
#     startup wait, so every tape died on `Wait+Screen /shift\+tab/` with the
#     command typed but no TUI on screen. It is starvation, not a port clash:
#     VHS gives each of its ttyd instances a random port, so they do not
#     collide. Raising the wait would let you parallelise, but four nested
#     agents on one laptop is slower end to end than four in sequence.
#
#  2. USE AN ABSOLUTE PATH TO claude. Inside tmux/ttyd, PATH may resolve to an
#     older Homebrew build, which gets SIGKILLed in a nested session.
#
#  3. DISMISS THE FIRST-RUN DIALOGS FIRST. A fresh install shows "Try the new
#     fullscreen renderer?", which blocks the composer footer that VHS waits
#     on, so the tape hangs until timeout with no useful error. Launch claude
#     once by hand and answer it before recording.
#
# Each segment gets its own directory, seeded with the artefacts its prompt
# needs, so the numbers on screen match the numbers on the slides.
set -euo pipefail

CLAUDE_BIN=${CLAUDE_BIN:-$HOME/.local/bin/claude}
SKILL=${SKILL:-$HOME/.claude/skills/agent-demo-recorder}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
WS="$REPO/live-demo/workspace"
WORK=${WORK:-${TMPDIR:-/tmp}/imbrave150-recordings}

[ -x "$CLAUDE_BIN" ] || { echo "no claude at $CLAUDE_BIN (set CLAUDE_BIN)"; exit 1; }
[ -d "$SKILL" ] || { echo "no agent-demo-recorder skill at $SKILL"; exit 1; }
[ -f "$WS/pooled.csv" ] || { echo "run the live-demo pipeline first: $WS/pooled.csv is missing"; exit 1; }

mkdir -p "$WORK" "$HERE/img"

seed() {           # seed <segdir> <file>...
  local d="$1"; shift
  mkdir -p "$d/.claude"
  cp "$SKILL/assets/settings.json" "$d/.claude/"
  sed -i '' -e "s|REPLACE_WITH_ABSOLUTE_PATH_TO/vhs_stop_hook.sh|$SKILL/scripts/vhs_stop_hook.sh|" \
    "$d/.claude/settings.json" 2>/dev/null || \
  sed -i -e "s|REPLACE_WITH_ABSOLUTE_PATH_TO/vhs_stop_hook.sh|$SKILL/scripts/vhs_stop_hook.sh|" \
    "$d/.claude/settings.json"
  cat > "$d/CLAUDE.md" <<EOF
# Working rules

- Python is \`$REPO/.venv/bin/python\`. It has pandas, numpy, lifelines and
  matplotlib. There is no sklearn and no statsmodels — write logistic
  regression yourself with numpy if you need it.
- Work in this directory. Write scripts as files here, then run them.
- Keep terminal output short: this session is being projected. Print the
  numbers that matter, not whole dataframes.
- Answer in English.
EOF
  for f in "$@"; do cp "$f" "$d/"; done
}

tape() {           # tape <segdir> <name> <prompt>
  local d="$1" name="$2" prompt="$3"
  python3 "$SKILL/scripts/gen_tape.py" --agent claude --format mp4 \
    --font-size 20 --word-delay 120 --read-pause 2 \
    -o "$d/$name.tape" "$prompt"
  # gen_tape.py types the bare agent name and assumes chat-length turns.
  perl -pi -e "s|Type \"claude\"|Type \"$CLAUDE_BIN\"|" "$d/$name.tape"
  perl -pi -e 's|Wait\+Screen\@60s|Wait+Screen\@180s|' "$d/$name.tape"
  perl -pi -e 's|Wait\+Screen\@120s|Wait+Screen\@900s|' "$d/$name.tape"
  perl -pi -e "s|Output claude-demo\.mp4|Output $name.mp4|" "$d/$name.tape"
}

record() {         # record <segdir> <name>
  local d="$1" name="$2"
  echo "=== $name  start $(date +%H:%M:%S)"
  ( cd "$d" && vhs "$name.tape" > vhs.log 2>&1 ) || true
  pkill -f ttyd 2>/dev/null || true
  if [ -s "$d/$name.mp4" ]; then
    echo "=== $name  ok  $(du -h "$d/$name.mp4" | cut -f1)  $(date +%H:%M:%S)"
  else
    echo "=== $name  FAILED"; tail -3 "$d/vhs.log"; return 1
  fi
}

# Seconds-from-end to grab the still from. The tape holds 5s on the finished
# response then exits, but the useful frame differs per segment: segment 5 ends
# while its four subagents are still running, and the frame that shows all four
# launched sits nearer the end than the others.
frame_offset() { case "$1" in 5) echo 2 ;; *) echo 5 ;; esac; }

frame() {          # frame <segdir> <name> <index> [seconds-from-end]
  local d="$1" name="$2" i="$3"
  local off="${4:-$(frame_offset "$i")}"
  ffmpeg -v error -sseof "-$off" -i "$d/$name.mp4" -frames:v 1 -y "$HERE/img/seg$i.png"
  echo "-> img/seg$i.png"
}

P1="Group the ten files in hospitals/ by their column fingerprint, not by filename. Report the actual values with unique(). Then convert all of them to one schema with fixed names and units, and never drop a row for missingness. Attach each hospital's type and region from hospitals_meta.csv. Write pooled.csv and print the row count, the counts per dialect, and the albumin and bilirubin medians."
P2="pooled.csv already has the ten hospitals merged. Fit a Cox model on treatment alone, nothing else. Write naive_hr.json with hr, ci_low and ci_high. Then compute the standardised mean difference between the two arms for age, ecog_ps, child_pugh_score, afp_ge_400, macrovascular_invasion, extrahepatic_spread, BCLC stage C, ALBI grade 2 or above, varices, male sex, and Asia region. Tell me in one sentence what you would conclude from the hazard ratio by itself, and then what the balance table does to that conclusion."
# "Sort treated by the score" is not enough: an agent given that will pick
# descending and return 765 pairs / 20.5% unmatched instead of 706 / 26.6%.
# Greedy matching is order-dependent, so the direction has to be stated.
P3="Using pooled.csv, estimate a propensity score by logistic regression on age, ecog_ps, child_pugh_score, afp_ge_400, macrovascular_invasion, extrahepatic_spread, BCLC stage C, ALBI grade 2 or above, varices, male sex and Asia region. Match 1:1 nearest neighbour without replacement, caliper 0.2 times the SD of the logit propensity score. Take the treated in ascending score order. Do not force a match outside the caliper. Report how many treated were left unmatched, the balance after matching, and then the Cox hazard ratio for overall survival in the matched cohort."
P4="Using pooled.csv, hold the data completely fixed and vary only the analytic choices. Build 15 covariate sets: the full 11, each of the 11 leave-one-out sets, and three smaller clinical sets. Cross those with 8 adjustment methods: multivariable Cox, stabilised IPTW, and propensity matching at calipers 0.1, 0.2 and 0.5 in both 1:1 and 1:2. That is 120 runs. Report the median, the IQR, the full range, and what fraction lands outside 0.55 to 0.61."
# Ask the reviewers to be brief. Four full manuscript reviews inside a nested
# session ran past two hours; the picture the slide needs is four agents open at
# once, not four complete reports.
P5="Open four review subagents in parallel in one single message: statistical, clinical, reporting-standards, reproducibility. Each may read manuscript.md and the csv and json files here, and nothing else. Tell each one to be brief: a one-line recommendation and its three strongest major comments as one line each, nothing more. When they return, print a four-row table of reviewer, recommendation, and its single most damaging finding."

only="${1:-all}"

run_one() {        # run_one <index>
  local i="$1"
  local d="$WORK/seg$i"
  rm -rf "$d"; mkdir -p "$d"
  case "$i" in
    1) seed "$d" "$REPO/hospitals_meta.csv"; cp -R "$REPO/hospitals" "$d/hospitals"
       rm -f "$d/hospitals/.DS_Store"; tape "$d" "seg1" "$P1" ;;
    2) seed "$d" "$WS/pooled.csv"; tape "$d" "seg2" "$P2" ;;
    3) seed "$d" "$WS/pooled.csv"; tape "$d" "seg3" "$P3" ;;
    4) seed "$d" "$WS/pooled.csv"; tape "$d" "seg4" "$P4" ;;
    5) seed "$d" "$WS/manuscript/manuscript.md" "$WS/pooled.csv" "$WS/matched.csv" \
            "$WS/balance.csv" "$WS/naive_hr.json" "$WS/km_summary.json" \
            "$WS/subgroups.csv" "$WS/multiverse.csv" "$WS/tmle.json" \
            "$WS/baseline_table1.csv" "$WS/site_profile.csv"
       tape "$d" "seg5" "$P5" ;;
  esac
  record "$d" "seg$i" && frame "$d" "seg$i" "$i"
}

if [ "$only" = "all" ]; then
  for i in 1 2 3 4 5; do run_one "$i"; done
else
  run_one "$only"
fi

echo "=== done $(date +%H:%M:%S). Now: python3 tools/make_backup_deck.py && make check"
