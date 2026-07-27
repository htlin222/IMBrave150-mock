# 第 05 章 — 試著把自己的結論弄壞

> 對應投影片：**Act V · Robustness**｜預估 8 分鐘｜Mission 5.1 – 5.3

到目前為止我們做了**一條**分析路徑，得到 0.578。
但那條路徑上有幾十個「我當時就這樣決定了」的選擇：放哪些共變數、卡尺多寬、
配 1:1 還是 1:2、用配對還是加權還是迴歸。

**換一條路，答案會不會變？** 這一章把 120 條路一次跑完。
然後 Mission 5.3 做一件更根本的事：**換一個 estimand**。

---

## Mission 5.1 — 120 種分析路徑

**目標**：`workspace/multiverse.csv`，120 列，每列一種合理的分析設定。

### ⛔ 硬性約束（寫第一行程式碼之前讀）

```python
# 1. IPTW 的 Cox 一定要 weights_col + robust=True
#    少了 robust=True 不報錯，只讓 CI 窄到不合理（點估計對、CI 錯）
CoxPHFitter().fit(d, "os_time_months", "os_event", weights_col="w", robust=True)

# 2. 用穩定化權重，不要用 1/ps
p_treat = df.treat.mean()
w = np.where(df.treat == 1, p_treat / ps, (1 - p_treat) / (1 - ps))

# 3. 傾向分數「每個共變數集合」只算一次（15 次），不是每個設定算一次（120 次）
#    算錯的話這支腳本會從 10 秒變成 1 分鐘以上
# 4. 迴圈裡印進度：[ 37/120] PSM · drop_age · cal=0.2 · 1:1 → HR 0.591
```

### 任務

> 寫 `workspace/multiverse.py`。**資料完全固定**，只變動分析選擇：
>
> **共變數集合（15 種）**
> - `full`：Mission 2.2 那 11 個
> - `drop_<X>`：11 種，每次拿掉一個
> - `core4`：`afp_ge_400, macrovascular_invasion, ecog_ps, albi_ge2`
> - `core6`：core4 + `extrahepatic_spread, varices_at_baseline`
> - `clin+site`：`afp_ge_400, macrovascular_invasion, ecog_ps, asia`
>
> **調整方法（每個共變數集合 8 種）**
> - 迴歸調整（多變數 Cox）× 1
> - IPTW（穩定化 ATE 權重）× 1
> - PSM 配對：卡尺 ∈ {0.1, 0.2, 0.5} × 比例 ∈ {1:1, 1:2} = 6
>
> 15 × 8 = **120 種設定**。每種輸出 `method, covset, caliper, ratio, n, hr, lo, hi`。
>
> 印出：天真估計、設定數、中位數 HR、IQR、全距、落在 0.55–0.61 的比例。

### 📖 你應該看到

```
Naive (unadjusted) OS HR : 0.505 (0.43-0.60)
Adjusted specifications  : 120
  median HR              : 0.583
  IQR                    : 0.560 - 0.608
  range                  : 0.515 - 0.699
  within 0.55-0.61       : 66%
```

**天真估計 0.505 孤零零地待在外面；120 種調整方法的中位數是 0.583。**

但請注意最後兩行——這是誠實的部分：全距是 **0.515 到 0.699**，
只有 **66%** 落在 0.55–0.61 這個窄帶裡。**不是每條路都給你 0.58。**
會場一定有人問這個，你要主動講。

### ⚠️ 地雷

1. 🔴 **不要宣稱「所有設定都一致」。** 66%、全距 0.515–0.699 就是 66%、0.515–0.699。
   誠實的說法是：**「每一種合理的調整都把估計從 0.505 拉離、拉向 0.58 附近；
   剩下的離散來自方法本身，而不是來自結論方向。」**
   沒有任何一個設定翻轉方向，沒有一個設定的 CI 蓋到 1.0——**這**才是重點。
2. 🔴 **IPTW 的 Cox 必須用 `weights_col=` 且 `robust=True`。**
   ```python
   CoxPHFitter().fit(d, "os_time_months", "os_event", weights_col="w", robust=True)
   ```
   忘了 `robust=True`，lifelines 會把權重當成頻率權重，**標準誤嚴重低估**，
   CI 會窄到不合理。點估計是對的，CI 是錯的——最難察覺的一種錯。
3. **用穩定化權重**：`w = p_treat/ps`（treated）、`(1-p_treat)/(1-ps)`（control），
   其中 `p_treat = df.treat.mean()`。未穩定化的 `1/ps` 在極端傾向分數處會爆出巨大權重，
   讓某幾個病人主導整個估計。
4. **`drop_asia` 那個設定會明顯偏掉——這是刻意的教材。** 拿掉醫院區域之後
   殘餘的醫院層級干擾就回來了。跑出來比別人偏，不是 bug。
   （這也回答了「醫院要不要當共變數」這個問題。）
