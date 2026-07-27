# 第 03 章 — 為什麼是 Kaplan–Meier，不是百分比

> 對應投影片：**Act III · Survival**｜預估 10 分鐘｜Mission 3.1 – 3.2

配對做完了，兩組人現在可以比較了。這一章要回答：**怎麼比？**
答案不是「算死亡率」——因為有**審查（censoring）**。

---

## Mission 3.1 — KM、log-rank、Cox

**目標**：在配對世代上得到 OS HR **0.578**——與真實隨機分派試驗的 0.58 一致。

### ⛔ 硬性約束（寫第一行程式碼之前讀）

```python
# 1. Cox 只餵三欄，不要把整張表丟進去
CoxPHFitter().fit(m[["os_time_months", "os_event", "treat"]],
                  "os_time_months", "os_event")

# 2. 12 個月存活率用 survival_function_at_times(12)，不要抓「最接近的那一列」
km.survival_function_at_times(12).iloc[0]

# 3. logrank_test 的參數順序：(時間A, 時間B, 事件A, 事件B) —— 放錯不報錯，給你錯的 p
logrank_test(a.os_time_months, s.os_time_months, a.os_event, s.os_event)

# 4. p 值存真實數值（8.6e-09），不要 f"{p:.3f}" 存成 0.000
# 5. median_survival_time_ 可能是 inf（未達到 / NR），要處理
```

**PFS 的答案是 0.632，不是真值 0.59。不要把數字改成理論值。**

### 任務

> 讀 `workspace/matched.csv`：
>
> 1. **先做一件事證明百分比會騙人**：分別算
>    (a) 天真的死亡比例 `os_event.mean()`
>    (b) Kaplan–Meier 估計的 12 個月存活率
>    把兩者放在一起，並說明為什麼 `1 − (a)` 不等於 (b)。
> 2. `KaplanMeierFitter` 分組配適 OS，取出：中位存活期、12 個月與 18 個月存活率。
> 3. `logrank_test` 比較兩條曲線。
> 4. `CoxPHFitter` 只放 `treat`，取 HR 與 95% CI。
> 5. PFS 重做一次 2–4。
> 6. 全部寫進 `workspace/km_summary.json`：
>
> ```json
> {"n": 1412, "n_pairs": 706,
>  "os": {"hr": 0.578, "ci_low": 0.48, "ci_high": 0.70, "logrank_p": 8.6e-9,
>         "deaths_treat_pct": 25.6, "deaths_control_pct": 38.0,
>         "surv12_treat_pct": 71.1, "surv12_control_pct": 55.7,
>         "median_treat": 21.3, "median_control": 13.5},
>  "pfs": {"hr": 0.632, "ci_low": 0.55, "ci_high": 0.72}}
> ```

### 📖 你應該看到

```
Deaths (raw)     : Atezo+Bev 25.6%   Sorafenib 38.0%
12-mo OS (KM)    : Atezo+Bev 71.1%   Sorafenib 55.7%
Median OS        : 21.3 mo  vs  13.5 mo
OS  HR : 0.578  (0.48-0.70)   log-rank p = 8.6e-09
PFS HR : 0.632  (0.55-0.72)
```

注意：Sorafenib 組「死了 38.0%」，但 12 個月存活率是 **55.7%**，不是 62%。
差在哪？**有人還沒死就退出觀察了**——他們的追蹤時間不夠長，
不能算進分母當作「活著」，也不能算成「死了」。這就是 KM 存在的理由。

**而 0.578 ≈ 0.58 = 真實 IMbrave150 隨機分派試驗的結果。**

### ⚠️ 地雷

1. 🔴 **不可以用 `1 - os_event.mean()` 當存活率。** 這是本章的核心教學點，
   但也是最容易在寫程式時順手犯的錯。有審查的資料，分母不是固定的。
2. **12 個月存活率要用 `survival_function_at_times(12)`。**
   不要用 `km.survival_function_.iloc[最接近 12 的那一列]`——
   KM 是階梯函數，「最接近的那一列」可能是 11.87 或 12.03 個月，
   兩者在陡峭的區段差好幾個百分點。`survival_function_at_times` 會正確取階梯值。
3. **`median_survival_time_` 可能是 `inf`。** 如果曲線沒有掉到 0.5 以下，
   中位數是「未達到（not reached, NR）」。這份資料 atezo 組 21.3、sora 組 13.5，
   都有達到，但你的程式要能處理 `inf` 而不是印出 `inf` 個月。
4. **log-rank 的 p 值是 8.6e-09，不要印成 `0.000` 或 `<0.05`。**
   期刊要求 p < 0.001 就寫 `<0.001`，但你的 JSON 要存真實數值。
   `f"{p:.3f}"` 會給你 `0.000`——那是排版，不是數字。
5. 🔴 **配對世代的 Cox 嚴格說要處理配對群集。**
   我們這裡跑的是**未考慮群集的標準 Cox**。1:1 配對後同一對的兩人並非獨立，
   理論上應該用 `strata=pair_id` 或 robust/cluster-robust 標準誤。
   實務上點估計幾乎不動，CI 會略微改變。
   **這件事必須寫進 Methods 和 Limitations**（第 06 章會檢查）。
   如果你想順手做：`CoxPHFitter().fit(..., cluster_col="pair_id", robust=True)`。
6. **PFS 的 HR 是 0.632，不是 0.58。** 真值是 0.59。
   配對後 PFS 偏離得比 OS 多——這是真的，不要「修」它，也不要在手稿裡寫成 0.59。
   誠實報告，並在 Discussion 說明 PFS 的判定（影像判讀時點）本來就比死亡更嘈雜。
