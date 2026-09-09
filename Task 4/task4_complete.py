"""
Task 3: Disciplinary rates of UEFA and CONMEBOL players

Research question:
Do players representing UEFA and CONMEBOL teams differ in their mean
disciplinary rate, measured as cards received per 100 fouls committed,
at the 2026 FIFA World Cup?

Data source:
FBref, 2026 World Cup Player Miscellaneous Statistics
https://fbref.com/en/comps/1/2026/misc/2026-World-Cup-Stats

The raw CSV must be manually extracted from FBref and saved in the same
folder as this Python file with the name shown in RAW_FILE_NAME below.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


# --------------------------------------------------
# 1. Settings and file locations
# --------------------------------------------------

FOLDER = Path(__file__).resolve().parent

RAW_FILE_NAME = "fbref_wc2026_player_misc_raw_manual.csv"
CLEANED_FILE_NAME = "fbref_wc2026_player_misc_cleaned.csv"
ELIGIBLE_FILE_NAME = "task3_eligible_players.csv"
SAMPLE_FILE_NAME = "task3_player_stratified_sample_80.csv"
DESCRIPTIVE_FILE_NAME = "task3_descriptive_statistics.csv"
CI_FILE_NAME = "task3_confidence_intervals.csv"
TTEST_FILE_NAME = "task3_ttest_results.csv"
FIGURE_FILE_NAME = "task3_disciplinary_rate_visualisation.png"

SAMPLE_SIZE_PER_GROUP = 40
RANDOM_SEED = 140
CONFIDENCE_LEVEL = 0.95
ALPHA = 0.05

raw_file = FOLDER / RAW_FILE_NAME


# --------------------------------------------------
# 2. Load the manually extracted raw data
# --------------------------------------------------

if not raw_file.exists():
    raise FileNotFoundError(
        f"Cannot find {RAW_FILE_NAME}. "
        "Place the raw CSV in the same folder as this Python file."
    )

players = pd.read_csv(raw_file, sep=";")

# Remove completely empty columns and clean column names.
players = players.dropna(axis=1, how="all")
players.columns = players.columns.str.strip()

required_columns = [
    "Rk",
    "Player",
    "Squad",
    "90s",
    "CrdY",
    "CrdR",
    "2CrdY",
    "Fls",
]

missing_columns = [
    column for column in required_columns
    if column not in players.columns
]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

print("Raw-data shape:", players.shape)
print("Raw-data columns:", players.columns.tolist())


# --------------------------------------------------
# 3. Clean and prepare the data
# --------------------------------------------------

players = players.dropna(subset=["Player", "Squad"]).copy()
players["Player"] = players["Player"].astype(str).str.strip()
players["Squad"] = players["Squad"].astype(str).str.strip()

# Separate the country code from the team name.
players[["Code", "Team"]] = players["Squad"].str.extract(
    r"^(\S+)\s+(.+)$"
)
players["Code"] = players["Code"].str.lower()

numeric_columns = ["90s", "CrdY", "CrdR", "2CrdY", "Fls"]

for column in numeric_columns:
    converted = pd.to_numeric(players[column], errors="coerce")

    invalid_values = converted.isna() & players[column].notna()
    if invalid_values.any():
        bad_values = players.loc[invalid_values, column].unique().tolist()
        raise ValueError(
            f"Non-numeric values found in {column}: {bad_values}"
        )

    players[column] = converted.fillna(0)


# --------------------------------------------------
# 4. Identify UEFA and CONMEBOL players
# --------------------------------------------------

uefa_codes = [
    "at", "be", "ba", "hr", "cz", "eng", "fr", "de",
    "nl", "no", "pt", "sct", "es", "se", "ch", "tr",
]

conmebol_codes = ["ar", "br", "co", "ec", "py", "uy"]

confederation_mapping = {
    code: "UEFA" for code in uefa_codes
}
confederation_mapping.update({
    code: "CONMEBOL" for code in conmebol_codes
})

players["Confederation"] = players["Code"].map(
    confederation_mapping
)

players.to_csv(
    FOLDER / CLEANED_FILE_NAME,
    index=False,
    encoding="utf-8-sig",
)


# --------------------------------------------------
# 5. Define the eligible population and metric
# --------------------------------------------------

# Only UEFA and CONMEBOL players with at least one foul are eligible.
eligible_players = players.loc[
    players["Confederation"].notna()
    & players["Fls"].gt(0)
].copy()

# CrdY already records yellow cards and CrdR records red cards.
# 2CrdY describes red cards caused by a second yellow and is not added
# again because that would double-count this type of dismissal.
eligible_players["Cards_received"] = (
    eligible_players["CrdY"]
    + eligible_players["CrdR"]
)

eligible_players["Cards_per_100_fouls"] = (
    eligible_players["Cards_received"]
    / eligible_players["Fls"]
    * 100
)

eligible_players.to_csv(
    FOLDER / ELIGIBLE_FILE_NAME,
    index=False,
    encoding="utf-8-sig",
)

print("\nEligible population:")
print(eligible_players["Confederation"].value_counts())
print("Total eligible players:", len(eligible_players))


# --------------------------------------------------
# 6. Take and save a stratified random sample
# --------------------------------------------------

group_samples = []

for confederation in ["UEFA", "CONMEBOL"]:
    group_population = eligible_players.loc[
        eligible_players["Confederation"].eq(confederation)
    ]

    if SAMPLE_SIZE_PER_GROUP > len(group_population):
        raise ValueError(
            f"The requested sample for {confederation} is larger "
            "than its eligible population."
        )

    group_sample = group_population.sample(
        n=SAMPLE_SIZE_PER_GROUP,
        random_state=RANDOM_SEED,
    )
    group_samples.append(group_sample)

sample = pd.concat(group_samples, ignore_index=True)

sample.to_csv(
    FOLDER / SAMPLE_FILE_NAME,
    index=False,
    encoding="utf-8-sig",
)

print("\nStratified random sample:")
print(sample["Confederation"].value_counts())
print("Total sample size:", len(sample))


# --------------------------------------------------
# 7. Descriptive statistics
# --------------------------------------------------

outcome = "Cards_per_100_fouls"

descriptive_stats = (
    sample.groupby("Confederation")[outcome]
    .agg(["count", "mean", "median", "std", "min", "max"])
    .rename(columns={
        "count": "Sample_size",
        "mean": "Mean",
        "median": "Median",
        "std": "Standard_deviation",
        "min": "Minimum",
        "max": "Maximum",
    })
    .round(2)
)

descriptive_stats.to_csv(
    FOLDER / DESCRIPTIVE_FILE_NAME,
    encoding="utf-8-sig",
)

print("\nDescriptive statistics:")
print(descriptive_stats)


# --------------------------------------------------
# 8. Confidence intervals for each group mean
# --------------------------------------------------

ci_results = []

for confederation in ["UEFA", "CONMEBOL"]:
    values = sample.loc[
        sample["Confederation"].eq(confederation),
        outcome,
    ]

    n = len(values)
    group_mean = values.mean()
    standard_error = stats.sem(values)
    t_critical = stats.t.ppf(
        (1 + CONFIDENCE_LEVEL) / 2,
        df=n - 1,
    )
    margin_of_error = t_critical * standard_error

    ci_results.append({
        "Confederation": confederation,
        "Sample_size": n,
        "Mean": group_mean,
        "Lower_95_CI": group_mean - margin_of_error,
        "Upper_95_CI": group_mean + margin_of_error,
    })

ci_table = pd.DataFrame(ci_results).round(2)

ci_table.to_csv(
    FOLDER / CI_FILE_NAME,
    index=False,
    encoding="utf-8-sig",
)

print("\n95% confidence intervals:")
print(ci_table)


# --------------------------------------------------
# 9. Welch two-sample t-test
# --------------------------------------------------

uefa_values = sample.loc[
    sample["Confederation"].eq("UEFA"),
    outcome,
]

conmebol_values = sample.loc[
    sample["Confederation"].eq("CONMEBOL"),
    outcome,
]

t_statistic, p_value = stats.ttest_ind(
    uefa_values,
    conmebol_values,
    equal_var=False,
)

uefa_component = uefa_values.var(ddof=1) / len(uefa_values)
conmebol_component = (
    conmebol_values.var(ddof=1) / len(conmebol_values)
)

welch_df = (
    (uefa_component + conmebol_component) ** 2
    / (
        (uefa_component ** 2) / (len(uefa_values) - 1)
        + (conmebol_component ** 2) / (len(conmebol_values) - 1)
    )
)

mean_difference = uefa_values.mean() - conmebol_values.mean()
difference_standard_error = np.sqrt(
    uefa_component + conmebol_component
)
difference_t_critical = stats.t.ppf(0.975, df=welch_df)
difference_margin = (
    difference_t_critical * difference_standard_error
)
difference_lower_ci = mean_difference - difference_margin
difference_upper_ci = mean_difference + difference_margin

if p_value < ALPHA:
    decision = "Reject the null hypothesis."
    conclusion = (
        "There is sufficient evidence of a difference between "
        "UEFA and CONMEBOL players."
    )
else:
    decision = "Fail to reject the null hypothesis."
    conclusion = (
        "There is insufficient evidence of a difference between "
        "UEFA and CONMEBOL players."
    )

test_results = pd.DataFrame([{
    "Test": "Welch two-sample t-test",
    "UEFA_mean": uefa_values.mean(),
    "CONMEBOL_mean": conmebol_values.mean(),
    "Mean_difference_UEFA_minus_CONMEBOL": mean_difference,
    "T_statistic": t_statistic,
    "Degrees_of_freedom": welch_df,
    "P_value": p_value,
    "Lower_95_CI_difference": difference_lower_ci,
    "Upper_95_CI_difference": difference_upper_ci,
    "Decision": decision,
}])

test_results.to_csv(
    FOLDER / TTEST_FILE_NAME,
    index=False,
    encoding="utf-8-sig",
)

print("\nWelch two-sample t-test:")
print(f"T-statistic: {t_statistic:.3f}")
print(f"Degrees of freedom: {welch_df:.2f}")
print(f"P-value: {p_value:.3f}")
print(f"Mean difference (UEFA - CONMEBOL): {mean_difference:.2f}")
print(
    "95% CI for mean difference: "
    f"[{difference_lower_ci:.2f}, {difference_upper_ci:.2f}]"
)
print("Decision:", decision)
print("Conclusion:", conclusion)


# --------------------------------------------------
# 10. Data visualisation
# --------------------------------------------------

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

maximum_rate = sample[outcome].max()
bins = np.arange(0, maximum_rate + 20, 10)

# Density places both distributions on the same comparison scale.
axes[0].hist(
    uefa_values,
    bins=bins,
    density=True,
    alpha=0.65,
    label="UEFA",
    color="royalblue",
    edgecolor="black",
)
axes[0].hist(
    conmebol_values,
    bins=bins,
    density=True,
    alpha=0.65,
    label="CONMEBOL",
    color="darkorange",
    edgecolor="black",
)
axes[0].set_title("Distribution of Disciplinary Rates")
axes[0].set_xlabel("Cards Received per 100 Fouls")
axes[0].set_ylabel("Density")
axes[0].legend()

boxplot = axes[1].boxplot(
    [uefa_values, conmebol_values],
    tick_labels=["UEFA", "CONMEBOL"],
    patch_artist=True,
)
boxplot["boxes"][0].set_facecolor("royalblue")
boxplot["boxes"][1].set_facecolor("darkorange")
axes[1].set_title("Disciplinary Rate by Confederation")
axes[1].set_xlabel("Confederation")
axes[1].set_ylabel("Cards Received per 100 Fouls")

plt.suptitle(
    "UEFA and CONMEBOL Player Comparison",
    fontsize=14,
)
plt.tight_layout()
plt.savefig(
    FOLDER / FIGURE_FILE_NAME,
    dpi=300,
    bbox_inches="tight",
)
plt.show()

print("\nSaved output files:")
for file_name in [
    CLEANED_FILE_NAME,
    ELIGIBLE_FILE_NAME,
    SAMPLE_FILE_NAME,
    DESCRIPTIVE_FILE_NAME,
    CI_FILE_NAME,
    TTEST_FILE_NAME,
    FIGURE_FILE_NAME,
]:
    print("-", file_name)
