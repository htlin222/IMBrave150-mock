# 第 02 章 — 未調整的答案在說謊

> 對應投影片：**Act II · De-confounding**｜預估 15 分鐘｜Mission 2.1 – 2.4

這一章是整場的軸心。我們會先算出一個**看起來很棒的錯誤答案**（HR 0.505），
證明它為什麼是錯的，然後用傾向分數配對把它修回 **0.578**。

---

## Mission 2.1 — 先問一個笨問題：不調整會怎樣？

**目標**：算出天真的、未調整的 Cox HR。這個數字會很漂亮，而且是錯的。

### 任務

> 讀 `workspace/pooled.csv`，建立 `treat = (arm == "Atezo+Bev")`，
> 用 `lifelines.CoxPHFitter` 只放 `treat` 一個變數，對 OS 配適 Cox 模型。
>
> 印出：兩組人數、事件數、HR、95% CI、p 值。
> 把結果寫成 `workspace/naive_hr.json`，格式：
>
> ```json
> {"n": 1800, "n_treat": 962, "n_control": 838,
>  "hr": 0.505, "ci_low": 0.43, "ci_high": 0.60, "p": 1.2e-13}
> ```
>
> 然後用中文說一句話：如果只看這個數字，你會下什麼結論？

### 📖 你應該看到

```
POOLED OBSERVATIONAL COHORT  n = 1800 | Atezo 962 / Sora 838
NAIVE unadjusted OS HR : 0.505 (0.43-0.60)
```

死亡風險降低 **49.5%**。而真實的隨機分派試驗說的是降低 42%（HR 0.58）。
**我們的觀察性資料「看起來」比隨機試驗還漂亮。** 這就是危險的地方——
偏誤讓結果變好看，沒有人會想去查。

### ⚠️ 地雷

- **`CoxPHFitter.fit()` 餵進去的 DataFrame 只能有時間、事件、共變數。**
  整個 `pooled.csv` 丟進去會因為字串欄（`arm`、`etiology`）直接爆，
  或更糟——被 lifelines 自動 dummy 化，變成你沒打算跑的多變數模型。
  明確挑 `df[["os_time_months","os_event","treat"]]`。
