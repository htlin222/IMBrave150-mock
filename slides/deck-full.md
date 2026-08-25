---
marp: true
theme: mono-academic
paginate: true
size: 16:9
lang: en
title: "Mission by Mission"
description: "Driving an AI coding agent end-to-end, from ten messy hospital CSVs to a typeset manuscript."
---

<!-- _class: title -->
<!-- _paginate: false -->

# Mission by Mission

<p class="subtitle">Reference edition — the complete mission-by-mission walkthrough behind the talk. Every number below was produced by the run recorded in this repository.</p>

<div class="byline">
<div class="name">Hsieh-Ting Lin, MD　林協霆</div>
<div class="affil">Department of Medical Oncology　腫瘤內科部<br>Koo Foundation Sun Yat-Sen Cancer Center　和信治癌中心醫院</div>
</div>

---

## Disclaimer and Conflict of Interest

- <span class="ic ic-alert"></span> **The data in this talk are entirely synthetic**
  - Simulated from the published summaries of the IMbrave150 trial<span class="ref">1</span>
  - No real patient is represented, and no record derives from any chart
  - Nothing here is evidence about atezolizumab, bevacizumab or sorafenib
- <span class="ic ic-target"></span> **What the talk is actually about**
  - The *workflow* — how to instruct an agent so its output can be audited
  - The recovered hazard ratio is a teaching target, not a finding
- <span class="ic ic-check"></span> **Conflict of interest**
  - The author declares no financial or non-financial conflict of interest
  - No industry funding, no honoraria, no relationship with any AI vendor

<!-- _footer: "<sup>1</sup> Finn RS, Qin S, Ikeda M, et al. Atezolizumab plus bevacizumab in unresectable hepatocellular carcinoma. <em>N Engl J Med</em>. 2020;382(20):1894-1905. doi:10.1056/NEJMoa1915745" -->

---

## What You Will See

- <span class="ic ic-database"></span> **The input**
  - 10 hospital CSV exports, 3 incompatible EHR schemas, 1,800 patients
- <span class="ic ic-package"></span> **The output**
  - A typeset preprint PDF whose every number and every reference is checked
- <span class="ic ic-terminal"></span> **The operator**
  - One person, typing prompts. No code written by hand.
- <span class="ic ic-eye"></span> **Two things to watch on every slide**
  - **Current step** — what the agent is being asked to do right now
  - **Good prompt** — why *that* wording, and what a bad one would cost

---

<!-- _class: section -->

<p class="kicker">Part I</p>

# The Operating Rhythm

<div class="rule"></div>

---

## The Unit of Work Is One Mission

- <span class="ic ic-pause"></span> **Current step**
  - Do one mission → run its acceptance script → summarise → **stop**
  - The agent is forbidden to continue because "the next step is obvious"
- <span class="ic ic-message"></span> **Good prompt**
  - State the stopping condition *in the instructions file*, not per turn
  - Give the halt a literal token the agent must emit

> Do one mission. Run `verify/chNN.py`. Say in three lines
> what we now see. Then output `PAUSED` and wait.

- <span class="ic ic-alert"></span> Without an explicit halt the agent will finish the whole project in one turn — correct, unwatchable, and unreviewable

---

## A Prompt That Survives Contact

<!-- _class: dense -->

- <span class="ic ic-target"></span> **Five parts, in this order**
  - **Goal** — one sentence, in the user's language, not the tool's
  - **Contract** — exact output paths, exact column names, exact value domains
  - **Constraints** — the failure modes you already know about
  - **Acceptance** — the command that decides pass or fail
  - **Stop** — what to emit, and to do nothing after it
- <span class="ic ic-check"></span> **Why the contract matters most**
  - A named file is checkable; "save the results" is not
  - If the schema is not pinned, the agent invents plausible column names — and every downstream step then fails for the wrong reason

---

## Constraints Are Cheaper Than Debugging

