# Recovering a Randomised Treatment Effect from Harmonised Multicentre Records: A Fully Synthetic, Machine-Auditable Replication

**Running title:** Auditable observational replication of IMbrave150

---

## Abstract

**Background.** Observational replications of randomised trials are routinely
doubted because treatment allocation in routine care is driven by prognosis. We
built a synthetic multicentre cohort with a known data-generating mechanism and
asked whether a conventional adjustment workflow recovers the known effect, and
whether every step of that workflow can be checked by machine.

**Methods.** Ten simulated hospitals contributed 1,800 patients with
unresectable hepatocellular carcinoma enrolled in 2018-2019. Records arrived in
three incompatible electronic health record schemas and were harmonised to a
single 27-field specification, including conversion of albumin from g/L to g/dL
and bilirubin from µmol/L to mg/dL at three sites. Treatment allocation was
confounded by hospital. We estimated overall survival by Cox regression before
and after 1:1 nearest-neighbour propensity-score matching without replacement
(caliper 0.2 × SD of the logit propensity score). Robustness was assessed across
120 pre-specified analytic specifications, and a secondary estimand, the
12-month risk difference for death, was estimated by targeted maximum likelihood
estimation with inverse probability of censoring weighting.

**Results.** Before adjustment, 8 of 11 covariates had a standardised mean
difference above 0.10 and 7 above 0.15; all seven of the latter were consistent
with a better prognosis in the atezolizumab-plus-bevacizumab group. The unadjusted hazard ratio for death was
0.505 (95% CI, 0.43 to 0.60). Matching produced 706 pairs (1,412 patients);
256 treated patients (26.6%) found no match within the caliper of 0.114, and the
largest remaining absolute standardised mean difference was 0.044. In the
matched cohort the hazard ratio for death was 0.578 (95% CI, 0.48 to 0.70;
log-rank P < 0.001), with 12-month survival of 71.1% versus 55.7% and median
overall survival of 21.3 versus 13.5 months. Progression-free survival gave a
hazard ratio of 0.632 (95% CI, 0.55 to 0.72). All 13 pre-specified subgroups
gave hazard ratios between 0.51 and 0.63 and none crossed 1.0. Across 120
specifications the median hazard ratio was 0.582 (interquartile range, 0.560 to
0.609; full range, 0.480 to 0.716), with 63% falling between 0.55 and 0.61. The
12-month risk difference was -0.151 (95% CI, -0.215 to -0.086) against a true
value of -0.154; the naive complete-case difference was -0.227.

**Conclusions.** In this synthetic setting a conventional propensity-score
workflow recovered the hazard ratio of 0.58 reported by the corresponding
randomised trial, whereas the unadjusted estimate overstated the effect. The
transferable result is the auditable procedure, not the estimate.

---

## Introduction

Atezolizumab plus bevacizumab is an established first-line option for
unresectable hepatocellular carcinoma, on the basis of a randomised phase 3
trial that reported a hazard ratio for death of 0.58 against sorafenib.<sup>1</sup>

Attempts to reproduce such results from routinely collected data face a
structural obstacle: in ordinary care, the treatment a patient receives and the
outcome that patient experiences are both influenced by where the patient is
treated. Propensity-score methods exist precisely to address this,<sup>2,3</sup>
and the target-trial framework gives a principled way to state what is being
estimated.<sup>9</sup> Yet observational replications remain widely distrusted,
for two reasons that are usually conflated. The first is that the adjustment may
be inadequate. The second is that the reader cannot check the analysis: numbers
in a manuscript are typically not traceable to the files that produced them, and
the analytic choices that were not taken are invisible.

Because the true effect is unknowable in real data, neither concern can be
settled empirically there. We therefore constructed a fully synthetic
multicentre cohort in which the data-generating mechanism, and hence the true
effect, is known by construction. Our aim was to ask two questions of a
conventional analysis workflow: whether it recovers the known effect, and
whether each step of it can be verified mechanically rather than trusted.

---

## Methods

### Study design and data sources

This study uses **entirely synthetic data**. Patient records were simulated from
the published summary statistics of the IMbrave150 trial.<sup>1</sup> No real
patient is represented and no record derives from any medical chart. Nothing in
this report constitutes evidence about atezolizumab, bevacizumab or sorafenib.

