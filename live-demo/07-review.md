# 第 07 章 — 讓它審自己的稿

> 延伸章節（投影片沒有這一幕）｜預估 15 分鐘｜Mission 7.1 – 7.4

稿子寫完了。現在做一件多數人跳過的事：**在投出去之前，先自己被審一次。**

這一章的核心設計是：**寫稿的和審稿的，不可以是同一個腦袋。**
所以我們派出**獨立的 subagent**，而且**刻意不讓它們看見這份教材**——
它們只能看手稿和產出檔，就像真正的審稿人一樣。

---

## Mission 7.1 — 派出四個獨立審稿人（平行）

**目標**：`workspace/manuscript/reviews/reviewer{1..4}.md`

### 任務

> 用 Agent 工具**同時**派出四個獨立的審稿 subagent（一則訊息裡四個 tool call，
> 不要一個一個等）。每個審稿人拿到的資料**只有**：
> `workspace/manuscript/*.md` 與 `workspace/` 底下的產出檔。
>
> **明確禁止它們讀取 `live-demo/*.md`（也就是這份教材本身）。**
>
> | #   | 角色               | 審什麼                                                                                                                                                    |
> | --- | ------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
> | 1   | **統計審稿人**     | estimand 定義是否清楚一致；傾向分數模型設定；卡尺與配對規則；平衡評估方法；配對後推論的獨立性假設；TMLE 的 positivity 與 IPCW；規格曲線的解讀是否過度樂觀 |
> | 2   | **臨床審稿人**     | 共變數選擇在 HCC 是否合理（有沒有漏掉重要預後因子）；次群組是否臨床上有意義；效果量的臨床意義；用藥禁忌（食道靜脈曲張 vs bevacizumab）是否處理正確        |
> | 3   | **報告規範審稿人** | 對照 **STROBE** 與 **RECORD** 檢核表逐項打勾；缺哪幾項；資料來源與連結描述是否足夠；流程圖（participant flow）是否交代 1,800 → 1,412 的去向               |
> | 4   | **可重現性審稿人** | 只照 Methods 寫的內容，能不能重跑出 Results？逐一比對手稿數字與 `workspace/` 檔案；軟體版本；隨機性/決定性；資料與程式可得性                              |
>
> 每位審稿人輸出格式固定：
>
> ```markdown
> # Reviewer N — <角色>
>
> ## Recommendation
>
> <Major revision | Minor revision | Reject>
>
> ## Major comments
>
> 1. **[位置：段落或句子]** 問題陳述。為什麼這是問題。建議怎麼改。
>
> ## Minor comments
>
> ## What is done well
> ```
>
> **每位至少提出 3 個 major comment。** 找不到就再讀一次——
> 一份「沒有問題」的審稿意見等於沒有審。

### ⚠️ 地雷

1. 🔴 **不要讓審稿 subagent 讀到 `live-demo/` 的 mission 檔。**
   那裡面寫著全部的標準答案和地雷清單。它讀了就不是審稿，是對答案，
   會產出一份看起來很銳利但毫無資訊量的意見。**在 prompt 裡明確禁止。**
2. 🔴 **不要讓審稿人直接改稿。** 審稿和修稿是兩個角色。
   讓同一個 agent 一邊挑錯一邊改，它會傾向挑「自己好改的錯」。
3. **四個要平行派出**（同一則訊息四個 tool call），不然這一關會拖到六分鐘以上。
4. **不要給審稿人「這篇很棒，幫我看看小問題」這種前言。** 諂媚是可以被 prompt 誘發的。
   給中性指示：「這是一份投稿前的手稿，請審查。」
5. **角色要真的不同。** 四個都叫「請仔細審查」等於跑四次同一個審稿人，
   拿到四份高度重複的意見。**分工要具體到檢查項目。**
6. **審稿人可能誤判。** 它們看不到 `_answer_key_pooled.csv`，也不知道 DGP。
   下一關要做的正是「判斷哪些意見該接受」——**不要無條件照單全收**。

### 驗收 `../.venv/bin/python verify/ch07.py --mission 7.1`

### 🎤 講者停頓點

> 「注意我做了什麼：我沒有問它『這篇寫得好不好』。
> 那樣問，它一定說好。**我派了四個角色，各自只被允許看手稿，然後要求每人至少挑三個大問題。**
> 問法決定答案的品質。」

