"""
驗收框架 — live-demo 每章共用。

Agent 不需要讀這個檔，也不應該修改它。跑 chNN.py 就好。
每個 chNN.py 只要提供一個 MISSIONS dict：{"1.2": callable(Check), ...}
然後呼叫 run("Chapter 01", MISSIONS)。
"""
import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent      # live-demo/verify
LIVE = HERE.parent                          # live-demo
WS = LIVE / "workspace"                     # 沙盒（agent 的產出都在這）
ROOT = LIVE.parent                          # repo 根目錄

GREEN, RED, YELLOW, DIM, BOLD, OFF = (
    "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m"
)


class Skip(Exception):
    """前置產出不存在 —— 該 Mission 還沒做，不是做錯了。"""


class Check:
    """一個 Mission 的檢查累加器。"""

    def __init__(self, label):
        self.label = label
        self.failed = 0
        self.passed = 0
        self.notes = []

    # ---- 基本斷言 -------------------------------------------------------
    def ok(self, msg):
        self.passed += 1
        print(f"  {GREEN}✓{OFF} {msg}")

    def bad(self, msg, detail=None):
        self.failed += 1
        print(f"  {RED}✗{OFF} {msg}")
        if detail:
            print(f"    {DIM}{detail}{OFF}")

    def note(self, msg):
        print(f"  {YELLOW}·{OFF} {DIM}{msg}{OFF}")

    def want(self, cond, msg, detail=None):
        self.ok(msg) if cond else self.bad(msg, detail)
        return bool(cond)

    def eq(self, got, expect, msg):
        return self.want(got == expect, f"{msg}：{got}", f"預期 {expect}")

    def near(self, got, expect, tol, msg, unit=""):
        """數值落在 expect ± tol。tol 刻意放寬以容許實作差異。"""
        if got is None or (isinstance(got, float) and math.isnan(got)):
            return self.bad(f"{msg}：缺值", f"預期 {expect}±{tol}")
        good = abs(got - expect) <= tol
        rng = f"允許 {expect - tol:g}–{expect + tol:g}"
        return self.want(good, f"{msg}：{got:g}{unit}（{rng}）",
                         f"實得 {got:g}，超出容忍範圍 —— 回去看該 Mission 的 ⚠️ 地雷")

    def le(self, got, limit, msg):
        return self.want(got <= limit, f"{msg}：{got:g} ≤ {limit:g}",
                         f"實得 {got:g}，超過上限 {limit:g}")

    def between(self, got, lo, hi, msg, unit=""):
        return self.want(lo <= got <= hi, f"{msg}：{got:g}{unit}（允許 {lo:g}–{hi:g}）",
                         f"實得 {got:g}")

    # ---- 檔案 -----------------------------------------------------------
    def file(self, rel, msg=None):
        p = WS / rel
        self.want(p.exists(), msg or f"{rel} 存在", f"找不到 {p}")
        return p

    def need(self, rel):
        """前置檔案：不存在就 Skip（提示先做前面的 Mission），而不是判定失敗。"""
        p = WS / rel
        if not p.exists():
            raise Skip(rel)
        return p

    def csv(self, rel):
        import pandas as pd
        return pd.read_csv(self.need(rel))

    def json(self, rel):
        return json.loads(self.need(rel).read_text())

    def cols(self, df, required, what):
        missing = [c for c in required if c not in df.columns]
        return self.want(not missing, f"{what} 欄位齊全（{len(required)} 欄）",
                         f"缺少：{', '.join(missing)}")

    # ---- 收尾 -----------------------------------------------------------
    def report(self):
        print(f"  {DIM}{'─' * 45}{OFF}")
        if self.failed:
            print(f"  {RED}{BOLD}FAIL{OFF}  {self.label}"
                  f"  {DIM}（{self.passed} 過 / {self.failed} 未過）{OFF}\n")
        else:
            print(f"  {GREEN}{BOLD}PASS{OFF}  {self.label}"
                  f"  {DIM}（{self.passed} 項）{OFF}\n")
        return self.failed


def get(d, path, default=None):
    """從巢狀 dict 取值：get(j, "os.hr")"""
    cur = d
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def smd(df, col, tcol="treat"):
    """標準化平均差（合併變異數當分母）—— 與 Mission 2.2 的定義一致。"""
    import numpy as np
    a = df.loc[df[tcol] == 1, col].astype(float)
    b = df.loc[df[tcol] == 0, col].astype(float)
    sp = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return 0.0 if sp == 0 or np.isnan(sp) else float((a.mean() - b.mean()) / sp)


def run(chapter, missions):
    """chNN.py 的統一進入點。"""
    ap = argparse.ArgumentParser(description=f"{chapter} 驗收")
    ap.add_argument("--mission", "-m", help="只跑某一個 Mission，例如 2.3")
    ap.add_argument("--chapter", "-c", action="store_true", help="跑整章（預設）")
    args = ap.parse_args()

    if not WS.exists():
        print(f"{RED}找不到 {WS}{OFF}\n先做 Mission 0.1 建立沙盒。")
        return 2

    todo = list(missions.items())
    if args.mission:
        key = args.mission.lstrip("Mm").strip()
        if key not in missions:
            print(f"{RED}沒有 Mission {key}{OFF}"
                  f"  可用：{', '.join(missions)}")
            return 2
        todo = [(key, missions[key])]

    print(f"\n{BOLD}{chapter}{OFF}")
    total = 0
    for key, fn in todo:
        label = f"Mission {key}" if key != "-" else chapter
        print(f"\n{DIM}── {label} {'─' * max(0, 40 - len(label))}{OFF}")
        c = Check(label)
        try:
            fn(c)
        except Skip as e:
            print(f"  {YELLOW}⊘{OFF} 尚未產出 {e} —— 先完成前面的 Mission")
            print(f"  {DIM}{'─' * 45}{OFF}")
            print(f"  {YELLOW}{BOLD}SKIP{OFF}  {label}\n")
            continue
        except Exception as e:  # noqa: BLE001 — 驗收腳本不該因例外而中斷
            c.bad(f"驗收時發生例外：{type(e).__name__}: {e}")
        total += c.report()

    return 1 if total else 0
