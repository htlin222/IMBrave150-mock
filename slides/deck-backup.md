---
marp: true
theme: mono-academic
paginate: true
size: 16:9
lang: en
title: "Mission by Mission — Backup"
description: "Backup edition: the talk with a recorded terminal capture after each signpost, for when the live demo will not cooperate."
---

<!-- _class: title -->
<!-- _paginate: false -->

# Mission by Mission

<p class="subtitle">Driving an AI coding agent, live — from ten messy hospital exports to a result you can audit.<br><em>Backup edition: every step shown as recorded output.</em></p>

<div class="byline">
<div class="name">Hsieh-Ting Lin, MD　林協霆</div>
<div class="affil">Department of Medical Oncology　腫瘤內科部<br>Koo Foundation Sun Yat-Sen Cancer Center　和信治癌中心醫院</div>
</div>

---

## Disclaimer and Conflict of Interest

- <span class="ic ic-alert"></span> **The data are entirely synthetic**
  - Simulated from the published summaries of the IMbrave150 trial<span class="ref">1</span>
  - No real patient is represented; no record comes from any chart
  - Nothing here is evidence about atezolizumab, bevacizumab or sorafenib
- <span class="ic ic-target"></span> **What this talk is about**
  - How to instruct an agent so that its output can be checked
  - The hazard ratio is a teaching target, not a finding
- <span class="ic ic-check"></span> **Conflict of interest**
  - No financial or non-financial conflict; no industry funding
  - No relationship with any AI vendor

<!-- _footer: "<sup>1</sup> Finn RS, Qin S, Ikeda M, et al. Atezolizumab plus bevacizumab in unresectable hepatocellular carcinoma. <em>N Engl J Med</em>. 2020;382(20):1894-1905. doi:10.1056/NEJMoa1915745" -->

---

## What an Agent Is, and Is Not

- <span class="ic ic-message"></span> **A chatbot** answers you
  - You paste data in, it writes text back. Nothing on your disk changes.
- <span class="ic ic-terminal"></span> **An agent** works on your machine
  - It reads your files, writes scripts, runs them, reads the error, tries again
  - It keeps going until a condition you set is met
- <span class="ic ic-eye"></span> **So the hard part moves**
  - Not *"can it write the code"* — it can
  - But *"how do I know the answer it handed me is right"*
- <span class="ic ic-check"></span> That question is the whole talk

---

<!-- _class: cols -->

## The Difference One Sentence Makes

<div class="columns">
<div>

### <span class="ic ic-alert"></span> What most people type

> Analyse this data and tell me
> if the treatment works.

- Picks its own method
- Picks its own file names
- Different answer every run
- Nothing to check it against

</div>
<div>

### <span class="ic ic-check"></span> What I will type

> Fit a Cox model on treatment
> alone. Write `naive_hr.json`
> with `hr`, `ci_low`, `ci_high`.
> Then tell me in one sentence
> what you would conclude.

- Named file, named fields
- Reruns identically
- A script can grade it

</div>
</div>

---

## Ten Hospitals, Three Dialects

- <span class="ic ic-database"></span> **What this step does**
  - Ten CSV exports, three incompatible record systems, into one table

> Group the ten files by their column
> fingerprint, not by filename. Report the
> actual values with `unique()`. Convert to
> this schema — 27 fields, names and units
> fixed. Never drop a row for missingness.

- <span class="ic ic-eye"></span> **What to watch**
  - Albumin is in g/L at some sites, g/dL at others — a tenfold error waiting
  - **1,800 patients, 962 vs 838.** Three sites record no AFP at all

<!-- _footer: "live-demo · Missions 1.1–1.3　·　Slides and repository: github.com/htlin222/IMBrave150-mock" -->

---

<!-- _class: term -->
<!-- _footer: "" -->

## <span class="tag">recorded</span>Ten hospitals, three dialects

```
pooled rows        1800
unique patient_id  1800
hospitals          10

by dialect
  Alpha    620   H01 H04 H07 H10
  Beta     620   H02 H05 H08
  Gamma    560   H03 H06 H09

arm                {'Atezo+Bev': np.int64(962), 'Sorafenib': np.int64(838)}
albumin  median    3.90 g/dL
bilirubin median   0.81 mg/dL

missing (%)
  albumin_g_dl             4.3
  bilirubin_mg_dl          5.1
  afp_ng_ml               35.3

vendor detected by fingerprint vs recorded in metadata: 0 mismatches out of 1800

```

