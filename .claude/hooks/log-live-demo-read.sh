#!/usr/bin/env bash
# PostToolUse(Read) hook —— 記錄 live-demo 的哪一章在什麼時候被打開。
#
# 用途：彩排與正式演出時量出每一關的實際耗時，回頭對照 RUNBOOK.md 的時間盒
# （現場路線宣稱 62 分鐘，那是 agent 的執行時間，不含講者講話）。
#
# 輸入：Claude Code 從 stdin 餵進 PostToolUse 的 JSON。
# 輸出：一行 TSV 追加到 .claude/live-demo-timing.log，欄位為
#       時刻 / epoch / 距上一筆的秒數 / 相對路徑
# 任何情況都 exit 0 —— 記錄失敗不該擋住 demo。
set -uo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
LOG="$ROOT/.claude/live-demo-timing.log"

f=$(jq -r '.tool_input.file_path // empty' 2>/dev/null) || exit 0
[ -n "$f" ] || exit 0

case "$f" in
  */live-demo/*.md) ;;
  *) exit 0 ;;
esac

rel="${f#"$ROOT"/}"
now=$(date +%s)

prev=$(tail -n 1 "$LOG" 2>/dev/null | cut -f2)
if [ -n "${prev:-}" ] && [ "$prev" -eq "$prev" ] 2>/dev/null; then
  delta="+$((now - prev))s"
else
  delta="start"
fi

printf '%s\t%s\t%s\t%s\n' "$(date +%H:%M:%S)" "$now" "$delta" "$rel" >> "$LOG"
exit 0
