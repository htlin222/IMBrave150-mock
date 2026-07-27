# 第 08 章 — 變成可以投出去的東西

> 延伸章節（投影片沒有這一幕）｜預估 10 分鐘｜Mission 8.1 – 8.4

Markdown 不能投稿。這一章把它變成 **PDF + DOCX + LaTeX 原始檔**，
引用用 AMA 格式，然後打包成一個可發佈的 preprint。

**工具鏈**（本 repo 已驗證可用）：

| 工具 | 版本 | 角色 |
|---|---|---|
| `pandoc` | 3.8.3 | 轉檔與 citeproc 引用排版 |
| `tectonic` | 0.15.0 | LaTeX 引擎（自帶套件，**不需要安裝 TeX Live**） |
| `rsvg-convert` | — | pandoc 自動用它把 SVG 轉成 PDF 圖 |
| `biber` | 2.21 | 備援（走 biblatex 路線時才需要） |

---

## Mission 8.1 — 建立 build 管線

**目標**：`workspace/build.sh`，一鍵重現全部輸出。

### ⛔ 硬性約束（動手前讀）

```bash
# 1. pandoc 一定要 --citeproc。忘了不報錯，[@key] 會原樣印在 PDF 上
# 2. build.sh 開頭一定要 cd 到 manuscript/ —— pandoc 解析圖片路徑是相對於「工作目錄」
# 3. LaTeX 不吃 SVG；pandoc 會自動轉，但前提是 PATH 上有 rsvg-convert 或 inkscape
command -v rsvg-convert || command -v inkscape || echo "⚠️ 圖會失敗"
# 4. tectonic 首跑要下載套件包（~20 秒）—— preflight.py --full 應該已經幫你暖機過
# 5. YAML front matter 缺 bibliography / csl 的話，citeproc 靜靜什麼都不做
```

**每次 build 完打開 PDF 看一眼參考文獻那一頁。** 這是唯一能確認 citeproc 真的跑了的方法。

### 任務

> 1. 確認 `manuscript.md` 的 YAML front matter 完整：
>    ```yaml
>    ---
>    title: "<Mission 6.7 選定的標題>"
>    author: "Hsieh-Ting Lin (林協霆)"
>    date: "<今天>"
>    bibliography: refs.bib
>    csl: ama.csl
>    link-citations: true
>    ---
>    ```
> 2. 確認 `refs.bib`（Mission 6.8 產出，全部 VERIFIED）與 `ama.csl` 都在
>    `workspace/manuscript/` 底下。缺 CSL 就抓：
>    ```bash
>    curl -sL -o ama.csl \
>      https://raw.githubusercontent.com/citation-style-language/styles/master/american-medical-association.csl
>    ```
> 3. 圖片：手稿引用的是 `../figures/*.svg`。**確認每個路徑相對於 `manuscript.md` 都正確。**
> 4. 寫 `workspace/build.sh`：
>    ```bash
>    #!/usr/bin/env bash
>    set -euo pipefail
>    cd "$(dirname "$0")/manuscript"
>    OUT=../dist; mkdir -p "$OUT"
>    COMMON=(--citeproc --bibliography=refs.bib --csl=ama.csl --metadata link-citations=true)
>
>    pandoc manuscript.md "${COMMON[@]}" -s -o "$OUT/manuscript.tex"
>    pandoc manuscript.md "${COMMON[@]}" -o "$OUT/manuscript.docx"
>    pandoc manuscript.md "${COMMON[@]}" --pdf-engine=tectonic \
>           -V geometry:margin=1in -V fontsize=11pt -V linestretch=1.5 \
>           -o "$OUT/manuscript.pdf"
>
>    ls -la "$OUT"
>    ```
>    `chmod +x workspace/build.sh`

### ⚠️ 地雷

1. 🔴 **LaTeX 本身不吃 SVG。** pandoc 會**自動**幫你把 SVG 轉成 PDF——
   但**前提是 PATH 上有 `rsvg-convert` 或 `inkscape`**。沒有的話會失敗，
   而錯誤訊息看起來像是 LaTeX 的問題，非常難查。
   本機兩者都有，所以直接嵌 SVG 可行。**換一台機器前先確認：**
   ```bash
   command -v rsvg-convert || command -v inkscape || echo "先轉檔：rsvg-convert -f pdf -o fig.pdf fig.svg"
   ```
2. 🔴 **`tectonic` 第一次執行會下載套件包（約 20 秒，需要網路）。**
   **演出前一定要先暖機跑一次**，否則現場會靜止二十秒。
   暖機之後有快取，後續每次 build 約 3–5 秒。
