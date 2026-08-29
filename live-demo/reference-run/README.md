# reference-run — what one complete run produced

`live-demo/workspace/` is git-ignored on purpose: it is the sandbox the demo
writes into, and it has to start empty on every clone. That leaves anyone
running this for the first time with nothing to compare against. This folder
is that comparison — a snapshot of one finished pass through Chapters 00–07,
taken with:

```bash
python3 scripts/make_reference_run.py
```

> ⛔ **If you are the agent executing `live-demo/` live, do not read this
> folder.** It is the answer sheet. The acceptance scripts in `verify/` are
> what you run; this is for the human afterwards.

## What is here

| | |
|---|---|
| `MANIFEST.tsv` | Every file the run produced: path, bytes, `rows×cols` for CSVs, SHA-256. |
| `results/` | The eight small result tables, copied verbatim. |

`pooled.csv` and `matched.csv` are not copied — ~280 KB each, and fully
determined by the committed inputs, so their checksums in the manifest are the
part worth keeping. The manuscript from this same run is tracked separately at
[`slides/stage/manuscript.md`](../../slides/stage/manuscript.md), with the
reviewers' triage in [`slides/stage/review_log.csv`](../../slides/stage/review_log.csv).

The ten input CSVs under `hospitals/` in the manifest checksum identically to
the repository's [`hospitals/`](../../hospitals/) — that is the point of
listing them: it shows the run did not modify its inputs.

## The numbers this run got

| Step | Result | Where |
|---|---|---|
| Pooled cohort | 1,800 patients, 30 columns, from 10 files in 3 EHR dialects | `MANIFEST.tsv` |
| **Unadjusted OS HR** | **0.505** (95% CI 0.427–0.597) — flattering, and wrong | `results/naive_hr.json` |
| Worst baseline imbalance | \|SMD\| 0.228 before matching → 0.044 after | `results/balance.csv` |
| Matching | 706 pairs, 1,412 patients retained of 1,800 | `results/km_summary.json` |
| **Matched OS HR** | **0.578** (0.479–0.698), log-rank p = 8.8 × 10⁻⁹ | `results/km_summary.json` |
| Matched PFS HR | 0.632 (0.554–0.721) | `results/km_summary.json` |
| 12-month OS | 71.1 % vs 55.7 %; medians 21.3 vs 13.5 months | `results/km_summary.json` |
| Subgroups | 14 strata across 6 variables, all consistent | `results/subgroups.csv` |
| Specification curve | 120 analyses (3 methods × 15 covariate sets × settings): median HR 0.582, IQR 0.560–0.609, range 0.480–0.716, **none crossing 1.0** | `results/multiverse.csv` |
| TMLE (12-month risk difference) | −0.151 (95% CI −0.216 to −0.087) against a true −0.154; the naive estimate was −0.227 | `results/tmle.json` |

The published trial reported an OS hazard ratio of **0.58**
(Finn RS et al., *N Engl J Med* 2020;382:1894). The matched estimate lands
there; the unadjusted one does not. That gap is the entire teaching point.

## Comparing your own run

Your numbers will not match to the last digit, and they are not supposed to.
An agent writes its own analysis code, and two runs make different defensible
choices — which covariates go into the propensity model, what caliper, how ties
are broken. What should hold:

- the unadjusted HR is clearly **lower** than the matched one;
- the matched OS HR sits near 0.58, roughly 0.54–0.62;
- matching keeps somewhere near 700 pairs, not 200 and not 890;
- every \|SMD\| after matching is under 0.10;
- no specification in the multiverse crosses 1.0.

Those tolerances are exactly what [`../verify/`](../verify/) enforces, mission
by mission. If a check fails, it is not the tolerance being strict — it is one
of the traps documented in that mission.

⚠️ All data are synthetic. No real patient is represented, and nothing here is
evidence about atezolizumab, bevacizumab or sorafenib.
