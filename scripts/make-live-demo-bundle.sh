#!/usr/bin/env bash
# 把 live-demo 打包成學員可以直接下載、原封不動跑一遍的 zip。
#
#   scripts/make-live-demo-bundle.sh [version]
#
# 產出 dist/imbrave150-live-demo-<version>.zip，解開後是一個
# imbrave150-live-demo/ 目錄，裡面的相對路徑與 repo 完全一致
# （live-demo/ 的驗收腳本靠 ../hospitals/ 找原始資料，結構不能動）。
#
# 刻意不放進去的東西見下方 FORBIDDEN —— 那些是衍生產物，
# 放進去等於直接把第 01 章的答案發給學員。打包完會斷言它們真的不在。
set -euo pipefail

VERSION="${1:-dev}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="imbrave150-live-demo"
OUT="$ROOT/dist"
STAGE="$(mktemp -d)/$NAME"

# 衍生產物：跑 `make data` 就會重新產生，但直接附上就是洩題。
FORBIDDEN=(
  "_answer_key_pooled.csv"        # 第 01 章的標準答案
  "imbrave150_pooled.csv"         # harmonize 的成品，就是第 01 章要做的東西
  "robustness_multiverse_results.csv"
)

mkdir -p "$STAGE" "$OUT"

# ---- live-demo 本體（workspace 必須是空的，只留 .gitignore）----
rsync -a \
  --exclude "workspace/*" \
  --exclude "__pycache__/" \
  --exclude ".DS_Store" \
  "$ROOT/live-demo/" "$STAGE/live-demo/"
mkdir -p "$STAGE/live-demo/workspace"
cp "$ROOT/live-demo/workspace/.gitignore" "$STAGE/live-demo/workspace/.gitignore"

# ---- 原始資料：十家醫院 + 醫院目錄 ----
rsync -a --exclude ".DS_Store" "$ROOT/hospitals/" "$STAGE/hospitals/"
cp "$ROOT/hospitals_meta.csv" "$STAGE/"

# ---- 單一試驗資料集與它的資料字典（`make analyze` 會用到）----
cp "$ROOT/imbrave150_simulated.csv" "$ROOT/DATA_DICTIONARY.md" "$STAGE/"

# ---- agent 指示、環境、授權 ----
cp "$ROOT/CLAUDE.md" "$ROOT/requirements.txt" "$ROOT/Makefile" "$ROOT/LICENSE" "$STAGE/"

# ---- 參考解：各 Mission 的「🆘 卡住時」會指向這些 ----
for f in analyze_imbrave150.py generate_imbrave150.py generate_multihospital.py \
         harmonize_hospitals.py psm_imbrave150.py robustness_multiverse.py \
         search_seed.py tmle_demo.py; do
  cp "$ROOT/$f" "$STAGE/"
done

# ---- 學員入口 ----
cp "$ROOT/scripts/bundle-START-HERE.md" "$STAGE/START-HERE.md"
printf '%s\n' "$VERSION" > "$STAGE/VERSION"

# ---- 斷言：不該在的東西真的不在 ----
fail=0
for bad in "${FORBIDDEN[@]}"; do
  if find "$STAGE" -name "$bad" -print -quit | grep -q .; then
    echo "✗ 打包出錯：$bad 不該出現在 bundle 裡" >&2
    fail=1
  fi
done
# workspace 必須是空的（除了 .gitignore），否則學員拿到的是跑過的沙盒
leftover="$(find "$STAGE/live-demo/workspace" -mindepth 1 ! -name ".gitignore" | wc -l | tr -d ' ')"
if [ "$leftover" != "0" ]; then
  echo "✗ 打包出錯：live-demo/workspace 不是空的（有 $leftover 個殘留）" >&2
  fail=1
fi
# 沒有 verify/ 就不是這份教材
[ -f "$STAGE/live-demo/verify/ch06.py" ] || { echo "✗ 打包出錯：缺 verify/ch06.py" >&2; fail=1; }
[ "$(find "$STAGE/hospitals" -name '*.csv' | wc -l | tr -d ' ')" = "10" ] \
  || { echo "✗ 打包出錯：hospitals/ 不是 10 個 CSV" >&2; fail=1; }
[ "$fail" = "0" ] || exit 1

# ---- 打包 ----
ZIP="$OUT/$NAME-$VERSION.zip"
rm -f "$ZIP"
(cd "$(dirname "$STAGE")" && zip -qr "$ZIP" "$NAME" -x '*.DS_Store')
rm -rf "$(dirname "$STAGE")"

echo "✓ $ZIP"
unzip -l "$ZIP" | tail -1
