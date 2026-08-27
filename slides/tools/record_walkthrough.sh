#!/usr/bin/env bash
# Record the walkthrough as ONE terminal session: the ordinary shape of a
# study done with an agent — data, cleaning, exploring, analysis, writing.
#
# Deliberately plain. No methodological arguments, no deliberate failures:
# the audience has never seen a terminal, and the thing being taught is the
# shape of the work, not the epistemology. The long version with the
# arguments in it is record_talk.sh.
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
WORK=${WORK:-walkwork}
REC=${REC:-walkrec}
COLS=${COLS:-105}
ROWS=${ROWS:-30}
IDLE=${IDLE:-3}
READ_SLIDE=${READ_SLIDE:-7}     # seconds a slide stays up before moving on
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TALK="$HERE/walkthrough"
OUT="$HERE/cast"
D=${D:-${TMPDIR:-/tmp}/imbrave150-walk}
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
MARKERS="$OUT/walk-markers.tsv"
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
  "asciinema rec walk.cast --cols $COLS --rows $ROWS -i $IDLE \
     -t 'From ten spreadsheets to a manuscript' \
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
# The walkthrough
# ===========================================================================

run_slides 00 "The ordinary shape of a study" 00-open.md 3

run_slides 01 "The data" 01-data.md 1
run_shell "what arrived" \
  "ls hospitals/" \
  "bat --style=header --line-range 1:2 hospitals/H01_Northshore_University.csv" \
  "bat --style=header --line-range 1:2 hospitals/H03_Metropolitan_Cancer_Ctr.csv"
run_turn "what is this data" \
  "There are ten CSV files in hospitals/ and a hospitals_meta.csv. Tell me what this data is: how many patients in total, how many per file, what the columns mean, and what the outcome variables are. Do not change anything yet."

run_slides 02 "Cleaning" 02-clean.md 1
run_turn "one table" \
  "The ten files do not use the same column names or the same units. Merge them into one table and write it to pooled.csv. Tell me every conversion you had to make, and attach each hospital's type and region from hospitals_meta.csv."
run_turn "what is missing" \
  "Which columns have missing values, and how much? Is any of it structural rather than random? Tell me how you would handle each one and why, before you do anything about it."

run_slides 03 "Exploring" 03-explore.md 1
run_turn "who are these patients" \
  "Describe this cohort the way a Table 1 would: age, sex, aetiology, performance status, stage, liver function, and the two treatment groups. Keep it to one table I can read on screen."
run_turn "how do the sites differ" \
  "Now compare the ten hospitals with each other. For each one: how many patients, what proportion got each drug, and what proportion have died. Sort it so the pattern is visible, and tell me what you see."
run_turn "are the arms comparable" \
  "Compare the two treatment groups at baseline, covariate by covariate, and tell me which ones are meaningfully different and in which direction. Then tell me what that would do to a naive comparison of survival."
run_turn "what does follow-up look like" \
  "How long were these patients followed, and how many events are there in each arm? Show me the distribution of follow-up time, and say whether it differs between the groups."
run_turn "a picture" \
  "Make one figure that shows me what you think is the most important thing you have found so far, and save it. Tell me why you chose that one."

run_slides 04 "Analysis" 04-analyse.md 1
run_turn "the naive comparison" \
  "Compare overall survival between the two arms with no adjustment at all. Give me the Kaplan-Meier curves, the median survival in each group, and the hazard ratio, and save the figure."
run_turn "account for the differences" \
  "Now account for the baseline differences you found earlier, using whatever method you think fits, and tell me why you chose it before you run it. Report the adjusted hazard ratio and how many patients the method could actually use."
run_turn "does it hold up" \
  "Does the result hold in the subgroups a reviewer would ask about? Decide the list first, tell me it, then run them and show me a forest plot."

run_slides 05 "Writing it up" 05-write.md 1
run_turn "methods" \
  "Write the Methods section into manuscript.md, reconstructed from the scripts you actually ran rather than from memory. Include the software versions."
run_turn "results" \
  "Now append the Results. Every number must come from a file on disk, and mark which file each one came from."
run_turn "read it back" \
  "Read manuscript.md back and check it against the files. Is there any number in it you cannot trace to a source, or any claim the data do not support?"

run_slides 06 "What this was" 06-close.md 1

# --- close ----------------------------------------------------------------
agent; sleep 3
"${TW[@]}" send-keys -t talk:agent C-c; sleep 1
"${TW[@]}" send-keys -t talk:agent C-c; sleep 3
"${TR[@]}" send-keys -t cap C-c; sleep 4
"${TW[@]}" kill-server 2>/dev/null
"${TR[@]}" kill-server 2>/dev/null

cp "$D/walk.cast" "$OUT/walk.cast" 2>/dev/null || {
  echo "no cast produced"; exit 1; }
echo
echo "cast   : $(du -h "$OUT/walk.cast" | cut -f1)"
echo "markers: $(($(wc -l < "$MARKERS") - 1))"
echo "turns  : $turn"