---

## 🎤 停 — `⏸ Mission 7.1 完成，等候指示。`

---

## Mission 7.2 — 分流、回應、真的去改

**目標**：`workspace/manuscript/response-to-reviewers.md` + 修改後的手稿

### 任務

> 1. 把四份意見合併去重，做成 `workspace/manuscript/review_log.csv`：
>    ```
>    id, reviewer, severity, comment_short, verdict, action_taken, file_changed
>    R1-1, 1, major, "estimand 在 Abstract 與 Methods 不一致", ACCEPT, "統一為 ATT", abstract.md
>    R2-3, 2, major, "應納入 portal vein thrombosis", REJECT, "資料無此欄位，改列為限制", discussion.md
>    ```
>    `verdict` 三選一：**ACCEPT** / **PARTIAL** / **REJECT**。
> 2. 每一條 REJECT 都必須寫出**技術性理由**，不可以只寫「不同意」。
> 3. 寫 `response-to-reviewers.md`：逐條回應，附上改了哪個檔、改成什麼。
> 4. **真的去改手稿。** 改完 `review_log.csv` 的 `action_taken` 不可以留空。
> 5. 改完**立刻重跑第 06 章的數字稽核**：
>    ```bash
>    ../.venv/bin/python verify/ch06.py --mission 6.9
>    ```

### ⚠️ 地雷

1. 🔴 **不可以全部 ACCEPT。** 那是諂媚，不是審稿回應。
   審稿人會提出「這份資料做不到」的要求（例如加入沒有測量的變數）——
   正確的回應是**說明為什麼做不到，並把它寫進 Limitations**，不是假裝做到了。
2. 🔴 **也不可以全部 REJECT。** 如果四個審稿人十二條意見你一條都沒接受，
   你不是在回應審稿，是在防衛。
3. 🔴 **改完一定要重跑數字稽核。** 潤字句最容易順手把 `0.578` 改成 `0.58`
   又在別處留著 `0.578`，或把「66%」改成「大多數」。**這是本章最常見的翻車點。**
4. **回應要對應到具體位置。** 「已修改」不算回應，要寫「已於 Methods 第 3 段
   加入卡尺數值 0.114」。
5. **不要為了回應審稿而製造新數字。** 需要新分析就回去跑，跑不了就寫成限制。
6. **PARTIAL 是最誠實的答案，不要迴避它。** 「我們接受這個顧慮，但只能部分處理，
   原因是……」——真實的審稿回應大半是這一類。

### 驗收 `../.venv/bin/python verify/ch07.py --mission 7.2`

---

## 🎤 停 — `⏸ Mission 7.2 完成，等候指示。`

---

## Mission 7.3 — Polish：一致性與期刊格式

**目標**：`workspace/manuscript/polish_report.md` + 修改後的手稿

> **這一關只碰形式，不碰科學內容。** 任何會改變意義的修改都屬於 7.2。

### 任務

> 逐項檢查並修正，把每一項的「發現 / 修正」記進 `polish_report.md`：
>
> | 項目           | 規則                                                                                                  |
> | -------------- | ----------------------------------------------------------------------------------------------------- |
> | **小數位一致** | HR 全文統一（三位或兩位）；百分比一位；SMD 三位                                                       |
> | **時態**       | Methods / Results 用過去式；Discussion / Conclusions 用現在式                                         |
> | **縮寫**       | 首次出現須定義；**Abstract 與正文各自獨立定義一次**；只出現一次的縮寫直接拿掉                         |
> | **術語一致**   | `atezolizumab plus bevacizumab` 不要中途變成 `atezo-bev` / `A+B`                                      |
> | **數字寫法**   | 句首的數字用英文拼字；千分位逗號統一（1,800 不是 1800）                                               |
> | **圖表引用**   | 文中 Figure 1–4 都必須被引用**且依序出現**；每張圖都有 legend                                         |
> | **章節順序**   | Title → Abstract → Intro → Methods → Results → Discussion → Conclusions → 聲明 → References → Legends |
> | **字數**       | Abstract ≤ 250；正文（Intro–Conclusions）報告實際字數                                                 |
> | **連結可用**   | Data availability 裡的路徑與指令真的存在、真的能跑                                                    |

### ⚠️ 地雷