- <span class="ic ic-alert"></span> **Current step**
  - Front-load every landmine you have already stepped on
- <span class="ic ic-message"></span> **Good prompt** — real examples from this repo

> Never call `lifelines.plotting.add_at_risk_counts()`; this
> environment raises `TypeError`. Use the manual version below.
>
> Set `matplotlib.use("Agg")` *before* importing `pyplot`.
>
> Weighted Cox must pass `weights_col=` **and** `robust=True`.
>
> After every merge, `assert len(df) == expected`.

- <span class="ic ic-eye"></span> The fourth one is the dangerous kind: omit `robust=True` and nothing errors — the point estimate is right and the confidence interval is silently wrong

---

<!-- _class: section -->

<p class="kicker">Part II</p>

# Ten Hospitals, Three Dialects

<div class="rule"></div>

---

## Mission 0.1 — Open the Box, Change Nothing

- <span class="ic ic-database"></span> **Current step**
  - Copy the raw exports into a sandbox; read column names and one row
  - Write no transformation code at all
- <span class="ic ic-message"></span> **Good prompt**
  - Ask for an *observation*, and forbid the fix

> Copy `hospitals/` into `workspace/hospitals/` — copy, do not
> symlink. Print the columns and first row of H01, H02, H03.
> Then tell me three things that look wrong.
> **Do not start writing a converter.**

- <span class="ic ic-eye"></span> Agents default to solving. Naming the problem first is what makes the next three missions legible to an audience

---

## Mission 1.1 — Diagnose the Dialects

- <span class="ic ic-search"></span> **Current step**
  - Cluster the 10 files by column fingerprint, not by filename
  - Compare value encodings, units, and per-column missingness
- <span class="ic ic-message"></span> **Good prompt**
  - Force evidence over recall: `unique()`, not "typical values"
  - Supply an independent check the agent can grade itself against
  - Fan out — three subagents, one per dialect family, then merge
- <span class="ic ic-check"></span> **What it finds**
  - Albumin in g/L at some sites, g/dL at others — one order of magnitude
  - Three sites have **no** continuous AFP column at all

---

## Mission 1.2 — Harmonise Into One Table

- <span class="ic ic-merge"></span> **Current step**
  - `detect_vendor()` → `harmonise_file()` → `load_pooled()` → `pooled.csv`
- <span class="ic ic-message"></span> **Good prompt**
  - Hand over the canonical schema as a table: 27 names, types, domains
  - Say where the medians should land, so unit errors surface immediately

> `albumin_g_dl` — float, **g/dL**, median should be near 3.9
> `child_pugh_score` — 5 or 6 as an **integer**, not `A5`

- <span class="ic ic-alert"></span> **Never `dropna()`** — missingness here is structural, not random. Dropping rows would delete three hospitals and the confounding with them

---

## Mission 1.3 — The First Confounder Appears

- <span class="ic ic-git"></span> **Current step**
  - Left-join hospital attributes; profile each site; sort by % treated
- <span class="ic ic-eye"></span> **What the table shows**
  - Treatment share ranges widely across the ten sites
  - The sites that treat most are also the sites with better prognosis
- <span class="ic ic-message"></span> **Good prompt** — end on a question, not a task

> If the hospital decides both *which drug a patient gets* and
> *how that patient does*, what happens when you compare the two
> arms directly?

- <span class="ic ic-target"></span> The answer to that question is the entire next section — and the audience arrives at it before you say it

<!-- _footer: "<sup>9</sup> Hernán MA, Robins JM. Using big data to emulate a target trial when a randomized trial is not available. <em>Am J Epidemiol</em>. 2016;183(8):758-764. doi:10.1093/aje/kwv254" -->

---

<!-- _class: section -->

<p class="kicker">Part III</p>

# The Unadjusted Answer Is Lying

<div class="rule"></div>

---

## Mission 2.1 — Ask the Naive Question First

