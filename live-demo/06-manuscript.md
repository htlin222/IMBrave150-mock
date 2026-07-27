# 第 06 章 — 從 log 反推一篇論文

> 對應投影片：**Act VI · Manuscript**｜預估 22 分鐘｜Mission 6.1 – 6.9

分析做完了。現在要寫論文——而這是整個流程裡**最容易產生假話**的一段。

規則只有一條：**每一個出現在手稿裡的數字，都必須指得回 `workspace/` 裡的某個檔案。**
Mission 6.9 會用程式稽核這件事。

---

## 寫作順序就是方法論（先講這個，再開始寫）

多數人從 Introduction 開始寫，然後卡住。因為 Introduction 要回答
「**為什麼這篇值得讀**」——而在你知道自己做出了什麼之前，那題無解。

真實的寫作順序是**由內而外**：

```
Methods ─→ Results ─→ Discussion ─→ Introduction ─→ Conclusions ─→ Abstract ─→ Title
  已知      已知        解讀          鋪陳            收束          壓縮        命名
```

- **Methods / Results** 純粹是「把已經發生的事寫下來」，不需要創造。
- **Discussion** 是第一個需要判斷的地方。
- **Introduction 要最後才寫**，因為它必須把讀者領到 Discussion 的那個問題上——
  在你知道 Discussion 講什麼之前，你不可能鋪對路。
- **Abstract 倒數第二寫**，它是全文的壓縮，不是全文的草稿。
- **Title 最後寫**，因為它是 Abstract 的壓縮。

**這一章的九個 Mission 就照這個順序走。不要跳。**

---

## Mission 6.1 — Methods：從腳本反推，不是從記憶寫

**目標**：`workspace/manuscript/methods.md`

### 任務

> **先把你自己寫的腳本重新讀一遍**：`harmonize.py`、`psm.py`、`multiverse.py`、`tmle.py`。
> Methods 要描述**程式碼實際做了什麼**，不是描述你以為你做了什麼。
>
> 章節：
> 1. **Study design and data sources** — 10 家醫院、3 種 EHR、1,800 人、2018–2019。
>    合成資料聲明放這裡（**不是只放在 Limitations**）。
> 2. **Harmonisation** — 三種方言、單位換算（g/L→g/dL、µmol/L→mg/dL）、
>    編碼統一、**Gamma 站無連續 AFP 因此全程使用 AFP ≥400 二元變數**。
> 3. **Statistical analysis**
>    - 傾向分數：邏輯迴歸，明列**全部 11 個共變數**
>    - 配對：1:1、最近鄰、無放回、卡尺 = 0.2 × SD(logit PS)（實際值 0.114）
>    - 平衡評估：SMD，門檻 0.1（**明說不用 p 值**）
>    - 存活：KM、log-rank、Cox
>    - 次群組：預先指定，描述性
>    - 敏感性：120 種設定的規格曲線
>    - 次要 estimand：12 個月死亡風險差，TMLE 搭配 IPCW
>    - 軟體與版本（**真的去查**：`../.venv/bin/pip list | grep -iE "lifelines|pandas|numpy"`）
> 4. **Estimand statement** — 主要 estimand 是什麼、對象母體是誰
>    （**配對後是 ATT，不是 ATE**）。

### ⚠️ 地雷

1. 🔴 **不要寫「standard propensity score methods were applied」這種句子。**
   Methods 的唯一功能是讓別人能重做一次。卡尺是多少？配對比例？有沒有放回？
   丟掉幾個人？沒寫就是不可重現。
2. 🔴 **不要憑記憶寫共變數清單。** 從 `psm.py` 的 `COVS` 讀出來，一個一個列。
   漏一個或多一個，Mission 6.9 的稽核會抓到。
3. **合成資料聲明要放在 Methods 開頭而不是藏在 Limitations 末尾。**
4. **估計目標（estimand）要寫清楚。** 配對後丟掉 256 個 treated，
   你估的是 ATT，不是 ATE。多數 PSM 論文跳過這段，然後在 Discussion 過度外推。
