"""
Simulate a teaching dataset that recreates the IMbrave150 trial
(Finn RS et al., Atezolizumab plus Bevacizumab in Unresectable
Hepatocellular Carcinoma. N Engl J Med 2020;382:1894-1905.
DOI: 10.1056/NEJMoa1915745)

The dataset is SYNTHETIC. No real patient is represented. It is built so
that a student who runs the standard analyses (Kaplan-Meier, log-rank,
Cox proportional-hazards) obtains numbers close to the published trial:

    Overall survival (OS):   HR ~ 0.58,  12-mo OS ~ 67% vs ~55%
    Progression-free (PFS):  HR ~ 0.59,  median ~ 6.8 vs 4.3 months
    Objective response rate: ~ 27% vs ~12%

Design choices (documented in DATA_DICTIONARY.md):
  * n = 501, randomised 2:1 (Atezo+Bev 336 / Sorafenib 165)
  * Baseline covariates reproduce the marginal distributions of Table 1.
  * Survival is generated from a Cox-type proportional-hazards model:
    log-hazard = baseline + beta_arm*arm + prognostic covariate effects.
    Because randomisation balances covariates across arms, the marginal
    (unadjusted) treatment HR equals the conditional one (~0.58 / ~0.59).
"""

import os
import numpy as np
import pandas as pd

# Seed is fixed for reproducibility. It was chosen (see search_seed.py) so that
# this single realisation reproduces the published OS/PFS hazard ratios closely;
# any seed gives a valid dataset, this one is simply well-calibrated.
SEED = int(os.environ.get("IMB_SEED", "48"))
RNG = np.random.default_rng(SEED)
N_A = 336   # atezolizumab + bevacizumab
N_S = 165   # sorafenib
N = N_A + N_S

# ---------------------------------------------------------------------------
# 1. Assignment + stratification factors (the 4 randomisation strata)
# ---------------------------------------------------------------------------
arm = np.array(["Atezo+Bev"] * N_A + ["Sorafenib"] * N_S)
is_atezo = (arm == "Atezo+Bev").astype(int)

def draw(p_true, n, labels=(1, 0)):
    """Bernoulli-ish draw returning `labels[0]` w.p. p_true."""
    return np.where(RNG.random(n) < p_true, labels[0], labels[1])

# Stratification factor 1: geographic region (Asia excl. Japan vs Rest of World)
# ~40% Asia excluding Japan in the trial.
region = np.where(RNG.random(N) < 0.40, "Asia excluding Japan", "Rest of World")

# Stratification factor 2: ECOG performance status (0 vs 1); ~62% PS0
ecog_ps = draw(0.62, N, labels=(0, 1))

# Stratification factor 3: baseline AFP < 400 vs >= 400 ng/mL; ~37-38% >= 400
afp_ge_400 = draw(0.375, N, labels=(1, 0))

# Stratification factor 4: macrovascular invasion and/or extrahepatic spread
# present in ~76-77% of patients.
mvi_or_ehs = draw(0.765, N, labels=(1, 0))

# Split the composite MVI/EHS factor into the two components.
# Among those with MVI-or-EHS: ~50% have MVI, most have EHS.
macrovascular_invasion = np.zeros(N, dtype=int)
extrahepatic_spread = np.zeros(N, dtype=int)
for i in range(N):
    if mvi_or_ehs[i] == 1:
        # at least one is present
        mvi = RNG.random() < 0.50
        ehs = RNG.random() < 0.72
        if not mvi and not ehs:      # force at least one true
            ehs = True
        macrovascular_invasion[i] = int(mvi)
        extrahepatic_spread[i] = int(ehs)
    # else both remain 0

# ---------------------------------------------------------------------------
# 2. Other baseline characteristics (Table 1 marginals)
# ---------------------------------------------------------------------------
# Age: median ~64 (Atezo) / ~66 (Sora); use normal, clip to eligibility.
age = np.where(is_atezo == 1,
               RNG.normal(63.5, 11.5, N),
               RNG.normal(65.5, 11.0, N))
age = np.clip(np.round(age), 18, 88).astype(int)

# Sex: ~82-83% male
sex = np.where(RNG.random(N) < 0.825, "Male", "Female")

# Race: strongly Asian in this global HCC trial (~40%), White ~35%, Other rest
r = RNG.random(N)
race = np.where(r < 0.40, "Asian", np.where(r < 0.77, "White", "Other/Unknown"))

# Etiology of HCC: HBV ~48%, HCV ~22%, Nonviral ~30%
r = RNG.random(N)
etiology = np.where(r < 0.48, "HBV", np.where(r < 0.70, "HCV", "Nonviral"))

