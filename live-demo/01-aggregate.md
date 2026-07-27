# 第 01 章 — 十家醫院，三種方言，一份資料

> 對應投影片：**Act I · Data aggregation**｜預估 12 分鐘｜Mission 1.1 – 1.3

真實世界研究裡，**這一章佔掉你 70% 的時間**，而且論文的 Methods 只會寫一句
「Data from 10 centres were harmonised」。這一章要把那句話背後的東西攤開來。

終點：`workspace/pooled.csv`，**1,800 位病人**，欄位統一，單位統一，編碼統一。

---

## Mission 1.1 — 診斷三種方言

**目標**：不寫轉換程式，先做出一份「差異清單」。沒有清單就開始轉，一定會漏。

### 任務

> 讀 `workspace/hospitals/` 全部十個檔案，做一份方言診斷報告，寫到
> `workspace/dialects.md`：
>
> 1. **分群**：這十個檔案分成幾種 schema？各是哪幾家？
>    用**欄位名稱的指紋**判斷，不要用檔名猜。
>    （提示：`hospitals_meta.csv` 有一欄 `ehr_vendor` 可以驗證你分對了。）
> 2. **對照表**：做一張表，左欄是「我們要的正規欄位名」，右邊三欄是三種方言各自叫什麼。
>    把**所有**不一致的欄位都列進去，不要只列你覺得重要的。
> 3. **值的編碼**：每一種方言的 `arm` / `sex` / 各種 Yes-No 旗標分別長什麼樣？
>    列出實際出現過的值（用 `unique()`，不要憑想像）。
> 4. **單位**：檢查 albumin 和 bilirubin 三種方言的**數值範圍**。
>    如果同一個生化值在不同醫院差了一個數量級，那不是病人不一樣，是單位不一樣。
> 5. **缺失**：每個檔案、每一欄的缺失比例。特別回答：**有沒有哪一欄在某些醫院是整欄不存在的？**
> 6. 最後用中文講**三個你認為最危險的差異**，並說明「如果沒發現會怎樣」。

> ⚡ **可以派 subagent 平行**：第 1–5 步對三個方言家族是同一套動作，
> 開三個 subagent 各查一群（Alpha / Beta / Gamma），各自回報欄位名、值編碼、
> 數值範圍與缺失率，你再合併成 `dialects.md` 並自己寫第 6 步的判斷。
> **禁止它們讀 `live-demo/` 底下任何檔案**（下面就是標準答案），
> 只准讀 `workspace/hospitals/`。合併完照樣要跑驗收再停。

### 產出

| 路徑 | 內容 |
|------|------|
| `workspace/dialects.md` | 方言診斷報告（給人看的 markdown） |

### 必須做到

- [ ] 正確分出 **Alpha / Beta / Gamma** 三群（4 / 3 / 3 家）
- [ ] 指出 Gamma 少一欄，且少的是**連續 AFP**
- [ ] 指出 Beta 的 albumin / bilirubin 是**不同單位**
- [ ] 指出 `hospital_type` / `hospital_region` **不在病人檔裡**

### 📖 標準答案（做完再對，不要先看）

| | **Alpha** | **Beta** | **Gamma** |
|---|---|---|---|
| 醫院 | H01 H04 H07 H10 | H02 H05 H08 | H03 H06 H09 |
| 欄數 | 26 | 26 | **25** |
| 指紋欄 | 都不符合另外兩組 | `treatment`,`albumin_g_L`,`os_death` | `regimen`,`male`,`afp_high` |
| 組別 | `arm`=`Atezo+Bev`/`Sorafenib` | `treatment`=`AtezoBev`/`Sorafenib` | `regimen`=`A+B`/`SOR` |
| 性別 | `sex`=`Male`/`Female` | `sex`=`M`/`F` | `male`=`1`/`0` |
| 白蛋白 | `albumin_g_dl`（g/dL） | `albumin_g_L`（**g/L**） | `alb`（g/dL） |
| 膽紅素 | `bilirubin_mg_dl` | `bilirubin_umol_L`（**µmol/L**） | `tbili`（mg/dL） |
| Child-Pugh | `child_pugh_score`=`5`/`6` | `cp_score`=`5`/`6` | `child_pugh`=`A5`/`A6` |
| 旗標 | `0`/`1` | `Yes`/`No` | `0`/`1` |
| AFP | `afp_ng_ml` + `afp_ge_400` | `afp` + `afp_over_400` | **只有** `afp_high` |
| 收案時間 | `enroll_date`=`2019-05` | `enroll_date`=`2019-05` | `enroll_yr`=`2019` |
| 病因 | `HBV`/`HCV`/`Nonviral` | 同左 | **小寫** `hbv`/`hcv`/`nonviral` |
| 反應 | `best_overall_response` | `recist` | `recist` |
| 存活 | `os_time_months`,`os_event` | `os_months`,`os_death` | `time_os`,`event_os` |
| 病人 ID | `patient_id` | `patient_id` | `record_id` |
| 醫院 ID | `hospital_id` | `site_code` | `site` |