3. **DOCX 不吃 `geometry` / `fontsize` 這些 LaTeX 變數**——傳了不會錯，只是無效。
   要控制 DOCX 樣式得用 `--reference-doc=template.docx`。
4. **`--citeproc` 必須加。** 忘了加不會報錯，`[@finn2020]` 會原封不動印在 PDF 上。
   **每次 build 完打開 PDF 看一眼參考文獻那一頁。**
5. **相對路徑陷阱。** pandoc 解析圖片路徑是**相對於工作目錄**，不是相對於 md 檔。
   所以 `build.sh` 一開頭要 `cd` 到 `manuscript/`。
6. **PDF 版本警告可以忽略**：
   `Trying to include PDF file with version (1.7), which is newer than (1.5)` 是
   tectonic 的資訊性警告，不影響輸出。

### 驗收 `../.venv/bin/python verify/ch08.py --mission 8.1`

---

## 🎤 停 — `⏸ Mission 8.1 完成，等候指示。`

---

## Mission 8.2 — 產出 PDF，並檢查引用真的排版了

**目標**：`workspace/dist/manuscript.pdf`

### 任務

> 1. 跑 `bash workspace/build.sh`。
> 2. **驗證引用真的被 citeproc 處理過**，不是原樣印出：
>    ```bash
>    pandoc workspace/manuscript/manuscript.md --citeproc \
>       --bibliography=... --csl=... -t plain | grep -A3 -i "finn"
>    ```
>    應該看到 AMA 格式：
>    ```
>    1. Finn RS, Qin S, Ikeda M, et al. Atezolizumab plus bevacizumab in
>       unresectable hepatocellular carcinoma. N Engl J Med. 2020;382(20):1894-1905.
>       doi:10.1056/NEJMoa1915745
>    ```
> 3. 報告：頁數、檔案大小、圖片是否都嵌進去了。

### ⚠️ 地雷

1. 🔴 **文中還看得到 `[@finn2020]` 就是 citeproc 沒跑。** 檢查三件事：
   `--citeproc` 有沒有加、`bibliography` 路徑對不對、citation key 有沒有拼錯。
   **key 拼錯時 pandoc 只會印一個警告然後把原文留著**，很容易漏看。
2. 🔴 **AMA 的作者規則：≤6 位全列，>6 位列前 3 位 + `et al`。**
   Finn 2020 有 **21 位作者**。如果你的 `.bib` 只寫了 4 位，
   CSL 會乖乖列出 4 位——**而那是錯的引用**。
   要嘛完整列 21 位讓 CSL 自己截斷，要嘛列前 3 位 + `and others`。
3. **`et al.` 後面的句點與 AMA 的斜體規則交給 CSL 處理**，不要手動排版。
4. **圖片沒出現時先看 pandoc 的 warning**，不要先怪 LaTeX。
5. **中文字元**：如果標題或作者含中文，`tectonic` 預設字型排不出來，
   會變成空白。要加 `-V CJKmainfont="PingFang TC"` 並用 `--pdf-engine=lualatex`，
   或**作者欄只寫羅馬拼音**。本 demo 建議後者，現場最穩。

### 驗收 `../.venv/bin/python verify/ch08.py --mission 8.2`

---

## 🎤 停 — `⏸ Mission 8.2 完成，等候指示。`

---

## Mission 8.3 — DOCX（因為期刊真的會要）

**目標**：`workspace/dist/manuscript.docx`

> ⚡ PDF 與 DOCX 兩條 build 沒有相依，**可以派兩個 subagent 同時跑**
> （8.2 一個、8.3 一個，共用同一份 `manuscript.md` 與 `refs.bib`）。
> 但驗收仍然一關一關跑、一關一關停。

### 任務

> 1. 產出 DOCX 並檢查：段落樣式、參考文獻是不是純文字（不是欄位碼）、圖片有沒有進去。
> 2. 產出一份**純投稿版**：`manuscript_submission.docx`，
>    圖說集中在最後、圖片另存 `dist/figures/`（多數期刊要求圖檔分開上傳）。
> 3. 順便產出 `dist/manuscript.tex`（有些期刊只收 LaTeX）。

### ⚠️ 地雷

1. **DOCX 的參考文獻是純文字**，不是 EndNote/Zotero 欄位碼。
   共同作者拿去用 Word 的「更新引用」會失效——**交稿時要說明**。