Ten simulated hospitals contributed 1,800 adults with unresectable
hepatocellular carcinoma enrolled between 2018 and 2019: four academic centres,
two regional hospitals and four community hospitals. Sites varied both in the
proportion of patients receiving atezolizumab plus bevacizumab (34.7% to 65.9%)
and in the observed death rate (27.2% to 36.8%), so that hospital influenced
both treatment assignment and prognosis.

### Harmonisation

Records arrived in three distinct electronic health record schemas, identified
by column fingerprint rather than by filename: Alpha (4 sites, 620 patients),
Beta (3 sites, 620 patients) and Gamma (3 sites, 560 patients). All records were
mapped to a single 27-field specification with fixed names, types and value
domains.

Three conversions were required. Beta sites reported albumin in g/L and
bilirubin in µmol/L; these were divided by 10 and by 17.104 respectively to give
g/dL and mg/dL. Gamma sites encoded Child-Pugh as a class-and-score string
("A5"), from which the numeric score was extracted, and recorded sex as a male
indicator rather than a sex field. Most consequentially, **Gamma sites carry no
continuous alpha-fetoprotein field at all**; the binary indicator of
alpha-fetoprotein of 400 ng/mL or above was therefore used throughout, and
continuous alpha-fetoprotein (missing for 35.3% of the cohort) was never
modelled. No records were dropped for missingness at any stage: the missingness
here is structural, and complete-case analysis would have removed three
hospitals together with the confounding they carry.

After harmonisation, the pooled cohort contained 1,800 patients with unique
identifiers; 962 received atezolizumab plus bevacizumab and 838 received
sorafenib.

### Statistical analysis

The propensity score was estimated by logistic regression of treatment on 11
covariates: age, ECOG performance status, Child-Pugh score, alpha-fetoprotein
of 400 ng/mL or above, macrovascular invasion, extrahepatic spread, BCLC stage C,
ALBI grade 2 or above, varices at baseline, male sex, and treatment in Asia
excluding Japan.

Matching was 1:1 nearest neighbour without replacement, with a caliper of
0.2 × the standard deviation of the **logit** propensity score (0.114 on this
cohort). Treated patients were processed in ascending order of the logit
propensity score. Greedy matching is order-dependent, and an unstated order
makes the cohort irreproducible; fixing the order makes a given input file
reproduce exactly. It does **not** make the result invariant to input row
order: 232 patients share a tied logit propensity score, and ties are broken by
position, so permuting the input changes roughly 46 of the 706 pairs and moves
the hazard ratio within 0.577-0.579. Treated patients with no control inside the
caliper were left unmatched rather than matched to a distant control.

Balance was assessed by the standardised mean difference with the pooled
standard deviation in the denominator, against a threshold of 0.10. Balance
tests based on P values were deliberately not used, since they measure sample
size rather than balance.<sup>10</sup>

Overall and progression-free survival were estimated by the Kaplan-Meier method,
compared by log-rank test, and summarised by Cox proportional-hazards models
containing treatment alone. Thirteen subgroups were specified before analysis
and are reported descriptively.

Robustness was assessed by a specification curve<sup>4,5</sup> over 120
analyses: 15 covariate sets (the full set, 11 leave-one-out sets, and three
reduced clinical sets) crossed with 8 adjustment methods (multivariable Cox
regression; stabilised inverse probability of treatment weighting; and
propensity-score matching at calipers of 0.1, 0.2 and 0.5 in 1:1 and 1:2 ratios).
Weighted Cox models used robust standard errors; omitting that correction leaves
the point estimate unchanged while badly understating the standard error.

A secondary estimand, the difference in probability of death by 12 months, was
estimated by targeted maximum likelihood estimation<sup>6</sup> with inverse
probability of censoring weighting. Patients censored before 12 months have an
unknown landmark outcome and were weighted back rather than discarded. Covariates
comprised the 11 clinical variables plus hospital indicator variables. The
treatment mechanism was truncated to [0.02, 0.98]; before truncation it ranged
from 0.118 to 0.904.

### Estimand statement

The primary estimand is the hazard ratio for death in the matched cohort. Because
matching discards treated patients who have no comparable control, this is an
average treatment effect **in the treated who could be matched**, not an average
treatment effect in the whole cohort. The secondary estimand is a risk difference
on the probability scale at a 12-month landmark. The two are not comparable and
are not presented as alternative expressions of the same quantity.

Analyses used Python with lifelines 0.30.0, pandas 3.0.3 and numpy 2.5.1. All
scripts are deterministic and contain no random number generation.

---

## Results

### Cohort