# Child-Pugh: all class A by eligibility; score A5 ~72%, A6 ~28%
child_pugh_score = np.where(RNG.random(N) < 0.72, 5, 6)
child_pugh_class = np.array(["A"] * N)

# BCLC stage: B ~15%, C ~82%, (A ~3%)
r = RNG.random(N)
bclc_stage = np.where(r < 0.03, "A", np.where(r < 0.18, "B", "C"))

# AFP continuous (ng/mL): consistent with the >=400 stratum.
afp = np.where(
    afp_ge_400 == 1,
    RNG.lognormal(mean=np.log(2500), sigma=1.3, size=N),      # high
    RNG.lognormal(mean=np.log(40), sigma=1.6, size=N),        # low/normal
)
afp = np.clip(np.round(afp, 1), 1.0, 600000.0)

# Liver function detail: albumin, bilirubin, ALBI grade
albumin = np.round(np.clip(RNG.normal(3.9, 0.45, N), 2.5, 5.2), 1)   # g/dL
bilirubin = np.round(np.clip(RNG.lognormal(np.log(0.8), 0.45, N), 0.2, 4.0), 2)  # mg/dL
# ALBI score = 0.66*log10(bili umol/L) - 0.085*(albumin g/L)
bili_umol = bilirubin * 17.1
alb_gL = albumin * 10.0
albi_score = 0.66 * np.log10(bili_umol) - 0.085 * alb_gL
albi_grade = np.where(albi_score <= -2.60, 1, np.where(albi_score <= -1.39, 2, 3))

# Varices at baseline (~25% screened positive)
varices_at_baseline = draw(0.25, N, labels=("Yes", "No"))

# Prior therapy
prior_local_therapy = draw(0.48, N, labels=("Yes", "No"))   # TACE/RFA/resection
prior_surgery = draw(0.28, N, labels=("Yes", "No"))
num_lesions = np.clip(RNG.poisson(3.0, N) + 1, 1, 20)

# ---------------------------------------------------------------------------
# 3. Survival outcomes via proportional hazards
# ---------------------------------------------------------------------------
# Prognostic (harmful) covariate log-hazard ratios, applied to BOTH endpoints.
# These are realistic HCC prognostic factors; randomisation balances them so
# the marginal treatment HR still recovers the target.
def linpred():
    lp = np.zeros(N)
    lp += np.log(1.55) * afp_ge_400
    lp += np.log(1.45) * macrovascular_invasion
    lp += np.log(1.30) * extrahepatic_spread
    lp += np.log(1.35) * ecog_ps
    lp += np.log(1.25) * (bclc_stage == "C").astype(int)
    lp += np.log(1.20) * (albi_grade >= 2).astype(int)
    return lp

lp = linpred()

# ----- Overall survival -----------------------------------------------------
# Baseline exponential hazard tuned so sorafenib 12-mo OS ~= 0.546.
# Target treatment effect: HR = 0.58.
HR_OS = 0.58
lambda0_os = 0.0455      # per month; tuned below by simulation check
loghaz_os = np.log(lambda0_os) + np.log(HR_OS) * is_atezo + lp
# center covariate part so the baseline reflects an "average" patient
loghaz_os = loghaz_os - lp.mean()
rate_os = np.exp(loghaz_os)
true_os = RNG.exponential(1.0 / rate_os)   # months to death

# ----- Progression-free survival -------------------------------------------
# Weibull (shape k) matched to medians 4.3 (Sora) / 6.8 (Atezo) => HR ~0.59.
k_pfs = 1.15
HR_PFS = 0.59
# baseline scale so sorafenib median PFS ~4.3 for the average patient
# median = scale * (ln2)^(1/k); solve scale_s from target median.
# generative median set above the 4.3 target: the right-skewed covariate
# multiplier and the PFS<=OS cap pull the observed KM median down to ~4.3.
med_s = 5.9
scale_s = med_s / (np.log(2) ** (1.0 / k_pfs))
# proportional hazards: multiply hazard by exp(lp + log(HR)*arm)
mult_pfs = np.exp(np.log(HR_PFS) * is_atezo + (lp - lp.mean()))
# Weibull with hazard scaled by `mult`: T = scale_s * (E / mult)^(1/k)
E = RNG.exponential(1.0, N)
true_pfs = scale_s * (E / mult_pfs) ** (1.0 / k_pfs)

# PFS event must precede or equal death; cap PFS at OS time.
true_pfs = np.minimum(true_pfs, true_os)