5. **軟體版本要真的去查**，不要寫「lifelines (latest)」。

### 驗收 `../.venv/bin/python verify/ch06.py --mission 6.1`

---

## 🎤 停 — `⏸ Mission 6.1 完成，等候指示。`

---

## Mission 6.2 — Results：每個數字都有出處

**目標**：`workspace/manuscript/results.md`

### 任務

> **只從 `workspace/` 的產出檔取數**，不要從對話歷史或記憶裡抄。
> 每一小節結尾用 HTML 註解標出來源檔，例如 `<!-- src: km_summary.json -->`。
>
> | 小節 | 必含數字 | 來源 |
> |---|---|---|
> | Cohort | 1,800；962 / 838；10 家 | `pooled.csv`, `site_profile.csv` |
> | Baseline imbalance | 7 個 \|SMD\|>0.15 | `baseline_table1.csv` |
> | Unadjusted | HR 0.505（0.43–0.60） | `naive_hr.json` |
> | Matching | 706 對、1,412 人、卡尺 0.114、**256 未配對**、最大 \|SMD\| 0.044 | `matched.csv`, `balance.csv` |
> | Survival | OS HR 0.578（0.48–0.70）、p<0.001、12 個月 71.1% vs 55.7%、中位 21.3 vs 13.5、PFS 0.632 | `km_summary.json` |
> | Subgroups | 13 群、0.51–0.63、全部排除 1.0 | `subgroups.csv` |
> | Sensitivity | 120 設定、中位 0.583、IQR 0.560–0.608、**全距 0.515–0.699、66%** | `multiverse.csv` |
> | Secondary | TMLE −0.150（−0.221 至 −0.078） | `tmle.json` |
>
> 圖表引用：Figure 1 = love plot、2 = KM OS、3 = forest、4 = 規格曲線。

### ⚠️ 地雷

1. 🔴 **Results 不解釋，只陳述。** 「與隨機試驗一致」是 Discussion 的話。
2. 🔴 **全距 0.515–0.699 和 66% 必須寫進去。** 只報中位數是選擇性報告，
   稽核會特別檢查這兩個數字。
3. **不要把 TMLE 的 −0.150 換算成 HR。** 不同 estimand，不可換算。
4. **`p < 0.001` 是排版慣例；JSON 存真值 8.6e-09。** 不要寫 `p = 0.000`。
5. **小數位全文統一。** HR 三位或兩位擇一；百分比一位。
6. **不要新增任何 `workspace/` 裡沒有的數字。** 想不起來就回去跑。

### 驗收 `../.venv/bin/python verify/ch06.py --mission 6.2`

---

## 🎤 停 — `⏸ Mission 6.2 完成，等候指示。`

---

## Mission 6.3 — Discussion：把限制寫滿

**目標**：`workspace/manuscript/discussion.md`

### 任務

> 三段（**結論先不要寫，那是 Mission 6.5**）：
> 1. **主要發現**（3–4 句）
> 2. **與既有文獻的關係** — IMbrave150 報告 OS HR 0.58；我們的配對估計 0.578。
>    說明「一致」的意義**與限度**。
> 3. **Limitations** — 至少涵蓋下列**七項**，每一項都要指得出具體數字與 Mission：
>
>    | # | 限制 | 出處 |
>    |---|------|------|
>    | 1 | **完全合成資料**，不構成任何藥物療效證據 | 全域 |
>    | 2 | **「無未測量干擾」在此是設計出來的**——真實資料永遠無法保證 | M2.3 |
>    | 3 | 256 個 treated（26.6%）未配對 → estimand 是 ATT 且外推性受限 | M2.3 |
>    | 4 | 配對後 Cox **未處理配對群集** | M3.1 |
>    | 5 | 次群組**未在群內重檢平衡**，未做交互作用檢定 | M4.1 |
>    | 6 | PFS 估計（0.632）偏離真值（0.59）較 OS 明顯 | M3.1 |
>    | 7 | 120 設定僅 66% 落在 0.55–0.61，全距 0.515–0.699 | M5.1 |

