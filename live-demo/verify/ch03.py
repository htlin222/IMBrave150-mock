#!/usr/bin/env python3
"""第 03 章驗收 — Kaplan–Meier、log-rank、Cox、出版級曲線。"""
import sys
import numpy as np
from _common import WS, get, run


def m3_1(c):
    j = c.json("km_summary.json")

    # ---- OS：本場的核心數字 ----
    hr = get(j, "os.hr", get(j, "hr"))
    c.near(float(hr) if hr is not None else np.nan, 0.578, 0.040,
           "配對世代 OS HR")
    if hr is not None and abs(float(hr) - 0.58) < 0.04:
        c.ok("與真實 IMbrave150 試驗報告的 HR 0.58 一致")

    lo = get(j, "os.ci_low")
    hi = get(j, "os.ci_high")
    if lo is not None and hi is not None:
        c.want(float(hi) < 1.0, f"OS 95% CI 上界 {float(hi):.2f} < 1.0")

    p = get(j, "os.logrank_p", get(j, "logrank_p"))
    if p is not None:
        c.want(0 < float(p) < 1e-4,
               f"log-rank p = {float(p):.2g}（< 1e-4）",
               "若 p 恰為 0，代表被格式化成 0.000 而非存真實值")
        c.want(float(p) != 0.0, "p 值存的是真實數值而非四捨五入後的 0")

    # ---- 審查的教學點：死亡比例 ≠ 1 − 存活率 ----
    d1 = get(j, "os.deaths_treat_pct")
    d0 = get(j, "os.deaths_control_pct")
    s1 = get(j, "os.surv12_treat_pct")
    s0 = get(j, "os.surv12_control_pct")

    if d1 is not None:
        c.near(float(d1), 25.6, 4.0, "Atezo 組原始死亡比例", unit="%")
    if d0 is not None:
        c.near(float(d0), 38.0, 4.0, "Sorafenib 組原始死亡比例", unit="%")
    if s1 is not None:
        c.near(float(s1), 71.1, 4.0, "Atezo 組 12 個月 KM 存活率", unit="%")
    if s0 is not None:
        c.near(float(s0), 55.7, 4.0, "Sorafenib 組 12 個月 KM 存活率", unit="%")

    if d0 is not None and s0 is not None:
        gap = abs((100 - float(d0)) - float(s0))
        c.want(gap > 2.0,
               f"KM 存活率與 1−死亡比例 相差 {gap:.1f} 個百分點（審查的證據）",
               "兩者若幾乎相等，可能是用 1-os_event.mean() 當存活率")

    # ---- 中位存活 ----
    m1, m0 = get(j, "os.median_treat"), get(j, "os.median_control")
    if m1 is not None and np.isfinite(float(m1)):
        c.near(float(m1), 21.3, 3.0, "Atezo 組中位 OS", unit=" 個月")
    if m0 is not None and np.isfinite(float(m0)):
        c.near(float(m0), 13.5, 3.0, "Sorafenib 組中位 OS", unit=" 個月")

    # ---- PFS：真值 0.59，配對後會落在 0.63，不要「修」它 ----
    ph = get(j, "pfs.hr")
    if ph is None:
        c.bad("km_summary.json 缺 pfs 區塊", "PFS 也要跑一次")
    else:
        c.near(float(ph), 0.632, 0.050, "配對世代 PFS HR")
        if abs(float(ph) - 0.59) < 0.005:
            c.bad("PFS HR 恰好等於真值 0.59",
                  "配對後的實際估計是 0.63 —— 不要把數字改成理論值")

    n = get(j, "n")
    if n is not None:
        c.near(int(n), 1412, 120, "配對世代人數")


def m3_2(c):
    c.need("figures/km_os.svg")          # 還沒畫 → SKIP，不是 FAIL
    for f in ["figures/km_os.svg", "figures/km_pfs.svg"]:
        p = c.file(f)
        if not p.exists():
            continue
        svg = p.read_text(errors="ignore")
        c.want(len(svg) > 5000, f"{f} 內容非空（{len(svg) // 1024} KB）")

        low = svg.lower()
        # number-at-risk 表是期刊硬性要求
        c.want("at risk" in low or "at-risk" in low or "number at" in low,
               f"{f} 含 number-at-risk 表",
               "KM 圖沒有 at-risk 表等於沒畫 —— 讀者看不出曲線尾端剩幾人")
        # 可讀的臨床標籤，而不是 treat=1 / 0
        c.want("sorafenib" in low or "atezo" in low,
               f"{f} 使用臨床藥名而非 treat=0/1")
        c.want("treat=1" not in low and "treat = 1" not in low,
               f"{f} 沒有殘留 treat=1 這種程式變數名")


if __name__ == "__main__":
    sys.exit(run("Chapter 03 · 為什麼是 Kaplan–Meier",
                 {"3.1": m3_1, "3.2": m3_2}))
