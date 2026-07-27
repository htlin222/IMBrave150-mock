#!/usr/bin/env python3
"""第 04 章驗收 — 次群組 HR 與森林圖。"""
import sys
from _common import run

NEEDED_VARS = ["region", "ecog", "afp", "invasion", "bclc", "etiolog"]


def m4_1(c):
    s = c.csv("subgroups.csv")
    c.cols(s, ["subgroup_level", "n", "hr", "ci_low", "ci_high"], "subgroups")
    if not {"hr", "ci_low", "ci_high", "n"} <= set(s.columns):
        return

    # Overall + 13 個次群組
    blob = " ".join(str(x).lower() for x in s.to_numpy().ravel())
    has_overall = "overall" in blob
    n_sub = len(s) - (1 if has_overall else 0)
    c.want(has_overall, "有 Overall 這一列（森林圖的參考列）")
    c.between(n_sub, 12, 14, "次群組列數（預先指定的 13 個）")

    # 六個預先指定的變數都在
    missing = [v for v in NEEDED_VARS if v not in blob]
    c.want(not missing, "六個預先指定的次群組變數都有",
           f"找不到：{missing}（region/ECOG/AFP/MVI/BCLC/etiology）")

    hr = s["hr"].astype(float)
    c.between(float(hr.min()), 0.40, 0.56, "最小次群組 HR")
    c.between(float(hr.max()), 0.56, 0.72, "最大次群組 HR")

    # 一致性：沒有任何一群反轉
    crossing = s[s["ci_high"].astype(float) >= 1.0]
    c.want(len(crossing) == 0,
           "所有次群組的 95% CI 都排除 1.0（沒有任何一群反轉）",
           f"有 {len(crossing)} 群跨過 1.0：{list(crossing.get('subgroup_level', []))}")

    # 樣本數合理
    total = float(s.loc[~s.astype(str).apply(
        lambda r: "overall" in " ".join(r).lower(), axis=1), "n"].astype(float).sum())
    c.between(total, 1412 * 5.4, 1412 * 6.3,
              "各次群組人數加總（6 個變數各把世代切一次 ≈ 6 × 1412）")

    # 最寬的 CI 應該是最小的次群組
    s2 = s.copy()
    s2["width"] = s2["ci_high"].astype(float) / s2["ci_low"].astype(float)
    widest = s2.loc[s2["width"].idxmax()]
    c.want(float(widest["n"]) < 400,
           f"CI 最寬的次群組 n={int(widest['n'])} < 400（精確度隨樣本數下降）",
           "若最寬的反而是大群組，檢查 CI 計算")


def m4_2(c):
    p = c.need("figures/forest.svg")     # 還沒畫 → SKIP，不是 FAIL
    c.ok("figures/forest.svg 存在")
    svg = p.read_text(errors="ignore")
    c.want(len(svg) > 3000, f"forest.svg 內容非空（{len(svg) // 1024} KB）")
    low = svg.lower()
    c.want("favour" in low or "favor" in low or "atezo" in low,
           "森林圖有方向標示（favours …）")
    c.want("overall" in low, "森林圖含 Overall 參考列")


if __name__ == "__main__":
    sys.exit(run("Chapter 04 · 次群組一致性",
                 {"4.1": m4_1, "4.2": m4_2}))
