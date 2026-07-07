# Meta-layer: 10-Hospital Cohort → PSM → Survival

A second, **upstream** teaching layer. Instead of the randomised trial, students
start from messy **real-world observational data** pooled from 10 hospitals,
apply **propensity-score matching (PSM)**, and recover the same treatment effect
the randomised IMbrave150 trial reported (OS HR ≈ 0.58).

```
 hospitals/H01…H10.csv   (10 SEPARATE files, 3 different EHR "dialects")
        │   read + HARMONISE + pool   (schema/units/codes differ per site!)
        ▼
 pooled observational cohort   (1,800 patients, CONFOUNDED BY INDICATION)
        │   propensity-score matching (remove confounding)
        ▼
 matched cohort (~700 pairs, covariates balanced)
        │   Kaplan-Meier / Cox
        ▼
 OS HR ≈ 0.58   ==  the randomised-trial result
```

## Step 0 — the data does NOT arrive tidy (this is the point)

Each hospital hands you its **own CSV with its own schema**. Three "EHR
vendors" are represented, so before any analysis the data must be *harmonised*:

| Vendor | Hospitals | What's different |
|--------|-----------|------------------|
| **Alpha** | H01, H04, H07, H10 | Canonical/tidy layout, blank = missing |
| **Beta** | H02, H05, H08 | `treatment`=`AtezoBev`; sex `M`/`F`; **albumin g/L, bilirubin µmol/L**; Yes/No flags; `os_death`/`pfs_prog`; missing = `NA` |
| **Gamma** | H03, H06, H09 | `regimen`=`A+B`/`SOR`; `male` 1/0; Child-Pugh as `A5`/`A6`; **only `afp_high` (no continuous AFP)**; `time_os`/`event_os` |

So a student/agent must, per site: rename columns, recode `arm`/`sex`/Yes-No,
convert units (÷10, ÷17.1), parse `A5`→5, and accept that Gamma sites have no
continuous AFP (only the ≥400 threshold — which is all PSM needs). Site type and
region are **not** in the patient files — they live in `hospitals_meta.csv` and
must be **joined** on `hospital_id`. `harmonize_hospitals.py` is a reference
solution; it validates itself against the answer key (`_answer_key_pooled.csv`).

## The core teaching point

| Analysis on the pooled cohort | OS HR | Interpretation |
|-------------------------------|-------|----------------|
| **Naive** (unadjusted `coxph(Surv ~ arm)`) | **≈ 0.51** | **Biased** — the atezo+bev group is *healthier* to begin with, so the raw comparison over-states benefit |
| **PSM** (1:1 caliper matching, then Cox) | **≈ 0.58** | Confounding removed → recovers the truth / trial |
| Multivariable Cox (regression adjustment) | ≈ 0.58 | Confirms PSM ≈ regression when confounders are measured |

> Built-in truth: the outcome model uses treatment **HR = 0.58 (OS), 0.59 (PFS)**.
> The bias in the naive estimate is entirely due to confounding, not to the drug.

## Why the raw data is confounded (by design — and realistically)

Treatment is **not** randomised. `logit P(atezo+bev)` depends on:

- **Hospital prescribing culture** — academic centres favour the combination
  (H01/H03/H06 ≈ 65% atezo) vs conservative community sites (H04/H07 ≈ 35%).
- **Patient fitness** — better ECOG, Child-Pugh A5, low AFP, no macrovascular
  invasion → more likely to get atezo+bev.
- **Varices at baseline** → *less* likely to get bevacizumab (real bleeding
  contraindication).
- Slightly older patients → less likely to get the combination.

All of these also affect survival, so they are **true confounders**. Crucially
they are **all measured and present in the CSV** → there is *no unmeasured
confounding*, which is the assumption ("no unmeasured confounders" / ignorability)
that lets PSM recover the causal effect. That makes it a clean teaching example;
a follow-up exercise can hide one confounder to show PSM break.

## Real-world messiness baked in

- **10 files, 3 schemas** (see table above) — harmonisation required.
- **Confounded treatment** — `arm` depends on prognosis + hospital, not random.
- **~5–6% missing** lab values (`afp_ng_ml`, `albumin_g_dl`, `bilirubin_mg_dl`);
  Gamma sites have **no continuous AFP at all** (threshold only).
- **Site attributes live elsewhere** — `hospital_type` / `hospital_region` are in
  `hospitals_meta.csv`, joined on `hospital_id` (also carries `ehr_vendor`, size).
- After harmonisation the pooled clinical + outcome columns match
  `DATA_DICTIONARY.md`.

## Files

| File | Purpose |
|------|---------|
| `hospitals/H01…H10_*.csv` | **10 per-hospital files** in 3 EHR dialects (the raw input) |
| `hospitals_meta.csv` | Catalog: id, name, type, region, vendor, size |
| `generate_multihospital.py` | Builds the 10 files (+ answer key) |
| `harmonize_hospitals.py` | Reference: read 10 → harmonise → pooled (self-validating) |
| `_answer_key_pooled.csv` | Correct pooled result (validation only — not for students) |
| `psm_imbrave150.py` | Pool → PSM → balance → survival (Python, `lifelines`) |
| `psm_imbrave150.R` | Same with `MatchIt` + `survival` (R) |

## Run it

```bash
.venv/bin/python generate_multihospital.py    # writes hospitals/*.csv + meta + key
.venv/bin/python harmonize_hospitals.py       # pool the 10 files (round-trip check)
.venv/bin/python psm_imbrave150.py            # naive → PSM → matched HR

Rscript psm_imbrave150.R                       # R version with MatchIt
```

Verified end-to-end: harmonisation round-trips exactly, naive OS HR ≈ **0.51**
(biased), PSM-matched OS HR ≈ **0.58**, all covariate |SMD| < 0.05 after matching.

## Suggested exercises

0. **Harmonise & pool** the 10 files — reconcile the 3 dialects (units, codes,
   column names), handle the sites with no continuous AFP, join `hospitals_meta`.
1. Pool the 10 hospitals; tabulate atezo share **by hospital** — see the
   prescribing variation (a *hospital-level* confounder → discuss clustering).
2. Fit the naive Cox model; note the HR is more extreme than the trial.
3. Estimate a propensity score; plot its distribution by arm (common-support /
   overlap check).
4. Match 1:1 with a caliper; produce a **Love plot** of SMDs before/after
   (rule of thumb |SMD| < 0.1 = balanced).
5. Re-run Cox on the matched cohort; compare with (a) the naive estimate and
   (b) multivariable regression adjustment.
6. Sensitivity: **drop `varices_at_baseline` (or `afp_ge_400`) from the
   propensity model** and watch the matched HR drift back toward the biased
   value — an intuition pump for *unmeasured confounding*.
7. Discuss why randomisation (the other dataset) made all of this unnecessary.