### ⚠️ 地雷

1. 🔴 **限制第 2 項是這篇稿子最重要的一句話。** 我們能還原 0.58，
   是因為所有干擾因子都被測量了——那是模擬時故意設計的。
   真實 EHR 裡的體能、營養、社經、醫師判斷幾乎都測不到。
   **不寫這一條，整篇稿子就是在誤導。**
2. **限制不要寫成罐頭。** 「本研究為回溯性研究，有其固有限制」等於沒寫。
3. **不可以寫 `proves` / `demonstrates causality` / `establishes`。**
4. **不要在 Discussion 引入新數字。**

### 驗收 `../.venv/bin/python verify/ch06.py --mission 6.3`

---

## 🎤 停 — `⏸ Mission 6.3 完成，等候指示。`

---

## Mission 6.4 — Introduction：現在才寫得出來

**目標**：`workspace/manuscript/introduction.md`

### 任務

> **先重讀你剛寫完的 Discussion。** Introduction 的唯一工作，是把讀者
> 從「一般常識」領到「Discussion 開頭那個問題」——不多也不少。
>
> 三段，倒金字塔：
> 1. **臨床背景**（廣）— 不可切除肝細胞癌的一線治療；IMbrave150 建立了
>    atezo+bev 的地位。
> 2. **問題缺口**（窄）— 真實世界資料的治療分配受預後驅動；
>    觀察性複製常被質疑不可信。**這裡要引用文獻。**
> 3. **本研究要做什麼**（最窄）— 建構一個「真值已知」的合成多中心世代，
>    問：常規調整流程能不能還原真值？**每一步能不能被機器稽核？**
>    最後一句是研究目的，不是結果。

### ⚠️ 地雷

1. 🔴 **Introduction 不可以出現結果數字。** 不要寫「我們發現 HR 0.578」。
   那是 Results。Introduction 只講「我們問了什麼」。
2. 🔴 **不要寫成教科書。** 三段就夠。臨床背景寫超過五句，
   審稿人會開始懷疑你沒有東西可講。
3. **問題缺口那段必須有引用。** 沒有引用的「一般認為」＝你自己認為。
   引用在 Mission 6.8 統一驗證，先用 `[@key]` 佔位。
4. **最後一句是目的（aim），不是假設（hypothesis），也不是結論。**
   這篇沒有預設假設——我們是在測試流程，不是在測試藥。
5. **不要重複 Methods。** 「我們用了傾向分數配對」不屬於 Introduction。

### 驗收 `../.venv/bin/python verify/ch06.py --mission 6.4`

---

## 🎤 停 — `⏸ Mission 6.4 完成，等候指示。`

---

## Mission 6.5 — Conclusions：兩句，語氣要配得上證據

**目標**：`workspace/manuscript/conclusions.md`

### 任務

> **兩到三句，不要更多。**
> 1. 這個研究顯示了什麼（限定在本研究的條件內）
> 2. 可以帶走的是什麼（**是流程，不是那個 0.58**）
>
> 語氣分級，選對一個：
>
> | 可以用 | 不可以用 |
> |---|---|
> | is consistent with | proves |
> | supports | demonstrates that X causes Y |
> | suggests | establishes |
> | in this synthetic setting, recovered | validates the method |

### ⚠️ 地雷

1. 🔴 **不可以說「本研究驗證了 PSM 可用於真實世界資料」。**
   我們驗證的是「**在所有干擾因子都被測量的情況下**，PSM 可以還原真值」。
   把條件拿掉，那句話就是假的。
