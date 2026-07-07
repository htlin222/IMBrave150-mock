# IMbrave150 — Simulated Teaching Dataset

A **fully synthetic** patient-level dataset built to *recreate* the IMbrave150
phase-3 trial for teaching survival analysis. If a student is handed
`imbrave150_simulated.csv` and runs the standard methods (Kaplan-Meier,
log-rank, Cox proportional-hazards), they obtain numbers close to the
published trial.

> **Source study:** Finn RS, Qin S, Ikeda M, et al. *Atezolizumab plus
> Bevacizumab in Unresectable Hepatocellular Carcinoma.* N Engl J Med
> 2020;382:1894-1905. DOI [10.1056/NEJMoa1915745](https://doi.org/10.1056/NEJMoa1915745).
> Key figures below were taken from the article abstract *(according to PubMed)*.
>
> ⚠️ **Synthetic data.** No real patient is represented. Numbers are drawn from
> statistical models tuned to the published summaries — use for teaching only,
> never for clinical or research claims about the actual drugs.

## Two teaching layers

1. **Randomised trial** (`imbrave150_simulated.csv`) — covariates balanced by
   randomisation; a single-covariate Cox recovers HR ≈ 0.58. *(this file)*
2. **Real-world meta-layer** (`hospitals/H01…H10.csv`) — 10 **separate**
   hospital files in 3 different EHR schemas; students **harmonise + pool** them,
   then run **propensity-score matching** on the confounded cohort and recover
   the same HR ≈ 0.58. See **[`MULTIHOSPITAL_PSM.md`](MULTIHOSPITAL_PSM.md)**.

## Files

| File | Purpose |
|------|---------|
| `imbrave150_simulated.csv` | Randomised dataset (501 patients × 35 variables) |
| `DATA_DICTIONARY.md` | Every column, type, units, and encoding |
| `generate_imbrave150.py` | The simulator (reproducible, `SEED=48`) |
| `analyze_imbrave150.py` | Reproduction check in Python (`lifelines`) |
| `analyze_imbrave150.R` | Same analysis in R (`survival`) |
| `search_seed.py` | How the calibrated seed was selected |
| `MULTIHOSPITAL_PSM.md` | **Meta-layer**: 10 hospitals → harmonise → PSM → survival |
| `hospitals/H01…H10_*.csv` | 10 per-hospital files in 3 EHR dialects (raw input) |
| `hospitals_meta.csv` | Per-hospital catalog (type / region / vendor / size) |
| `generate_multihospital.py` | Builds the 10 hospital files + answer key |
| `harmonize_hospitals.py` | Reads 10 files → harmonises → pooled cohort |
| `psm_imbrave150.py` / `.R` | Pool → PSM + balance + survival (Python / R) |
| `robustness_multiverse.py` | 120 analytic specs → HR distribution figure |
| `tmle_demo.py` | TMLE / AIPW (doubly robust) vs the true DGP estimand |

## Quick start

```bash
make setup      # uv venv + install requirements.txt   (or: pip install -r requirements.txt)
make data       # generate both datasets + pool the 10 hospitals
make analyze    # reproduce trial result + PSM + TMLE
make figure     # render the robustness figure

# R equivalents
Rscript analyze_imbrave150.R
Rscript psm_imbrave150.R
```

Datasets are regenerated deterministically (fixed seeds), so `make data` on any
machine reproduces the committed CSVs byte-for-byte.

## Reproduction — simulated vs published

| Endpoint | Simulated | Published (Finn 2020) |
|----------|-----------|-----------------------|
| N (Atezo+Bev / Sorafenib) | 336 / 165 | 336 / 165 |
| **OS hazard ratio (death)** | **0.57** (95% CI 0.41–0.79) | **0.58** (0.42–0.79) |
| OS log-rank p | 7 × 10⁻⁴ | < 0.001 |
| 12-month OS (Atezo / Sora) | 70% / 58% | 67.2% / 54.6% |
| **PFS hazard ratio** | **0.61** (0.49–0.76) | **0.59** (0.47–0.76) |
| Median PFS (Atezo / Sora) | 6.9 / 4.4 mo | 6.8 / 4.3 mo |
| Objective response rate | 26% / 13% | 27.3% / 11.9% |
| Grade 3/4 AE | 60% / 55% | 56.5% / 55.1% |
| Grade 3/4 hypertension (Atezo) | 16% | 15.2% |

Baseline **Table 1** marginals (age, sex, region, ECOG, etiology HBV/HCV/nonviral,
BCLC stage, AFP≥400, MVI, EHS, Child-Pugh A5/A6) also reproduce the trial —
see `DATA_DICTIONARY.md`.

## Why it reproduces (the design, briefly)

- **2:1 randomisation, n=501** matches the trial's power structure.
- **Randomisation balances covariates** across arms, so the single-covariate
  Cox HR ≈ the covariate-adjusted HR — that is what lets `coxph(Surv ~ arm)`
  recover the headline result.
- Times-to-event are generated from a **proportional-hazards model** whose
  treatment coefficient *is* the published HR (0.58 for OS, 0.59 for PFS),
  with realistic prognostic effects layered on (AFP, MVI, EHS, ECOG, BCLC,
  ALBI) so multivariable Cox is also a genuine exercise.
- **Censoring** comes from staggered accrual + one administrative cutoff (the
  "primary analysis") — the realistic reason KM, not raw proportions, is
  required. Event counts are calibrated to the published ~29% vs ~39% deaths.

## Suggested teaching exercises

1. Plot Kaplan-Meier OS curves by arm; add the number-at-risk table.
2. Run the log-rank test and a univariable Cox model; interpret the HR and CI.
3. Estimate 6- and 12-month OS from the KM curve (not from raw death %).
4. Fit a multivariable Cox model; discuss why the arm effect barely moves
   after adjustment (→ randomisation).
5. Check the proportional-hazards assumption (Schoenfeld residuals,
   `cox.zph` in R).
6. Build the ORR 2×2 table and test with a chi-square / Fisher test.
7. Discuss coprimary endpoints and why medians can be "not reached".