7. **`logrank_test` 的參數順序**是 `(durations_A, durations_B, event_observed_A, event_observed_B)`。
   放錯位置不會報錯，會給你一個錯的 p。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch03.py --mission 3.1
```

---

## 🎤 停 — `⏸ Mission 3.1 完成，等候指示。`

---

## Mission 3.2 — 畫成可以放進論文的曲線

**目標**：兩張出版等級的 KM 圖，含 number-at-risk 表。

### ⛔ 硬性約束（寫第一行程式碼之前讀）

```python
# 1. Agg 後端必須在 import pyplot 之前
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# 2. 不要用 lifelines.plotting.add_at_risk_counts() —— 本機版本會崩潰。
#    at risk 的定義就是「追蹤時間 >= t 的人數」，手工版三行搞定：
TICKS = [0, 6, 12, 18, 24]
n_at = [int((d[tcol] >= t).sum()) for t in TICKS]

# 3. 圖例用臨床藥名，不要 treat=0/1
# 4. y 軸 0–1，不要裁切
```

完整的手工 at-risk 表程式碼在下方地雷 3。**照那段寫，這一關就不會出事。**

### 任務

> 畫兩張圖：
> - `workspace/figures/km_os.svg`
> - `workspace/figures/km_pfs.svg`
>
> 每張圖必須有：
> 1. 兩條 KM 曲線（依 arm），加上 95% 信賴帶
> 2. **number-at-risk 表**，貼在 x 軸下方，時間點 0/6/12/18/24 個月
> 3. 審查記號（`+`）
> 4. 圖內標註 HR、95% CI、log-rank p
> 5. y 軸 **0 到 1**（或 0–100%），x 軸標「Months from treatment start」
> 6. colorblind-safe 配色

### ⚠️ 地雷

1. 🔴 **y 軸一定要從 0 開始。** 把 y 軸裁成 0.4–1.0 會讓兩條線的差距在視覺上放大兩倍。
   這在同儕審查會被抓，在演講被抓更難看。
2. **沒有 number-at-risk 表的 KM 圖等於沒畫。** 曲線尾端往往只剩十幾個人，
   讀者必須看得到那裡的估計有多不穩。這是期刊硬性要求。
3. 🛡 **預防**｜**`lifelines.plotting.add_at_risk_counts()` 在本 repo 的環境會直接崩潰。**
   （已列入 ⛔ 區塊；`verify/preflight.py` 上台前會實測一次。）
   實測環境是 `lifelines 0.30.0` + `numpy 2.5.1` + `pandas 3.0.3`，呼叫它會拋：

   ```
   TypeError: only 0-dimensional arrays can be converted to Python scalars
     lifelines/plotting.py:557  counts.extend([int(c) for c in event_table_slice.loc[rows_to_show]])
   ```

   原因是 lifelines 內部用 `lambda x: x.tail(1).values` 產生一個長度 1 的陣列，
   而 NumPy 2.x 起 `int(np.array([5]))` 不再允許。**這不是你的錯，是套件版本相沖。**

   **現場請直接用手工版本**（已驗證可跑）——at risk 的定義就是「追蹤時間 ≥ t 的人數」：

   ```python
   TICKS = [0, 6, 12, 18, 24]
   fig, (ax, axt) = plt.subplots(2, 1, figsize=(7, 6.6),
                                 gridspec_kw={"height_ratios": [4, 1]})
   # …在 ax 上畫兩條 KM 曲線…
   axt.axis("off")
   axt.text(0, 1.0, "Number at risk", transform=axt.transAxes, fontweight="bold")
   for r, (label, d, colour) in enumerate(groups):
       n_at = [int((d[tcol] >= t).sum()) for t in TICKS]
       axt.text(0, 0.62 - 0.30 * r, label, transform=axt.transAxes, color=colour)
       for t, n in zip(TICKS, n_at):
           axt.text(t / 24, 0.62 - 0.30 * r, str(n),
                    transform=axt.transAxes, ha="center")
   ```

   別花現場時間去 debug 或降版套件。**看到那個 TypeError 就換手工版，30 秒解決。**
4. **兩條曲線的 label 要是可讀的臨床名稱**（`Atezolizumab + bevacizumab` /
   `Sorafenib`），不要留 `treat=1` / `treat=0`。演講當下沒人看得懂 0 和 1。
5. **存 SVG 不是 PNG。** 投影和期刊都要向量圖。若一定要 PNG，`dpi>=300`。
   存檔加 `bbox_inches="tight"`。
6. **matplotlib 在無視窗環境要 `matplotlib.use("Agg")`**，而且要在
   `import matplotlib.pyplot` **之前**設定，否則在某些機器上會卡住等視窗。
7. **不要在圖上寫「Atezo+Bev 顯著較佳」這種結論句。** 圖呈現資料，結論留給正文。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch03.py --mission 3.2
```

---

## 🎤 停 — 講者接話

`⏸ Mission 3.2 完成，等候指示。`

> 講者（詳見 [RUNBOOK.md](RUNBOOK.md#m32)）：這是全場的情緒高點。
> 讓 OS 曲線在螢幕上停久一點。
> 「觀察性資料，做得夠小心，得到 0.58。隨機分派試驗，花了幾億美金，得到 0.58。」
> 然後**立刻降溫**：「一致不等於證明。所以接下來我要試著把它弄壞。」

下一關：[04-subgroup.md](04-subgroup.md)
