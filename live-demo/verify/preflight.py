#!/usr/bin/env python3
"""
上台前跑這支。把「現場才會發現」的環境問題全部提前引爆。

    ../.venv/bin/python verify/preflight.py            # 現場路線（00–06）
    ../.venv/bin/python verify/preflight.py --full     # 完整路線（含 07–08）

它不檢查你的分析對不對（那是 chNN.py 的事），只檢查
「這台機器今天能不能把這場 demo 跑完」。
"""
import argparse
import importlib
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from _common import GREEN, RED, YELLOW, DIM, BOLD, OFF, LIVE, ROOT, WS

PY = sys.executable


class Pre:
    def __init__(self):
        self.fail = 0
        self.warn = 0

    def ok(self, msg, extra=""):
        print(f"  {GREEN}✓{OFF} {msg}" + (f" {DIM}{extra}{OFF}" if extra else ""))

    def bad(self, msg, fix):
        self.fail += 1
        print(f"  {RED}✗{OFF} {msg}\n    {DIM}修：{fix}{OFF}")

    def soft(self, msg, fix):
        self.warn += 1
        print(f"  {YELLOW}!{OFF} {msg}\n    {DIM}{fix}{OFF}")


def section(t):
    print(f"\n{BOLD}{t}{OFF}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="也檢查第 07–08 章需要的工具")
    args = ap.parse_args()
    p = Pre()

    # ---------------------------------------------------------------- Python
    section("Python 與套件")
    versions = {}
    for mod, need in [("pandas", None), ("numpy", None),
                      ("lifelines", None), ("matplotlib", None)]:
        try:
            m = importlib.import_module(mod)
            v = getattr(m, "__version__", "?")
            versions[mod] = v
            p.ok(f"{mod} {v}")
        except ImportError:
            p.bad(f"{mod} 未安裝", "make setup")

    # 🔴 已知相沖：lifelines 的 add_at_risk_counts 在 numpy 2.x 會崩潰。
    # 與其相信版本號，直接跑一次真的呼叫。
    if {"lifelines", "numpy", "matplotlib"} <= versions.keys():
        code = (
            "import matplotlib; matplotlib.use('Agg');"
            "import matplotlib.pyplot as plt;"
            "from lifelines import KaplanMeierFitter;"
            "from lifelines.plotting import add_at_risk_counts;"
            "k=KaplanMeierFitter().fit([1,2,3,4,5,6],[1,0,1,1,0,1]);"
            "f,a=plt.subplots(); k.plot_survival_function(ax=a);"
            "add_at_risk_counts(k, ax=a)"
        )
        r = subprocess.run([PY, "-c", code], capture_output=True, text=True)
        if r.returncode == 0:
            p.ok("lifelines add_at_risk_counts() 可用",
                 "（Mission 3.2 可直接用官方函式）")
        else:
            first = (r.stderr.strip().splitlines() or ["?"])[-1]
            p.soft(f"add_at_risk_counts() 不可用 — {first}",
                   "已知相沖，非環境損壞。Mission 3.2 有手工 at-risk 表替代碼，"
                   "照那段寫就不會在台上炸。")

    # ------------------------------------------------------------- 資料與沙盒
    section("資料與沙盒")
    src = sorted((ROOT / "hospitals").glob("*.csv"))
    p.ok(f"原始資料 hospitals/ 有 {len(src)} 個檔") if len(src) == 10 else \
        p.bad(f"hospitals/ 只有 {len(src)} 個檔（應 10）", "git checkout hospitals/")
    p.ok("hospitals_meta.csv 存在") if (ROOT / "hospitals_meta.csv").exists() else \
        p.bad("缺 hospitals_meta.csv", "git checkout hospitals_meta.csv")

    leftovers = [x for x in WS.iterdir() if x.name != ".gitignore"] if WS.exists() else []
    if leftovers:
        p.soft(f"沙盒不是空的（{len(leftovers)} 個項目）",
               "上一場的產出還在，Mission 0.1 就不是『從零開始』了。"
               "清：rip live-demo/workspace/* && git checkout live-demo/workspace/.gitignore")
    else:
        p.ok("沙盒是空的（Mission 0.1 會從零開始）")

    # ------------------------------------------------------------ 驗收腳本本身
    section("驗收腳本")
    broken = []
    for f in sorted((LIVE / "verify").glob("ch*.py")):
        r = subprocess.run([PY, "-c", f"import ast,sys;ast.parse(open('{f}').read())"],
                           capture_output=True, text=True)
        if r.returncode:
            broken.append(f.name)
    p.ok(f"9 支 chNN.py 語法正常") if not broken else \
        p.bad(f"語法錯誤：{broken}", "修好再上台")

    r = subprocess.run([PY, str(LIVE / "verify" / "run_all.py")],
                       capture_output=True, text=True, cwd=LIVE / "verify")
    if "Traceback" in r.stderr or "Traceback" in r.stdout:
        p.bad("空跑 run_all.py 出現 Traceback", "驗收腳本本身有問題，先修")
    else:
        n_skip = r.stdout.count("SKIP")
        p.ok(f"空跑 run_all.py 正常（{n_skip} 個 Mission 標為 SKIP）",
             "只有第 00 章 FAIL 是正確的")

    if not args.full:
        done(p, "現場路線（00–06）")
        return 1 if p.fail else 0

    # -------------------------------------------------- 第 07–08 章的外部工具
    section("寫作與 build 工具鏈（第 07–08 章）")
    for tool, why, hard in [("pandoc", "轉檔與引用排版", True),
                            ("tectonic", "LaTeX 引擎", True),
                            ("curl", "Crossref 驗證", True)]:
        path = shutil.which(tool)
        (p.ok(f"{tool} 可用", why) if path else
         (p.bad if hard else p.soft)(f"缺 {tool}（{why}）", f"brew install {tool}"))

    svg = shutil.which("rsvg-convert") or shutil.which("inkscape")
    if svg:
        p.ok(f"SVG→PDF 轉換器：{Path(svg).name}", "LaTeX 不吃 SVG，靠它")
    else:
        p.bad("沒有 rsvg-convert 也沒有 inkscape",
              "brew install librsvg —— 缺了的話第 08 章的錯誤訊息會偽裝成 LaTeX 問題")

    # tectonic 冷啟動：第一次會下載套件包，現場會靜止 ~20 秒
    if shutil.which("pandoc") and shutil.which("tectonic"):
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "warm.pdf"
            r = subprocess.run(
                ["pandoc", "-o", str(out), "--pdf-engine=tectonic", "-"],
                input="warmup\n", capture_output=True, text=True, timeout=300)
            if r.returncode == 0 and out.exists():
                p.ok("tectonic 已暖機（套件包已快取）", "現場 build 約 3–5 秒")
            else:
                p.bad("tectonic 暖機失敗",
                      (r.stderr or "")[-200:] or "檢查網路")

    # 去 AI 腔的 pattern linter（選用，Mission 7.4）
    if shutil.which("llmstrip"):
        p.ok("llmstrip 可用", "Mission 7.4 的機器檢查")
    else:
        p.soft("沒有 llmstrip（選用）",
               "裝了可讓 Mission 7.4 有可稽核的前後對照："
               "curl -fsSL https://raw.githubusercontent.com/HugoLopes45/"
               "llmstrip/main/scripts/install.sh | sh"
               "  ——沒裝就靠 Mission 7.4 的人工清單，不影響流程")

    # Crossref 連線 + polite pool
    if shutil.which("curl"):
        r = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
             "https://api.crossref.org/works/10.1056/NEJMoa1915745",
             "-H", "User-Agent: imbrave150-livedemo/1.0 (mailto:ppoiu87@gmail.com)"],
            capture_output=True, text=True, timeout=60)
        if r.stdout.strip() == "200":
            p.ok("Crossref API 可連（polite pool）", "Mission 6.8 要用")
        else:
            p.soft(f"Crossref 回應 {r.stdout.strip() or '無'}",
                   "沒網路的話 Mission 6.8 要改成離線示範，先準備好備案")

    done(p, "完整路線（00–08）")
    return 1 if p.fail else 0


def done(p, route):
    print(f"\n{DIM}{'─' * 52}{OFF}")
    if p.fail:
        print(f"  {RED}{BOLD}{p.fail} 項阻斷{OFF}"
              f"{f'  {YELLOW}{p.warn} 項提醒{OFF}' if p.warn else ''}"
              f"  {DIM}— {route} 還不能上台{OFF}\n")
    elif p.warn:
        print(f"  {YELLOW}{BOLD}可以上台{OFF}  {DIM}{route}；"
              f"{p.warn} 項提醒已有對策，照 Mission 寫的做就不會炸{OFF}\n")
    else:
        print(f"  {GREEN}{BOLD}可以上台{OFF}  {DIM}{route} 全部就緒{OFF}\n")


if __name__ == "__main__":
    sys.exit(main())