2. **不要在結論裡加新的限制。** 限制在 Discussion 已經寫完了。
3. **不要呼籲「需要更多研究」。** 那是廢話句，審稿人一眼看出。
   要寫就寫具體的下一步（例如：藏一個干擾因子重跑，看 PSM 何時失效）。

### 驗收 `../.venv/bin/python verify/ch06.py --mission 6.5`

---

## 🎤 停 — `⏸ Mission 6.5 完成，等候指示。`

---

## Mission 6.6 — Abstract：全文的壓縮，不是草稿

**目標**：`workspace/manuscript/abstract.md`

### 任務

> 結構式摘要，**250 字以內**：
> **Background**（2 句）/ **Methods**（3–4 句）/ **Results**（4–5 句，全是數字）/
> **Conclusions**（2 句）。
>
> **每一個數字都要重新從 `workspace/` 的檔案取一次**，
> 不可以從 `results.md` 複製貼上——複製會把 Results 裡的排版錯誤一起帶過來。

### ⚠️ 地雷

1. 🔴 **Abstract 是幻覺最愛出沒的地方。** 因為它最後寫、最短、
   而且人們習慣「憑印象總結」。Mission 6.9 的稽核會**單獨再掃一次 Abstract**。
2. 🔴 **Abstract 的結論不能比正文強。** 這是同儕審查最常見的指控之一
   （"spin"）。正文說 consistent with，摘要就不能說 confirms。
3. **Results 段不可以只有形容詞。** 「顯著改善」沒有資訊量，
   要寫「0.578（95% CI 0.48–0.70）」。
4. **不要在 Abstract 引用文獻。**
5. **字數要真的數。** `wc -w abstract.md`。超過 250 就砍 Background。

### 驗收 `../.venv/bin/python verify/ch06.py --mission 6.6`

---

## 🎤 停 — `⏸ Mission 6.6 完成，等候指示。`

---

## Mission 6.7 — Title：最後一步

**目標**：`workspace/manuscript/title.md` — **給出 5 個候選 + 1 個選定**

### 任務

> 產生五個標題候選，各標註類型與字數：
> - **描述型**（講做了什麼）
> - **結論型**（講發現了什麼）
> - **問句型**
> - **方法導向型**
> - **簡短版**（≤ 12 字）
>
> 然後**選一個**並說明理由。附上 running title（≤ 50 字元）。

### ⚠️ 地雷

1. 🔴 **結論型標題不可以宣稱因果。**
   「Propensity matching recovers randomised results」——這在**一般情況下是假的**，
   我們只在「干擾因子全測量」的條件下成立。標題放不下條件，就不要用結論型。
2. **標題裡必須有 "synthetic" 或 "simulated"。** 這篇如果被單獨轉發，
   標題是唯一會被讀到的東西。**沒有這個字就是誤導。**
3. **不要用冒號堆三段。** `A:B:C` 型標題在 PubMed 會被截斷。
4. **不要放 HR 數字進標題。**
5. 檢查是否已有同名論文（Mission 6.8 順便查 Crossref）。

### 驗收 `../.venv/bin/python verify/ch06.py --mission 6.7`

---

## 🎤 停 — `⏸ Mission 6.7 完成，等候指示。`

---

## Mission 6.8 — References：每一筆都去 Crossref 對證 ⭐

**目標**：`workspace/manuscript/refs.bib` + `workspace/manuscript/refs_validated.csv`

> **這是整份教材裡第二重要的一關。** 語言模型編造引用是紀錄最完整的失敗模式：
> 作者是真的、期刊是真的、DOI 格式是合法的——**但那篇論文不存在**。
> 這一關要做的就是：**不准有任何一筆引用沒被外部資料庫確認過。**

### ⛔ 硬性約束（動手前讀）

