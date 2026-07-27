#!/usr/bin/env python3
"""
第 06 章驗收 — IMRaD 手稿 + 數字稽核。

Mission 6.4 的稽核是這一章的重點：把手稿裡所有「結果型數字」抓出來，
逐一比對 workspace/ 產出的檔案。找不到出處的，就是編的。
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from _common import WS, run

MS = WS / "manuscript"

# 結構性常數：方法學裡本來就會出現的「分析選擇」，不算「結果宣稱」。
# 判準：這個數字是你「決定」的（門檻、卡尺、截斷界、換算係數），
# 而不是資料「算出來」的。算出來的一律要有出處。
STRUCTURAL = {
    0.1, 0.2, 0.25, 0.5, 1.0, 2.0, 0.05, 1.1, 17.1, 10.0, 1.96,
    12.0, 18.0, 24.0, 6.0, 95.0, 100.0, 400.0, 120.0, 150.0, 1.0e-3,
    0.02, 0.98,          # positivity 截斷界
    1e-8, 1e-6,          # ridge 穩定項
}
# 必列的七項限制（關鍵詞任一命中即算）
LIMITATIONS = [
    ("合成資料", ["synthetic", "simulated", "合成", "模擬"]),
    ("無未測量干擾是設計出來的", ["unmeasured", "未測量", "by design", "設計"]),
    ("未配對的 treated / ATT", ["att", "unmatched", "256", "未配對"]),
    ("配對群集未處理", ["cluster", "paired", "群集", "配對結構", "robust standard"]),
    ("次群組為描述性且未檢定交互作用", ["interaction", "exploratory", "交互作用", "描述性"]),
    ("PFS 偏離較大", ["progression-free", "pfs", "0.63"]),
    ("敏感性分析的離散度", ["0.515", "0.699", "range", "66", "全距"]),
]


def _read(c, name):
    p = MS / name
    if not p.exists():
        from _common import Skip
        raise Skip(f"manuscript/{name}")
    return p.read_text(errors="ignore")


def _has(text, *keys):
    low = text.lower()
    return any(k.lower() in low for k in keys)


# --------------------------------------------------------------------------
def m6_1(c):
    t = _read(c, "methods.md")
    c.ok(f"methods.md 存在（{len(t)} 字元）")

    covs = ["age", "ecog", "child", "afp", "macrovascular", "extrahepatic",
            "bclc", "albi", "varice"]
    hit = [k for k in covs if k in t.lower()]
    c.want(len(hit) >= 8, f"傾向分數共變數列出 {len(hit)}/9 類",
           f"缺少：{[k for k in covs if k not in hit]} —— 不要憑記憶寫，從 psm.py 的 COVS 讀")

    c.want(_has(t, "0.114", "0.2", "caliper", "卡尺"), "有寫出卡尺設定")
    c.want(_has(t, "1:1", "one-to-one", "nearest"), "有寫出配對方式（1:1 最近鄰）")
    c.want(_has(t, "without replacement", "無放回", "不放回"),
           "有寫出「無放回」",
           "有無放回會改變標準誤，別人重做不出來就是不可重現")
    c.want(_has(t, "standardi"), "有寫出以 SMD 評估平衡")
    c.want(_has(t, "synthetic", "simulated", "合成", "模擬"),
           "Methods 內有合成資料聲明",
           "讀者必須在讀到任何數字之前就知道這不是真實病人")
    c.want(_has(t, "afp") and _has(t, "400"),
           "有說明使用 AFP ≥400 二元變數",
           "Gamma 站無連續 AFP 是本研究的關鍵資料限制，Methods 必須交代")
    c.want(_has(t, "att", "average treatment effect on the treated", "estimand"),
           "有 estimand 陳述（配對後為 ATT）",
           "配對丟掉 256 個 treated，估的不是 ATE")
    c.want(_has(t, "lifelines", "python", "version"), "有軟體與版本")
    c.want(not _has(t, "standard methods were applied", "standard propensity"),
           "沒有『standard methods were applied』這種空話")


def m6_2(c):
    t = _read(c, "results.md")
    c.ok(f"results.md 存在（{len(t)} 字元）")

    for label, keys in [
        ("世代人數 1,800", ["1800", "1,800"]),
        ("兩組人數 962 / 838", ["962"]),
        ("天真 HR 0.505", ["0.505", "0.51"]),
        ("配對 706 對", ["706"]),
        ("配對世代 OS HR 0.578", ["0.578", "0.58"]),
        ("PFS HR 0.632", ["0.632", "0.63"]),
        ("次群組全距 0.51–0.63", ["0.51", "0.63"]),
        ("多重設定中位數 0.583", ["0.583", "0.58"]),
        ("TMLE 風險差 −0.150", ["-0.150", "−0.150", "0.150", "0.15"]),
    ]:
        c.want(_has(t, *keys), f"有報告{label}")

    # 誠實檢查：離散度不可省略
    c.want(_has(t, "0.515") and _has(t, "0.699"),
           "有報告 120 設定的全距 0.515–0.699",
           "只報中位數不報離散度是選擇性報告")
    c.want(_has(t, "66"), "有報告『66% 落在 0.55–0.61』",
           "這是誠實度的關鍵數字，不可寫成『大多數』")
    c.want(_has(t, "256", "unmatched", "未配對"),
           "有交代 256 個 treated 未配對成功")

    # 出處註記
    n_src = len(re.findall(r"<!--\s*src:", t))
    c.want(n_src >= 5, f"有 {n_src} 個來源註記 <!-- src: … -->（應 ≥ 5）",
           "每個小節都要指得回 workspace/ 的檔案")

    # Results 不該解釋
    c.want(not _has(t, "we conclude", "this proves", "證明了", "demonstrates that"),
           "Results 沒有出現結論性語句（那是 Discussion 的工作）")


def m6_3(c):
    t = _read(c, "discussion.md")
    c.ok(f"discussion.md 存在（{len(t)} 字元）")

    missing = [name for name, keys in LIMITATIONS if not _has(t, *keys)]
    c.want(not missing, f"七項必列限制全部涵蓋",
           f"缺少：{missing}")

    c.want(_has(t, "finn", "imbrave", "nejm", "1915745"),
           "有與 IMbrave150 原始試驗比較")
    c.want(not _has(t, "proves", "prove causality", "establishes causality"),
           "結論語氣未過度宣稱因果",
           "觀察性資料可以 support / be consistent with，不能 prove")
    c.want(_has(t, "limitation", "限制"), "有明確的 Limitations 段落")


# --------------------------------------------------------------------------
RESULT_NUMS = ["0.578", "0.505", "0.583", "0.632", "0.150", "0.154"]


def _words(t):
    return len(re.sub(r"[^\w\s]", " ", t).split())


def m6_4(c):
    t = _read(c, "introduction.md")
    c.ok(f"introduction.md 存在（{_words(t)} 字）")

    leaked = [n for n in RESULT_NUMS if n in t]
    c.want(not leaked, "Introduction 沒有洩漏結果數字",
           f"出現了 {leaked} —— 那是 Results 的工作，Introduction 只講問題")

    c.want(_has(t, "[@", "\\cite", "doi", "10."),
           "問題缺口段有文獻引用（可先用 [@key] 佔位）",
           "沒有引用的「一般認為」等於你自己認為")
    c.between(_words(t), 120, 520, "Introduction 字數")

    paras = [p for p in t.split("\n\n") if len(p.strip()) > 60 and not p.strip().startswith("#")]
    c.between(len(paras), 2, 5, "Introduction 段落數（倒金字塔三段）")

    c.want(_has(t, "aim", "objective", "we asked", "this study", "we set out",
                "本研究", "目的"),
           "結尾有研究目的陳述")
    c.want(_has(t, "synthetic", "simulated", "合成", "模擬"),
           "有交代這是合成世代")


def m6_5(c):
    t = _read(c, "conclusions.md")
    c.ok(f"conclusions.md 存在（{_words(t)} 字）")

    c.le(_words(t), 130, "Conclusions 字數（兩三句就夠）")

    banned = [w for w in ["proves", "proven", "establishes causality",
                          "validates the method", "demonstrates that",
                          "confirms that"] if w in t.lower()]
    c.want(not banned, "沒有過強的因果宣稱", f"出現了 {banned}")

    c.want(_has(t, "synthetic", "simulated", "in this setting", "measured",
                "本研究條件", "合成"),
           "結論有限定條件（不是無條件宣稱 PSM 可用）",
           "我們驗證的是『所有干擾因子都被測量時』PSM 可還原真值 —— 條件拿掉就是假的")

    c.want(not _has(t, "further research is needed", "more studies are needed",
                    "需要更多研究"),
           "沒有『需要更多研究』這種廢話句")


def m6_6(c):
    t = _read(c, "abstract.md")
    n = _words(t)
    c.ok(f"abstract.md 存在（{n} 字）")
    c.le(n, 260, "Abstract 字數（上限 250，容許 10 字誤差）")

    for sec in ["background", "method", "result", "conclusion"]:
        c.want(sec in t.lower(), f"結構式摘要含 {sec.capitalize()} 段")

    for label, keys in [("世代人數", ["1800", "1,800"]),
                        ("配對後 OS HR", ["0.578", "0.58"]),
                        ("天真估計", ["0.505", "0.51"]),
                        ("配對數", ["706"])]:
        c.want(_has(t, *keys), f"Results 段有{label}")

    c.want(not re.search(r"\[@\w+\]", t), "Abstract 內沒有文獻引用")
    c.want(not _has(t, "significantly improved", "confirms", "proves"),
           "Abstract 的結論沒有比正文強（無 spin）")


def m6_7(c):
    t = _read(c, "title.md")
    c.ok(f"title.md 存在（{len(t)} 字元）")

    cands = re.findall(r"^\s*(?:[-*]|\d+[.)])\s+\S.*$", t, flags=re.M)
    c.want(len(cands) >= 5, f"提供了 {len(cands)} 個標題候選（應 ≥ 5）")

    c.want(_has(t, "synthetic", "simulated", "合成", "模擬"),
           "標題含 synthetic / simulated",
           "這篇若被單獨轉發，標題是唯一會被讀到的東西 —— 沒有這個字就是誤導")

    c.want(_has(t, "selected", "chosen", "選定", "final"),
           "有明確指出選定哪一個")
    c.want(_has(t, "running title", "running head", "短標"),
           "有 running title")

    hr_in_title = re.search(r"(?i)(hazard ratio|HR)\s*(=|of)?\s*0\.\d", t)
    c.want(not hr_in_title, "標題沒有塞 HR 數字")


DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Za-z0-9]+")


def m6_8(c):
    bib = c.need("manuscript/refs.bib").read_text(errors="ignore")
    c.ok(f"refs.bib 存在（{len(bib)} 字元）")

    val = c.csv("manuscript/refs_validated.csv")
    c.cols(val, ["key", "doi", "status"], "refs_validated")
    if "status" not in val.columns:
        return

    bad = val[val["status"].astype(str).str.upper() != "VERIFIED"]
    c.want(len(bad) == 0,
           f"全部 {len(val)} 筆引用都通過 Crossref 驗證",
           f"未驗證：{list(bad.get('key', []))} —— 未驗證的引用必須從稿子裡刪掉")

    # 每筆都要有格式合法的 DOI
    for r in val.itertuples():
        doi = str(getattr(r, "doi", ""))
        if not DOI_RE.fullmatch(doi.strip()):
            c.bad(f"{r.key} 的 DOI 格式不合法：{doi}",
                  "不要憑記憶生成 DOI —— 先搜尋拿到真 DOI，再驗證")
    if all(DOI_RE.fullmatch(str(r).strip()) for r in val.get("doi", [])):
        c.ok(f"{len(val)} 筆 DOI 格式皆合法")

    # 六個欄位的比對結果都要留下紀錄
    match_cols = [x for x in val.columns if x.endswith("_match")]
    c.want(len(match_cols) >= 4,
           f"逐欄比對紀錄齊全（{len(match_cols)} 個 *_match 欄）",
           "至少要記錄標題／作者／年份／期刊的比對結果")

    # bib 的 key 與手稿的 [@key] 要對得上
    bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib))
    used = set()
    for f in ["introduction.md", "discussion.md", "manuscript.md"]:
        p = MS / f
        if p.exists():
            used |= set(re.findall(r"\[@([\w:.-]+)\]", p.read_text(errors="ignore")))
    orphan = sorted(used - bib_keys)
    c.want(not orphan, "手稿引用的 key 都在 refs.bib 裡",
           f"找不到：{orphan} —— pandoc 只會警告然後把 [@key] 原樣印出來")

    csl = MS / "ama.csl"
    c.want(csl.exists(), "ama.csl 已下載")
    if csl.exists():
        head = csl.read_text(errors="ignore")[:2000]
        c.want("<style" in head and "csl" in head, "ama.csl 是合法的 CSL 檔")


# --------------------------------------------------------------------------
def _whitelist():
    """從 workspace 的產出檔蒐集所有『合法數字』。"""
    vals = set()

    def add(x):
        try:
            f = float(x)
        except (TypeError, ValueError):
            return
        if not np.isfinite(f):
            return
        vals.add(abs(f))
        if 0 < abs(f) < 1:          # 0.256 也可能以 25.6% 出現
            vals.add(abs(f) * 100)
        if abs(f) > 1:              # 25.6 也可能以 0.256 出現
            vals.add(abs(f) / 100)

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o:
                walk(v)
        else:
            add(o)

    for p in WS.glob("*.json"):
        try:
            walk(json.loads(p.read_text()))
        except Exception:  # noqa: BLE001
            pass

    import pandas as pd
    for name in ["subgroups.csv", "balance.csv", "baseline_table1.csv",
                 "site_profile.csv"]:
        p = WS / name
        if p.exists():
            try:
                d = pd.read_csv(p)
                for col in d.select_dtypes("number"):
                    for v in d[col]:
                        add(v)
            except Exception:  # noqa: BLE001
                pass

    # 資料集規模與 multiverse 的摘要統計
    for name, key in [("pooled.csv", "n"), ("matched.csv", "n")]:
        p = WS / name
        if p.exists():
            try:
                d = pd.read_csv(p)
                add(len(d))
                if "pair_id" in d.columns:
                    add(d["pair_id"].nunique())
                if "treat" in d.columns:
                    add(int((d.treat == 1).sum()))
                    add(int((d.treat == 0).sum()))
                    add(len(d) - int((d.treat == 1).sum()) * 2 + len(d))
            except Exception:  # noqa: BLE001
                pass

    p = WS / "multiverse.csv"
    if p.exists():
        try:
            d = pd.read_csv(p)
            hr = d["hr"].astype(float).dropna()
            for v in [len(d), hr.median(), np.percentile(hr, 25),
                      np.percentile(hr, 75), hr.min(), hr.max(),
                      ((hr >= 0.55) & (hr <= 0.61)).mean() * 100]:
                add(v)
        except Exception:  # noqa: BLE001
            pass

    # 962 - 706 = 256（未配對的 treated），屬於可推導的合法數字
    add(256)
    return vals


# 尾端只擋「後面還有數字」，句尾的 0.743. 也要抓得到
NUM_RE = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?!\d)")
PCT_RE = re.compile(r"^\s*(%|per\s*cent|percent|％)", re.I)


def _worth_scanning(tok, tail):
    """只稽核『結果型』數字：有小數、夠大的整數、或帶百分號的。"""
    if "," in tok:
        return True
    if "." in tok:
        return len(tok.split(".")[1]) >= 2
    if PCT_RE.match(tail):          # 66 per cent / 94% 這種兩位數也要查
        return True
    return len(tok) >= 3


def _traceable(tok, x, allowed):
    """依手稿的書寫精度四捨五入比對 —— 0.58 可對回 0.578，但 0.612 對不回 0.61。"""
    dp = len(tok.split(".")[1]) if "." in tok else 0
    xr = round(x, dp)
    return any(round(v, dp) == xr for v in allowed)


def _scan(text, allowed):
    """抓出手稿裡找不到出處的結果型數字。"""
    # 移除不該掃的區塊
    text = re.sub(r"```.*?```", " ", text, flags=re.S)           # 程式碼
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)          # 來源註記
    text = re.sub(r"(?is)\n#+\s*(references|參考文獻)\b.*?(?=\n#+\s|\Z)",
                  " ", text)                                     # 參考文獻整段
    text = re.sub(r"10\.\d{4,}/\S+", " ", text)                  # DOI
    text = re.sub(r"\d{4};\d+(\(\d+\))?:\S*", " ", text)         # 期刊卷期頁碼
    text = re.sub(r"(?i)(figure|table|fig\.?|ref\.?)\s*\d+", " ", text)
    text = re.sub(r"(?i)https?://\S+", " ", text)
    # 套件／語言版本號：三段式（0.30.0）與兩段式（Python 3.12）都要擋
    text = re.sub(r"\b\d+\.\d+\.\d+\b", " ", text)
    text = re.sub(r"(?i)\b(python|lifelines|pandas|numpy|matplotlib|scipy|sklearn|"
                  r"pandoc|tectonic|quarto|biber|R)\s+v?\d+(\.\d+)*", r"\1 ", text)

    bad = []
    for line in text.splitlines():
        for mt in NUM_RE.finditer(line):
            tok = mt.group(1)
            tail = line[mt.end():mt.end() + 12]
            if not _worth_scanning(tok, tail):
                continue
            x = abs(float(tok.replace(",", "")))
            if x in STRUCTURAL or 1900 <= x <= 2100 or x in {0.0, 1.0}:
                continue
            if not _traceable(tok, x, allowed):
                bad.append((tok, line.strip()[:90]))
    return bad


def _claims_audit(c, t, min_rows):
    """claims.csv 出處對照 + 幻覺偵測。6.9 與 6.9-live 共用同一套嚴格度。

    回傳 allowed 集合，供呼叫端再做局部掃描（例如 Abstract）。
    """
    claims = c.csv("manuscript/claims.csv")
    c.cols(claims, ["claim_id", "value", "source_file"], "claims.csv")
    c.want(len(claims) >= min_rows,
           f"claims.csv 有 {len(claims)} 列（應 ≥ {min_rows}）",
           "手稿裡的每個實質數字都要有一列")

    allowed = _whitelist()
    for v in claims.get("value", []):
        try:
            f = abs(float(v))
            allowed.add(f)
            allowed.add(f * 100)
            allowed.add(f / 100)
        except (TypeError, ValueError):
            pass

    if "source_file" in claims.columns:
        missing_src = [str(s) for s in claims["source_file"].unique()
                       if s and not (WS / str(s)).exists()
                       and not (MS / str(s)).exists()]
        c.want(not missing_src, "claims.csv 的來源檔都真的存在",
               f"找不到：{missing_src}")

    bad = _scan(t, allowed)
    if bad:
        c.bad(f"偵測到 {len(bad)} 個無來源的數字宣稱",
              "以下數字在 workspace/ 的任何產出檔與 claims.csv 中都找不到出處")
        seen = set()
        for tok, line in bad:
            if tok in seen:
                continue
            seen.add(tok)
            print(f"      \033[31m{tok}\033[0m  ← {line}")
            if len(seen) >= 12:
                print(f"      … 另有 {len(bad) - 12} 處")
                break
        print("      \033[2m修手稿或回去把分析跑出來 —— 不要改這支稽核腳本。\033[0m")
    else:
        c.ok("未偵測到無來源的數字宣稱")

    return allowed


def m6_9_live(c):
    """現場 60 分鐘短路線的收尾（6.2 之後直接跳這裡）。

    短路線沒做 6.3–6.8，所以手稿裡不會有 Abstract / Introduction /
    Discussion / Conclusions / References —— 這關**不檢查**那些章節。
    但數字稽核的嚴格度與完整版 6.9 完全相同：這才是整場的論點。

    產出檔名刻意與完整路線分開（manuscript-live.md），
    這樣事後補跑完整路線時，6.9 仍然會正確地 SKIP 而不是 FAIL。
    """
    t = _read(c, "manuscript-live.md")
    c.ok(f"manuscript-live.md 存在（{len(t)} 字元）")

    for sec, keys in [
        ("Title（工作標題即可）", ["# "]),
        ("Methods", ["methods", "方法"]),
        ("Results", ["results", "結果"]),
        ("Data / code availability", ["availability", "reproduc", "資料可得"]),
        ("Synthetic data disclaimer", ["synthetic", "simulated", "合成"]),
        ("Figure legends", ["figure 1", "figure legend", "圖說"]),
    ]:
        c.want(_has(t, *keys), f"章節齊全：{sec}")

    c.note("短路線不檢查 Abstract / Introduction / Discussion / Conclusions / "
           "References —— 那些是 Mission 6.3–6.8，走完整路線時跑 --mission 6.9")

    _claims_audit(c, t, min_rows=8)

    # 短路線沒有 Discussion，但這兩項在 Methods 裡就該寫，不因為趕時間而消失
    for name, keys in (LIMITATIONS[0], LIMITATIONS[2]):
        c.want(_has(t, *keys), f"短路線也必須保留：{name}")


def m6_9(c):
    t = _read(c, "manuscript.md")
    c.ok(f"manuscript.md 存在（{len(t)} 字元）")

    for sec, keys in [
        ("Title", ["# "]),
        ("Abstract", ["abstract", "摘要"]),
        ("Introduction", ["introduction", "background", "前言"]),
        ("Methods", ["methods", "方法"]),
        ("Results", ["results", "結果"]),
        ("Discussion", ["discussion", "討論"]),
        ("Conclusions", ["conclusion", "結論"]),
        ("Data / code availability", ["availability", "reproduc", "資料可得"]),
        ("Synthetic data disclaimer", ["synthetic", "simulated", "合成"]),
        ("References", ["reference", "參考文獻"]),
        ("Figure legends", ["figure 1", "figure legend", "圖說"]),
    ]:
        c.want(_has(t, *keys), f"章節齊全：{sec}")

    # ---- 數字出處對照表 + 幻覺偵測 ----
    allowed = _claims_audit(c, t, min_rows=10)

    # ---- Abstract 是幻覺最愛出沒的地方，單獨再掃一次 ----
    mabs = re.search(r"(?is)#+\s*abstract(.*?)(?=\n#+\s|\Z)", t)
    if mabs:
        abad = _scan(mabs.group(1), allowed)
        c.want(not abad, "Abstract 內的數字全部有出處",
               f"可疑：{[x[0] for x in abad][:6]}")

    # ---- 七項限制在完整稿裡也要在 ----
    missing = [name for name, keys in LIMITATIONS if not _has(t, *keys)]
    c.want(not missing, "完整手稿保留了七項限制", f"組稿時掉了：{missing}")


def number_audit(c, why="改稿後"):
    """給第 07 章重複呼叫：每改一輪字就重驗一次數字沒被改壞。"""
    p = MS / "manuscript.md"
    if not p.exists():
        from _common import Skip
        raise Skip("manuscript/manuscript.md")
    t = p.read_text(errors="ignore")

    allowed = _whitelist()
    cl = MS / "claims.csv"
    if cl.exists():
        import pandas as pd
        for v in pd.read_csv(cl).get("value", []):
            try:
                f = abs(float(v))
                allowed |= {f, f * 100, f / 100}
            except (TypeError, ValueError):
                pass

    bad = _scan(t, allowed)
    if bad:
        c.bad(f"{why}偵測到 {len(bad)} 個無來源的數字",
              "潤稿把數字改壞了 —— 這正是每一輪都要重跑稽核的理由")
        for tok, line in bad[:8]:
            print(f"      \033[31m{tok}\033[0m  ← {line}")
    else:
        c.ok(f"{why}數字稽核仍然通過（沒有數字被改壞）")

    missing = [n for n, k in LIMITATIONS if not _has(t, *k)]
    c.want(not missing, f"{why}七項限制仍然齊全", f"掉了：{missing}")


MISSIONS = {
    "6.1": m6_1, "6.2": m6_2, "6.3": m6_3, "6.4": m6_4, "6.5": m6_5,
    "6.6": m6_6, "6.7": m6_7, "6.8": m6_8, "6.9": m6_9,
    # 現場 60 分鐘短路線的收尾：6.2 之後直接跳這個，不需要 6.3–6.8。
    # 走完整路線的人不會產出 manuscript-live.md，這關會 SKIP。
    "6.9-live": m6_9_live,
}

if __name__ == "__main__":
    sys.exit(run("Chapter 06 · 寫稿、引用驗證與數字稽核", MISSIONS))
