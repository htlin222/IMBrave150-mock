#!/usr/bin/env bash
# Record the whole 45-minute talk as ONE terminal session.
#
# Two tmux servers, on their own sockets so nothing touches your sessions:
#
#   -L talkwork   the content: window "agent" runs Claude Code for the whole
#                 talk (context is never lost), window "stage" runs presenterm
#                 and the odd shell command.
#   -L talkrec    the camera: a client attached to that session, running under
#                 asciinema, so switching windows is just terminal output and
#                 lands in the recording.
#
# Markers are written for every slide shown and every prompt submitted, so the
# presenter can play to the next marker, pause, talk, and carry on.
#
# Paid-for lessons, do not undo:
#   - Dedicated tmux sockets. A long-lived server hands the nested session the
#     environment it started with; the symptom is "Login expired" inside the
#     TUI while `claude -p` works fine from the same shell.
#   - Absolute path to claude. PATH inside tmux may find an older build that
#     gets SIGKILLed when nested.
#   - Prompt text and Enter as two separate send-keys, a second apart, or the
#     composer takes the burst for a paste and drops the submit.
#   - Window NAMES, not indices: base-index may be 1.
set -uo pipefail

CLAUDE_BIN=${CLAUDE_BIN:-$HOME/.local/bin/claude}
WORK=${WORK:-talkwork}
REC=${REC:-talkrec}
COLS=${COLS:-105}
ROWS=${ROWS:-30}
IDLE=${IDLE:-3}
READ_SLIDE=${READ_SLIDE:-7}     # seconds a slide stays up before moving on
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TALK="$HERE/talk"
OUT="$HERE/cast"
D=${D:-${TMPDIR:-/tmp}/imbrave150-talk}
WIPE="/bin/rm -rf"

# These are throwaway servers for the recording, so they must NOT read your
# ~/.tmux.conf: a config that auto-creates sessions or sets hooks will steal the
# attached client away from the talk session and the recording captures the
# wrong screen. -f /dev/null gives each server a clean slate.
TW=(tmux -f /dev/null -L "$WORK")
TR=(tmux -f /dev/null -L "$REC")

command -v presenterm >/dev/null || { echo "presenterm not installed"; exit 1; }
command -v bat >/dev/null || { echo "bat not installed"; exit 1; }
[ -x "$CLAUDE_BIN" ] || { echo "no claude at $CLAUDE_BIN"; exit 1; }