```bash
# 1. 順序永遠是「先搜尋 → 拿到真 DOI → 再驗證」，絕不是「先寫 DOI → 再驗證」
# 2. 每個 Crossref 請求都要帶 mailto 的 User-Agent（polite pool），否則會被限流
UA="User-Agent: imbrave150-livedemo/1.0 (mailto:YOUR@EMAIL)"
curl -s "https://api.crossref.org/works/<DOI>" -H "$UA"
# 3. 驗不過（404 或欄位不符）→ 從稿子裡刪掉那個引用，不要「改一下再試」
# 4. Crossref 查得到 ≠ 那篇支持你的說法 —— 還是要讀 abstract
```

> 🎭 **刻意示範**：講者可能會要求你當場打一個**假 DOI**（例如
> `10.1056/NEJMoa9999999`）給觀眾看它回 404。**只在被要求時做。**

### 任務

> 1. 掃過 `introduction.md` / `discussion.md` 裡所有 `[@key]` 佔位，列出你**想引用**的文獻。
> 2. 每一筆都做兩步：
>    - **找**：用 WebSearch 查該主題的實際文獻（不要憑記憶生 DOI）。
>    - **證**：拿到 DOI 後打 Crossref API 驗證：
>      ```bash
>      curl -s "https://api.crossref.org/works/10.1056/NEJMoa1915745" \
>        -H "User-Agent: imbrave150-livedemo/1.0 (mailto:YOUR@EMAIL)" \
>      | python -c "import json,sys; m=json.load(sys.stdin)['message']; \
>        print(m['title'][0]); print(m['container-title'][0], m['issued']['date-parts'][0][0], \
>        m.get('volume'), m.get('page'))"
>      ```
>      沒有 DOI 就用書目查詢：
>      ```bash
>      curl -s -G "https://api.crossref.org/works" \
>        --data-urlencode "query.bibliographic=atezolizumab bevacizumab unresectable hepatocellular" \
>        --data-urlencode "rows=5" -H "User-Agent: …"
>      ```
> 3. 逐筆比對**六個欄位**：標題、第一作者姓、年份、期刊、卷、頁碼。
>    寫進 `refs_validated.csv`：
>    ```
>    key, doi, title_match, author_match, year_match, journal_match, volume_page_match, status
>    finn2020, 10.1056/NEJMoa1915745, TRUE, TRUE, TRUE, TRUE, TRUE, VERIFIED
>    ```
>    **任何一筆 status 不是 `VERIFIED`，就從稿子裡刪掉那個引用。**
> 4. 用**通過驗證的欄位值**（不是你原本寫的值）產生 `refs.bib`。
> 5. 下載 AMA 樣式：
>    ```bash
>    curl -sL -o workspace/manuscript/ama.csl \
>      https://raw.githubusercontent.com/citation-style-language/styles/master/american-medical-association.csl
>    ```

### ⚠️ 地雷（這一關的雷最貴）

1. 🔴 **絕對不要從記憶生成 DOI。** `10.1056/NEJMoa` 開頭看起來很專業，
   後面八碼是猜的——Crossref 會回 404，那就是編造。
   **流程一定是「先搜尋 → 拿到真 DOI → 再驗證」，不是「先寫 DOI → 再去驗證」。**
2. 🔴 **Crossref 查得到 ≠ 那篇論文支持你的說法。**
   驗證只證明「這篇存在」。你還是要讀 abstract 確認它真的講了你引用它的那件事。
   引用一篇存在但不相干的論文，比不引用更糟。
3. **API 一定要帶 `mailto` 的 User-Agent。** Crossref 的 polite pool 會給你穩定的
   速率；匿名請求在現場很容易被限流，然後你就卡在台上。
4. **期刊名稱有全名與縮寫兩種。** Crossref 的 `container-title` 給全名
   （`New England Journal of Medicine`），AMA 要縮寫（`N Engl J Med`）。
   **這不算不符**——但 `.bib` 裡要存哪一個要一致，並讓 CSL 去處理。
5. **頁碼的破折號。** Crossref 給 `1894-1905`（hyphen），BibTeX 慣例是 `1894--1905`（en dash）。
   轉換時不要把它當成不符。