- <span class="ic ic-activity"></span> **Current step**
  - Fit a Cox model on treatment alone. One covariate. Nothing else.
  - Result: **HR 0.505 (95% CI 0.43–0.60)**
- <span class="ic ic-message"></span> **Good prompt**
  - Pin the output format so the number is machine-readable later

> Write `naive_hr.json` as
> `{"n":…, "hr":…, "ci_low":…, "ci_high":…, "p":…}`.
> Then tell me in one sentence what you would conclude
> from this number alone.

- <span class="ic ic-alert"></span> This is the slide the audience believes. Let them — it is the only way the correction lands

---

## Mission 2.2 — Prove It: The Arms Differ at Baseline

- <span class="ic ic-scale"></span> **Current step**
  - Standardised mean difference for all 11 covariates, by arm
  - Seven covariates exceed |SMD| 0.15 before any adjustment
- <span class="ic ic-message"></span> **Good prompt**
  - Write the formula out; do not let the agent pick a variant

> `SMD = (mean_t − mean_c) / sqrt((var_t + var_c) / 2)`

- <span class="ic ic-eye"></span> **Then ask for direction, not just magnitude**
  - Which covariates are imbalanced, which way do they lean, and does that bias the naive HR up or down?
  - "Report the SMDs" gets a table; this gets a diagnosis

<!-- _footer: "<sup>10</sup> Austin PC. Balance diagnostics for comparing the distribution of baseline covariates between treatment groups in propensity-score matched samples. <em>Stat Med</em>. 2009;28(25):3083-3107. doi:10.1002/sim.3697" -->

---

## Mission 2.3 — Propensity-Score Matching

<!-- _class: dense -->

- <span class="ic ic-scale"></span> **Current step**
  - Logistic PS on the same 11 covariates → 1:1 nearest neighbour, no replacement
  - Caliper = 0.2 × SD of **logit(PS)**<span class="ref">3</span> = 0.114
  - **706 pairs, 1,412 patients — 256 treated patients find no match**
- <span class="ic ic-message"></span> **Good prompt** — three clauses that decide reproducibility

> The caliper is 0.2 × SD of **logit(PS)**, not of PS.
> Sort treated by `logit_ps` ascending **before** matching.
> Report how many treated were left unmatched.

- <span class="ic ic-alert"></span> Greedy matching depends on order. Unstated order means a different cohort every run — and an unauditable manuscript

<!-- _footer: "<sup>2</sup> Austin PC. An introduction to propensity score methods for reducing the effects of confounding in observational studies. <em>Multivariate Behav Res</em>. 2011;46(3):399-424. doi:10.1080/00273171.2011.568786 · <sup>3</sup> Austin PC. Optimal caliper widths for propensity-score matching. <em>Pharm Stat</em>. 2011;10(2):150-161. doi:10.1002/pst.433" -->

---

## Mission 2.4 — Did the Matching Actually Work?

- <span class="ic ic-eye"></span> **Current step**
  - Love plot: |SMD| before vs after, reference line at 0.10
  - Propensity-score overlap, before and after
  - Largest remaining |SMD| after matching: **0.044**
- <span class="ic ic-message"></span> **Good prompt**
  - Specify the plot, not the impression: axes, reference line, pairing
  - Then ask the question the plot exists to answer

> Is there any region of the propensity score where one arm
> has no patients at all?

- <span class="ic ic-alert"></span> Do **not** ask for balance p-values — they measure sample size, not balance

---

<!-- _class: section -->

<p class="kicker">Part IV</p>

# Survival, and Whether It Holds

<div class="rule"></div>

---

## Mission 3.1 — Kaplan–Meier, Log-Rank, Cox

- <span class="ic ic-activity"></span> **Current step**
  - On the matched cohort: **OS HR 0.578 (0.48–0.70)**, p < 0.001
  - 12-month survival 71.1% vs 55.7%; median 21.3 vs 13.5 months