- **HR < 1 代表比較好，但別把 0.505 唸成「存活率 50%」。** 那是風險比，不是存活率。
- **不要在這一關做任何調整。** 觀眾必須先相信這個錯答案，反轉才有力道。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch02.py --mission 2.1
```

---

## 🎤 停 — `⏸ Mission 2.1 完成，等候指示。`

---

## Mission 2.2 — 證明它在說謊：兩組人本來就不一樣

**目標**：做 Table 1，用**標準化平均差（SMD）**而不是 p 值，指認出干擾因子。

### 任務

> 對 `pooled.csv` 做一張分組基線表，寫到 `workspace/baseline_table1.csv`。
>
> 共變數（之後傾向分數模型也用同一組，先在這裡建好）：
>
> ```python
> df["bclc_C"]   = (df.bclc_stage == "C").astype(int)
> df["albi_ge2"] = (df.albi_grade >= 2).astype(int)
> df["male"]     = (df.sex == "Male").astype(int)
> df["asia"]     = (df.hospital_region == "Asia excluding Japan").astype(int)
>
> COVS = ["age","ecog_ps","child_pugh_score","afp_ge_400",
>         "macrovascular_invasion","extrahepatic_spread","bclc_C",
>         "albi_ge2","varices_at_baseline","male","asia"]
> ```
>
> 每一列輸出：`covariate, mean_treat, mean_control, smd`
>
> SMD 定義（兩組合併標準差當分母）：
>
> ```
> SMD = (mean_treat - mean_control) / sqrt((var_treat + var_control) / 2)
> ```
>
> 然後用中文回答：**哪些變數 |SMD| > 0.1？它們各自往哪個方向偏？
> 這個偏法會讓天真的 HR 變大還是變小？**

### 📖 你應該看到

| covariate | atezo | sora | SMD |
|---|---|---|---|
| age | 62.8 | 65.2 | **−0.210** |
| ecog_ps | 0.358 | 0.434 | **−0.157** |
| child_pugh_score | 5.306 | 5.308 | −0.005 |
| afp_ge_400 | 0.325 | 0.436 | **−0.228** |
| macrovascular_invasion | 0.319 | 0.427 | **−0.225** |
| extrahepatic_spread | 0.552 | 0.652 | **−0.204** |
| bclc_C | 0.827 | 0.842 | −0.040 |
| albi_ge2 | 0.499 | 0.587 | **−0.178** |
| varices_at_baseline | 0.244 | 0.323 | **−0.176** |
| male | 0.820 | 0.805 | +0.038 |
| asia | 0.541 | 0.483 | **+0.115** |

**每一個預後不良因子都往同一個方向偏**：拿到 atezo+bev 的人比較年輕、體能狀態比較好、
AFP 比較低、比較少大血管侵犯、比較少肝外轉移、肝功能比較好。

他們**本來就比較會活**。所以 0.505 裡面混了「藥的效果」＋「病人本來就比較好」。

### ⚠️ 地雷

1. **不要用 p 值判斷平衡。** n=1,800 的時候，一個臨床上完全不重要的差異也會 p<0.05；
   反過來在小樣本裡，天大的差異也可能 p>0.05。**p 值衡量的是證據強度，不是不平衡程度。**
   SMD 才是不受樣本數影響的指標。這是審稿人最常抓的錯誤之一。
2. **SMD 的分母是「兩組變異數平均後開根號」，不是 pooled SD 的統計課公式**
   （那個要用 n 加權）。配對前後要用**同一個定義**，否則前後不可比。
3. **二元變數的 SMD 也用同一條公式就好。** 有些教科書給二元變數另一條
   `(p1-p0)/sqrt((p1(1-p1)+p0(1-p0))/2)`——其實一樣，因為二元變數的變異數就是 p(1−p)。
   不要混用兩套。
4. **`child_pugh_score` 和 `bclc_C` 的 SMD 很小（0.005 / 0.040）——這是對的，不是你算錯。**
   不是每個變數都是干擾因子。留在模型裡無妨（它們與預後有關），但不要因為「太小」就刪掉。
5. **`asia` 這一欄來自 Mission 1.3 join 進來的 `hospital_region`。**
   如果你 Mission 1.3 沒 join，這裡會 KeyError。**醫院層級的變數是干擾因子的一部分**。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch02.py --mission 2.2
```

---

## 🎤 停 — `⏸ Mission 2.2 完成，等候指示。`

---

## Mission 2.3 — 傾向分數配對

**目標**：估計傾向分數，1:1 卡尺配對，得到 **706 對**。

### ⛔ 硬性約束（寫第一行程式碼之前讀）

```python
# 1. 共變數用 afp_ge_400（二元），絕不用 afp_ng_ml（連續）
#    → 用連續值會靜靜刪掉 Gamma 三站共 635 人。詳見地雷 1。

# 2. 卡尺是 logit(PS) 的標準差，不是 PS 的
caliper = 0.2 * df["logit_ps"].std()      # ← 應該落在 0.114 附近

# 3. 配對前一定要排序，否則結果不可重現
treated = df[df.treat == 1].sort_values("logit_ps")

# 4. 無放回：用過的對照必須標記掉
d = np.abs(ctrl_lp - t_lp); d[used] = np.inf

# 5. 邏輯迴歸加 ridge 避免 Hessian 奇異；用 sklearn 則要 penalty=None
H = X.T @ (X * W[:, None]) + 1e-8 * np.eye(k)
```

**三個自我檢查點**：卡尺 ≈ 0.114、配對後 `patient_id` 全部唯一、
配對世代仍包含 H03/H06/H09。任何一項不對，回來看對應的地雷。

### 任務

