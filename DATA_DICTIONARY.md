# Data Dictionary — `imbrave150_simulated.csv`

**501 rows (one per patient) × 35 columns.** Fully synthetic teaching data
modelled on IMbrave150 (Finn RS et al., *N Engl J Med* 2020;382:1894-1905,
DOI [10.1056/NEJMoa1915745](https://doi.org/10.1056/NEJMoa1915745)).
No real patient is represented.

The four **randomisation stratification factors** are marked ★.

| # | Column | Type | Values / units | Notes |
|---|--------|------|----------------|-------|
| 1 | `patient_id` | ID | `IMB-0001`… | Unique key |
| 2 | `arm` | factor | `Atezo+Bev`, `Sorafenib` | Treatment (2:1). Reference = Sorafenib |
| 3 | `age` | int | years (18–88) | Median ~64 vs ~66 |
| 4 | `sex` | factor | `Male`, `Female` | ~82% male |
| 5 | `race` | factor | `Asian`, `White`, `Other/Unknown` | ~40% Asian |
| 6 | `region` ★ | factor | `Asia excluding Japan`, `Rest of World` | Stratum |
| 7 | `ecog_ps` ★ | int | `0`, `1` | ECOG performance status; ~62–65% =0 |
| 8 | `etiology` | factor | `HBV`, `HCV`, `Nonviral` | ~48 / 22 / 30% |
| 9 | `child_pugh_class` | factor | `A` | All class A by eligibility |
| 10 | `child_pugh_score` | int | `5`, `6` | ~72% = A5 |
| 11 | `albi_grade` | int | `1`, `2`, `3` | Derived from albumin + bilirubin |
| 12 | `albumin_g_dl` | float | g/dL | Liver synthetic function |
| 13 | `bilirubin_mg_dl` | float | mg/dL | |
| 14 | `bclc_stage` | factor | `A`, `B`, `C` | ~82% stage C |
| 15 | `afp_ng_ml` | float | ng/mL | Alpha-fetoprotein (continuous) |
| 16 | `afp_ge_400` ★ | int | `0`, `1` | AFP ≥ 400 ng/mL; ~37% =1. Stratum |
| 17 | `macrovascular_invasion` | int | `0`, `1` | MVI present; ~38% |
| 18 | `extrahepatic_spread` | int | `0`, `1` | EHS present; ~63% |
| 19 | `mvi_or_ehs` ★ | int | `0`, `1` | MVI and/or EHS; ~76%. Stratum |
| 20 | `num_target_lesions` | int | count | RECIST target lesions |
| 21 | `varices_at_baseline` | factor | `Yes`, `No` | ~25% |
| 22 | `prior_local_therapy` | factor | `Yes`, `No` | TACE/RFA/resection |
| 23 | `prior_surgery` | factor | `Yes`, `No` | |
| 24 | `os_time_months` | float | months | **Overall survival time** (time to death or censoring) |
| 25 | `os_event` | int | `1`=death, `0`=censored | OS event indicator |
| 26 | `pfs_time_months` | float | months | **Progression-free survival time** |
| 27 | `pfs_event` | int | `1`=progression/death, `0`=censored | PFS event indicator |
| 28 | `best_overall_response` | factor | `CR`,`PR`,`SD`,`PD`,`NE` | RECIST 1.1 best response |
| 29 | `objective_response` | int | `1`=CR/PR, `0`=other | ORR numerator |
| 30 | `duration_of_response_months` | float | months / `NA` | Defined only for responders |
| 31 | `any_adverse_event` | factor | `Yes`, `No` | |
| 32 | `grade34_adverse_event` | int | `0`, `1` | Grade 3/4 AE |
| 33 | `grade34_hypertension` | int | `0`, `1` | Grade 3/4 hypertension |
| 34 | `treatment_discontinuation_ae` | int | `0`, `1` | AE leading to discontinuation |
| 35 | `followup_months` | float | months | Observed follow-up time |

## Time-to-event conventions (important)

- Times are in **months**. `event = 1` means the event was observed;
  `event = 0` means **right-censored** (patient alive / progression-free at
  last contact). This is the standard `(time, event)` pair consumed by
  `survfit`/`coxph` (R) or `lifelines` (Python).
- `pfs_time_months ≤ os_time_months` always (progression cannot follow death).
- Censoring arises from staggered accrual + a single administrative data
  cutoff (the "primary analysis"), plus mild random loss to follow-up —
  exactly the mechanism that makes Kaplan-Meier (not raw proportions) the
  correct estimator here.

## How the numbers were made to line up ("rules of thumb" baked in)

- **2:1 allocation, n=501** → same power structure as the trial.
- **Randomisation balances covariates** across arms, so the *unadjusted*
  treatment HR ≈ the *adjusted* one — the property that lets a single-covariate
  Cox model recover the headline result.
- Survival simulated from a **proportional-hazards** model with
  `HR_OS = 0.58`, `HR_PFS = 0.59` as the generative truth, plus realistic
  prognostic effects (AFP≥400, MVI, EHS, ECOG, BCLC-C, ALBI) so multivariable
  Cox is also a meaningful exercise.
- Event counts calibrated to the published ~29% vs ~39% deaths so the
  log-rank test reaches p < 0.001.