- <span class="ic ic-target"></span> **The point of the whole exercise**
  - The published randomised trial reported **HR 0.58**<span class="ref">1</span>
  - Naive 0.505 → adjusted 0.578. The gap was confounding, and it is recoverable
- <span class="ic ic-message"></span> **Good prompt**
  - Ask it to show that raw percentages mislead *before* it draws the curve — censoring becomes visible instead of asserted

<!-- _footer: "<sup>1</sup> Finn RS, Qin S, Ikeda M, et al. Atezolizumab plus bevacizumab in unresectable hepatocellular carcinoma. <em>N Engl J Med</em>. 2020;382(20):1894-1905. doi:10.1056/NEJMoa1915745" -->

---

## Mission 4 — Subgroups Test Consistency, Not Winners

- <span class="ic ic-git"></span> **Current step**
  - 13 pre-specified subgroups, one univariable Cox each, then a forest plot
  - All hazard ratios fall between 0.51 and 0.63; none crosses 1.0
- <span class="ic ic-message"></span> **Good prompt** — the third question is the teaching one

> ECOG 0 gives 0.61 and ECOG 1 gives 0.54.
> **May I say that ECOG 1 patients benefit more?**

- <span class="ic ic-check"></span> **The answer is no**, and the agent should say why: overlapping intervals, no interaction test, subgroups pre-specified for consistency
- <span class="ic ic-alert"></span> An agent asked "which subgroup benefits most" will happily answer

---

<!-- _class: statement -->

<p>The result survived one analysis.<br>Now try to break it.</p>

<p class="attrib">Part V — Robustness</p>

---

## Mission 5.1 — One Hundred Twenty Analytic Paths

- <span class="ic ic-shuffle"></span> **Current step**
  - Data held fixed; only analytic choices vary
  - 15 covariate sets × 8 adjustment methods = **120 specifications**
  - Median HR **0.582**, IQR 0.560–0.609, range 0.480–0.716
- <span class="ic ic-message"></span> **Good prompt**
  - Enumerate the grid explicitly — the agent must not choose the sensitivity analyses that flatter the result
- <span class="ic ic-alert"></span> **Report the honest number**
  - Only **63%** of specifications land in 0.55–0.61
  - That fraction belongs in the Limitations, not in the abstract

<!-- _footer: "<sup>4</sup> Steegen S, Tuerlinckx F, Gelman A, Vanpaemel W. Increasing transparency through a multiverse analysis. <em>Perspect Psychol Sci</em>. 2016;11(5):702-712. doi:10.1177/1745691616658637" -->

---

## Mission 5.2 — The Specification Curve

- <span class="ic ic-shuffle"></span> **Current step**
  - 120 specifications sorted by HR, each with its interval
  - Reference lines at 0.58 (trial) and 0.505 (naive)
- <span class="ic ic-message"></span> **Good prompt**
  - Ask for a title that states the conclusion, so the figure can be read without you standing next to it

> Title the figure:
> *Every reasonable adjustment lands near 0.58 · 120 specifications*

- <span class="ic ic-eye"></span> This is the slide that answers "did you just pick the analysis that worked?" — and it answers it before anyone asks

<!-- _footer: "<sup>5</sup> Simonsohn U, Simmons JP, Nelson LD. Specification curve analysis. <em>Nat Hum Behav</em>. 2020;4(11):1208-1214. doi:10.1038/s41562-020-0912-z" -->

---

## Mission 5.3 — Change the Estimand Entirely

- <span class="ic ic-flask"></span> **Current step**
  - Landmark 12-month mortality risk difference, TMLE with IPCW<span class="ref">6</span>
  - **RD −0.151 (−0.215 to −0.086)** — a different target, same direction
- <span class="ic ic-message"></span> **Good prompt**
  - Specify the censoring rule rather than letting it be inferred

> `Y = 1` if death before 12 months; `Y = 0` if alive at 12 months;
> if censored before 12 months, **`Y` is unknown** — set `Delta = 0`.