> 寫 `workspace/psm.py`：
>
> 1. **傾向分數**：邏輯迴歸 `treat ~ COVS`（就是 Mission 2.2 那 11 個變數），
>    輸出每個人的 `ps` 和 `logit_ps = log(ps/(1-ps))`。
> 2. **卡尺**：`caliper = 0.2 * SD(logit_ps)`。**注意是 logit(PS) 的標準差，不是 PS 的。**
> 3. **配對**：1:1、最近鄰、**不放回**。
>    為了可重現，**先把 treated 依 `logit_ps` 由小到大排序**再依序配。
>    距離超過卡尺就這個 treated 不配（丟掉）。
> 4. 寫出 `workspace/matched.csv`——配對成功的病人（treated + 其對照），
>    保留 `pooled.csv` 全部欄位，另加 `ps`、`logit_ps`、`pair_id`。
> 5. 印出：卡尺數值、配對成功對數、配對後總人數、**沒配到的 treated 有幾人**。

### 📖 你應該看到

```
[2] Propensity model fitted on 11 covariates.
[3] 1:1 caliper matching -> 706 matched pairs (1412 patients, caliper=0.114 on logit PS)
```

962 個 treated 只配到 706 個 → **256 人被丟掉（26.6%）**。這是有代價的：
估計的 estimand 從「全體的平均處理效果」變成「有可比對照的那群 treated 的效果」（ATT），
而且樣本變小、CI 變寬。**這件事必須寫進 Limitations。**

### ⚠️ 地雷（本章最毒的一關）

1. 🎭 **刻意示範**｜**連續 AFP 會靜靜吃掉三家醫院。**

   > **只在講者說「示範一下」時才做這段。** 平常一律用 `afp_ge_400`。

   30 秒的現場示範——把連續 AFP 放進模型，然後數一下還剩幾個人：

   ```python
   sub = df.dropna(subset=["afp_ng_ml"])          # 任何 complete-case 都等於這行
   print(len(df), "→", len(sub))                  # 1800 → 1165
   print("剩下的醫院:", sorted(sub.hospital_id.unique()))
   print("這個子集的天真 HR:", cox_hr(sub))        # 0.488，比 0.505 更偏
   ```

   ```
   n = 1800 → 1165   （少了 635 人，35.3%）
   剩下的醫院：H01 H02 H04 H05 H07 H08 H10   ← H03/H06/H09 整批消失
   那個子集的天真 HR = 0.488   ← 比原本 0.505 更偏
   ```

   **三家醫院不見了，而且不會有任何警告。** 你會得到一個看起來完全正常的分析，
   對象卻已經不是原本那個世代了。
   → 示範完，**改回 `afp_ge_400`（二元）**，這也是 PSM 真正需要的資訊。
   這正是 Mission 1.2 堅持「Gamma 的 AFP 留 NaN」的理由。

2. 🛡 **預防**（講者可選擇當場示範一次）｜**卡尺是 `0.2 × SD(logit(PS))`，不是 `0.2 × SD(PS)`。**
   後者會給你一個大約 0.2 × 0.09 ≈ 0.018 的卡尺（因為 PS 侷限在 0–1），
   配對數會掉到剩下兩三百對，而且你完全看不出哪裡錯了。
   **檢查點：卡尺應該落在 0.11 附近。** 差一個數量級就是踩到這顆雷。

3. 🛡 **預防**｜**不排序就配，結果不可重現。** 貪婪最近鄰配對對「處理順序」敏感。
   用 `df[df.treat==1].iterrows()` 的原始順序，換一次 pandas 版本或
   重跑一次 harmonise 就可能得到 698 或 712 對。
   **先 `sort_values("logit_ps")`**，讓順序由資料決定而非由檔案順序決定。

4. **不放回 = 用過的對照要標記掉。** 常見寫法是
   `d = np.abs(ctrl_lp - t_lp); d[used] = np.inf`。
   如果忘了 `d[used] = np.inf`，同一個對照會被重複配給多個 treated，
   配對數會漂亮地衝到 962 對——**然後你的標準誤全錯**。
   **檢查點：`matched.csv` 的 `patient_id` 必須全部唯一。**

5. **邏輯迴歸要收斂。** 手刻 Newton-Raphson 時 Hessian 可能奇異
   （共變數共線，例如 `bclc_C` 和 `ecog_ps`）。加一個小的 ridge：
   `H = X.T @ (X*W) + 1e-8 * np.eye(k)`。
   用 `sklearn.LogisticRegression` 的話記得 `penalty=None`——
   預設的 L2 會把傾向分數往中間縮，改變配對結果。