### ⚠️ 地雷

- **不要用檔名或醫院代號硬編死方言。** 真實世界醫院會換系統。用欄位指紋。
- **`unique()` 要跑在原始字串上。** 先 `read_csv(dtype=str)` 看原貌，
  否則 pandas 會幫你把 `1`/`0` 讀成 int、把 `NA` 讀成 NaN，你就看不到編碼差異了。
- **不要相信「缺失 = 空白」。** 這份資料三家廠商的缺失表示法不同（空字串 / `NA`），
  pandas 預設兩個都會轉 NaN，但你**必須知道**它幫你轉了什麼——換一批資料就不一定了。
  建議明寫 `na_values=["NA", "unknown", ""]`。
- **這一關不要寫轉換函式。** 只做診斷。

### 🆘 卡住時

`hospitals_meta.csv` 的 `ehr_vendor` 欄直接給你答案，可以拿來檢查分群對不對
（但要先自己用指紋分一次）。

---

## 🎤 停 — `⏸ Mission 1.1 完成，等候指示。`

---

## Mission 1.2 — 寫 harmoniser，併成一張表

**目標**：把十個檔案轉成一個統一 schema 的 `pooled.csv`，1,800 列。

### ⛔ 硬性約束（寫第一行程式碼之前讀）

```python
# 1. 兩個單位換算，忘了不會報錯，只會讓 albumin 變成 40 g/dL
df["albumin_g_dl"]    = df["albumin_g_L"] / 10.0
df["bilirubin_mg_dl"] = df["bilirubin_umol_L"] / 17.1

# 2. Child-Pugh 是 "A5" 字串，int("A5") 會爆
df["child_pugh_score"] = df["child_pugh"].str[1:].astype(int)

# 3. Gamma 站的連續 AFP 明確設為 NaN —— 不准用門檻反推
df["afp_ng_ml"] = np.nan

# 4. Yes/No → 0/1 用 nullable dtype，否則 concat 後整欄變 object
s.map({"Yes": 1, "No": 0}).astype("Float64")

# 5. Gamma 沒有 enroll_date，只有 enroll_yr（Alpha/Beta 是 "2019-05"，取前四碼）
# 6. 最後強制欄位順序：df = df[CANON_COLS]
# 7. 全程不准 dropna()，收尾 assert len(pooled) == 1800
```

**做完立刻看兩個中位數**：`albumin ≈ 3.9`、`bilirubin ≈ 0.81`。
差一個數量級就是第 1 條沒做。

### 任務