- <span class="ic ic-alert"></span> Left implicit, an agent will complete-case this and quietly bias the estimate. Naming the third state is the whole prompt

<!-- _footer: "<sup>6</sup> van der Laan MJ, Rubin D. Targeted maximum likelihood learning. <em>Int J Biostat</em>. 2006;2(1):Article 11. doi:10.2202/1557-4679.1043" -->

---

<!-- _class: section -->

<p class="kicker">Part VI</p>

# Writing the Paper Backwards

<div class="rule"></div>

---

## The Order of Writing Is the Method

<!-- _class: dense -->

- <span class="ic ic-file"></span> **Current step** — write the sections in this order, never another
  - **Methods** first — reconstructed by re-reading the scripts, not from memory
  - **Results** — every number pulled from a file in `workspace/`
  - **Discussion**, then **Introduction** — the intro exists to set up the discussion
  - **Conclusions**, then **Abstract**, then **Title** — last, once there is something to name
- <span class="ic ic-message"></span> **Good prompt**
  - "Re-read `harmonize.py`, `psm.py`, `multiverse.py`, `tmle.py`. Describe what the code **did**, not what you intended."
  - Ask for the software versions from `pip list`, not from the agent's memory
- <span class="ic ic-alert"></span> Written in any other order, the Introduction promises a paper you did not write

---

## Mission 6.2 — Every Number Carries Its Source

- <span class="ic ic-target"></span> **Current step**
  - Draft Results reading **only** from the output files
  - Tag each subsection with the file it came from
- <span class="ic ic-message"></span> **Good prompt**

> Take every number from files in `workspace/`. Do not copy from
> our conversation. End each subsection with `<!-- src: … -->`.

- <span class="ic ic-alert"></span> **The failure this prevents**
  - An agent recalling "HR was about 0.58" writes a plausible number
  - Plausible numbers pass human review and fail the audit in Mission 6.9
  - Source tags turn a reviewer's spot check into a scripted one

---

## Mission 6.8 — Every Reference Verified at Crossref

- <span class="ic ic-book"></span> **Current step**
  - Search for the real paper → resolve the DOI → confirm six bibliographic fields against the Crossref record
  - One subagent per reference; this stage is network-bound and embarrassingly parallel
- <span class="ic ic-message"></span> **Good prompt**
  - "Never write a DOI from memory. Search, then verify. A reference that fails verification is deleted, not guessed at."
  - Send a `mailto:` User-Agent — anonymous Crossref requests get rate-limited mid-demo
- <span class="ic ic-alert"></span> Fabricated citations are the single most reputationally expensive failure mode of this whole workflow

<!-- _footer: "<sup>11</sup> Crossref REST API. Accessed August 2026. https://api.crossref.org" -->

---

## Mission 6.9 — The Numeric Audit

- <span class="ic ic-check"></span> **Current step**
  - A script re-reads every output file, re-extracts every number in the manuscript, and compares them
  - Any mismatch fails the build. Not a warning — a failure.
- <span class="ic ic-message"></span> **Good prompt**
  - The audit is not written by the agent that wrote the manuscript
  - It is fixed in advance, in the repo, and the agent is told the command

```
python verify/ch06.py --mission 6.9
```

- <span class="ic ic-target"></span> This is what "auditable" means operationally: a claim of correctness that does not depend on trusting the writer

---

<!-- _class: section -->

<p class="kicker">Part VII</p>

# Reviewing Its Own Work

<div class="rule"></div>

---

## Mission 7.1 — Four Independent Reviewers

- <span class="ic ic-users"></span> **Current step**
  - Four subagents dispatched in one message, blind to one another
  - Statistical · Clinical · Reporting standards (STROBE<span class="ref">7</span>, RECORD<span class="ref">8</span>) · Reproducibility
- <span class="ic ic-message"></span> **Good prompt** — two clauses do the real work