1. 🔴 **潤稿之後必須第三次重跑數字稽核。** 「統一小數位」這個動作本身
   就是在改數字。改完不查等於白改。
2. **不要在 polish 階段改動宣稱強度。** 把 `suggests` 改成 `shows` 讀起來比較有力——
   但那是科學內容的改動，屬於 7.2，而且多半是錯的。
3. **縮寫規則常被忽略的一條：Abstract 是獨立的。** 讀者可能只讀摘要，
   所以摘要裡第一次出現的 HR 要寫成 `hazard ratio (HR)`，正文再定義一次。
4. **句首數字**：`1,800 patients were included` 應改成
   `A total of 1,800 patients were included`（不要把數字拼成 `One thousand eight hundred`）。
5. **不要用 sed 全域取代數字。** `sed s/0.58/0.578/g` 會把 `0.583` 變成 `0.5783`。
   逐處確認。

### 驗收 `../.venv/bin/python verify/ch07.py --mission 7.3`

---

## 🎤 停 — `⏸ Mission 7.3 完成，等候指示。`

---

## Mission 7.4 — Humanize：把 AI 腔拿掉

**目標**：讀起來像人寫的，而且**數字一個都沒動**。

### ⛔ 這一關的界線（先讀，這是原則問題不是技術問題）

「AI humanizer」這個生態系裡有三類工具，**第三類一律不准碰**：

