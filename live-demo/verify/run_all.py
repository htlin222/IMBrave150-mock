#!/usr/bin/env python3
"""跑完全部七章的驗收，最後印一張總表。"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable

CHAPTERS = [
    ("ch00.py", "00 · 建沙盒"),
    ("ch01.py", "01 · 十家醫院三種方言"),
    ("ch02.py", "02 · 未調整的答案在說謊"),
    ("ch03.py", "03 · 為什麼是 Kaplan–Meier"),
    ("ch04.py", "04 · 次群組一致性"),
    ("ch05.py", "05 · 試著把結論弄壞"),
    ("ch06.py", "06 · 寫稿、引用驗證與數字稽核"),
    ("ch07.py", "07 · 審稿、回應、潤稿、去 AI 腔"),
    ("ch08.py", "08 · build 與 preprint 發佈"),
]

GREEN, RED, BOLD, DIM, OFF = "\033[32m", "\033[31m", "\033[1m", "\033[2m", "\033[0m"


def main():
    results = []
    for script, label in CHAPTERS:
        r = subprocess.run([PY, str(HERE / script)], cwd=HERE)
        results.append((label, r.returncode))

    print(f"\n{BOLD}{'═' * 52}{OFF}")
    print(f"{BOLD}  live-demo 總結{OFF}")
    print(f"{BOLD}{'═' * 52}{OFF}")
    for label, code in results:
        mark = f"{GREEN}PASS{OFF}" if code == 0 else f"{RED}FAIL{OFF}"
        print(f"  {mark}  {label}")
    failed = sum(1 for _, c in results if c != 0)
    print(f"{DIM}{'─' * 52}{OFF}")
    if failed:
        print(f"  {RED}{BOLD}{failed} 章未通過{OFF}\n")
    else:
        print(f"  {GREEN}{BOLD}全部通過 —— 這篇稿子的每個數字都對得上出處。{OFF}\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
