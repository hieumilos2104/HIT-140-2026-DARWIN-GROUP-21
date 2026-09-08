import numpy as np
import pandas as pd
import scipy.stats as stats

# ==============================================================================
# CONFIGURATION & DATA LOADING
# ==============================================================================
# File name of your sample dataset
DATA_FILE = "Shooting Stat_40 random samples (updated v2).csv"

# Load the dataset
df = pd.read_csv(DATA_FILE)

# Identify column names (adjust if your confederation column name is different)
# Options: 'Conf', 'Confederation', 'Squad', etc.
CONF_COL = "Federation"
GOALS_COL = "Gls"
SHOTS_COL = "Sh"

# ==============================================================================
# STEP 2 & 3: DATA WRANGLING & PREPARATION
# ==============================================================================
# Filter out players with 0 shots taken to avoid division by zero
df_clean = df[df[SHOTS_COL] > 0].copy()

# Feature construction: Goals per Shot conversion ratio
df_clean["conversion_ratio"] = df_clean[GOALS_COL] / df_clean[SHOTS_COL]

print(f"Loaded {len(df_clean)} valid samples across confederations.\n")

# ==============================================================================
# STEP 4: DESCRIPTIVE STATISTICS
# ==============================================================================
desc_stats = df_clean.groupby(CONF_COL)["conversion_ratio"].agg(
    Count="count",
    Mean="mean",
    Median="median",
    Std_Dev="std",
    Min="min",
    Max="max",
    IQR=lambda x: x.quantile(0.75) - x.quantile(0.25),
)

# Format to 4 decimal places for presentation
desc_stats_formatted = desc_stats.round(4)
print("=== DESCRIPTIVE STATISTICS BY CONFEDERATION ===")
print(desc_stats_formatted)
print("-" * 50)

# Export descriptive statistics to CSV
desc_stats_formatted.to_csv("descriptive_stats_output.csv")

# ==============================================================================
# STEP 5: INFERENTIAL STATISTICS — 95% CONFIDENCE INTERVALS
# ==============================================================================
ci_results = []

for group, group_data in df_clean.groupby(CONF_COL):
    data = group_data["conversion_ratio"]
    n = len(data)
    mean = data.mean()
    std = data.std(ddof=1)

    # 95% Confidence Interval using Student's t-distribution
    ci_lower, ci_upper = stats.t.interval(
        confidence=0.95, df=n - 1, loc=mean, scale=std / np.sqrt(n)
    )

    ci_results.append(
        {
            "Confederation": group,
            "Sample_Size": n,
            "Mean_Conversion_Ratio": round(mean, 4),
            "Std_Dev": round(std, 4),
            "95%_CI_Lower": round(ci_lower, 4),
            "95%_CI_Upper": round(ci_upper, 4),
        }
    )

ci_df = pd.DataFrame(ci_results)
print("=== 95% CONFIDENCE INTERVALS ===")
print(ci_df.to_string(index=False))
print("-" * 50)

# ==============================================================================
# STEP 6: INFERENTIAL STATISTICS — INDEPENDENT TWO-SAMPLE t-TEST
# ==============================================================================
# Separate conversion ratios for UEFA and CONMEBOL
uefa_ratios = df_clean[df_clean[CONF_COL] == "UEFA"]["conversion_ratio"]
conmebol_ratios = df_clean[df_clean[CONF_COL] == "CONMEBOL"][
    "conversion_ratio"
]

# Conduct Welch's t-test (two-tailed, unequal variance)
t_stat, p_value = stats.ttest_ind(conmebol_ratios, uefa_ratios, equal_var=False)

alpha = 0.05
decision = (
    "Reject Null Hypothesis (H0)"
    if p_value < alpha
    else "Fail to Reject Null Hypothesis (H0)"
)

print("=== TWO-SAMPLE t-TEST RESULTS (CONMEBOL vs UEFA) ===")
print(f"t-statistic: {t_stat:.4f}")
print(f"p-value:     {p_value:.4f}")
print(f"Significance Level (alpha): {alpha}")
print(f"Decision:    {decision}")
print("-" * 50)

# Save combined inferential test results into a single CSV
inferential_df = ci_df.copy()
inferential_df["t_stat_CONMEBOL_vs_UEFA"] = round(t_stat, 4)
inferential_df["p_value"] = round(p_value, 4)
inferential_df["Test_Decision"] = decision
inferential_df.to_csv("inferential_stats_output.csv", index=False)

print("Analysis complete! Outputs saved to:")
print(" - 'descriptive_stats_output.csv'")
print(" - 'inferential_stats_output.csv'")