6. **`ps` 不要 clip 得太兇。** 這份資料重疊性很好，不需要 trimming。
   如果你發現需要 clip 到 0.05/0.95 才跑得動，先回去檢查是不是踩到第 1 點。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch02.py --mission 2.3
```

### 🆘 卡住時

參考解在 repo 根目錄 `psm_imbrave150.py` 第 56–92 行（**先自己寫過一次**）。

---

## 🎤 停 — `⏸ Mission 2.3 完成，等候指示。`

---

## Mission 2.4 — 檢查配對有沒有效：Love plot 與重疊圖

**目標**：證明配對後兩組真的變像了。**這是 PSM 論文唯一有說服力的圖。**

### 任務

> 1. 對 `matched.csv` 重算 Mission 2.2 的 SMD，做 `workspace/balance.csv`：
>    `covariate, smd_before, smd_after`（用配對前 `pooled.csv` 的值當 before）。
> 2. 畫 **Love plot** → `workspace/figures/love_plot.svg`
>    - y 軸：共變數；x 軸：|SMD|
>    - 每個共變數兩個點（before / after），用線連起來
>    - 在 0.1 畫一條垂直參考線
> 3. 畫 **傾向分數重疊圖** → `workspace/figures/ps_overlap.svg`
>    - 兩組 `ps` 的分布（密度圖或鏡像直方圖）
>    - 配對前後各一個面板
> 4. 用中文回答：**共同支持（common support）看起來如何？有沒有哪一段區間某一組完全沒有人？**

### 📖 你應該看到

| covariate | before | after |
|---|---|---|
| age | 0.210 | **0.019** |
| ecog_ps | 0.157 | **0.023** |
| child_pugh_score | 0.005 | 0.003 |
| afp_ge_400 | 0.228 | **0.017** |
| macrovascular_invasion | 0.225 | **0.044** |
| extrahepatic_spread | 0.204 | **0.038** |
| bclc_C | 0.040 | 0.019 |
| albi_ge2 | 0.178 | **0.034** |
| varices_at_baseline | 0.176 | **0.012** |
| male | 0.038 | 0.025 |
| asia | 0.115 | **0.003** |

**全部 11 個共變數配對後 |SMD| < 0.05**，遠低於 0.1 的門檻。

### ⚠️ 地雷

1. **|SMD| < 0.1 是經驗法則，不是統計檢定。** 不要寫成「p > 0.05 所以平衡」
   （見 Mission 2.2 地雷 1），也不要說「顯著平衡」——平衡沒有顯著性這回事。
2. **Love plot 的 before 必須來自「配對前的全體」，不是「配對後的 pooled 子集」。**
   拿配對後的資料去算 before，兩條線會重疊，圖就變成廢圖。
3. **Love plot 畫 |SMD| 絕對值。** 混著正負畫會讓「有沒有改善」看不出來。
   （分開報告方向是可以的，但主圖用絕對值。）
4. **重疊圖不是拿來炫技的。** 要看的是**共同支持**：有沒有某一段傾向分數區間，
   只有一組有人。如果有，那段區間的人根本無法配對，你的結論不適用於他們。
5. **不要只畫配對後的重疊圖。** 只畫後面看起來一定很好——那是配對的定義，不是證據。
   必須前後對照。
6. **配色用 colorblind-safe（Okabe-Ito）**，投影機色彩會失真，紅綠對比在會場常常糊掉。
   建議 `#0072B2`（藍）/ `#D55E00`（橘）。
7. **SVG 存檔用 `bbox_inches="tight"`**，否則 y 軸的長變數名會被裁掉。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch02.py --mission 2.4
```

---

## 🎤 停 — 講者接話

`⏸ Mission 2.4 完成，等候指示。`

> 講者（詳見 [RUNBOOK.md](RUNBOOK.md#m24)）：Love plot 是這場演講的第一個高潮。
> 左邊一排點散開，右邊一排點全部收在 0.1 線內。
> 「我們沒有改變任何一個病人的資料，我們只是**選了可以比較的人來比較**。」

下一關：[03-survival.md](03-survival.md)
