#!/usr/bin/env python3
"""第 00 章驗收 — 沙盒建立。"""
import sys
from _common import ROOT, WS, run


def m0_1(c):
    csvs = sorted((WS / "hospitals").glob("*.csv")) if (WS / "hospitals").exists() else []
    c.eq(len(csvs), 10, "workspace/hospitals/ 的 CSV 數")

    ids = {p.name[:3] for p in csvs}
    c.want(ids == {f"H{i:02d}" for i in range(1, 11)},
           "十家醫院 H01–H10 都在", f"實得：{sorted(ids)}")

    c.file("hospitals_meta.csv")
    c.want((WS / "figures").is_dir(), "workspace/figures/ 已建立")

    # 原始資料必須完好 —— 這是「原始資料唯讀」的紀律
    src = sorted((ROOT / "hospitals").glob("*.csv"))
    c.eq(len(src), 10, "repo 根目錄 hospitals/ 未被搬走")

    if csvs and src:
        same = sum(1 for a, b in zip(csvs, src)
                   if a.read_bytes() == b.read_bytes())
        c.eq(same, 10, "副本與原始檔逐位元相同")

    # 常見雜訊
    junk = [p.name for p in WS.rglob("*") if p.name == ".DS_Store"]
    if junk:
        c.note(f"沙盒裡有 {len(junk)} 個 .DS_Store，建議只複製 *.csv")


if __name__ == "__main__":
    sys.exit(run("Chapter 00 · 建沙盒", {"0.1": m0_1}))