<p class="caption"><strong>1,800</strong> patients, one table. Albumin median lands at <strong>3.90 g/dL</strong> — the unit conversion worked.</p>

---

## The Unadjusted Answer Is Lying

- <span class="ic ic-activity"></span> **What this step does**
  - Compares the two arms with no adjustment whatsoever

> Fit a Cox model on treatment alone.
> Write `naive_hr.json`. Then tell me in one
> sentence what you would conclude from
> this number by itself.

- <span class="ic ic-eye"></span> **What to watch**
  - **HR 0.505** — the drug looks better than the trial ever claimed
  - Then: **8 of 11 baseline factors differ**, every one favouring the treated arm
  - Believe the first number for thirty seconds. That is the point

<!-- _footer: "live-demo · Missions 2.1–2.2" -->

---

<!-- _class: term -->
<!-- _footer: "" -->

## <span class="tag">recorded</span>The unadjusted answer

```
n = 1800   Atezo+Bev 962   Sorafenib 838
deaths        231 vs 334

UNADJUSTED OS   HR 0.505  (95% CI 0.43-0.60)   p = 1.64e-15

baseline |SMD| > 0.10 : 8 of 11 covariates
baseline |SMD| > 0.15 : 7

  afp_ge_400                  0.325    0.436  -0.228  <-
  macrovascular_invasion      0.319    0.427  -0.225  <-
  age                        62.812   65.165  -0.210  <-
  extrahepatic_spread         0.552    0.652  -0.204  <-
  albi_ge2                    0.499    0.587  -0.178  <-
  varices_at_baseline         0.244    0.323  -0.176  <-
  ecog_ps                     0.358    0.434  -0.157  <-
  asia                        0.541    0.483  +0.115  <-
  bclc_C                      0.827    0.842  -0.040
  male                        0.820    0.805  +0.038
  child_pugh_score            5.306    5.308  -0.005

```

<p class="caption"><strong>HR 0.505</strong>, then <strong>8 of 11</strong> baseline factors out of balance. The first number was never real.</p>

---

## Make the Two Arms Comparable

- <span class="ic ic-scale"></span> **What this step does**
  - Pairs each treated patient with an untreated patient of similar profile

> Match 1:1 on the propensity score, nearest
> neighbour, no replacement. Sort treated by
> the score **before** matching. Do not force
> a match outside the caliper. Report how
> many treated were left unmatched.

- <span class="ic ic-eye"></span> **What to watch**
  - **706 pairs. 256 treated patients found no match** — that is honesty, not failure
  - **HR 0.578.** The randomised trial reported **0.58**<span class="ref">1</span>

<!-- _footer: "live-demo · Missions 2.3–3.1　·　<sup>1</sup> Finn RS, et al. <em>N Engl J Med</em>. 2020;382(20):1894-1905. doi:10.1056/NEJMoa1915745" -->

---

<!-- _class: term -->
<!-- _footer: "" -->

## <span class="tag">recorded</span>Matching, and what it costs

```
caliper = 0.2 x SD(logit PS) = 0.1142
matched pairs         706
patients after match  1412
treated unmatched     256 (26.6% of treated)

max |SMD| before      0.228
max |SMD| after       0.044
covariates > 0.10     0

raw proportion who died (ignores censoring)
  Atezo+Bev  25.6%
  Sorafenib  38.0%
  median follow-up  8.0 vs 6.0 months

OS   HR 0.578 (0.48-0.70)   log-rank p = 8.75e-09
     12-month 71.1% vs 55.7%   median 21.3 vs 13.46 months
     figures/km_os.svg
PFS  HR 0.632 (0.55-0.72)   log-rank p = 5.47e-12
```

<p class="caption"><strong>706 pairs</strong>, <strong>256 treated left out</strong>, and <strong>HR 0.578</strong> against a trial value of 0.58.</p>

---

## Try to Break Your Own Result

- <span class="ic ic-shuffle"></span> **What this step does**
  - Re-runs the same data through every defensible analysis, not the one that worked

> Hold the data fixed. Vary only the analytic
> choices: 15 covariate sets × 8 adjustment
> methods = 120 runs. Report the median, the
> spread, and **what fraction lands outside
> the range I was hoping for.**

- <span class="ic ic-eye"></span> **What to watch**
  - Median **0.582**, range **0.480–0.716**; only **63%** land in 0.55–0.61
  - That 63% belongs in the limitations, not in the abstract