5. **1:2 配對的實作。** 每個 treated 取最近的 2 個尚未使用的對照，
   且**兩個都要在卡尺內**才收（或至少收有進卡尺的那些）。
   決定好一種規則並寫在註解裡——這正是「分析者自由度」的具體例子。
6. ⏱ **這支腳本約 10 秒跑完**（實測 9.7 秒：120 次 Cox 配適 + 90 次配對）。
   不需要為它道歉，但**還是要在迴圈裡印進度**：
   `[ 37/120] PSM · drop_age · cal=0.2 · 1:1 → HR 0.591`——
   觀眾看得到 120 次真的在跑，比看到一個結果數字有說服力得多。
   如果你的版本跑超過一分鐘，八成是在迴圈裡重複讀 CSV 或重複配適傾向分數模型：
   **傾向分數每個共變數集合只要算一次**（15 次），不是每個設定算一次（120 次）。
7. **不要把 120 個設定的 p 值拿去做任何檢定或校正。** 這是描述性的規格曲線，
   不是多重檢定。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch05.py --mission 5.1
```

---

## 🎤 停 — `⏸ Mission 5.1 完成，等候指示。`

---

## Mission 5.2 — 規格曲線圖

**目標**：`workspace/figures/multiverse.png`，一張圖說完上面那段話。

### 任務

> 左右兩個面板：
> - **左（寬）**：規格曲線。x 軸是 120 個設定（**依 HR 由小到大排序**），
>   y 軸是 HR，每點帶 95% CI。依方法上色（PSM / IPTW / Regression）。
>   畫兩條水平線：**0.58（真值／試驗）虛線**、**0.505（天真估計）點線**，都要標字。
> - **右（窄）**：120 個調整後 HR 的直方圖，標出中位數、真值、天真估計。
>
> 標題要說結論：`Every reasonable adjustment lands near 0.58 · 120 specifications`

### ⚠️ 地雷

1. **排序是「依估計值」，不是依設定名稱。** 規格曲線的意義就在於看分布形狀。
2. **天真估計那條線要用不同線型 + 不同顏色**，而且要標數字。
   它是這張圖的反派，不能跟其他線混在一起。
3. **y 軸範圍要涵蓋天真估計的 CI 下界**（約 0.43），否則那條線會被擠出畫面。
4. **這張圖用 PNG 可以接受**（120 個誤差棒的 SVG 檔會很肥，投影時可能卡頓），
   但 `dpi >= 130`。
5. 配色 Okabe-Ito：PSM `#0072B2`、IPTW `#E69F00`、Regression `#009E73`、
   天真 `#D55E00`。**不要用預設的 matplotlib 色環**，投影機下藍綠會分不出來。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch05.py --mission 5.2
```

---

## 🎤 停 — `⏸ Mission 5.2 完成，等候指示。`

---

## Mission 5.3 — 換一個 estimand：TMLE

**目標**：示範「**先講清楚你要估什麼，再選方法**」。

到現在為止所有數字都是**風險比（hazard ratio）**。但臨床上更好懂的問題是：
**「12 個月的時候，兩組的死亡機率差多少？」** 那是**風險差（risk difference）**，
是完全不同的尺度。

而因為這是模擬資料，**我們知道真值**，可以直接檢查誰估得準。

### ⛔ 硬性約束（寫第一行程式碼之前讀）

```python
# 1. 審查權重的 KM 要把「審查」當成事件 —— 寫成 fit(t, os_event) 方向完全相反
kmG = KaplanMeierFitter().fit(df.os_time_months, 1 - df.os_event)

# 2. 醫院虛擬變數一定要 drop_first=True，否則設計矩陣共線、Hessian 奇異
hdum = pd.get_dummies(df.hospital_id, prefix="site", drop_first=True).astype(float)