The harmonised cohort comprised 1,800 patients from 10 hospitals, of whom 962
received atezolizumab plus bevacizumab and 838 received sorafenib. Three
electronic health record schemas contributed 620, 620 and 560 patients.

<!-- src: pooled.csv, site_profile.csv -->

### Baseline imbalance

Before adjustment, 8 of the 11 covariates had an absolute standardised mean
difference above 0.10 and 7 above 0.15. Every one of the seven favoured the
atezolizumab-plus-bevacizumab group: those patients were younger and less likely
to have alpha-fetoprotein of 400 ng/mL or above, macrovascular invasion,
extrahepatic spread, ALBI grade 2 or above, varices, or ECOG performance status
of 1. The largest imbalance was 0.228.

<!-- src: baseline_table1.csv -->

### Unadjusted survival

Without adjustment, the hazard ratio for death was 0.505 (95% CI, 0.43 to 0.60;
P = 1.6 × 10⁻¹⁵).

<!-- src: naive_hr.json -->

### Matching and balance

Matching produced 706 pairs comprising 1,412 patients. **256 treated patients
(26.6%) had no control within the caliper of 0.114 and were left unmatched.**
After matching, the largest absolute standardised mean difference was 0.044 and
no covariate exceeded 0.10 (Figure 1).

<!-- src: matched.csv, balance.csv -->

### Survival in the matched cohort

In the matched cohort the hazard ratio for death was 0.578 (95% CI, 0.48 to 0.70;
log-rank P < 0.001) (Figure 2). Kaplan-Meier survival at 12 months was 71.1% with
atezolizumab plus bevacizumab and 55.7% with sorafenib; median overall survival
was 21.3 and 13.5 months respectively. The corresponding raw proportions who
died, which ignore differential follow-up, were 25.6% and 38.0%; the gap between
1 minus that proportion and the Kaplan-Meier estimate illustrates why the two
must not be interchanged. Progression-free survival gave a hazard ratio of 0.632
(95% CI, 0.55 to 0.72).

<!-- src: km_summary.json -->

### Subgroups

All 13 pre-specified subgroups gave hazard ratios between 0.51 and 0.63, and the
95% confidence interval excluded 1.0 in every one (Figure 3). Differences between
subgroups were small relative to their confidence intervals; no interaction test
was performed and no subgroup is claimed to benefit more than another.

<!-- src: subgroups.csv -->

### Sensitivity across analytic specifications

Across 120 specifications the median hazard ratio was 0.582 (interquartile range,
0.560 to 0.609), with a full range of 0.480 to 0.716 (Figure 4). **63% of
specifications fell between 0.55 and 0.61.** No specification produced a hazard
ratio at or above 1.0, and no confidence interval covered 1.0. Regression
adjustment gave systematically lower estimates (median 0.556) than
propensity-score matching (median 0.595).

<!-- src: multiverse.csv -->

### Secondary estimand

The estimated difference in probability of death by 12 months was -0.151
(95% CI, -0.215 to -0.086), against a true value of -0.154 computed from the
known data-generating mechanism. The naive complete-case difference was -0.227,
overstating the true difference by 47%.

<!-- src: tmle.json -->

---

## Discussion

A conventional propensity-score workflow applied to a confounded synthetic
multicentre cohort produced a hazard ratio for death of 0.578, close to the 0.58
reported by the corresponding randomised trial,<sup>1</sup> while the unadjusted
estimate of 0.505 overstated the effect by an amount entirely attributable to
measured confounding. The direction and approximate magnitude were stable across
120 analytic specifications and 13 pre-specified subgroups, and a differently
defined estimand estimated by a doubly robust method recovered its own known
target to within 0.003.

The agreement with the randomised estimate should be read narrowly. It shows
that when confounding is measured, the workflow can remove it. It does not show
that the workflow removes confounding in general, because here the covariates
that generate the confounding are exactly the covariates available for
adjustment. That condition was designed into the data and cannot be verified in
any real dataset.

### Limitations

1. **The data are entirely synthetic.** No result here is evidence about any
   drug. The cohort exists to make the true effect knowable.
2. **No unmeasured confounding holds by construction.** Real observational data
   offer no such guarantee, and no sensitivity analysis presented here can
   detect a confounder that was never recorded.
3. **256 treated patients (26.6%) were left unmatched**, so the estimand is an
   effect in the matchable treated, and generalisation beyond that group is not
   supported.
