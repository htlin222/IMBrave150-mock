# Reproduce IMbrave150 key results from the simulated dataset (R version).
# Requires: survival (base R recommends), optionally survminer for plots.
#   install.packages("survival")
library(survival)

df <- read.csv("imbrave150_simulated.csv", stringsAsFactors = TRUE)
df$arm <- relevel(df$arm, ref = "Sorafenib")   # Sorafenib = reference

cat("==== OVERALL SURVIVAL ====\n")
os_fit <- survfit(Surv(os_time_months, os_event) ~ arm, data = df)
print(summary(os_fit, times = 12)$surv)                 # 12-month OS per arm
cox_os <- coxph(Surv(os_time_months, os_event) ~ arm, data = df)
print(summary(cox_os)$conf.int)                          # HR + 95% CI (paper 0.58)
print(survdiff(Surv(os_time_months, os_event) ~ arm, data = df))  # log-rank

cat("\n==== PROGRESSION-FREE SURVIVAL ====\n")
pfs_fit <- survfit(Surv(pfs_time_months, pfs_event) ~ arm, data = df)
print(pfs_fit)                                           # medians (paper 6.8 / 4.3)
cox_pfs <- coxph(Surv(pfs_time_months, pfs_event) ~ arm, data = df)
print(summary(cox_pfs)$conf.int)                         # HR (paper 0.59)

cat("\n==== OBJECTIVE RESPONSE ====\n")
print(round(tapply(df$objective_response, df$arm, mean) * 100, 1))  # ORR %

cat("\n==== MULTIVARIABLE COX (OS) ====\n")
cox_mv <- coxph(Surv(os_time_months, os_event) ~ arm + afp_ge_400 +
                macrovascular_invasion + extrahepatic_spread + ecog_ps,
                data = df)
print(summary(cox_mv)$conf.int)

# Optional KM plot:
# library(survminer); ggsurvplot(os_fit, data = df, risk.table = TRUE,
#   pval = TRUE, xlab = "Months", ylab = "Overall survival")
