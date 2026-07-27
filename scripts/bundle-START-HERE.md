# 從這裡開始

你手上這包東西，是一場現場 demo 的**完整可執行版本**：
一堆格式各異的醫院檔案，一關一關做成一篇可以投稿的手稿。
講者台上跑的就是這一包，你在自己電腦上跑的會是同一份。

---

## ⚠️ 先講最重要的一件事

**這批資料是合成的。** 模擬自 Finn RS et al., *N Engl J Med* 2020;382:1894-1905
（DOI [10.1056/NEJMoa1915745](https://doi.org/10.1056/NEJMoa1915745)）。
**沒有任何真實病人。** 它不構成關於 atezolizumab、bevacizumab 或 sorafenib
的任何證據。你在這裡產出的手稿，標題、摘要與正文都必須寫明這件事——
教材裡的驗收腳本會檢查這三個地方。

---

## 一、把環境裝起來

需要 Python 3.12。用 [uv](https://docs.astral.sh/uv/)：

```bash
make setup
```

沒有 uv 的話，手動也行：

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

第 08 章（產出 PDF / DOCX）另外需要 `pandoc`、`tectonic`、`rsvg-convert`。
只想做分析（00–05 章）的話不用裝。

## 二、確認可以上路

```bash
cd live-demo && ../.venv/bin/python verify/preflight.py --full
```

它會把「跑到一半才會發現」的問題提前引爆：套件版本相沖、工具鏈缺件、
沙盒不乾淨。看到「可以上台」就沒問題了。

> `add_at_risk_counts() 不可用` 這個黃色提醒是**預期的**，不是環境壞掉。
> 那是 lifelines 0.30.0 + numpy 2.5.1 的已知相沖，Mission 3.2 有寫好的
> 手工替代碼。**不要去 debug 它，也不要升版或降版。**
>
> `requirements.txt` 的版本是**刻意釘死**的，跟講者台上那台一模一樣
> （pandas 3.0.3 / numpy 2.5.1 / lifelines 0.30.0 / matplotlib 3.11.0）。
> 你看到的每一個數字、每一個警告，都會和現場一致。
> 想升級套件請等你把整份做完——升上去那個 TypeError 就不見了，
> 而 Mission 3.2 有一半的教學點正是建立在它身上。

## 三、開始

在這個目錄開一個 [Claude Code](https://claude.com/claude-code) 會話，
然後打一句：

```
開始
```

就這樣。`CLAUDE.md` 會把 agent 導到 `live-demo/`，它會讀 `live-demo/README.md`、
執行 Mission 0.1、跑驗收、用中文講三五行「這一步看到了什麼」，然後**停下來等你**。

之後你用這些短語控制節奏：

| 你說 | 它做 |
|---|---|
| `next` / `繼續` / `下一關` | 做下一個 Mission |
| `skip` | 跳過，並告訴你後面哪幾關會受影響 |
| `why` / `解釋` | 講**為什麼**要這樣做（方法學，可以用術語） |
| `?` / `???` / `蛤` | 用**完全不含術語**的白話重講剛剛那一關發生了什麼 |

`?` 是給「聽不懂」用的求救訊號——它會停下來，用生活比喻重講一次，
不會趁機往下做。`???` 比 `?` 更急，會從整章開頭重講。

---

## 兩條路線

| 路線 | 章節 | 時間 |
|---|---|---|
| **短** | 00–05 + 6.1 / 6.2 / **6.9-live** | ~62 分（這是講者台上跑的） |
| **完整** | 00–08 全部 | ~100 分 |

短路線在 Mission 6.2 之後直接跳 **6.9-live**（不是 6.9）。
完整路線多做 Discussion、Introduction、Abstract、Title、Crossref 引用驗證、
四個獨立審稿 subagent、以及 build 成 PDF / DOCX。

自學建議走完整路線——反正沒有人在等你，而且 06–08 章才是這份教材真正的重點：
**每一個數字都指得回某個產出檔，每一筆引用都被外部資料庫查證過。**

---

## 這包裡面有什麼

```
live-demo/          9 章 32 個 Mission 的逐關指南 + 驗收腳本
  README.md           規則與章節索引（agent 的入口）
  RUNBOOK.md          講者口稿：每一站講什麼、觀眾會問什麼、炸了怎麼救
  verify/             驗收腳本。你只負責「跑」，不要改它
  workspace/          你所有的產出都放這裡（一開始是空的）
hospitals/          十家醫院的原始檔（唯一的輸入）
hospitals_meta.csv  醫院目錄——注意它不在病人檔裡，要自己 join
CLAUDE.md           agent 的行為規則
*.py                參考解
```

**參考解是給你卡住時看的，不是給你照抄的。** 每個 Mission 底下的
「🆘 卡住時」會告訴你什麼時候可以看——條件是**你已經自己試過至少一次**。
先看答案的話，這份教材對你就沒有價值了。

## 沒放進來的東西

`_answer_key_pooled.csv` 和 `imbrave150_pooled.csv` 是衍生產物，
也正好是第 01 章要你做出來的東西，所以刻意沒附。需要的話：

```bash
make data
```

會重新生成。**但請先自己把第 01 章做完再說。**

---

## 授權

見 `LICENSE`。合成資料與教材可自由使用，
引用時請一併註明原始試驗（Finn 2020, NEJM）。