2. **Word 對 SVG 的支援不穩**。pandoc 走 DOCX 路線時圖片可能被轉成 PNG，
   解析度不足。要交稿的話 `rsvg-convert -f png -d 300 -p 300` 另外輸出 300 dpi 版本。
3. **多數期刊要求圖檔與正文分開上傳**，而且檔名要 `Figure1.tif` 這種格式。
   不要交一個把圖嵌在裡面的 DOCX 就以為完事。
4. **不要用 `--reference-doc` 套一個來路不明的模板**，
   期刊模板常帶巨集與樣式衝突。乾淨的預設輸出反而比較安全。

### 驗收 `../.venv/bin/python verify/ch08.py --mission 8.3`

---

## 🎤 停 — `⏸ Mission 8.3 完成，等候指示。`

---

## Mission 8.4 — 打包成 preprint 發佈

**目標**：`workspace/dist/` 是一個可以直接上傳的完整包。

### 任務

> 1. `workspace/dist/README.md` — 這個包是什麼、怎麼重現、內容清單。
> 2. `workspace/dist/CHECKSUMS.txt`：
>    ```bash
>    cd workspace/dist && shasum -a 256 * > CHECKSUMS.txt
>    ```
> 3. `workspace/dist/metadata.yaml` — preprint 送件用的欄位：
>    ```yaml
>    title: …
>    authors:
>      - name: Hsieh-Ting Lin
>        affiliation: "Department of Oncology, Koo Foundation Sun Yat-Sen Cancer Center"
>        orcid: …            # 沒有就留空，不要編
>    abstract: |
>      …（從 abstract.md 取，不要重寫）
>    keywords: [hepatocellular carcinoma, propensity score, synthetic data, reproducibility]
>    license: CC-BY-4.0
>    data_availability: …
>    disclaimer: "All data are synthetic. No real patient is represented."
>    ```
> 4. **最後一次跑完整驗收**：
>    ```bash
>    ../.venv/bin/python verify/run_all.py
>    ```
> 5. 印出一份**發佈前檢核**，逐項確認：
>    - [ ] 全部九章驗收 PASS
>    - [ ] `refs_validated.csv` 每一筆都是 `VERIFIED`
>    - [ ] 手稿、Abstract、標題**都**含合成資料聲明
>    - [ ] 七項限制都在
>    - [ ] PDF 的參考文獻是 AMA 格式且非 `[@key]` 原文
>    - [ ] `CHECKSUMS.txt` 涵蓋 dist 內所有檔案

### ⚠️ 地雷

1. 🔴 **不要真的把這份東西上傳到 medRxiv/bioRxiv。**
   這是**合成資料**的教學示範。把它送上預印本伺服器會污染文獻庫，
   而且一旦被索引就很難撤下。**這一關只做「打包」，不做「投遞」。**
   要練習投遞流程，用該平台的 sandbox。
2. 🔴 **ORCID / 機構代碼不要編。** 缺就留空。編一個格式合法的 ORCID
   是本章最容易犯、也最難察覺的造假。
3. **授權要選定並寫進包裡。** 這個 repo 是 MIT；手稿本身建議 CC-BY-4.0。
   兩者不同，要分別說明。
4. **checksum 要在最後一次 build 之後才算**。先算 checksum 再改檔案，
   那份 checksum 就是錯的——而且沒有人會發現。
5. **`dist/` 要進 `.gitignore` 還是進版本控制？** 建議**進版本控制並打 tag**，
   因為「這個 PDF 是哪一版程式產生的」正是這整章想證明的事。
   ```bash
   git add -f live-demo/workspace/dist && git commit -m "preprint v0.1 (synthetic demo)"
   git tag -a preprint-v0.1 -m "…"
   ```
6. **發佈前檢核不要用嘴巴確認。** 每一項都要有指令或檔案佐證。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch08.py --mission 8.4
```

---

## 🎤 收尾 — 講者接話

`⏸ Mission 8.4 完成。全部 32 個 Mission 結束。`

> 講者（詳見 [RUNBOOK.md](RUNBOOK.md#m84)）：
> 「從十個亂七八糟的 CSV 開始，到一份可以投出去的 PDF。
> 中間沒有一個數字是我打的，沒有一筆引用是憑印象寫的，
> 而且每一步都留下了可以被別人重跑的東西。
>
> 我不是在示範 AI 有多厲害。**我是在示範怎麼把 AI 放進一個它騙不了你的流程裡。**」

---

## 全部跑完

```bash
cd live-demo && ../.venv/bin/python verify/run_all.py
```