> 寫 `workspace/harmonize.py`：
>
> 1. 一個 `detect_vendor(columns)` 函式，用欄位指紋回傳 `"Alpha"` / `"Beta"` / `"Gamma"`。
> 2. 一個 `harmonise_file(path)` 函式，讀一個檔、依方言轉換、回傳統一 schema 的 DataFrame。
> 3. 一個 `load_pooled()` 把十個檔接起來，加一欄 `ehr_vendor` 記錄來源方言。
> 4. 寫出 `workspace/pooled.csv`。
> 5. 印出：總列數、各方言列數、每一欄的缺失比例。
>
> **正規 schema（欄名與值域必須完全照這個表，驗收會檢查）：**
>
> | 欄位 | 型別 / 值域 |
> |------|------|
> | `patient_id` | 字串，全域唯一 |
> | `hospital_id` | `H01`…`H10` |
> | `enroll_year` | int，2018 或 2019 |
> | `arm` | `Atezo+Bev` / `Sorafenib` |
> | `age` | int |
> | `sex` | `Male` / `Female` |
> | `etiology` | `HBV` / `HCV` / `Nonviral` |
> | `ecog_ps` | 0 / 1 |
> | `child_pugh_score` | 5 / 6（**數字**，不是 `A5`） |
> | `albi_grade` | 1 / 2 / 3 |
> | `albumin_g_dl` | float，**g/dL**（中位數應落在 3.9 附近） |
> | `bilirubin_mg_dl` | float，**mg/dL**（中位數應落在 0.8 附近） |
> | `bclc_stage` | `A` / `B` / `C` |
> | `afp_ng_ml` | float，**Gamma 三家一律 NaN** |
> | `afp_ge_400` | 0 / 1 |
> | `macrovascular_invasion` | 0 / 1 |
> | `extrahepatic_spread` | 0 / 1 |
> | `varices_at_baseline` | 0 / 1 |
> | `os_time_months` | float |
> | `os_event` | 0 / 1 |
> | `pfs_time_months` | float |
> | `pfs_event` | 0 / 1 |
> | `best_overall_response` | `CR`/`PR`/`SD`/`PD`/`NE` |
> | `objective_response` | 0 / 1 |
> | `grade34_adverse_event` | 0 / 1 |
> | `grade34_hypertension` | 0 / 1 |
> | `ehr_vendor` | `Alpha` / `Beta` / `Gamma` |

### 產出

| 路徑 | 內容 |
|------|------|
| `workspace/harmonize.py` | 可重跑的轉換腳本 |
| `workspace/pooled.csv` | 1,800 × 27 |

### 必須做到

- [ ] 1,800 列，`patient_id` 全域唯一（不需要加前綴，原始 ID 已經不重複）
- [ ] 三個換算：Beta albumin ÷ 10、Beta bilirubin ÷ 17.1、Gamma `A5` → `5`
- [ ] Gamma 的 `afp_ng_ml` 明確設成 `NaN`
- [ ] `etiology` 大小寫統一
- [ ] 十家醫院都在，沒有任何一家的列被靜靜吃掉

### ⚠️ 地雷（這一關是本章最容易翻車的地方）

1. **單位換算：bilirubin 是 ÷ 17.1，不是 ÷ 17 或 × 0.0585 隨便挑。**
   忘記換算不會拋任何例外——albumin 會變成 40 g/dL（生理上不可能），
   然後一路帶到 Act II 的傾向分數模型，把整個分析搞歪。
   **做完一定要看中位數：albumin ≈ 3.9、bilirubin ≈ 0.81。**
2. **不要用 `afp_ge_400` 去反推 Gamma 的連續 AFP。** 例如填 400、填組平均、
   或者乾脆抄 `afp_high * 400`——這是編造資料。Gamma 就是沒有這個測量，
   誠實地留 `NaN`。第 02 章你會看到為什麼這件事非常重要。
3. **Yes/No → 0/1 時的 dtype 陷阱。** `.map({"Yes":1,"No":0})` 遇到 NaN 會回傳
   `object` dtype，`pd.concat` 之後整欄變成 object，後面 `.astype(float)` 就爆。
   用 `.astype("Float64")`（nullable）或最後統一 `pd.to_numeric(errors="coerce")`。
4. **`child_pugh` 是 `"A5"` 字串。** `int("A5")` 會爆。用 `.str[1:].astype(int)`。
   不要用 `.str.replace("A","")` 然後忘了轉型。
5. **Gamma 沒有 `enroll_date`，只有 `enroll_yr`。** Alpha/Beta 是 `"2019-05"` 這種
   `YYYY-MM` 字串，要取前四碼；Gamma 已經是年份。兩邊都要走到 `enroll_year`(int)。
   直接 `pd.to_datetime` 會在 Gamma 上得到 1970-01-01 附近的怪東西。
6. **`pd.concat` 欄位順序。** 三個方言處理完的欄位順序不一樣，
   concat 會用聯集並產生你沒預期的欄。最後強制 `df[CANON_COLS]` 挑一次。
7. **不要 `dropna()`。** 這一關任何形式的 drop 都是錯的。
   `albumin` 缺 4.3%、`bilirubin` 缺 5.1%、`afp_ng_ml` 缺 35.3%——
   `dropna()` 會讓你從 1,800 掉到 1,000 出頭，而且掉的是整整三家醫院。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch01.py --mission 1.2
