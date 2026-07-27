# IMbrave150-mock — 給 Claude Code 的指示

這個 repo 的主要用途是**現場 demo**：一位講者在台上，觀眾在看，
由你一關一關把一個完整的真實世界資料分析做出來，直到產出一份可投稿的手稿。

## 🚦 開場：使用者說「開始」時要做什麼

當使用者以任何形式表示「開始」——例如
**`hey, lets go`**、`let's go`、`start`、`begin`、`開始`、`走吧`、
`follow the ./live-demo mission by mission`、`/live-demo`——

**你要做的是：**

1. 讀 **`live-demo/README.md`**（那是完整的規則與章節索引）。
2. 讀 **`live-demo/00-setup.md`**。
3. 執行 **Mission 0.1**，跑它的驗收，用三到五行中文說「這一步看到了什麼」。
4. 輸出 `⏸ Mission 0.1 完成，等候指示。` 然後**停住**。

**不要**先問「你想做什麼？」。開場語就是指令。
**不要**一口氣把整章或整個專案做完——這是有觀眾的現場演出，
講者需要在每個 Mission 之間對觀眾說話。

## 🎬 核心節奏（違反這條會毀掉現場）

- **一次只做一個 Mission。** 做完 → 跑驗收 → 三五行中文摘要 → **停**。
- 等使用者說 `next` / `繼續` / `下一關` 才做下一個。
- `skip` = 跳過該 Mission（要提醒後面哪些會受影響）。
- `why` / `解釋` = 展開講原理，**不要趁機往下做**。

## 📁 這個 repo 有什麼

| 路徑 | 是什麼 |
|---|---|
| `live-demo/` | **主要交付物。** 9 章 26 個 Mission 的逐關指南 + 驗收腳本。 |
| `live-demo/README.md` | Agent 入口：規則、全域硬性約束、章節索引。**先讀這個。** |
| `live-demo/verify/` | 驗收腳本。你只負責「跑」，**不要改**。 |
| `live-demo/workspace/` | 你所有的產出都放這裡。**絕不動 repo 根目錄。** |
| `claude-demo/` | 同一個故事的動畫投影片（備援用），與 demo 執行無關。 |
| 根目錄的 `*.py` | **參考解。** 只有在 Mission 標示「🆘 卡住時」而且你已自己試過一次，才可以看。 |

## ⛔ 幾條硬規則

1. **不要偷看根目錄的參考解**（`harmonize_hospitals.py`、`psm_imbrave150.py` 等），
   除非該 Mission 明確允許。
2. **不要動 repo 根目錄的任何檔案。** 產出一律寫進 `live-demo/workspace/`。
3. **不要憑印象寫數字。** 每個數字都要是這一輪真的跑出來的——手稿階段會被程式稽核。
4. **不要憑記憶生成 DOI 或引用。** 一律 WebSearch 找到真文獻 → Crossref 驗證。
5. 每個 Mission 底下的 `⛔ 硬性約束` 區塊，**在寫該關第一行程式碼之前讀完**。
   那些是已知會在台上炸掉的東西。

## 🐍 環境

Python 用 `.venv/bin/python`（`make setup` 可建）。
第 08 章另需 `pandoc`、`tectonic`、`rsvg-convert`。

上台前先跑：

```bash
cd live-demo && ../.venv/bin/python verify/preflight.py --full
```

## 🧪 這批資料是合成的

模擬自 Finn RS et al., *NEJM* 2020;382:1894。**沒有任何真實病人。**
不構成關於 atezolizumab、bevacizumab 或 sorafenib 的任何證據。
手稿的標題、摘要與正文都必須寫明這件事。