<!-- _footer: "live-demo · Missions 5.1–5.2　·　Steegen S, Tuerlinckx F, Gelman A, Vanpaemel W. Increasing transparency through a multiverse analysis. <em>Perspect Psychol Sci</em>. 2016;11(5):702-712. doi:10.1177/1745691616658637" -->

---

<!-- _class: term -->
<!-- _footer: "" -->

## <span class="tag">recorded</span>120 analytic paths

```
naive (unadjusted)      0.505
specifications          120  (15 covariate sets x 8 methods)
median HR               0.582
IQR                     0.560 - 0.609
range                   0.480 - 0.716
within 0.55-0.61        63%
specs crossing HR 1.0   0
specs whose CI hits 1.0 0

            count  median    min    max
method                                 
iptw           15   0.584  0.557  0.595
psm            90   0.595  0.480  0.716
regression     15   0.556  0.546  0.576
```

<p class="caption">Median <strong>0.582</strong>, but only <strong>63%</strong> inside 0.55–0.61. Both numbers get reported.</p>

---

## Let It Review Its Own Manuscript

- <span class="ic ic-users"></span> **What this step does**
  - Opens four reviewers at once, each blind to the other three

> Open four reviewers in parallel: statistical,
> clinical, reporting standards, reproducibility.
> Each may read the manuscript and the output
> files **only**. Each must raise at least three
> major comments. Found none? Read it again.

- <span class="ic ic-eye"></span> **What to watch**
  - Four windows moving at once — that picture is the point
  - The reproducibility reviewer re-checks **every number against its source file**

<!-- _footer: "live-demo · Mission 7.1" -->

---

<!-- _class: term -->
<!-- _footer: "" -->

## <span class="tag">recorded</span>Four reviewers, blind to each other

```
Dispatching 4 review subagents in parallel...

  Reviewer 1  statistical            [running]
  Reviewer 2  clinical               [running]
  Reviewer 3  reporting standards    [running]
  Reviewer 4  reproducibility        [running]

  Reviewer 3  done  198s   Major revision   7 major comments
  Reviewer 1  done  280s   Major revision   7 major comments
  Reviewer 2  done  306s   Major revision   7 major comments
  Reviewer 4  done  380s   Major revision   6 major comments

R4-3  site_join.py writes back over pooled.csv and crashes on rerun
R4-1  "order-independent" is false: 232 tied scores, ~46/706 pairs move
R3-7  PFS true value 0.59 carries no src tag and is in no output file
```

<p class="caption">All four returned <strong>Major revision</strong>. Three of the findings were real bugs, and were fixed.</p>

---

<!-- _class: cols -->

## The Whole Path, on One Slide

<div class="columns">
<div>

### <span class="ic ic-git"></span> What we just did

- 10 CSVs, 3 record systems
- → 1,800 patients, one table
- → **HR 0.505** unadjusted
- → **HR 0.578** matched
- → 120 re-runs: **0.480–0.716**
- → four reviewers, blind

</div>
<div>

### <span class="ic ic-target"></span> The benchmark

- The randomised trial reported
  **HR 0.58**<span class="ref">1</span>
- The gap between 0.505 and
  0.578 was confounding —
  and it was recoverable
- Nothing above was typed
  by hand except the prompts

</div>
</div>

<!-- _footer: "<sup>1</sup> Finn RS, Qin S, Ikeda M, et al. Atezolizumab plus bevacizumab in unresectable hepatocellular carcinoma. <em>N Engl J Med</em>. 2020;382(20):1894-1905. doi:10.1056/NEJMoa1915745" -->

---

## Four Habits Worth Stealing

- <span class="ic ic-target"></span> **Name the file and the fields**
  - "Save the results" cannot be checked. `naive_hr.json` with `hr`, `ci_low` can
- <span class="ic ic-alert"></span> **Write your known traps into the instructions**
  - Every constraint you state is a debugging session you do not have on stage
- <span class="ic ic-check"></span> **Let something else decide pass or fail**
  - A script you did not write this turn, that the agent cannot edit
- <span class="ic ic-pause"></span> **Tell it where to stop**
  - Otherwise it finishes the whole project in one turn — correct, and unreviewable

---

<!-- _class: title -->
<!-- _paginate: false -->

# Thank You

<p class="subtitle">Every mission, prompt and acceptance script:<br>github.com/htlin222/IMBrave150-mock</p>

<div class="byline">
<div class="name">Hsieh-Ting Lin, MD　林協霆</div>
<div class="affil">Department of Medical Oncology　腫瘤內科部<br>Koo Foundation Sun Yat-Sen Cancer Center　和信治癌中心醫院</div>
</div>
