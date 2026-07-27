#!/usr/bin/env python3
"""第 07 章驗收 — 獨立審稿、回應、潤稿、去 AI 腔。"""
import re
import statistics
import sys
from pathlib import Path

from _common import WS, Skip, run
from ch06 import LIMITATIONS, MS, _has, _words, number_audit

REVIEWS = MS / "reviews"

ROLE_KEYS = {
    1: ["estimand", "propensity", "caliper", "smd", "positivity", "ipcw",
        "standard error", "cluster"],
    2: ["hepatocellular", "clinical", "child-pugh", "varice", "bevacizumab",
        "prognostic", "ecog"],
    3: ["strobe", "record", "checklist", "flow", "reporting"],
    4: ["reproduc", "version", "rerun", "re-run", "script", "availability",
        "deterministic"],
}

# 常見 AI 腔（Mission 7.4 要清掉）
AI_PHRASES = [
    "delve into", "leverage the", "it is worth noting", "it is important to note",
    "in the realm of", "testament to", "showcase", "intricate", "tapestry",
    "underscore the", "pivotal role", "comprehensive overview", "navigate the",
    "a myriad of", "shed light on", "paradigm shift",
]


def _reviews(c):
    if not REVIEWS.is_dir():
        raise Skip("manuscript/reviews/")
    return sorted(REVIEWS.glob("reviewer*.md"))


def m7_1(c):
    files = _reviews(c)
    c.eq(len(files), 4, "審稿意見檔數")

    texts = {}
    for p in files:
        t = p.read_text(errors="ignore")
        texts[p.name] = t
        c.want(_has(t, "recommendation", "建議"), f"{p.name} 有 Recommendation")

        majors = re.findall(r"^\s*\d+[.)]\s+\S", t, flags=re.M)
        n_major = len(majors)
        sect = re.search(r"(?is)major comments?(.*?)(?=\n#+\s*minor|\Z)", t)
        if sect:
            n_major = len(re.findall(r"^\s*\d+[.)]\s+\S", sect.group(1), flags=re.M))
        c.want(n_major >= 3, f"{p.name} 提出 {n_major} 個 major comment（應 ≥ 3）",
               "一份『沒有問題』的審稿意見等於沒有審")

        # 🔴 審稿人不可以看過教材
        leak = [k for k in ["live-demo/", "mission 2.3", "⚠️ 地雷", "01-aggregate",
                            "02-deconfound", "verify/ch"] if k in t.lower()]
        c.want(not leak, f"{p.name} 沒有讀到教材（獨立審稿）",
               f"出現 {leak} —— subagent 讀了 mission 檔就是對答案，不是審稿")

    # 四個角色必須真的不同
    blob = {n: t.lower() for n, t in texts.items()}
    covered = 0
    for i, keys in ROLE_KEYS.items():
        if any(sum(k in t for k in keys) >= 2 for t in blob.values()):
            covered += 1
    c.want(covered >= 3, f"四種審稿視角涵蓋了 {covered}/4",
           "四個都寫『請仔細審查』等於跑四次同一個審稿人")

    if len(texts) >= 2:
        vals = list(texts.values())
        a = set(re.findall(r"\w{6,}", vals[0].lower()))
        b = set(re.findall(r"\w{6,}", vals[1].lower()))
        jac = len(a & b) / max(1, len(a | b))
        c.le(round(jac, 2), 0.72, "前兩份意見的用詞重疊度（過高代表角色沒分開）")


def m7_2(c):
    log = c.csv("manuscript/review_log.csv")
    c.cols(log, ["id", "verdict", "action_taken"], "review_log")
    if "verdict" not in log.columns:
        return

    v = log["verdict"].astype(str).str.upper()
    n = len(log)
    c.want(n >= 8, f"彙整了 {n} 條意見（四位審稿人應 ≥ 8 條）")

    n_acc = int((v == "ACCEPT").sum())
    n_rej = int((v == "REJECT").sum())
    c.want(n_acc < n, "沒有全部 ACCEPT（那是諂媚，不是回應）",
           f"{n_acc}/{n} 條全接受")
    c.want(n_rej < n, "沒有全部 REJECT（那是防衛，不是回應）",
           f"{n_rej}/{n} 條全駁回")
    c.want(n_acc >= 1, "至少接受了一條意見")

    empty = int(log["action_taken"].isna().sum() +
                (log["action_taken"].astype(str).str.strip() == "").sum())
    c.want(empty == 0, "每一條都有 action_taken", f"{empty} 條留空")

    # REJECT 必須附理由
    if "comment_short" in log.columns:
        short = log[(v == "REJECT") &
                    (log["action_taken"].astype(str).str.len() < 15)]
        c.want(len(short) == 0, "每一條 REJECT 都有技術性理由",
               f"{len(short)} 條理由過短")

    resp = c.need("manuscript/response-to-reviewers.md").read_text(errors="ignore")
    c.ok(f"response-to-reviewers.md 存在（{_words(resp)} 字）")
    ids = [str(x) for x in log["id"]]
    covered = sum(1 for i in ids if i in resp)
    c.want(covered >= max(1, int(len(ids) * 0.8)),
           f"回應涵蓋 {covered}/{len(ids)} 條意見")

    number_audit(c, "回應審稿後 ")