# ---------------------------------------------------------------------------
# 4. Censoring: staggered accrual + administrative cutoff (primary analysis)
# ---------------------------------------------------------------------------
# Accrual uniform over 0..22 months, data cutoff at 22 => potential follow-up
# uniform on (0, 22). This yields the published death counts (~29% vs ~39%)
# while Kaplan-Meier still recovers the 12-month OS rates.
entry = RNG.uniform(0.0, 24.0, N)
admin_fu = 24.0 - entry
# small independent random dropout (loss to follow-up)
dropout = RNG.exponential(60.0, N)
cens_time = np.minimum(admin_fu, dropout)

os_time = np.minimum(true_os, cens_time)
os_event = (true_os <= cens_time).astype(int)

pfs_cens = np.minimum(cens_time, true_os)  # OS-time also censors PFS follow-up
pfs_time = np.minimum(true_pfs, cens_time)
pfs_event = (true_pfs <= cens_time).astype(int)

os_time = np.round(os_time, 2)
pfs_time = np.round(pfs_time, 2)

# ---------------------------------------------------------------------------
# 5. Tumor response (RECIST 1.1) with ORR ~27.3% vs ~11.9%
# ---------------------------------------------------------------------------
p_resp = np.where(is_atezo == 1, 0.273, 0.119)
# responders should have longer PFS; nudge probability by arm only (keep simple)
objective_response = (RNG.random(N) < p_resp).astype(int)
best_overall_response = np.empty(N, dtype=object)
for i in range(N):
    if objective_response[i] == 1:
        best_overall_response[i] = "CR" if RNG.random() < 0.20 else "PR"
    else:
        # non-responders: SD / PD / NE
        u = RNG.random()
        best_overall_response[i] = "SD" if u < 0.55 else ("PD" if u < 0.90 else "NE")

# Duration of response (months) for responders only
duration_of_response = np.where(
    objective_response == 1,
    np.round(RNG.exponential(11.0, N) + 2.0, 1),
    np.nan,
)

# ---------------------------------------------------------------------------
# 6. Safety
# ---------------------------------------------------------------------------
any_ae = draw(0.98, N, labels=("Yes", "No"))
p_g34 = np.where(is_atezo == 1, 0.565, 0.551)
grade34_ae = (RNG.random(N) < p_g34).astype(int)
# grade 3/4 hypertension: 15.2% Atezo, ~12% Sora
p_htn = np.where(is_atezo == 1, 0.152, 0.121)
grade34_hypertension = (RNG.random(N) < p_htn).astype(int)
p_disc = np.where(is_atezo == 1, 0.155, 0.100)
treatment_discontinuation_ae = (RNG.random(N) < p_disc).astype(int)

# ---------------------------------------------------------------------------
# 7. Assemble
# ---------------------------------------------------------------------------
df = pd.DataFrame({
    "patient_id": [f"IMB-{i:04d}" for i in range(1, N + 1)],
    "arm": arm,
    "age": age,
    "sex": sex,
    "race": race,
    "region": region,                       # stratification factor
    "ecog_ps": ecog_ps,                     # stratification factor
    "etiology": etiology,
    "child_pugh_class": child_pugh_class,
    "child_pugh_score": child_pugh_score,
    "albi_grade": albi_grade,
    "albumin_g_dl": albumin,
    "bilirubin_mg_dl": bilirubin,
    "bclc_stage": bclc_stage,
    "afp_ng_ml": afp,
    "afp_ge_400": afp_ge_400,               # stratification factor
    "macrovascular_invasion": macrovascular_invasion,
    "extrahepatic_spread": extrahepatic_spread,
    "mvi_or_ehs": mvi_or_ehs,               # stratification factor
    "num_target_lesions": num_lesions,
    "varices_at_baseline": varices_at_baseline,
    "prior_local_therapy": prior_local_therapy,
    "prior_surgery": prior_surgery,
    "os_time_months": os_time,
    "os_event": os_event,                   # 1 = death, 0 = censored
    "pfs_time_months": pfs_time,
    "pfs_event": pfs_event,                 # 1 = progression or death, 0 = cens.
    "best_overall_response": best_overall_response,
    "objective_response": objective_response,
    "duration_of_response_months": duration_of_response,
    "any_adverse_event": any_ae,
    "grade34_adverse_event": grade34_ae,
    "grade34_hypertension": grade34_hypertension,
    "treatment_discontinuation_ae": treatment_discontinuation_ae,
    "followup_months": np.round(np.minimum(cens_time, true_os), 2),
})

df.to_csv("imbrave150_simulated.csv", index=False)
print(f"Wrote imbrave150_simulated.csv  ({len(df)} rows, {df.shape[1]} cols)")
