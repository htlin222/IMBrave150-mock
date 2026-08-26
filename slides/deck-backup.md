---
marp: true
theme: mono-academic
paginate: true
size: 16:9
lang: en
title: "Mission by Mission — Backup"
description: "Backup edition: the talk with a still frame from a recorded agent session after each signpost."
---

<!-- _class: title -->
<!-- _paginate: false -->

# Mission by Mission

<p class="subtitle">Driving an AI coding agent, live — from ten messy hospital exports to a result you can audit.<br><em>Backup edition: every step shown as recorded session.</em></p>

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
> one schema, names and units fixed. Never
> drop a row for missingness. Then attach
> each hospital's type and region.

- <span class="ic ic-eye"></span> **What to watch**
  - Albumin is in g/L at some sites, g/dL at others — a tenfold error waiting
  - **1,800 patients, 962 vs 838.** Three sites record no AFP at all

<!-- _footer: "live-demo · Missions 1.1–1.3　·　Slides and repository: github.com/htlin222/IMBrave150-mock" -->

---

<!-- _class: shot -->
<!-- _footer: "" -->

## <span class="tag">recorded</span>Ten hospitals, three dialects

![](img/seg1.png)

<p class="caption">It built the comparison table itself and found the trap: <strong>dialect B stores albumin in g/L and bilirubin in µmol/L</strong>.</p>

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

<!-- _class: shot -->
<!-- _footer: "" -->

## <span class="tag">recorded</span>The unadjusted answer

![](img/seg2.png)

<p class="caption"><strong>HR 0.505</strong> — then the balance table. Every serious imbalance leans the same way, toward the treated arm.</p>

---

## Make the Two Arms Comparable

- <span class="ic ic-scale"></span> **What this step does**
  - Pairs each treated patient with an untreated patient of similar profile

> Match 1:1 on the propensity score, nearest
> neighbour, no replacement. Take the treated
> in **ascending** score order. Do not force a
> match outside the caliper. Report how many
> treated were left unmatched.

- <span class="ic ic-eye"></span> **What to watch**
  - **706 pairs. 256 treated patients found no match** — that is honesty, not failure
  - **HR 0.578.** The randomised trial reported **0.58**<span class="ref">1</span>

<!-- _footer: "live-demo · Missions 2.3–3.1　·　<sup>1</sup> Finn RS, et al. <em>N Engl J Med</em>. 2020;382(20):1894-1905. doi:10.1056/NEJMoa1915745" -->

---

<!-- _class: shot -->
<!-- _footer: "" -->

## <span class="tag">recorded</span>Matching, and what it costs

![](img/seg3.png)

<p class="caption"><strong>706 pairs, 256 treated left unmatched.</strong> It separates the 124 who could never match from the 132 caliper failures.</p>

---

## Try to Break Your Own Result

- <span class="ic ic-shuffle"></span> **What this step does**
  - Re-runs the same data through every defensible analysis, not the one that worked

> Hold the data fixed. Vary only the analytic
> choices: 15 covariate sets × 8 adjustment
> methods = 120 runs. Report the median, the
> spread, and **how many landed outside the
> range I was hoping for.**

- <span class="ic ic-eye"></span> **What to watch**
  - The median lands on **0.58** every time. The **spread does not** — about a
    third of the runs fall outside 0.55–0.61
  - Nothing crosses 1.0. The direction is solid; the third decimal is not

<!-- _footer: "live-demo · Missions 5.1–5.2　·　Steegen S, Tuerlinckx F, Gelman A, Vanpaemel W. Increasing transparency through a multiverse analysis. <em>Perspect Psychol Sci</em>. 2016;11(5):702-712. doi:10.1177/1745691616658637" -->

---

<!-- _class: shot -->
<!-- _footer: "" -->

## <span class="tag">recorded</span>120 analytic paths

![](img/seg4.png)

<p class="caption">It found its own outlier: the 0.822 run matches on a near-degenerate score that reuses one control <strong>212 times</strong>.</p>

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

<!-- _class: shot -->
<!-- _footer: "" -->

## <span class="tag">recorded</span>Four reviewers, blind to each other

![](img/seg5.png)

<p class="caption"><strong>Four background agents launched</strong> from one message, each reading the manuscript and the output files, none seeing the others.</p>

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
- → 120 re-runs: median **0.58**
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