> Each reviewer may read the manuscript and `workspace/` output
> files **only**. Reading the course material is forbidden.
>
> Each must raise at least three major comments. If you find
> none, read it again.

- <span class="ic ic-alert"></span> Give a reviewer the answer key and you get an answer check. Let it off with "looks good" and you got no review at all

<!-- _footer: "<sup>7</sup> von Elm E, Altman DG, Egger M, et al. The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement. <em>Lancet</em>. 2007;370(9596):1453-1457. doi:10.1016/S0140-6736(07)61602-X · <sup>8</sup> Benchimol EI, Smeeth L, Guttmann A, et al. The RECORD statement. <em>PLoS Med</em>. 2015;12(10):e1001885. doi:10.1371/journal.pmed.1001885" -->

---

## Mission 7.2 — Triage, Respond, Actually Edit

- <span class="ic ic-refresh"></span> **Current step**
  - Merge and de-duplicate into `review_log.csv`
  - Each comment gets ACCEPT / PARTIAL / **REJECT** — and a file that changed
- <span class="ic ic-message"></span> **Good prompt**
  - "Every REJECT needs a technical reason. 'We disagree' is not one."
  - "`action_taken` may not be left blank."
  - "Re-run the numeric audit immediately after editing."
- <span class="ic ic-alert"></span> Left unconstrained, an agent writes a courteous response letter and changes nothing. The edited file is the deliverable, not the letter

---

## Mission 7.4 — Removing the Machine Voice

- <span class="ic ic-eye"></span> **Current step**
  - Deterministic pattern check first, report-only, count the hits
  - Back up, rewrite, then diff — and re-run the numeric audit
- <span class="ic ic-message"></span> **Good prompt**
  - Calibrate on the author's real writing samples, not on "sound natural"
  - Forbid new claims: rewriting may change words, never numbers
- <span class="ic ic-alert"></span> **The order matters**
  - Humanise **after** the audit passes, then audit again
  - A rewriter with no backup and no diff is an unreviewable change

---

<!-- _class: section -->

<p class="kicker">Part VIII</p>

# Shipping It

<div class="rule"></div>

---

## Mission 8 — From Markdown to a Submittable File

- <span class="ic ic-package"></span> **Current step**
  - One build pipeline → PDF and DOCX in parallel; they share no dependency
  - Bibliography rendered from the verified `refs.bib`
- <span class="ic ic-message"></span> **Good prompt**
  - Name the flag that fails silently

> `pandoc` must be called with `--citeproc`. Without it there is
> no error — the raw `[@key]` markers are typeset into the PDF.

- <span class="ic ic-check"></span> **Then verify the artefact, not the command**
  - Extract text from the built PDF and assert no `[@` survives
  - "The build exited zero" is not evidence that the build is correct

---

## What CI Does in This Repo

- <span class="ic ic-git"></span> **Current step**
  - Push to `main` touching `slides/**` → the deck is re-rendered to PDF
  - The PDF is uploaded as a build artefact on every push
  - Push a tag `slides-v*` → a GitHub Release is cut with the PDF attached
- <span class="ic ic-check"></span> **Why bother for a talk**
  - The version being projected is the version in the repository
  - A slide corrected at 23:00 the night before cannot diverge from the file
- <span class="ic ic-target"></span> Same principle as the numeric audit: make the machine hold the invariant, not the human

---

<!-- _class: section -->

<p class="kicker">Part IX</p>

# What to Take Home

<div class="rule"></div>

---

## Six Prompt Patterns Worth Stealing

- <span class="ic ic-target"></span> **Pin the contract** — exact filenames, exact columns, exact value domains
- <span class="ic ic-alert"></span> **Front-load known landmines** — every constraint is a debugging session you do not have on stage
- <span class="ic ic-check"></span> **Make acceptance external** — a script you did not write this turn decides pass or fail
- <span class="ic ic-eye"></span> **Ask for evidence, not recall** — `unique()`, `pip list`, the output file; never "as I remember"
- <span class="ic ic-pause"></span> **Name the stopping point** — an explicit halt token, stated once in the instructions
- <span class="ic ic-message"></span> **End on a question** — the last line of a good prompt is often what the agent should *ask*, not do

