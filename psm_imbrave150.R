# PSM + survival on the 10-hospital observational cohort (R version).
# Requires: MatchIt, survival, (optional) cobalt for Love plots.
#   install.packages(c("MatchIt","survival","cobalt"))
library(MatchIt); library(survival)

# The 10 hospital files use 3 different schemas; harmonise then pool.
# (Simplest path in R: let Python's reference harmoniser write the pooled file,
#  or reproduce the mapping here. We read the pooled output for brevity.)
#   python harmonize_hospitals.py   # -> imbrave150_pooled.csv
df <- read.csv("imbrave150_pooled.csv", stringsAsFactors = TRUE)
meta <- read.csv("hospitals_meta.csv")[, c("hospital_id","hospital_region")]
df <- merge(df, meta, by = "hospital_id", all.x = TRUE)
df$treat <- as.integer(df$arm == "Atezo+Bev")
df$bclc_C   <- as.integer(df$bclc_stage == "C")
df$albi_ge2 <- as.integer(df$albi_grade >= 2)
df$asia     <- as.integer(df$hospital_region == "Asia excluding Japan")

# ---- 1. Naive, unadjusted (biased) ----
cat("Naive OS HR:\n")
print(summary(coxph(Surv(os_time_months, os_event) ~ treat, df))$conf.int)

# ---- 2-3. Propensity score + 1:1 nearest-neighbour caliper matching ----
f <- treat ~ age + ecog_ps + child_pugh_score + afp_ge_400 +
     macrovascular_invasion + extrahepatic_spread + bclc_C +
     albi_ge2 + varices_at_baseline + sex + asia
mo <- matchit(f, data = df, method = "nearest", distance = "glm",
              caliper = 0.2, ratio = 1)

# ---- 4. Balance ----
print(summary(mo))                       # Std. Mean Diff before/after
md <- match.data(mo)

# ---- 5. Survival on matched cohort (recovers HR ~0.58) ----
cat("\nMatched OS HR:\n")
print(summary(coxph(Surv(os_time_months, os_event) ~ treat,
                    data = md, weights = weights))$conf.int)
cat("Matched PFS HR:\n")
print(summary(coxph(Surv(pfs_time_months, pfs_event) ~ treat,
                    data = md, weights = weights))$conf.int)

# Optional balance ("Love") plot:
# library(cobalt); love.plot(mo, thresholds = c(m = .1))