| 類別                                                             | 例子                                                                                                             | 這裡能不能用                                        |
| ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| **確定性 pattern linter** — 列出你寫作上的 AI 慣性，讓你自己改   | `llmstrip`、`slopbuster`、Vale                                                                                   | ✅ 用這類。可稽核、不改語意。                       |
| **公開規則的 agent 改寫技能** — 規則寫在檔案裡、明令不得捏造事實 | [`blader/humanizer`](https://github.com/blader/humanizer)（33 個 pattern，源自 Wikipedia _Signs of AI writing_） | ⚠️ 可以用，**但必須夾在 linter 與稽核之間**（見下） |
| **「undetectable」改寫器** — 目標是騙過 AI 偵測器                | 各種標榜 _undetectable_ / _bypass detector_ 的服務                                                               | ❌ **不准用。**                                     |

第二類為什麼要加條件：`humanizer` 是**語言模型改寫**，不是確定性工具。
同一份稿子跑兩次結果不會一樣。它自己的規則裡寫著
「rewrites may not invent facts, names, dates, or citations not present in the source」——
**但那是它的自律，不是我們的保證。** 我們的保證是 Mission 6.9 的數字稽核。
所以流程一定是：**先量（linter）→ 再改（humanizer）→ 再量 → 再稽核。**

第三類為什麼一律不准：**我們的目標是讓文字更好讀，不是隱瞞 AI 參與過。**
在科學稿件上做後者，等於對期刊與讀者謊報作者身分。多數期刊現在都要求揭露 AI 使用。

**所以這一關同時要做一件事：確認手稿帶有 AI 使用揭露聲明。**
如果你把文字修得像人寫的、卻拿掉了揭露，那不是 humanize，那是造假。

### 任務

> **A. 先跑機器檢查（確定性、可重跑）**
>
> `llmstrip`（Rust CLI，MIT，**只報告不改檔**）：
>
> ```bash
> # 安裝一次即可
> curl -fsSL https://raw.githubusercontent.com/HugoLopes45/llmstrip/main/scripts/install.sh | sh
>
> # 只報告，不動檔案
> llmstrip --report workspace/manuscript/manuscript.md
> ```
>
> 記下**修改前的問題數**。
>
> 若環境另有這些，一併用（都是 MIT、都可 report-only）：
>
> - `slopbuster`（152 個 pattern，`--score-only` 只評分不改寫）
> - `human-write` skill：`/human-write workspace/manuscript/manuscript.md`
>
> **B. 先備份，再用 `humanizer` 改寫**
>
> ```bash
> # 備份。這一步不是形式——沒有它就沒辦法 diff，也沒辦法回滾
> cp workspace/manuscript/manuscript.md workspace/manuscript/manuscript.pre-humanize.md
> ```
>
> 安裝（三選一，擇其一即可）：
>
> ```bash
> npx skills add blader/humanizer --global        # Skills CLI
> # 或 Claude Code plugin：
> #   /plugin marketplace add blader/humanizer
> #   /plugin install humanizer@humanizer   → 用 /humanizer:humanizer 叫出
> # 或手動：
> git clone https://github.com/blader/humanizer.git ~/.claude/skills/humanizer
> ```
>
> `humanizer`（v2.9.x）是 33 條 pattern 的 LLM 改寫 skill，自帶
> draft→audit→final 迴圈與 no-fabrication 自律。它的「不捏造事實」是自律，
> **`verify/ch06.py --mission 6.9` 才是我們的保證**——所以下面每一趟都要能 diff、要能回滾。
>
> ---
>
> **B.1 Voice calibration——餵真樣本，不要讓它回到「通用乾淨英文」**
>
> `humanizer` 自己警告：沒餵樣本時它會回到一種 generic clean English，
> **那本身也是一種 AI tell**。對醫學手稿，餵 2–3 段**目標期刊已刊登的 editorial
> 或同主題已發表論文的 Discussion**（例如 NEJM／JCO 的社論）當語感樣本。
> 它只學節奏、用詞習慣與段落呼吸，**不會把別人的事實搬進來**——
> 但你仍要在 prompt 裡重申 no-fabrication，不要假設它自己會守。
>
> ```
> /humanizer
> 語感樣本（僅供 voice matching，不得搬取其事實到我的稿裡）：
> <貼 2–3 段已刊登 editorial>
>
> 以下為待改寫的稿件……
> ```
>
> 沒有樣本時**明確告訴它**：「這是醫學期刊手稿，用正式、中性、過去式的學術 register，
> 不要注入第一人稱意見或部落格腔。」——把它從「通用乾淨」推往「學術乾淨」。
>
> ---
>
> **B.2 分段呼叫 + 分段豁免集（這一步是效果強弱的關鍵）**
>
> 🔴 **不要整篇丟進去。** 整篇丟，`humanizer` 會對 Methods 的被動語態與
> Discussion 的 hedge 套用同一套規則，結果要嘛 Methods 被改成主動（違反期刊慣例），
> 要嘛 Discussion 的 `suggests` 被偷掉（= spin）。**逐段呼叫，每段重述不同的豁免**：
>
> | 段落                   | humanizer 想動的 pattern                          | 該段豁免（不准動）                                                         | 該段可收（准動）          |
> | ---------------------- | ------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------- |
> | **Methods**            | §13 被動、§14 em dash、§15 boldface               | **被動語態保留**；卡尺、ATT、合成資料聲明原文；數字                        | em dash、無意義 boldface  |
> | **Results**            | §7 AI 詞彙、§8 copula、§13 被動                   | 數字／單位／CI／p 一字不改                                                 | AI 詞彙、`serves as`→`is` |
> | **Discussion**         | §7 詞彙、§24 hedging、§31 staccato                | **`suggests`/`is consistent with`/`recovered` 一字不改**；不准加不確定語氣 | AI 詞彙、句長打散         |
> | **Limitations**        | §10 rule-of-three、§16 inline-header list         | **七項條列保持**，不准改散文                                               | 過度 boldface             |
> | **Intro／Conclusions** | §1 significance inflation、§25 generic conclusion | 不得新增事實；不得把 `suggests` 升級                                       | 空心副詞、套話結尾        |
> | **Use of AI tools 段** | 全部                                              | **整段豁免，一字不改**                                                     | 無                        |
>
> 每段呼叫時把該列的豁免**逐條寫進 prompt**，不要只寫「請遵守學術慣例」。
> 以下四條通用硬性界線**每段都要重申**：
>
> 1. 不得更動任何數字、單位、小數位、信賴區間、p 值。
> 2. 不得更動宣稱強度（suggests／is consistent with／recovered 一字不改）。
> 3. 不得新增來源裡沒有的事實、人名、年份或引用。
> 4. 不得更動 "Use of AI tools" 那一段。
>
> ---
>
> **B.3 第二趟節奏專修（直接打 verify 的句長變異指標）**
>
> `verify/ch07.py` 量句長變異——AI 文最大特徵是句長過於平均。`humanizer` 的
> §31（manufactured punchlines／staccato drama）只在「連續短句」時觸發，
> 對「全部中等長度」的被動均勻不會動。對 Discussion 與 Conclusions 再跑一趟
> **定向呼喚**（embedded mode，只要最終文字）：
>
> ```
> /humanizer
> 只做一件事：把這段的句長打散，每段刻意插一個八字內的短句。
> 硬性界線：不准動數字、不准動 hedge（suggests／consistent with／recovered）、
> 不准加軼事、不准加不確定語氣。其他 AI pattern 這趟先不要動。
> ```
>
> ---
>
> **B.4 用 audit bullets 當第二條量測軸**
>
> `humanizer` 在 **pasted-text mode** 會吐出「What makes this obviously AI generated?」
> 的 audit bullets，以及「Does the rewrite state any fact not in the source?」的回覆。
> **逐段用 pasted-text mode 跑**（不要用 file mode 黑箱），把每段的 audit bullets
> 收進 `humanize_report.md`。這給你一條 `llmstrip` 數字之外的**質性證據**，
> 證明「改了什麼、為什麼」，也讓你在改寫當下就能看到它自承的 fabrication 風險。
>
> 改完**先 diff 再說**：
>
> ```bash
> diff -u workspace/manuscript/manuscript.pre-humanize.md \
>         workspace/manuscript/manuscript.md | head -200
> ```
>
> **逐段看過 diff**。凡是動到數字、動到 hedging、動到 Limitations 條目的，**改回去**。
>
> **C. 依 linter 報告逐項修改**（下面 1–6 是即使沒有工具也要自己做的，
> 也是用來收拾 `humanizer` 沒處理到 / 處理過頭的地方）
>
> **D. 修改後再跑一次 `llmstrip --report`**，記下**修改後的問題數**。
> 兩個數字都要寫進報告——**沒有前後對照就無法證明你真的改了什麼**。
>
> **E. 確認手稿有 AI 使用揭露**（見下方地雷 7）。
> **`humanizer` 本身也要寫進那段揭露裡**——它改過正文，就是參與過寫作的工具。
>
> 把全部處理結果寫進 `workspace/manuscript/humanize_report.md`，至少包含：
> 用了哪些工具與版本／voice calibration 樣本來源／
> `llmstrip` 前後問題數／`humanizer` 各段的 audit bullets 摘要／
> 分段 diff 摘要（Methods／Results／Discussion／Limitations 各改了幾處、哪幾處被你改回去）／
> 第二趟節奏專修前後的句長分布對照／最終 Limitations 仍是七項的 `grep -c` 證據。
>
> **1. 詞彙**——找出並替換這些高頻 AI 詞：
> `delve into`, `leverage`(當動詞), `robust`(非統計意義的濫用), `comprehensive`,
> `landscape`, `underscore`, `pivotal`, `testament to`, `it is worth noting that`,
> `it is important to note`, `in the realm of`, `navigate`(比喻用法),
> `showcase`, `intricate`, `crucial`(每段都出現時), `furthermore`+`moreover`+`additionally` 連發
>
> **2. 句子節奏**——AI 寫的句子長度過於平均。
> 統計每段的句長分布，**刻意製造長短交錯**。一個八字的短句，力量比三個長句大。
>
> **3. 段落結構**——不要每段都「三句：主張 + 支持 + 小結」。
> 學術寫作的段落長度本來就參差。
>
> **4. 刪掉總結性重複**——AI 喜歡在段末重述段首。找出來刪掉。
>
> **5. 刪掉空心副詞**——`significantly`（非統計義）、`notably`、`remarkably`、`clearly`。
>
> **6. 主動語態**——`We matched patients 1:1` 勝過
> `Patients were matched in a 1:1 fashion`。（但方法學段落用被動是可以的。）

### ⚠️ 地雷

1. 🔴 **不准動任何數字、任何宣稱強度、任何限制條款。**
   humanize 只改「怎麼說」，不改「說什麼」。
   **改完第四次重跑數字稽核。**
2. 🔴 **`significant` 在統計語境是專有詞，不要當成空心副詞刪掉。**
   `statistically significant` 保留；`significantly improved outcomes`（沒有檢定）刪掉。
3. **不要為了「像人」而加入不確定語氣。** 「我們認為可能也許」不是人味，是心虛。
4. **不要加入第一人稱軼事。** 這是論文不是部落格。
5. **英式 / 美式拼法要選一個並統一**（randomised vs randomized）。
   本 repo 既有文件用**英式**，跟著用。
6. **警告：這一關最容易把 Limitations 稀釋掉。** AI 腔的一個特徵是
   「條列式的、機械的限制清單」——但那份清單**本來就應該是機械的**。
   把它改成流暢的散文很可能會弄丟其中一兩項。**改完數一次：還是七項嗎？**
7. 🔴 **手稿必須有 AI 使用揭露聲明，而且這一關不准動它。**
   放在 Data availability 附近，一段就好，具體寫出：

   ```markdown
   ## Use of AI tools

   Analyses were executed by an AI coding agent under author supervision,
   following the mission specifications in `live-demo/`. The agent wrote the
   harmonisation, matching, survival, robustness and TMLE scripts, and drafted
   the manuscript from the artefacts those scripts produced. Every reported
   number was re-checked against its source artefact by `live-demo/verify/`;
   every reference was validated against Crossref. Prose was subsequently
   edited for readability with pattern-based tools (`llmstrip`,
   `blader/humanizer`); no numerical result, effect estimate or limitation was
   altered in that pass. The author is responsible for the design, the
   interpretation and the final text.
   ```

   **「讓文字讀起來像人寫的」與「假裝沒有用 AI」是兩回事。** 前者是編輯，後者是造假。
   `verify/ch07.py` 會檢查這段還在。

8. **不准使用標榜 “undetectable” / “bypass AI detector” 的工具或提示詞。**
   本關的成功指標是 `llmstrip --report` 的問題數下降，**不是**任何偵測器的分數。
9. 🔴 **`humanizer` 的 33 條規則有四條跟學術寫作正面衝突，要手動豁免：**
   這四條對應的 pattern 號碼與分段處理方式，已列在上方 **B.2 的分段豁免表**——
   這裡是濃縮版，方便台上講：

   | pattern                                       | 它想改的                         | 在論文裡的實情               | 怎麼辦                                   |
   | --------------------------------------------- | -------------------------------- | ---------------------------- | ---------------------------------------- |
   | §24 _excessive hedging_                       | `suggests`、`is consistent with` | Mission 6.5 精算過的語氣分級 | **一字不改。**去掉 hedge 就是 spin       |
   | §13 _passive voice_                           | `Patients were matched…`         | Methods 用被動是期刊慣例     | Methods 段豁免；Results／Discussion 才收 |
   | §10 _rule-of-three_／§16 _inline-header list_ | 七項 Limitations                 | **本來就該是機械的清單**     | 保持條列，改散文一定漏項                 |
   | §14 _em dash_／§15 _boldface_                 | 過度裝飾                         | 這條可以照收                 | 唯一可以全盤接受的一類                   |

   **改完數一次 Limitations：還是七項嗎？`grep -c` 一下，不要用眼睛數。**
   （B.2 的分段豁免表是這條的執行細節；兩處講的是同一件事，不要漏掉任何一條。）

10. 🔴 **`humanizer` 是 LLM 改寫，不是 linter——它動的是整段，不是幾個詞。**
    所以順序不可以顛倒：**先量、備份、分段改寫（B.2）、節奏專修（B.3）、diff、再量、再稽核。**
    沒有 `manuscript.pre-humanize.md` 就沒有 diff，沒有 diff 你根本不知道它改了什麼；
    沒有分段，你根本不知道是哪一段被改壞。等到數字稽核跳紅字，
    你已經找不到是哪一輪、哪一段改壞的。
    **它的「不捏造事實」是自律，`verify/ch06.py --mission 6.9` 才是保證。**
    B.4 的 audit bullets 是它在改寫當下**自承**的 fabrication 風險——逐段收下來，
    事後比對 diff，凡是它自己 flagged 卻還是動了的，一律改回去。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch07.py --mission 7.4
```

---

## 🎤 停 — 講者接話

`⏸ Mission 7.4 完成，等候指示。`

> 講者（詳見 [RUNBOOK.md](RUNBOOK.md#m74)）：
> 「我們改了四輪字。稽核跑了四次。**四次都通過，代表這四輪裡沒有一個數字被改壞。**
> 如果沒有這個稽核，我根本不敢讓 AI 幫我潤稿。」

下一關：[08-release.md](08-release.md) — 變成可以投出去的 PDF。