---

## Four Ways It Goes Wrong

- <span class="ic ic-alert"></span> **The agent solves too early**
  - Ask it to describe the problem and forbid the fix in the same breath
- <span class="ic ic-alert"></span> **The number is remembered, not read**
  - Every figure re-derived from a file; source tags; a scripted audit
- <span class="ic ic-alert"></span> **The reviewer has seen the answer key**
  - Reviewer subagents get the manuscript and the outputs, nothing else
- <span class="ic ic-alert"></span> **The citation looks perfect**
  - Search, resolve, verify six fields at Crossref. Unverified means deleted

---

<!-- _class: statement -->

<p>The agent did not make the analysis trustworthy.<br>The acceptance scripts did.</p>

<p class="attrib">Every mission in this talk is reproducible from a public repository: github.com/htlin222/IMBrave150-mock</p>

---

## References

<!-- _class: dense refs -->

1. Finn RS, Qin S, Ikeda M, et al. Atezolizumab plus bevacizumab in unresectable hepatocellular carcinoma. *N Engl J Med*. 2020;382(20):1894-1905. doi:10.1056/NEJMoa1915745
2. Austin PC. An introduction to propensity score methods for reducing the effects of confounding in observational studies. *Multivariate Behav Res*. 2011;46(3):399-424. doi:10.1080/00273171.2011.568786
3. Austin PC. Optimal caliper widths for propensity-score matching when estimating differences in means and differences in proportions in observational studies. *Pharm Stat*. 2011;10(2):150-161. doi:10.1002/pst.433
4. Steegen S, Tuerlinckx F, Gelman A, Vanpaemel W. Increasing transparency through a multiverse analysis. *Perspect Psychol Sci*. 2016;11(5):702-712. doi:10.1177/1745691616658637
5. Simonsohn U, Simmons JP, Nelson LD. Specification curve analysis. *Nat Hum Behav*. 2020;4(11):1208-1214. doi:10.1038/s41562-020-0912-z

---

## References (continued)

<!-- _class: dense refs -->

6. van der Laan MJ, Rubin D. Targeted maximum likelihood learning. *Int J Biostat*. 2006;2(1):Article 11. doi:10.2202/1557-4679.1043
7. von Elm E, Altman DG, Egger M, et al. The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: guidelines for reporting observational studies. *Lancet*. 2007;370(9596):1453-1457. doi:10.1016/S0140-6736(07)61602-X
8. Benchimol EI, Smeeth L, Guttmann A, et al. The REporting of studies Conducted using Observational Routinely-collected health Data (RECORD) statement. *PLoS Med*. 2015;12(10):e1001885. doi:10.1371/journal.pmed.1001885
9. Hernán MA, Robins JM. Using big data to emulate a target trial when a randomized trial is not available. *Am J Epidemiol*. 2016;183(8):758-764. doi:10.1093/aje/kwv254
10. Austin PC. Balance diagnostics for comparing the distribution of baseline covariates between treatment groups in propensity-score matched samples. *Stat Med*. 2009;28(25):3083-3107. doi:10.1002/sim.3697
11. Crossref REST API documentation. Crossref. Accessed August 25, 2026. https://api.crossref.org

---

<!-- _class: title -->
<!-- _paginate: false -->

# Thank You

<p class="subtitle">Repository, mission guide and acceptance scripts:<br>github.com/htlin222/IMBrave150-mock</p>

<div class="byline">
<div class="name">Hsieh-Ting Lin, MD　林協霆</div>
<div class="affil">Department of Medical Oncology　腫瘤內科部<br>Koo Foundation Sun Yat-Sen Cancer Center　和信治癌中心醫院</div>
</div>
