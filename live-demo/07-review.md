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
> | # | 角色 | 審什麼 |
> |---|---|---|
> | 1 | **統計審稿人** | estimand 定義是否清楚一致；傾向分數模型設定；卡尺與配對規則；平衡評估方法；配對後推論的獨立性假設；TMLE 的 positivity 與 IPCW；規格曲線的解讀是否過度樂觀 |
> | 2 | **臨床審稿人** | 共變數選擇在 HCC 是否合理（有沒有漏掉重要預後因子）；次群組是否臨床上有意義；效果量的臨床意義；用藥禁忌（食道靜脈曲張 vs bevacizumab）是否處理正確 |
> | 3 | **報告規範審稿人** | 對照 **STROBE** 與 **RECORD** 檢核表逐項打勾；缺哪幾項；資料來源與連結描述是否足夠；流程圖（participant flow）是否交代 1,800 → 1,412 的去向 |
> | 4 | **可重現性審稿人** | 只照 Methods 寫的內容，能不能重跑出 Results？逐一比對手稿數字與 `workspace/` 檔案；軟體版本；隨機性/決定性；資料與程式可得性 |
>
> 每位審稿人輸出格式固定：
> ```markdown
> # Reviewer N — <角色>
> ## Recommendation
> <Major revision | Minor revision | Reject>
> ## Major comments
> 1. **[位置：段落或句子]** 問題陳述。為什麼這是問題。建議怎麼改。
> ## Minor comments
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
> | 項目 | 規則 |
> |---|---|
> | **小數位一致** | HR 全文統一（三位或兩位）；百分比一位；SMD 三位 |
> | **時態** | Methods / Results 用過去式；Discussion / Conclusions 用現在式 |
> | **縮寫** | 首次出現須定義；**Abstract 與正文各自獨立定義一次**；只出現一次的縮寫直接拿掉 |
> | **術語一致** | `atezolizumab plus bevacizumab` 不要中途變成 `atezo-bev` / `A+B` |
> | **數字寫法** | 句首的數字用英文拼字；千分位逗號統一（1,800 不是 1800） |
> | **圖表引用** | 文中 Figure 1–4 都必須被引用**且依序出現**；每張圖都有 legend |
> | **章節順序** | Title → Abstract → Intro → Methods → Results → Discussion → Conclusions → 聲明 → References → Legends |
> | **字數** | Abstract ≤ 250；正文（Intro–Conclusions）報告實際字數 |
> | **連結可用** | Data availability 裡的路徑與指令真的存在、真的能跑 |

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

### 任務

> 若環境有 `human-write` skill，先用它掃一遍：
> ```
> /human-write workspace/manuscript/manuscript.md
> ```
> 然後人工複查下列各項，把處理結果寫進 `workspace/manuscript/humanize_report.md`：
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
