#!/usr/bin/env python3
"""第 01 章驗收 — 方言診斷、harmonise、join meta。"""
import sys
import numpy as np
from _common import WS, run

CANON = [
    "patient_id", "hospital_id", "enroll_year", "arm", "age", "sex", "etiology",
    "ecog_ps", "child_pugh_score", "albi_grade", "albumin_g_dl", "bilirubin_mg_dl",
    "bclc_stage", "afp_ng_ml", "afp_ge_400", "macrovascular_invasion",
    "extrahepatic_spread", "varices_at_baseline", "os_time_months", "os_event",
    "pfs_time_months", "pfs_event", "best_overall_response", "objective_response",
    "grade34_adverse_event", "grade34_hypertension", "ehr_vendor",
]
GAMMA = {"H03", "H06", "H09"}
BETA = {"H02", "H05", "H08"}


def m1_1(c):
    p = c.need("dialects.md")
    txt = p.read_text()
    c.ok("dialects.md 存在")

    low = txt.lower()
    for name, keys, why in [
        ("三種方言都點名了", ["alpha", "beta", "gamma"], "應分出 Alpha/Beta/Gamma"),
        ("指出 Gamma 缺連續 AFP", ["afp"], "應說明 Gamma 只有門檻值"),
        ("指出單位差異", ["g/l", "umol", "µmol"], "應指出 g/L 與 µmol/L"),
        ("指出醫院屬性不在病人檔", ["meta"], "應指出要 join hospitals_meta.csv"),
    ]:
        c.want(any(k in low for k in keys), name, why)

    hits = sum(h.lower() in low for h in
               ["h01", "h02", "h03", "h04", "h05", "h06", "h07", "h08", "h09", "h10"])
    c.want(hits >= 8, f"報告點名了 {hits}/10 家醫院", "應逐家分群，不要只講三個代表")


def _pooled(c):
    df = c.csv("pooled.csv")
    return df


def m1_2(c):
    df = _pooled(c)
    c.eq(len(df), 1800, "pooled.csv 列數")
    c.cols(df, CANON, "正規 schema")

    if not all(x in df.columns for x in CANON):
        return

    c.eq(df["patient_id"].nunique(), 1800, "patient_id 唯一值")
    c.eq(df["hospital_id"].nunique(), 10, "醫院數")

    # 值域
    c.want(set(df["arm"].dropna()) == {"Atezo+Bev", "Sorafenib"},
           "arm 已正規化", f"實得 {sorted(set(df['arm'].dropna()))}")
    c.want(set(df["sex"].dropna()) == {"Male", "Female"},
           "sex 已正規化", f"實得 {sorted(set(df['sex'].dropna()))}")
    c.want(set(df["etiology"].dropna()) == {"HBV", "HCV", "Nonviral"},
           "etiology 大小寫已統一", f"實得 {sorted(set(df['etiology'].dropna()))}")
    c.want(set(df["bclc_stage"].dropna()) <= {"A", "B", "C"},
           "bclc_stage 值域", f"實得 {sorted(set(df['bclc_stage'].dropna()))}")

    cps = df["child_pugh_score"]
    c.want(cps.dtype.kind in "if" and set(cps.dropna().astype(int)) <= {5, 6},
           "child_pugh_score 已從 'A5' 轉成數字 5/6",
           f"dtype={cps.dtype} 值={sorted(set(cps.dropna()))[:5]}")

    # 🔴 單位換算 —— 沒換算的話 albumin 中位數會是 39 而不是 3.9
    alb = df["albumin_g_dl"].median()
    c.near(alb, 3.90, 0.30, "albumin 中位數（g/dL）",
           unit="")
    if alb and alb > 10:
        c.note("albumin 中位數 >10 —— Beta 站的 g/L 沒有 ÷10")
    bil = df["bilirubin_mg_dl"].median()
    c.near(bil, 0.81, 0.20, "bilirubin 中位數（mg/dL）")
    if bil and bil > 5:
        c.note("bilirubin 中位數 >5 —— Beta 站的 µmol/L 沒有 ÷17.1")

    # 🔴 Gamma 站不得有連續 AFP
    g = df[df["hospital_id"].isin(GAMMA)]
    n_fake = int(g["afp_ng_ml"].notna().sum())
    c.want(n_fake == 0, "Gamma 三站（H03/H06/H09）的連續 AFP 全為 NaN",
           f"有 {n_fake} 筆被填了值 —— 那是編造的資料，不是測量")
    c.near(float(df["afp_ng_ml"].isna().mean() * 100), 35.3, 3.0,
           "afp_ng_ml 整體缺失率", unit="%")

    # 沒有人被 dropna 吃掉
    per = df.groupby("hospital_id").size()
    c.want((per >= 75).all() and per.sum() == 1800,
           "十家醫院的列數都完整保留", f"最小一家 {per.min()} 人")

    # 缺失率
    c.between(float(df["albumin_g_dl"].isna().mean() * 100), 2.5, 6.5,
              "albumin 缺失率", unit="%")

    if "ehr_vendor" in df.columns:
        v = df.groupby("ehr_vendor")["hospital_id"].nunique().to_dict()
        c.want(v.get("Alpha") == 4 and v.get("Beta") == 3 and v.get("Gamma") == 3,
               "方言分群 4 / 3 / 3", f"實得 {v}")
        got_beta = set(df.loc[df.ehr_vendor == "Beta", "hospital_id"])
        c.want(got_beta == BETA, "Beta 群是 H02/H05/H08", f"實得 {sorted(got_beta)}")

    c.file("harmonize.py", "harmonize.py 存在（可重跑）")


def m1_3(c):
    df = _pooled(c)
    # join 之後列數不可變
    c.eq(len(df), 1800, "join 之後列數仍是")
    for col in ["hospital_region", "hospital_type"]:
        c.want(col in df.columns, f"{col} 已 join 進來",
               "hospitals_meta.csv 沒 join，第 02 章的 asia 共變數會 KeyError")

    prof = c.csv("site_profile.csv")
    c.eq(len(prof), 10, "site_profile.csv 列數")
    c.cols(prof, ["hospital_id", "n", "pct_atezo"], "site_profile")

    if {"hospital_id", "n", "pct_atezo"} <= set(prof.columns):
        c.eq(int(prof["n"].sum()), 1800, "各院人數加總")
        pct = prof.set_index("hospital_id")["pct_atezo"].astype(float)
        # 允許 0–1 或 0–100 兩種寫法
        scale = 100.0 if pct.max() <= 1.5 else 1.0
        pct = pct * scale
        c.near(float(pct.get("H01", np.nan)), 65.9, 2.0, "H01 atezo 比例", unit="%")
        c.near(float(pct.get("H07", np.nan)), 34.7, 2.0, "H07 atezo 比例", unit="%")
        c.want(float(pct.max() - pct.min()) > 25,
               f"院間處方差異 {pct.max() - pct.min():.1f} 個百分點（> 25）",
               "醫院層級的干擾應該非常明顯")


if __name__ == "__main__":
    sys.exit(run("Chapter 01 · 十家醫院三種方言",
                 {"1.1": m1_1, "1.2": m1_2, "1.3": m1_3}))