def m7_3(c):
    rep = c.need("manuscript/polish_report.md")
    c.ok(f"polish_report.md 存在（{len(rep.read_text(errors='ignore'))} 字元）")

    t = c.need("manuscript/manuscript.md").read_text(errors="ignore")

    # 圖表必須都被引用且依序
    order = [int(m) for m in re.findall(r"(?i)figure\s+(\d)", t)]
    cited = sorted(set(order))
    c.want(cited == [1, 2, 3, 4], f"Figure 1–4 都有被引用（實得 {cited}）")
    first = {}
    for i, f in enumerate(order):
        first.setdefault(f, i)
    c.want(list(first) == sorted(first), "圖片依序首次出現",
           f"首次出現順序 {list(first)}")

    # 術語一致
    bad_terms = [x for x in ["atezo-bev", "A+B ", "AtezoBev", "atezo+bev"]
                 if x.lower() in t.lower()]
    c.want(not bad_terms, "藥名術語全文一致", f"混用了 {bad_terms}")

    # 小數位一致
    hrs = re.findall(r"(?i)hazard ratio[^.]{0,40}?(\d\.\d+)", t)
    dps = {len(x.split(".")[1]) for x in hrs}
    c.want(len(dps) <= 1 or dps <= {2, 3},
           f"HR 小數位一致（實得 {sorted(dps)} 位）")

    ab = MS / "abstract.md"
    if ab.exists():
        c.le(_words(ab.read_text(errors="ignore")), 260, "Abstract 字數")

    number_audit(c, "潤稿後 ")


def m7_4(c):
    rt = c.need("manuscript/humanize_report.md").read_text(errors="ignore")
    c.ok(f"humanize_report.md 存在（{len(rt)} 字元）")

    t = c.need("manuscript/manuscript.md").read_text(errors="ignore")
    low = t.lower()

    # 🔴 揭露不可以在潤稿時被拿掉 —— 那不是 humanize，是造假
    c.want(_has(t, "use of ai", "ai tools", "ai-assisted", "coding agent",
                "AI 使用", "人工智慧"),
           "手稿保留了 AI 使用揭露聲明",
           "把文字修得像人寫的、卻拿掉揭露，等於謊報作者身分")
    c.want(_has(t, "supervis", "responsible for", "author is responsible", "監督", "負責"),
           "揭露聲明有寫明作者責任歸屬")

    # 只准用 pattern linter，不准用「規避偵測」那一類。
    # 注意：要抓的是「使用」，不是「提及」——報告裡寫「未使用 undetectable 工具」是對的。
    BANNED = ["undetectable", "bypass ai detect", "bypass detector",
              "evade detection", "beat ai detector", "humanize to avoid detection"]
    NEGATION = ["未使用", "沒有使用", "不使用", "不准", "未採用", "避免使用", "禁止",
                "not used", "did not use", "no ", "avoided", "without using",
                "**未**", "never used"]
    offending = []
    for line in rt.splitlines():
        low = line.lower()
        if any(b in low for b in BANNED) and not any(n.lower() in low for n in NEGATION):
            offending.append(line.strip()[:80])
    c.want(not offending, "沒有使用規避 AI 偵測的工具或提示詞",
           f"報告中這幾行像是真的用了：{offending[:3]}"
           " —— 本關的目標是可讀性，不是騙過偵測器")

    # 前後對照：沒有數字就無法證明真的改了
    nums = re.findall(r"(?i)(?:before|前|修改前)\D{0,20}(\d+)", rt)
    after = re.findall(r"(?i)(?:after|後|修改後)\D{0,20}(\d+)", rt)
    if nums and after:
        b, a = int(nums[0]), int(after[0])
        c.want(a <= b, f"AI-tell 問題數 {b} → {a}（下降或持平）")
    else:
        c.note("報告沒有 llmstrip 前後問題數對照 —— 建議補上，才能證明改了什麼")

    found = [p for p in AI_PHRASES if p in low]
    c.want(not found, f"AI 腔詞彙已清除（檢查 {len(AI_PHRASES)} 個）",
           f"仍有：{found}")

    # 空心副詞（statistically significant 要保留）
    hollow = len(re.findall(r"(?i)\b(notably|remarkably|clearly)\b", t))
    c.le(hollow, 2, "空心副詞出現次數")

    # 句長變化：AI 傾向平均句長
    body = re.sub(r"(?s)```.*?```|<!--.*?-->", " ", t)
    sents = [s for s in re.split(r"(?<=[.!?])\s+", body) if 3 < len(s.split()) < 90]
    if len(sents) >= 12:
        lens = [len(s.split()) for s in sents]
        cv = statistics.pstdev(lens) / statistics.mean(lens)
        c.want(cv >= 0.38,
               f"句長變異係數 {cv:.2f}（≥ 0.38 才有人的節奏）",
               "句長過於平均是 AI 文最明顯的特徵 —— 加幾個短句")
        c.want(min(lens) <= 9, f"有短句（最短 {min(lens)} 字）",
               "一個八字的短句，力量比三個長句大")

    # 英式／美式拼法擇一
    brit = len(re.findall(r"(?i)randomis|analys(e|ing)|standardis", t))
    amer = len(re.findall(r"(?i)randomiz|analyz|standardiz", t))
    c.want(brit == 0 or amer == 0,
           f"拼法統一（英式 {brit} 處 / 美式 {amer} 處）",
           "randomised 與 randomized 不可混用")

    number_audit(c, "去 AI 腔後 ")


if __name__ == "__main__":
    sys.exit(run("Chapter 07 · 審稿、回應、潤稿、去 AI 腔",
                 {"7.1": m7_1, "7.2": m7_2, "7.3": m7_3, "7.4": m7_4}))
