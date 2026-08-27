#!/usr/bin/env bash
# Record the whole talk as ONE asciinema session: prompt, wait, prompt, wait.
#
# Produces
#   slides/cast/talk.cast      the recording (terminal text, not video)
#   slides/cast/chapters.tsv   when each prompt was submitted
#
# Why a .cast and not a video: it is a JSONL stream of terminal output, so it
# is far smaller than an MP4, the text stays real text (selectable, copyable in
# asciinema-player), and markers let you jump straight to any prompt instead of
# scrubbing.
#
# The terminal is deliberately NARROW (105 columns). The player scales the grid
# to the container, so fewer columns means bigger glyphs on a projector.
#
# Lessons already paid for, do not undo:
#   - `claude` must be an absolute path: inside tmux, PATH may resolve to an
#     older build that gets SIGKILLed when nested.
#   - Dismiss first-run dialogs by hand before recording ("Try the new
#     fullscreen renderer?" hides the composer and the wait never matches).
#   - Send the prompt text and Enter as two separate send-keys about a second
#     apart, or the composer treats the burst as a paste and drops the submit.
#   - Run on a DEDICATED tmux socket (-L). A long-lived tmux server hands the
#     nested session the environment it was started with, which can be months
#     old; the symptom is "Login expired - Please run /login" inside the TUI
#     while `claude -p` works fine from the same shell. A fresh server on its
#     own socket picks up the current environment and leaves existing sessions
#     alone.
set -uo pipefail

CLAUDE_BIN=${CLAUDE_BIN:-$HOME/.local/bin/claude}
SESSION=${SESSION:-imbrave-cast}
SOCKET=${SOCKET:-imbrave}   # dedicated tmux server; see note above
COLS=${COLS:-105}
ROWS=${ROWS:-30}
IDLE=${IDLE:-2}          # cap dead air at 2s so a 40-min run plays in ~10
D=${D:-${TMPDIR:-/tmp}/imbrave150-cast}
OUT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/cast"

mkdir -p "$OUT"
rm -f "$D/talk.cast" "$OUT/chapters.tsv"
printf 'idx\tlabel\tepoch\tsubmitted_at\n' > "$OUT/chapters.tsv"

LABELS=(
  "Ten hospitals, three dialects"
  "The unadjusted answer is lying"
  "Make the two arms comparable"
  "Try to break your own result"
  "Let it review its own manuscript"
)
PROMPTS=(
"Group the ten files in hospitals/ by their column fingerprint, not by filename. Report the actual values with unique(). Then convert all of them to one schema with fixed names and units, and never drop a row for missingness. Attach each hospital's type and region from hospitals_meta.csv. Write pooled.csv and print the row count, the counts per dialect, and the albumin and bilirubin medians."
"Fit a Cox model on treatment alone, nothing else. Write naive_hr.json with hr, ci_low and ci_high. Then compute the standardised mean difference between the arms for the eleven covariates we will adjust for. Tell me in one sentence what you would conclude from the hazard ratio by itself, and then what the balance table does to that conclusion."
"Estimate a propensity score by logistic regression on those eleven covariates. Match 1:1 nearest neighbour without replacement, caliper 0.2 times the SD of the logit propensity score. Take the treated in ascending score order. Do not force a match outside the caliper. Report how many treated were left unmatched, the balance after matching, and the Cox hazard ratio for overall survival in the matched cohort."
"Now hold the data completely fixed and vary only the analytic choices. Fifteen covariate sets: the full eleven, each leave-one-out, and three smaller clinical sets. Cross those with eight adjustment methods: multivariable Cox, stabilised IPTW, and propensity matching at calipers 0.1, 0.2 and 0.5 in both 1:1 and 1:2. That is 120 runs. Report the median, the spread, and how many landed outside the range I was hoping for."
"Open four review subagents in parallel in one single message: statistical, clinical, reporting-standards, reproducibility. Each may read manuscript/manuscript.md and the csv and json files here, and nothing else. Tell each to be brief: a one-line recommendation and its three strongest major comments, one line each. When they return, print a four-row table of reviewer, recommendation, and its single most damaging finding."
)

[ -x "$CLAUDE_BIN" ] || { echo "no claude at $CLAUDE_BIN"; exit 1; }

echo "recording ${COLS}x${ROWS} into $D/talk.cast"
tmux -L "$SOCKET" kill-server 2>/dev/null
tmux -L "$SOCKET" new-session -d -s "$SESSION" -x "$COLS" -y "$ROWS" -c "$D" \
  "env VHS_DEMO=1 asciinema rec talk.cast -i $IDLE --cols $COLS --rows $ROWS \
     -t 'Mission by Mission - one agent session, end to end' \
     -c '$CLAUDE_BIN'; exec sleep 5"

# --- wait for the composer -------------------------------------------------
for _ in $(seq 1 90); do
  tmux -L "$SOCKET" capture-pane -p -t "$SESSION" 2>/dev/null | grep -qE 'shift\+tab|for shortcuts' && break
  sleep 2
done
tmux -L "$SOCKET" capture-pane -p -t "$SESSION" | grep -qE 'shift\+tab|for shortcuts' || {
  echo "startup never reached the composer:"; tmux -L "$SOCKET" capture-pane -p -t "$SESSION" | tail -12; exit 1; }
echo "composer ready"
sleep 2

# --- prompt, wait, prompt, wait -------------------------------------------
for i in "${!PROMPTS[@]}"; do
  n=$((i + 1))
  epoch=$(date +%s)
  printf '%s\t%s\t%s\t%s\n' "$n" "${LABELS[$i]}" "$epoch" "$(date +%H:%M:%S)" >> "$OUT/chapters.tsv"
  echo "--- turn $n  ${LABELS[$i]}  $(date +%H:%M:%S)"

  tmux -L "$SOCKET" send-keys -t "$SESSION" -l "${PROMPTS[$i]}"
  sleep 1
  tmux -L "$SOCKET" send-keys -t "$SESSION" Enter

  # The Stop hook prints VHS_TURN_DONE_<n>. Old sentinels stay on screen, so
  # always grep for this turn's exact number.
  ok=0
  for _ in $(seq 1 900); do        # 900 x 2s = 30 min per turn
    if tmux -L "$SOCKET" capture-pane -p -t "$SESSION" | grep -q "VHS_TURN_DONE_$n"; then ok=1; break; fi
    tmux -L "$SOCKET" has-session -t "$SESSION" 2>/dev/null || break
    sleep 2
  done
  if [ "$ok" = 1 ]; then
    echo "    turn $n done $(date +%H:%M:%S)"
  else
    echo "    turn $n TIMED OUT $(date +%H:%M:%S)"; tmux -L "$SOCKET" capture-pane -p -t "$SESSION" | tail -6
  fi
  sleep 3
done

# --- close ----------------------------------------------------------------
sleep 4
tmux -L "$SOCKET" send-keys -t "$SESSION" C-c; sleep 1
tmux -L "$SOCKET" send-keys -t "$SESSION" C-c; sleep 4
tmux -L "$SOCKET" kill-server 2>/dev/null

cp "$D/talk.cast" "$OUT/talk.cast" 2>/dev/null || { echo "no cast produced"; exit 1; }
echo
echo "cast : $(du -h "$OUT/talk.cast" | cut -f1)  $(wc -l < "$OUT/talk.cast") events"
cat "$OUT/chapters.tsv"
