#!/usr/bin/env python3
"""第 02 章驗收 — 天真估計、Table 1、傾向分數配對、平衡。"""
import sys
import numpy as np
from _common import WS, get, run, smd

COVS = ["age", "ecog_ps", "child_pugh_score", "afp_ge_400",
        "macrovascular_invasion", "extrahepatic_spread", "bclc_C",
        "albi_ge2", "varices_at_baseline", "male", "asia"]

# 配對前的真實 |SMD|（實跑值），用來確認 Table 1 沒算錯
SMD_BEFORE = {
    "age": 0.210, "ecog_ps": 0.157, "child_pugh_score": 0.005,
    "afp_ge_400": 0.228, "macrovascular_invasion": 0.225,
    "extrahepatic_spread": 0.204, "bclc_C": 0.040, "albi_ge2": 0.178,
    "varices_at_baseline": 0.176, "male": 0.038, "asia": 0.115,
}


def m2_1(c):
    j = c.json("naive_hr.json")
    c.near(float(get(j, "hr", np.nan)), 0.505, 0.030, "天真未調整 OS HR")
    c.eq(int(get(j, "n", 0)), 1800, "世代人數")
    if get(j, "n_treat") is not None:
        c.eq(int(j["n_treat"]), 962, "Atezo+Bev 人數")
        c.eq(int(j["n_control"]), 838, "Sorafenib 人數")
    lo, hi = get(j, "ci_low"), get(j, "ci_high")
    if lo is not None and hi is not None:
        c.want(float(hi) < 1.0, f"95% CI 上界 {float(hi):.2f} < 1.0")
        c.want(float(lo) < float(hi), "CI 上下界順序正確")
    hr = float(get(j, "hr", 1))
    if hr < 0.52:
        c.note("這個數字比真值 0.58 更「好看」—— 偏誤讓結果更漂亮，這正是危險之處")


def m2_2(c):
    t = c.csv("baseline_table1.csv")
    c.cols(t, ["covariate", "smd"], "baseline_table1")
    if "covariate" not in t.columns or "smd" not in t.columns:
        return

    got = {str(r.covariate): abs(float(r.smd)) for r in t.itertuples()}
    missing = [k for k in COVS if k not in got]
    c.want(not missing, f"11 個共變數全部列出", f"缺少：{missing}")

    wrong = []
    for k, want in SMD_BEFORE.items():
        if k in got and abs(got[k] - want) > 0.035:
            wrong.append(f"{k}: 得 {got[k]:.3f} 期望 {want:.3f}")
    c.want(not wrong, "各共變數 |SMD| 與實跑值相符",
           "；".join(wrong) + "  ← SMD 分母應為兩組變異數平均後開根號")

    big = [k for k, v in got.items() if v > 0.15 and k in SMD_BEFORE]
    c.want(len(big) >= 6, f"|SMD| > 0.15 的共變數有 {len(big)} 個（應 ≥ 6）",
           f"實得 {sorted(big)}")

    # 方向一致性：預後不良因子應該都偏向 sorafenib 組
    signed = {str(r.covariate): float(r.smd) for r in t.itertuples()}
    neg = [k for k in ["age", "ecog_ps", "afp_ge_400", "macrovascular_invasion",
                       "extrahepatic_spread", "albi_ge2", "varices_at_baseline"]
           if signed.get(k, 0) < 0]
    c.want(len(neg) >= 6,
           f"{len(neg)}/7 個預後不良因子在 atezo 組較低（同方向偏移）",
           "若方向散亂，可能是 treat 定義反了")


def _matched(c):
    return c.csv("matched.csv")


def m2_3(c):
    m = _matched(c)
    n = len(m)
    pairs = m["pair_id"].nunique() if "pair_id" in m.columns else n // 2

    c.near(pairs, 706, 60, "配對成功對數")
    c.eq(n, pairs * 2, "配對後總人數 = 對數 × 2")

    # 🔴 不放回：ID 不可重複
    if "patient_id" in m.columns:
        dup = int(m["patient_id"].duplicated().sum())
        c.want(dup == 0, "patient_id 無重複（配對確實無放回）",
               f"有 {dup} 筆重複 —— 忘了把用過的對照標記成 inf")

    # 兩組人數相等
    if "treat" in m.columns:
        t1, t0 = int((m.treat == 1).sum()), int((m.treat == 0).sum())
        c.want(t1 == t0, f"兩組人數相等（{t1} vs {t0}）", "1:1 配對兩組必須一樣多")

    # 🔴 卡尺量級：0.2×SD(logit PS) ≈ 0.114；若用了 0.2×SD(PS) 會小一個量級
    if "logit_ps" in m.columns:
        cal = 0.2 * float(m["logit_ps"].std())
        c.between(cal, 0.06, 0.20,
                  "0.2 × SD(logit PS) 的量級（配對後樣本上重算）")
    if "ps" in m.columns:
        ps = m["ps"].astype(float)
        c.between(float(ps.min()), 0.0, 0.45, "傾向分數最小值")
        c.between(float(ps.max()), 0.55, 1.0, "傾向分數最大值")

    # 🔴 AFP 陷阱：配對世代必須仍含 Gamma 三站
    if "hospital_id" in m.columns:
        h = set(m["hospital_id"])
        gamma_left = {"H03", "H06", "H09"} & h
        c.want(len(gamma_left) == 3,
               "Gamma 三站（H03/H06/H09）仍在配對世代中",
               f"只剩 {sorted(gamma_left)} —— 傾向分數模型用了連續 afp_ng_ml，"
               "complete-case 把整整三家醫院刪掉了")
        c.eq(len(h), 10, "配對世代涵蓋的醫院數")

    c.file("psm.py", "psm.py 存在（可重跑）")


def m2_4(c):
    b = c.csv("balance.csv")
    c.cols(b, ["covariate", "smd_before", "smd_after"], "balance")
    if not {"covariate", "smd_before", "smd_after"} <= set(b.columns):
        return

    after = {str(r.covariate): abs(float(r.smd_after)) for r in b.itertuples()}
    before = {str(r.covariate): abs(float(r.smd_before)) for r in b.itertuples()}

    c.want(len(after) >= 11, f"balance.csv 涵蓋 {len(after)} 個共變數（應 ≥ 11）")

    worst = max(after.values()) if after else 9
    c.le(round(worst, 3), 0.10, "配對後最大 |SMD|")
    if worst <= 0.05:
        c.ok("配對後全部 |SMD| < 0.05（遠優於 0.10 門檻）")

    # before 必須來自配對前全體，不可與 after 雷同
    same = sum(1 for k in after if k in before and abs(after[k] - before[k]) < 0.01)
    c.want(same <= 4,
           f"before / after 有明顯差異（僅 {same} 個共變數幾乎相同）",
           "smd_before 可能誤用了配對後的資料 —— 應取自 pooled.csv")

    improved = [k for k in after if k in before and before[k] > 0.15
                and after[k] < 0.05]
    c.want(len(improved) >= 5,
           f"{len(improved)} 個原本嚴重失衡的共變數已收斂到 |SMD| < 0.05")

    for f in ["figures/love_plot.svg", "figures/ps_overlap.svg"]:
        c.file(f)


if __name__ == "__main__":
    sys.exit(run("Chapter 02 · 未調整的答案在說謊",
                 {"2.1": m2_1, "2.2": m2_2, "2.3": m2_3, "2.4": m2_4}))
