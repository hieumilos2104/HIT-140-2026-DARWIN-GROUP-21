# Task 2 - Filtering and sampling
# Source: FBref "Player Miscellaneous Stats", 2026 World Cup
# Run: python task2_filter.py

import pandas as pd
import numpy as np

RAW_FILE = "task2_raw.csv"
MIN_90S  = 2.0    # at least 180 minutes
SAMPLE_N = 40
SEED     = 42

UEFA = ["Austria", "Belgium", "Bosnia–Herz", "Croatia", "Czechia", "England",
        "France", "Germany", "Netherlands", "Norway", "Portugal", "Scotland",
        "Spain", "Sweden", "Switzerland", "Türkiye"]
CONMEBOL = ["Argentina", "Brazil", "Colombia", "Ecuador", "Paraguay", "Uruguay"]

df = pd.read_csv(RAW_FILE)
log = []

# FBref writes squad as 'us United States'
df["Country"] = df["Squad"].str.split(" ", n=1).str[1]
df["Confederation"] = np.where(df["Country"].isin(UEFA), "UEFA",
                        np.where(df["Country"].isin(CONMEBOL), "CONMEBOL", "Other"))

print(f"Raw data: {len(df)} players, {df['Squad'].nunique()} teams\n")


# --- Filtering ---
work = df.copy()

def apply_filter(name, condition, mask, reason):
    global work
    before = len(work)
    work = work[mask].copy()
    log.append({"Step": name, "Condition": condition,
                "Remaining": len(work), "Removed": before - len(work),
                "Reason": reason})
    print(f"  {name:<34} {before:>5} -> {len(work):>5}")

apply_filter("1. Remove duplicates", "drop_duplicates()",
             ~work.duplicated(subset=["Player", "Squad"]),
             "Avoid counting a player twice")

apply_filter("2. Keep UEFA and CONMEBOL", "Confederation != 'Other'",
             work["Confederation"] != "Other",
             "Scope of the study")

apply_filter("3. Remove goalkeepers", "Pos not contains 'GK'",
             ~work["Pos"].str.contains("GK", na=False),
             "Goalkeepers rarely tackle")

apply_filter("4. Remove low playing time", f"90s >= {MIN_90S}",
             work["90s"] >= MIN_90S,
             "Small denominators distort the rate")

apply_filter("5. Remove missing values", "dropna(TklW, 90s)",
             work[["TklW", "90s"]].notna().all(axis=1),
             "Rate not computable")


# --- Derived variable ---
work["TklW_90"]  = (work["TklW"] / work["90s"]).round(3)
work["Pos_main"] = work["Pos"].str[:2]


# --- Population ---
pop = work.reset_index(drop=True)
pop.insert(0, "No", range(1, len(pop) + 1))
N = len(pop)

print(f"\nPOPULATION  N = {N}   mu = {pop['TklW_90'].mean():.3f}"
      f"   sigma = {pop['TklW_90'].std(ddof=0):.3f}")
for k, v in pop["Confederation"].value_counts().items():
    sub = pop[pop.Confederation == k]["TklW_90"]
    print(f"  {k:<10} N={v:>3}  mean={sub.mean():.3f}  std={sub.std(ddof=1):.3f}")


# --- Simple random sampling ---
sample = pop.sample(n=SAMPLE_N, random_state=SEED)

print(f"\nSAMPLE      n = {len(sample)}   x_bar = {sample['TklW_90'].mean():.3f}"
      f"   s = {sample['TklW_90'].std(ddof=1):.3f}")
for k, v in sample["Confederation"].value_counts().items():
    sub = sample[sample.Confederation == k]["TklW_90"]
    print(f"  {k:<10} n={v:>3}  mean={sub.mean():.3f}  std={sub.std(ddof=1):.3f}")

n1 = (sample.Confederation == "UEFA").sum()
n2 = (sample.Confederation == "CONMEBOL").sum()
if min(n1, n2) < 10:
    print(f"\n! Smaller group has only {min(n1,n2)} players - limits statistical power.")


# --- Export ---
cols = ["No", "Player", "Country", "Confederation", "Pos", "Pos_main",
        "90s", "TklW", "TklW_90"]

pop[cols].to_csv("task2_population.csv", index=False)
sample[cols].sort_values("TklW_90", ascending=False).to_csv("task2_sample_40.csv", index=False)
pd.DataFrame(log).to_csv("task2_cleaning_log.csv", index=False)

print("\nSaved: task2_population.csv, task2_sample_40.csv, task2_cleaning_log.csv")