6. **作者數量與 AMA 規則。** AMA 第 11 版：作者 ≤6 全列；>6 列前 3 位 + `et al`。
   Finn 2020 有 **21 位作者**——不要全部列進 `.bib` 的 author 欄然後讓 CSL 吐出一整頁。
7. **預印本（bioRxiv/medRxiv）有 DOI 但不是 journal-article。**
   Crossref 回傳的 `type` 要看；引用預印本必須在文中標明 preprint。
8. **不要引用「教科書上都這樣說」的東西卻找不到出處。** 找不到就改寫句子，
   不要硬塞一個看起來相關的引用。

### 驗收 `../.venv/bin/python verify/ch06.py --mission 6.8`

### 🎤 講者停頓點

> 這一關值得停久一點。當場打一個**假 DOI** 進 Crossref，讓觀眾看到 404。
> 「模型很樂意幫你生一個長得非常專業的 DOI。**專業的長相不等於存在。**」

---

## 🎤 停 — `⏸ Mission 6.8 完成，等候指示。`

---

## Mission 6.9 — 組裝 + 數字稽核 ⭐

**目標**：`workspace/manuscript/manuscript.md`，然後**用程式抓出幻覺數字**。

### 任務

> 1. 依序組裝：Title、Abstract、Introduction、Methods、Results、Discussion、
>    Conclusions、**Data and code availability**、**Synthetic data disclaimer**、
>    References、Figure legends（4 張）。
>    → `workspace/manuscript/manuscript.md`
>    YAML front matter 要有 `title` / `author` / `bibliography: refs.bib` / `csl: ama.csl`。
>
> 2. 做數字出處對照表 `workspace/manuscript/claims.csv`：
>    ```
>    claim_id, statement, value, source_file, source_key
>    C01, Pooled cohort size, 1800, pooled.csv, nrow
>    C04, Naive OS hazard ratio, 0.505, naive_hr.json, hr
>    C08, Caliper on logit propensity score, 0.114, psm.py, 0.2*SD(logit_ps)
>    …
>    ```
>    **手稿裡每一個實質數字都要有一列。**
>
> 3. 跑稽核。它做四件事：
>    - `claims.csv` 每個 value 是否真的等於來源檔裡的值
>    - 手稿裡是否有**沒有出處**的類結果數字（幻覺偵測）
>    - **Abstract 單獨再掃一次**
>    - 七項必列限制是否都在

### ⚠️ 地雷

1. 🔴 **稽核用「書寫精度」比對**：你寫 `0.58`，它會接受 `0.578`；
   你寫 `0.612`，它**不會**接受 `0.61`。想模糊帶過是行不通的。
2. 🔴 **不要在組裝時「順手潤飾」數字。** 0.578 → 0.58 可以（要全文一致）；
   把 66% 寫成「大多數」、把全距省略——這正是稽核要抓的東西。
3. **`claims.csv` 不是事後補的裝飾。** 找不到來源的數字，**就是編的**。
4. **Data availability 要寫得能真的執行**：repo 路徑、指令、產出清單。
5. **Figure legend 要能獨立看懂**：含 n、方法、誤差線代表什麼。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch06.py --mission 6.9
```

### 🆘 卡住時

稽核抓到「無來源數字」時會印出該數字與所在句子。
**不要去改稽核腳本**，去改手稿或去補跑分析。

---

## 🎤 停 — 講者接話

`⏸ Mission 6.9 完成，等候指示。`

> 講者（詳見 [RUNBOOK.md](RUNBOOK.md#m69)）：
> 「今天沒有一個數字是我打字打進去的，也沒有一筆引用是憑印象寫的。
> 全部跑出來、全部被外部資料庫對過、全部剛剛被稽核過一次。」

下一關：[07-review.md](07-review.md) — 讓它自己審自己的稿。
