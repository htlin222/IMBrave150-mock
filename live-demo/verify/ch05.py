#!/usr/bin/env python3
"""第 05 章驗收 — 120 種設定的規格曲線 + TMLE 換 estimand。"""
import sys
import numpy as np
from _common import get, run


def m5_1(c):
    m = c.csv("multiverse.csv")
    c.cols(m, ["method", "covset", "hr"], "multiverse")
    if "hr" not in m.columns:
        return

    c.between(len(m), 110, 130, "分析設定數（15 共變數集合 × 8 方法 = 120）")

    if "covset" in m.columns:
        c.between(m["covset"].nunique(), 14, 16, "共變數集合種數")
        names = " ".join(str(x) for x in m["covset"].unique()).lower()
        c.want("full" in names, "含 full 共變數集合")
        c.want(sum(1 for x in m["covset"].unique() if str(x).startswith("drop_")) >= 10,
               "含 ≥10 個 leave-one-out 設定")

    if "method" in m.columns:
        meth = {str(x).lower() for x in m["method"].unique()}
        for want, keys in [("PSM 配對", ["psm", "match"]),
                           ("IPTW 加權", ["iptw", "weight"]),
                           ("迴歸調整", ["regress", "cox", "adjust"])]:
            c.want(any(any(k in x for k in keys) for x in meth), f"含 {want}")

    hr = m["hr"].astype(float).dropna()
    c.near(float(hr.median()), 0.583, 0.030, "120 設定的中位數 HR")
    c.near(float(np.percentile(hr, 25)), 0.560, 0.035, "IQR 下界")
    c.near(float(np.percentile(hr, 75)), 0.608, 0.035, "IQR 上界")

    # 誠實檢查：離散度不可被壓掉
    c.between(float(hr.min()), 0.46, 0.56, "全距下界")
    c.between(float(hr.max()), 0.63, 0.78, "全距上界")
    within = float(((hr >= 0.55) & (hr <= 0.61)).mean() * 100)
    c.near(within, 66.0, 12.0, "落在 0.55–0.61 的比例", unit="%")
    c.want(within < 90,
           f"僅 {within:.0f}% 落在窄帶內 —— 這是誠實的離散度，不要宣稱『全部一致』",
           "若接近 100%，可能只跑了少數幾種設定")

    # 沒有任何設定翻轉方向
    c.want(float(hr.max()) < 1.0,
           "沒有任何設定的 HR 跨過 1.0（結論方向穩健）")

    if "hi" in m.columns or "ci_high" in m.columns:
        col = "hi" if "hi" in m.columns else "ci_high"
        n_cross = int((m[col].astype(float) >= 1.0).sum())
        c.want(n_cross == 0, "沒有任何設定的 CI 蓋到 1.0",
               f"有 {n_cross} 個設定的 CI 上界 ≥ 1.0")

    c.file("multiverse.py", "multiverse.py 存在（可重跑）")


def m5_2(c):
    p = c.need("figures/multiverse.png")  # 還沒畫 → SKIP，不是 FAIL
    c.ok("figures/multiverse.png 存在")
    c.want(p.stat().st_size > 40_000,
           f"multiverse.png 內容非空（{p.stat().st_size // 1024} KB）",
           "檔案過小，可能只畫了空白畫布")


def m5_3(c):
    j = c.json("tmle.json")

    true_rd = get(j, "rd_true", get(j, "true"))
    tmle = get(j, "tmle", get(j, "tmle_est"))
    if isinstance(tmle, dict):
        tmle = tmle.get("est", tmle.get("estimate"))

    if true_rd is not None:
        c.near(float(true_rd), -0.154, 0.015, "資料生成機制的真實風險差")
    c.near(float(tmle) if tmle is not None else np.nan, -0.150, 0.030,
           "TMLE 估計的 12 個月死亡風險差")

    naive = get(j, "naive")
    if naive is not None:
        c.near(float(naive), -0.228, 0.035, "天真 complete-case 風險差")
        if true_rd is not None:
            bias_n = abs(float(naive) - float(true_rd))
            bias_t = abs(float(tmle) - float(true_rd)) if tmle is not None else 9
            c.want(bias_t < bias_n,
                   f"TMLE 偏誤 {bias_t:.3f} < 天真偏誤 {bias_n:.3f}",
                   "雙重穩健估計應該比天真估計更接近真值")

    for key, want, tol, label in [
        ("gcomp", -0.168, 0.035, "G-computation"),
        ("iptw", -0.140, 0.035, "IPTW"),
        ("aipw", -0.144, 0.035, "AIPW"),
    ]:
        v = get(j, key)
        if isinstance(v, dict):
            v = v.get("est", v.get("estimate"))
        if v is not None:
            c.near(float(v), want, tol, label)
        else:
            c.note(f"tmle.json 沒有 {label} —— 四種估計都跑才看得出差異")

    se = get(j, "tmle_se", get(j, "se"))
    if se is not None:
        c.near(float(se), 0.037, 0.015, "TMLE 影響函數 SE")

    # estimand 提醒：風險差不可能落在 HR 的量級
    if tmle is not None and float(tmle) > 0:
        c.bad("TMLE 風險差為正",
              "負值代表 atezo+bev 組死亡較少；若為正，檢查 treat−control 的順序")
    if tmle is not None and abs(float(tmle)) > 0.6:
        c.bad("TMLE 值不像風險差",
              "風險差的單位是機率（−1 到 1），不是 hazard ratio")

    c.file("tmle.py", "tmle.py 存在（可重跑）")


if __name__ == "__main__":
    sys.exit(run("Chapter 05 · 試著把結論弄壞",
                 {"5.1": m5_1, "5.2": m5_2, "5.3": m5_3}))
