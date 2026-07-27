# 第 00 章 — 建沙盒，然後先看一眼

> 對應投影片：開場（尚未進入 Act I）｜預估 3 分鐘｜Mission 0.1

這一章不寫任何分析。目的只有兩個：把乾淨的沙盒建起來，
以及讓觀眾看到**真實世界的資料拿到手時長什麼樣子**。

---

## Mission 0.1 — 把資料搬進沙盒，然後打開來看

**目標**：建立 `workspace/`，複製十家醫院的原始檔進去，然後**只用眼睛看**，不做任何處理。

### 任務

> 在 `live-demo/workspace/` 底下建立工作區：
>
> 1. 把 repo 根目錄的 `hospitals/` 整個資料夾複製進 `workspace/hospitals/`，
>    並把 `hospitals_meta.csv` 複製到 `workspace/`。**用複製，不要用連結**——
>    我們要示範「原始資料唯讀，分析只碰副本」這個習慣。
> 2. 建立 `workspace/figures/` 空資料夾。
> 3. 列出 `workspace/hospitals/` 裡的每個檔案：檔名、列數、欄數。
> 4. 印出 **H01、H02、H03** 三個檔案的**欄位名稱**和**第一列資料**。
>    這三家刻意選過，代表三種不同的 EHR 系統。
> 5. 印出 `hospitals_meta.csv` 全部十列。
> 6. 然後用中文告訴我：**這三個檔案，光看欄位名稱，你注意到什麼不對勁的地方？**
>    至少講出三點。不要開始寫轉換程式——這一關只負責「看見問題」。

### 產出

| 路徑 | 內容 |
|------|------|
| `workspace/hospitals/*.csv` | 十家醫院原始檔（原封不動的副本） |
| `workspace/hospitals_meta.csv` | 醫院目錄 |
| `workspace/figures/` | 空資料夾，之後放圖 |

### 必須做到

- [ ] `workspace/hospitals/` 底下正好 10 個 CSV
- [ ] 複製而非移動——repo 根目錄的 `hospitals/` 必須完好無損
- [ ] 有講出「欄數不一樣」這件事（H03 只有 25 欄，H01/H02 有 26 欄）
- [ ] 有講出「同一件事三個名字」（例如 `arm` / `treatment` / `regimen`）

### ⚠️ 地雷

- **不要在這一關就開始寫 harmoniser。** 觀眾需要先感受到「這團東西有多亂」，
  問題才有張力。你一秒解決掉，Act I 就沒戲了。
- **不要用 `cat` 把整個 CSV 印出來。** 1,800 列會洗掉整個終端機，投影幕上什麼都看不到。
  `head -2` 或 pandas 的 `.head(1)` 就夠。
- 複製時注意 macOS 的 `.DS_Store`：只複製 `*.csv`。

### 驗收

```bash
cd live-demo && ../.venv/bin/python verify/ch00.py
```

預期：

```
  ✓ workspace/hospitals/ 有 10 個 CSV
  ✓ workspace/hospitals_meta.csv 存在
  ✓ 原始 hospitals/ 未被更動
  ✓ workspace/figures/ 已建立
  ─────────────────────────────
  PASS  Chapter 00
```

### 🆘 卡住時

不會卡。真的卡住就用 `cp -R ../hospitals live-demo/workspace/hospitals`。

---

## 🎤 停 — 講者接話

`⏸ Mission 0.1 完成，等候指示。`

> 講者要講的三件事（詳見 [RUNBOOK.md](RUNBOOK.md#m01)）：
> 這十個檔案是三家不同 EHR 廠商匯出的；真實世界要嘛你自己去要，要嘛等資料處理中心，
> 通常兩三個月；而且沒有人會幫你統一欄位。**今天我們就從這個狀態開始。**

下一關：[01-aggregate.md](01-aggregate.md)