# 3. 12 個月前被審查的人 Y 未知（Delta=0），不可以直接丟掉 —— 要 IPCW 加權回來
# 4. g(W) clip 到 [0.02, 0.98]，並報告 clip 前的實際範圍
# 5. 整支腳本必須是決定性的：重跑要逐位元相同
```

**輸出是風險差（−1 到 1 的機率尺度），不是 hazard ratio。看到正數或看到 0.5 附近就是錯了。**

### 任務

> 寫 `workspace/tmle.py`，估計
> `RD = P(12 個月內死亡 | atezo+bev) − P(12 個月內死亡 | sorafenib)`：
>
> 1. **Landmark 結果變數**：`Y = 1` 若在 12 個月內死亡；`Y = 0` 若在 12 個月時仍存活；
>    **若在 12 個月前就被審查則 `Y` 未知（`Delta = 0`）**。
> 2. **共變數 W**：Mission 2.2 那組臨床變數 + **醫院虛擬變數**（`drop_first=True`）。
> 3. **處理機制** `g(W) = P(A=1|W)`：邏輯迴歸，clip 到 [0.02, 0.98]。
> 4. **審查權重**：對「審查」做 Kaplan–Meier 得到 `G(u)`，取 `gc = G(min(t, 12))`。
> 5. 估四個量：`G-computation`、`IPTW`、`AIPW`、`TMLE`（後兩者附影響函數 SE）。
> 6. 另外算**天真的 complete-case 差值**當對照。
> 7. 寫 `workspace/tmle.json`，含上述全部 + 你算出的真值（見下）。
>
> **真值（本資料的資料生成機制是已知的，可解析計算）：**
> ```python
> lp = (np.log(1.55)*afp_ge_400 + np.log(1.45)*mvi + np.log(1.30)*ehs +
>       np.log(1.35)*ecog_ps + np.log(1.25)*bclc_C + np.log(1.20)*albi_ge2)
> lp_c = lp - lp.mean()
> FRAILTY = {H01:-0.10, H02:+0.05, H03:-0.06, H04:+0.12, H05:+0.02,
>            H06:-0.04, H07:+0.15, H08:-0.08, H09:+0.06, H10:+0.03}
> rate_a = exp(log(0.05) + log(0.58)*a + lp_c + frailty)
> R_a    = mean(1 - exp(-12 * rate_a))
> RD_true = R_1 - R_0
> ```

### 📖 你應該看到

```
Estimand: risk difference in DEATH BY 12 MONTHS  (treat - control)
  TRUE  (from DGP)     : -0.154   [= 0.302 - 0.456]
  NAIVE complete-case  : -0.228   <- biased (confounded)
  G-computation        : -0.168
  IPTW                 : -0.140
  AIPW  (doubly robust): -0.144  (SE 0.037)
  TMLE  (doubly robust): -0.150  (SE 0.037)  95% CI [-0.221, -0.078]
```

真值 **−0.154**，TMLE 給 **−0.150**。天真估計 −0.228 誇大了將近 50%。

### ⚠️ 地雷

1. 🔴 **−0.150 不能拿去跟 0.578 比較。** 它們是**不同的估計目標**：
   一個是 12 個月死亡機率的絕對差（百分點），一個是整段追蹤期的風險比（比值）。
   在手稿裡把它們並列時，必須明說是兩個 estimand。
   **「Estimand first, method second」** 是這一關唯一要觀眾記住的一句話。
2. 🔴 **12 個月前被審查的人不能直接丟掉。** 直接 complete-case 就是上面那個 −0.228
   的一部分原因。必須用 IPCW（對審查分布做 KM）加權回來。
3. **審查權重的 KM 要把「審查」當成事件**：`KaplanMeierFitter().fit(t, 1 - os_event)`。
   寫成 `fit(t, os_event)` 會得到存活曲線而不是審查曲線，方向完全相反。
4. 🔴 **醫院必須進 W。** 醫院同時影響處方（Mission 1.3 那張 65.9% vs 34.7% 的表）
   和預後（資料生成裡的 frailty 項）。少了醫院虛擬變數就有殘餘干擾，
   TMLE 會系統性偏掉。用 `pd.get_dummies(hospital_id, drop_first=True)`——
   **一定要 `drop_first`**，不然設計矩陣共線、Hessian 奇異。
5. **positivity（正性假設）**：`g(W)` clip 到 [0.02, 0.98]。
   如果 clip 之前就有一堆人落在 0.001 附近，代表有些人「幾乎不可能拿到某種治療」，
   對他們的因果對比是外推出來的。這份資料重疊性好，但要檢查並報告 `g` 的範圍。
6. **雙重穩健不是萬靈丹。** AIPW/TMLE 只要處理模型**或**結果模型其一正確就一致——
   但「其一正確」在真實資料裡沒人能保證。這裡兩個都正確（因為我們知道 DGP），
   所以表現很好。**真實研究不會這麼幸運**，Discussion 要寫。
7. **這支腳本是完全確定性的**（沒有隨機數），重跑必須逐位元相同。
   如果你的結果每次不一樣，代表某處用了隨機（例如 `sklearn` 的 `solver` 有隨機初始化）。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch05.py --mission 5.3
```

---

## 🎤 停 — 講者接話

`⏸ Mission 5.3 完成，等候指示。`

> 講者（詳見 [RUNBOOK.md](RUNBOOK.md#m53)）：
> 「我花了三分鐘試著把自己的結論弄壞，沒弄壞。這三分鐘的價值，
> 比前面那個 0.578 高。因為 0.578 是**一個**答案，這裡是**一百二十個**答案。」

下一關：[06-manuscript.md](06-manuscript.md)
