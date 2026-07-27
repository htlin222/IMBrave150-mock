#!/usr/bin/env python3
"""第 08 章驗收 — build 管線、PDF/DOCX/TeX、preprint 發佈包。"""
import hashlib
import os
import re
import shutil
import subprocess
import sys

from _common import WS, Skip, run
from ch06 import MS, _has

DIST = WS / "dist"


def m8_1(c):
    b = c.need("build.sh")
    c.ok("build.sh 存在")
    c.want(os.access(b, os.X_OK), "build.sh 可執行",
           "chmod +x live-demo/workspace/build.sh")

    src = b.read_text(errors="ignore")
    c.want("--citeproc" in src, "build.sh 有加 --citeproc",
           "忘了加不會報錯，[@key] 會原樣印在 PDF 上")
    c.want("csl" in src, "build.sh 指定了 CSL 樣式")
    c.want("cd " in src, "build.sh 有切到 manuscript/（圖片相對路徑才會對）")
    for fmt in ["pdf", "docx", "tex"]:
        c.want(f".{fmt}" in src, f"build.sh 產出 {fmt.upper()}")

    ms = c.need("manuscript/manuscript.md").read_text(errors="ignore")
    fm = re.match(r"(?s)^---\n(.*?)\n---", ms)
    c.want(fm is not None, "manuscript.md 有 YAML front matter")
    if fm:
        y = fm.group(1)
        for k in ["title", "bibliography", "csl"]:
            c.want(re.search(rf"(?m)^{k}\s*:", y), f"front matter 有 {k}")

    for f in ["manuscript/refs.bib", "manuscript/ama.csl"]:
        c.file(f)

    # 工具鏈
    for tool, why in [("pandoc", "轉檔"), ("tectonic", "LaTeX 引擎")]:
        c.want(shutil.which(tool) is not None, f"{tool} 可用（{why}）")
    svg = shutil.which("rsvg-convert") or shutil.which("inkscape")
    c.want(svg is not None, "有 SVG→PDF 轉換器（rsvg-convert / inkscape）",
           "LaTeX 不吃 SVG；缺這個時錯誤訊息會偽裝成 LaTeX 問題")


def _dist(c, name):
    p = DIST / name
    if not p.exists():
        raise Skip(f"dist/{name}")
    return p


def m8_2(c):
    p = _dist(c, "manuscript.pdf")
    size = p.stat().st_size
    c.want(p.read_bytes()[:5] == b"%PDF-", "manuscript.pdf 是合法 PDF")
    c.want(size > 20_000, f"PDF 大小 {size // 1024} KB（> 20 KB）",
           "過小通常代表圖片沒嵌進去")

    # 🔴 citeproc 沒跑的話 [@key] 會留在內文
    ms = (MS / "manuscript.md").read_text(errors="ignore")
    keys = set(re.findall(r"\[@([\w:.-]+)\]", ms))
    if keys and shutil.which("pandoc"):
        r = subprocess.run(
            ["pandoc", "manuscript.md", "--citeproc",
             "--bibliography=refs.bib", "--csl=ama.csl", "-t", "plain"],
            cwd=MS, capture_output=True, text=True)
        out = r.stdout
        leftover = [k for k in keys if f"[@{k}]" in out]
        c.want(not leftover, "所有 [@key] 都被 citeproc 解析了",
               f"未解析：{leftover} —— key 拼錯時 pandoc 只警告不報錯")
        c.want(re.search(r"(?m)^\s*\d+\.\s+\w+ \w{1,3}[,.]", out) is not None,
               "參考文獻已排成 AMA 編號格式")
        c.want("doi:" in out.lower() or "https://doi.org" in out.lower(),
               "參考文獻含 DOI")
    elif keys:
        c.note("pandoc 不可用，略過引用排版檢查")