```

### 🆘 卡住時

參考解在 repo 根目錄 `harmonize_hospitals.py`（**自己先寫過一次再看**）。

---

## 🎤 停 — `⏸ Mission 1.2 完成，等候指示。`

---

## Mission 1.3 — 接上醫院屬性，看見第一個干擾因子

**目標**：把 `hospitals_meta.csv` join 進來，然後做一件事——
**按醫院拆開看用藥比例**。這是全場第一個「啊」的時刻。

### 任務

> 1. 把 `hospitals_meta.csv` 以 `hospital_id` **left join** 到 `pooled.csv`，
>    取得 `hospital_type`、`hospital_region`、`ehr_vendor`（驗證與你偵測的一致）。
>    覆寫 `workspace/pooled.csv`。
> 2. 做一張 `workspace/site_profile.csv`，每家醫院一列：
>    `hospital_id, hospital_name, hospital_type, hospital_region, ehr_vendor,
>     n, pct_atezo, median_age, pct_ecog1, pct_mvi, pct_afp_ge400, os_event_rate`
> 3. 依 `pct_atezo` 由高到低印出來。
> 4. 用中文回答：**如果醫院同時決定「病人拿到哪種藥」又決定「病人的預後」，
>    那麼直接比較兩組存活會發生什麼事？** 這個問題的答案就是下一章。

### 產出

| 路徑 | 內容 |
|------|------|
| `workspace/pooled.csv` | 加上 3 欄醫院屬性，仍是 1,800 列 |
| `workspace/site_profile.csv` | 10 列的醫院輪廓表 |

### 📖 你應該看到

```
H01 Northshore University   Academic  Asia   n=320  atezo 65.9%
H06 Harbor City Medical     Academic  RoW    n=210  atezo 64.8%
H03 Metropolitan Cancer Ctr Academic  Asia   n=240  atezo 61.2%
H08 Eastgate University     Academic  RoW    n=155  atezo 54.2%
H05 Lakeside Regional       Regional  Asia   n=180  atezo 47.2%
H09 Valley District         Community Asia   n=110  atezo 46.4%
H02 Riverside General       Community RoW    n=285  atezo 44.9%
H10 Summit General          Regional  RoW    n=130  atezo 44.6%
H04 St Aldys Community      Community RoW    n= 95  atezo 37.9%
H07 Pinecrest Community     Community Asia   n= 75  atezo 34.7%
```

學術中心 **65.9%** vs 社區醫院 **34.7%**——幾乎兩倍。這不是隨機分派，
這是**處方文化**。而學術中心收的病人本來就比較適合積極治療。

### ⚠️ 地雷

1. **join 之後一定要重數列數。** 必須還是 **1,800**。
   如果變多，是 `hospitals_meta.csv` 有重複 `hospital_id`（或你用了 `how="outer"`）；
   如果變少，你用了 `how="inner"` 而且某家 ID 對不上（例如大小寫或空白）。
   `assert len(df) == 1800` 寫進腳本裡。
2. **不要用 `hospital_name` 當 join key。** 名稱有空格、有縮寫（`Metropolitan Cancer Ctr`），
   遲早會對不上。用 `hospital_id`。
3. **`ehr_vendor` 會撞名。** 你在 Mission 1.2 已經自己算了一欄 `ehr_vendor`，
   meta 裡也有一欄。join 之後會變成 `ehr_vendor_x` / `ehr_vendor_y`。
   **這是好事**——拿來互相驗證，確認兩者 100% 一致，然後只留一欄。
4. **`pct_atezo` 的分母。** 是該院全部病人，不是有 outcome 的病人。
5. 別急著下結論說「學術中心比較好」。你現在還不知道那是藥的效果還是病人的差別。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch01.py --mission 1.3
```

---

## 🎤 停 — 講者接話

`⏸ Mission 1.3 完成，等候指示。`

> 講者（詳見 [RUNBOOK.md](RUNBOOK.md#m13)）：指著 65.9% 和 34.7% 那兩行。
> 「同一種病，同一個年份，兩家醫院的用藥比例差兩倍。你覺得這兩群病人一樣嗎？」

下一關：[02-deconfound.md](02-deconfound.md)