4. **The Cox models in the matched cohort do not account for pair clustering.**
   Confidence intervals are therefore likely to be slightly narrow.
5. **Subgroups were not re-checked for balance within stratum**, and no
   interaction tests were performed. The subgroup analysis supports a claim of
   consistency only.
6. **The progression-free survival estimate (0.632) is further from the overall
   survival estimate (0.578) than a shared treatment effect would imply.** We do
   not quote a true value for progression-free survival: unlike the 12-month risk
   difference, it is not computed by any script here, so it could not be audited
   and has been removed rather than asserted.
7. **Only 63% of the 120 specifications fell within 0.55 to 0.61**, and the full
   range was 0.480 to 0.716. The conclusion is directionally robust; the point
   estimate is not as stable as a single headline number implies.
8. **Continuous alpha-fetoprotein was never modelled**, because three of ten
   sites do not record it. The binary threshold discards information that a
   real analysis with complete data would use.

---

## Conclusions

In this synthetic multicentre cohort, propensity-score matching on measured
confounders recovered a hazard ratio consistent with the randomised benchmark,
whereas the unadjusted comparison did not. The finding that transfers is the
procedure — a pinned harmonisation specification, a pre-declared matching rule,
an honest count of unmatched patients, a specification curve, and numbers that a
script can trace back to the files that produced them — rather than the estimate
itself.

---

## Declarations

**Data and code availability.** The generator, the harmonisation and analysis
scripts, and the acceptance checks are in the repository; every figure and every
number in this report is reproduced by rerunning them.

**Funding.** None.

**Conflicts of interest.** None declared.

---

## References

1. Finn RS, Qin S, Ikeda M, et al. Atezolizumab plus bevacizumab in unresectable
   hepatocellular carcinoma. *N Engl J Med*. 2020;382(20):1894-1905.
   doi:10.1056/NEJMoa1915745
2. Austin PC. An introduction to propensity score methods for reducing the
   effects of confounding in observational studies. *Multivariate Behav Res*.
   2011;46(3):399-424. doi:10.1080/00273171.2011.568786
3. Austin PC. Optimal caliper widths for propensity-score matching when
   estimating differences in means and differences in proportions in
   observational studies. *Pharm Stat*. 2011;10(2):150-161. doi:10.1002/pst.433
4. Steegen S, Tuerlinckx F, Gelman A, Vanpaemel W. Increasing transparency
   through a multiverse analysis. *Perspect Psychol Sci*. 2016;11(5):702-712.
   doi:10.1177/1745691616658637
5. Simonsohn U, Simmons JP, Nelson LD. Specification curve analysis. *Nat Hum
   Behav*. 2020;4(11):1208-1214. doi:10.1038/s41562-020-0912-z
6. van der Laan MJ, Rubin D. Targeted maximum likelihood learning. *Int J
   Biostat*. 2006;2(1):Article 11. doi:10.2202/1557-4679.1043
7. von Elm E, Altman DG, Egger M, et al. The Strengthening the Reporting of
   Observational Studies in Epidemiology (STROBE) statement: guidelines for
   reporting observational studies. *Lancet*. 2007;370(9596):1453-1457.
   doi:10.1016/S0140-6736(07)61602-X
8. Benchimol EI, Smeeth L, Guttmann A, et al. The REporting of studies Conducted
   using Observational Routinely-collected health Data (RECORD) statement.
   *PLoS Med*. 2015;12(10):e1001885. doi:10.1371/journal.pmed.1001885
9. Hernán MA, Robins JM. Using big data to emulate a target trial when a
   randomized trial is not available. *Am J Epidemiol*. 2016;183(8):758-764.
   doi:10.1093/aje/kwv254
10. Austin PC. Balance diagnostics for comparing the distribution of baseline
    covariates between treatment groups in propensity-score matched samples.
    *Stat Med*. 2009;28(25):3083-3107. doi:10.1002/sim.3697

---

## Figure legends

**Figure 1.** Absolute standardised mean differences for the 11 propensity-score
covariates before and after matching, with a reference line at 0.10.

**Figure 2.** Kaplan-Meier estimates of overall survival in the matched cohort,
with numbers at risk.

**Figure 3.** Hazard ratios for death in 13 pre-specified subgroups; marker area
is proportional to subgroup size and the dotted line marks the overall estimate.

**Figure 4.** Specification curve over 120 analyses, sorted by hazard ratio, with
the randomised benchmark (0.58) and the unadjusted estimate (0.505) marked.