def m8_3(c):
    d = _dist(c, "manuscript.docx")
    c.want(d.read_bytes()[:2] == b"PK", "manuscript.docx 是合法 DOCX（zip）")
    c.want(d.stat().st_size > 10_000, f"DOCX 大小 {d.stat().st_size // 1024} KB")

    t = _dist(c, "manuscript.tex").read_text(errors="ignore")
    c.want("\\documentclass" in t, "manuscript.tex 是完整可編譯檔（-s）")
    c.want("[@" not in t, "TeX 內沒有殘留 [@key]")

    figs = DIST / "figures"
    if figs.is_dir():
        n = len(list(figs.glob("*")))
        c.ok(f"dist/figures/ 另存了 {n} 個圖檔（多數期刊要求分開上傳）")
    else:
        c.note("沒有 dist/figures/ —— 期刊多半要求圖檔與正文分開上傳")


ORCID_RE = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


def m8_4(c):
    c.want(DIST.is_dir(), "dist/ 存在")
    if not DIST.is_dir():
        raise Skip("dist/")

    readme = _dist(c, "README.md").read_text(errors="ignore")
    c.want(_has(readme, "reproduc", "重現", "how to"), "dist/README.md 說明如何重現")
    c.want(_has(readme, "synthetic", "simulated", "合成"),
           "dist/README.md 有合成資料聲明")

    meta = _dist(c, "metadata.yaml").read_text(errors="ignore")
    for k in ["title", "authors?", "abstract", "license", "disclaimer"]:
        c.want(re.search(rf"(?mi)^[ \t]*{k}[ \t]*:", meta),
               f"metadata.yaml 有 {k.rstrip('?')}")
    c.want(_has(meta, "synthetic", "合成"), "metadata 的 disclaimer 提到合成資料")

    # 🔴 ORCID 不可以編（[ \t]* 而非 \s*，否則會吃掉換行誤判下一行）
    for m in re.finditer(r"(?mi)^[ \t]*orcid[ \t]*:[ \t]*(\S.*)$", meta):
        v = m.group(1).strip().strip('"\'')
        if v and v.lower() not in {"null", "~", "none", "tbd"}:
            c.want(ORCID_RE.match(v) is not None,
                   f"ORCID 格式合法：{v}",
                   "格式不對就是編的 —— 沒有就留空")

    # checksum 必須涵蓋所有檔案且為最新
    sums = _dist(c, "CHECKSUMS.txt").read_text(errors="ignore")
    listed = {}
    for line in sums.splitlines():
        parts = line.split()
        if len(parts) == 2:
            listed[os.path.basename(parts[1])] = parts[0]

    actual = [p for p in DIST.iterdir()
              if p.is_file() and p.name != "CHECKSUMS.txt"]
    missing = [p.name for p in actual if p.name not in listed]
    c.want(not missing, f"CHECKSUMS.txt 涵蓋 dist 全部 {len(actual)} 個檔案",
           f"漏了：{missing}")

    stale = []
    for p in actual:
        if p.name in listed:
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            if h != listed[p.name]:
                stale.append(p.name)
    c.want(not stale, "CHECKSUMS.txt 與檔案內容相符",
           f"已過期：{stale} —— checksum 要在最後一次 build 之後才算")

    # 發佈前檢核
    val = WS / "manuscript" / "refs_validated.csv"
    if val.exists():
        import pandas as pd
        v = pd.read_csv(val)
        ok = (v["status"].astype(str).str.upper() == "VERIFIED").all()
        c.want(bool(ok), "所有引用皆為 VERIFIED")

    for f in ["title.md", "abstract.md", "manuscript.md"]:
        p = MS / f
        if p.exists():
            c.want(_has(p.read_text(errors="ignore"),
                        "synthetic", "simulated", "合成"),
                   f"{f} 含合成資料聲明")


if __name__ == "__main__":
    sys.exit(run("Chapter 08 · build 與 preprint 發佈",
                 {"8.1": m8_1, "8.2": m8_2, "8.3": m8_3, "8.4": m8_4}))