# --- sandbox --------------------------------------------------------------
$WIPE "$D"; mkdir -p "$D/.claude"
cp -R "$HERE/../hospitals" "$D/hospitals"; $WIPE "$D/hospitals/.DS_Store"
cp "$HERE/../hospitals_meta.csv" "$D/"
cp "$TALK"/*.md "$TALK"/theme.yaml "$D/"
SKILL=${SKILL:-$HOME/.claude/skills/agent-demo-recorder}
cp "$SKILL/assets/settings.json" "$D/.claude/"
perl -pi -e "s|REPLACE_WITH_ABSOLUTE_PATH_TO/vhs_stop_hook.sh|$SKILL/scripts/vhs_stop_hook.sh|" \
  "$D/.claude/settings.json"
cat > "$D/CLAUDE.md" <<EOF
# Working rules

- Python is \`$HERE/../.venv/bin/python\`. It has pandas, numpy, lifelines and
  matplotlib. No sklearn, no statsmodels — write logistic regression yourself
  with numpy if you need it.
- Work in this directory. Write scripts as files, then run them.
- This session is projected on a ${COLS}-column screen. Keep output narrow and
  short: the numbers that matter, never a whole dataframe.
- Lead with the number, then the caveat. Answer in English.
EOF

mkdir -p "$OUT"
MARKERS="$OUT/talk-markers.tsv"
printf 'epoch\tkind\tlabel\n' > "$MARKERS"
mark() { printf '%s\t%s\t%s\n' "$(date +%s)" "$1" "$2" >> "$MARKERS"; }

stage() { "${TW[@]}" select-window -t talk:stage; }
agent() { "${TW[@]}" select-window -t talk:agent; }
skeys() { "${TW[@]}" send-keys -t "talk:$1" "${@:2}"; }

# --- start ----------------------------------------------------------------
"${TW[@]}" kill-server 2>/dev/null; "${TR[@]}" kill-server 2>/dev/null
sleep 1
"${TW[@]}" new-session -d -s talk -n agent -x "$COLS" -y "$ROWS" -c "$D" \
  "env VHS_DEMO=1 '$CLAUDE_BIN'; exec sleep 30"
"${TW[@]}" new-window -t talk -n stage -c "$D" 'exec bash --noprofile --norc'
"${TW[@]}" set -t talk status off
"${TW[@]}" select-window -t talk:agent

echo "waiting for the agent window"
for _ in $(seq 1 90); do
  "${TW[@]}" capture-pane -p -t talk:agent 2>/dev/null \
    | grep -qE 'shift\+tab|for shortcuts' && break
  sleep 2
done
"${TW[@]}" capture-pane -p -t talk:agent | grep -qE 'shift\+tab|for shortcuts' || {
  echo "agent never reached the composer:"
  "${TW[@]}" capture-pane -p -t talk:agent | tail -10; exit 1; }

"${TR[@]}" new-session -d -s cap -x "$COLS" -y "$ROWS" -c "$D" \
  "asciinema rec talk-full.cast --cols $COLS --rows $ROWS -i $IDLE \
     -t 'Mission by Mission - the whole thing, one session' \
     -c 'tmux -f /dev/null -L $WORK attach -t talk'; exec sleep 30"
sleep 5
echo "recording"

turn=0

run_slides() {                       # run_slides <id> <title> <deck> <pages>
  echo "=== $1  $2  $(date +%H:%M:%S)"
  stage; sleep 1
  mark slide "$1 · $2"
  skeys stage "clear; presenterm --present $3" Enter
  sleep 3
  for _ in $(seq 2 "$4"); do sleep "$READ_SLIDE"; skeys stage Right; done
  sleep "$READ_SLIDE"
  skeys stage q; sleep 1
  skeys stage clear Enter; sleep 1
}

run_shell() {                        # run_shell <label> <cmd>...
  mark shell "$1"
  stage; sleep 1
  for c in "${@:2}"; do skeys stage "$c" Enter; sleep 7; done
  sleep 3
}

run_turn() {                         # run_turn <label> <prompt>
  turn=$((turn + 1))
  agent; sleep 1
  mark prompt "$1"
  echo "  turn $turn  $(date +%H:%M:%S)  $1"
  "${TW[@]}" send-keys -t talk:agent -l "$2"
  sleep 1
  "${TW[@]}" send-keys -t talk:agent Enter
  for _ in $(seq 1 900); do
    "${TW[@]}" capture-pane -p -t talk:agent | grep -q "VHS_TURN_DONE_$turn" && break
    "${TW[@]}" has-session -t talk 2>/dev/null || break
    sleep 2
  done
  echo "    done $(date +%H:%M:%S)"
  sleep 4
}

# ===========================================================================
# The talk
# ===========================================================================

run_slides 00 "What we are about to do" 00-open.md 3

run_slides 01 "Look at it before you touch it" 01-look.md 1
run_shell "the raw files" \
  "bat --style=header --line-range 1:2 hospitals/H01_Northshore_University.csv" \
  "bat --style=header --line-range 1:2 hospitals/H02_Riverside_General.csv" \
  "bat --style=header --line-range 1:2 hospitals/H03_Metropolitan_Cancer_Ctr.csv"
run_turn "what do you notice" \
  "There are ten CSV files in hospitals/. Do not write a converter and do not fix anything yet. Read enough of them to tell me what you notice, and rank what you find by how much damage it would do if nobody caught it."

run_slides 02 "Three dialects, one table" 02-dialects.md 1
run_turn "build the table, your schema" \
  "Now build the single table. You decide the schema and tell me what you chose. Two things I care about: how you decide which file is which dialect, and what you do with the fields that only some sites record."
run_turn "did you lose anyone" \
  "How many patients ended up in each arm, and did you lose anyone along the way?"

run_slides 03 "The obvious comparison" 03-naive.md 1
run_turn "simplest comparison" \
  "Compare overall survival between the two arms the simplest way you can. No adjustment at all. Give me the hazard ratio and tell me in one sentence what a reader would conclude from it."
run_turn "do you believe it" \
  "Do you believe that number? Show me whatever would convince you either way."

run_slides 04 "Making the arms comparable" 04-match.md 1
run_turn "handle it, plan first" \
  "The two arms are not the same kind of patient. Handle it. Tell me your plan before you run anything, then run it and report how many patients you had to leave behind."
run_turn "which direction did you sort" \
  "You sorted the treated patients before matching. Which direction did you sort, and does it matter? Try the other one."
run_turn "which one do you publish" \
  "So which of those two numbers is the right one to publish?"

run_slides 05 "Why a curve, not a percentage" 05-survival.md 1
run_turn "survival, your choice of form" \
  "Give me the survival difference in the matched cohort, and give it to me in whatever form you think a clinician should see. Save any figure you make."
run_turn "explain the gap" \
  "What fraction of each arm was still alive at twelve months, and how does that compare with just counting who died? Explain the gap."

run_slides 06 "Subgroups test consistency" 06-subgroups.md 1
run_turn "fix the list first" \
  "Break the result down by the subgroups a reviewer would ask about. Do not go hunting: decide the list first and tell me it, then run them."
run_turn "which subgroup benefits most" \
  "Is there a subgroup that benefits more than the others? Answer carefully."

run_slides 07 "Try to break your own result" 07-multiverse.md 1
run_turn "vary every choice" \
  "Someone will say you picked the analysis that worked. Hold the data completely fixed, vary every analytic choice you can defend, and show me the whole distribution rather than your favourite point."
run_turn "which runs are junk" \
  "Which of those runs would you throw away, and why? Give me the honest summary after you have thrown them away."

run_slides 08 "Writing it down, from the log" 08-write.md 1
run_turn "methods from the scripts" \
  "Write the Methods section into manuscript.md. Reconstruct it from the scripts you actually ran, not from what you meant to do, and mark anything you cannot source."
run_turn "results, every number sourced" \
  "Now the Results, appended to the same file. Every number has to come from a file on disk, and I want to see which file each one came from."

run_slides 09 "Let it review its own work" 09-review.md 1
run_turn "four reviewers in parallel" \
  "Open four reviewers in parallel, in one single message: statistical, clinical, reporting standards, reproducibility. They may read manuscript.md and the output files here and nothing else. Ask each for a recommendation and its three strongest objections, one line each."
run_turn "real defects, fix one" \
  "Of everything they raised, which findings are real defects in the work rather than matters of taste? Fix one of them now."

run_slides 10 "What to take home" 10-close.md 1

# --- close ----------------------------------------------------------------
agent; sleep 3
"${TW[@]}" send-keys -t talk:agent C-c; sleep 1
"${TW[@]}" send-keys -t talk:agent C-c; sleep 3
"${TR[@]}" send-keys -t cap C-c; sleep 4
"${TW[@]}" kill-server 2>/dev/null
"${TR[@]}" kill-server 2>/dev/null

cp "$D/talk-full.cast" "$OUT/talk-full.cast" 2>/dev/null || {
  echo "no cast produced"; exit 1; }
echo
echo "cast   : $(du -h "$OUT/talk-full.cast" | cut -f1)"
echo "markers: $(($(wc -l < "$MARKERS") - 1))"
echo "turns  : $turn"
