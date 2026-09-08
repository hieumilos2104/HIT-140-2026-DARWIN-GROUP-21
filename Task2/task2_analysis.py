# Task 2 - Descriptive statistics, confidence interval, two-sample t-test
# Run: python task2_analysis.py

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

POP_FILE = "task2_population.csv"
SAMPLE_N = 40
SEED     = 42
ALPHA    = 0.05

pop    = pd.read_csv(POP_FILE)
sample = pop.sample(n=SAMPLE_N, random_state=SEED)
x      = sample["TklW_90"]
N, n   = len(pop), len(sample)


# =====================================================================
# SKILL 4 - DESCRIPTIVE STATISTICS
# =====================================================================
print("=" * 60)
print("SKILL 4 - DESCRIPTIVE STATISTICS")
print("=" * 60)

desc = pd.Series({
    "n": n, "Mean": x.mean(), "Median": x.median(),
    "Mode": x.round(1).mode().iloc[0],
    "Std": x.std(ddof=1), "Variance": x.var(ddof=1),
    "Minimum": x.min(), "Q1": x.quantile(.25),
    "Q3": x.quantile(.75), "Maximum": x.max(),
    "Range": x.max() - x.min(),
    "IQR": x.quantile(.75) - x.quantile(.25),
    "Skewness": x.skew(), "Kurtosis": x.kurt(),
}).round(4)
print(desc.to_string())

# Outliers: 1.5 x IQR rule
q1, q3 = x.quantile(.25), x.quantile(.75)
iqr = q3 - q1
lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
out = sample[(x < lo) | (x > hi)]

print(f"\nOutlier bounds [{lo:.3f} ; {hi:.3f}] - {len(out)} found")
if len(out):
    print(out[["Player","Country","90s","TklW","TklW_90"]].to_string(index=False))
    print("Retained: genuine data, not entry error.")

shape = ("right-skewed" if x.skew() > 0.5 else
         "left-skewed" if x.skew() < -0.5 else "symmetric")
print(f"\nMean {x.mean():.3f} > Median {x.median():.3f} -> {shape} "
      f"(skew = {x.skew():.3f})")
print(f"Players with TklW = 0: {(sample['TklW']==0).sum()} - retained, "
      f"zero is a valid observation")

desc.to_frame("Value").to_csv("task2_descriptive_statistics.csv")

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].hist(x, bins=10, edgecolor="black", color="#5B8FF9")
ax[0].axvline(x.mean(), color="red", ls="--", lw=2, label=f"Mean = {x.mean():.2f}")
ax[0].axvline(x.median(), color="green", ls=":", lw=2, label=f"Median = {x.median():.2f}")
ax[0].set_xlabel("Tackles won per 90 minutes")
ax[0].set_ylabel("Frequency")
ax[0].set_title(f"Distribution of TklW/90  (n = {n})")
ax[0].legend()
ax[1].boxplot(x, vert=False, widths=.5, patch_artist=True,
              boxprops=dict(facecolor="#9AD0F5"))
ax[1].set_xlabel("Tackles won per 90 minutes")
ax[1].set_title("Boxplot")
plt.tight_layout()
plt.savefig("task2_histogram.png", dpi=150)
plt.close()


# =====================================================================
# SKILL 5 - CONFIDENCE INTERVAL
# =====================================================================
print("\n" + "=" * 60)
print("SKILL 5 - CONFIDENCE INTERVAL")
print("=" * 60)

mean, s = x.mean(), x.std(ddof=1)
sem, dfree = stats.sem(x), n - 1

# t-distribution used because population sigma is unknown
print(f"x_bar = {mean:.4f}  s = {s:.4f}  n = {n}  df = {dfree}  SE = {sem:.4f}\n")

rows = []
for conf in (0.90, 0.95, 0.99):
    tc = stats.t.ppf(1 - (1-conf)/2, dfree)
    mg = tc * sem
    rows.append({"Confidence_level": conf, "t_critical": round(tc,4),
                 "Margin_of_error": round(mg,4),
                 "Lower_bound": round(mean-mg,4), "Upper_bound": round(mean+mg,4)})
    print(f"  {conf*100:>3.0f}%  t = {tc:.3f}  margin = {mg:.4f}  "
          f"[{mean-mg:.4f} ; {mean+mg:.4f}]")

pd.DataFrame(rows).to_csv("task2_confidence_intervals.csv", index=False)

tc95 = stats.t.ppf(.975, dfree)
mg95 = tc95 * sem
lo95, hi95 = mean - mg95, mean + mg95
mu = pop["TklW_90"].mean()

print(f"""
95% CI: [{lo95:.3f} ; {hi95:.3f}]

We are 95% confident the population mean lies in this interval.
Correct reading: repeating the sampling process, ~95% of intervals
would contain mu. Mu is a fixed constant, not a random variable.

Validation: true mu = {mu:.3f} -> {'INSIDE' if lo95 <= mu <= hi95 else 'OUTSIDE'} the interval""")

print("\nPosition of the two finalists:")
for c in ["Spain", "Argentina"]:
    v = pop[pop.Country == c]["TklW_90"].mean()
    posn = ("ABOVE" if v > hi95 else "BELOW" if v < lo95 else "WITHIN")
    print(f"  {c:<10} = {v:.3f}  ->  {posn}")


# =====================================================================
# SKILL 6 - TWO-SAMPLE T-TEST
# =====================================================================
print("\n" + "=" * 60)
print("SKILL 6 - TWO-SAMPLE T-TEST")
print("=" * 60)

g1 = sample.loc[sample["Confederation"] == "UEFA", "TklW_90"]
g2 = sample.loc[sample["Confederation"] == "CONMEBOL", "TklW_90"]
n1, n2 = len(g1), len(g2)

print(f"""
H0: mu_UEFA  = mu_CONMEBOL
H1: mu_UEFA != mu_CONMEBOL      alpha = {ALPHA}
""")

print(pd.DataFrame({
    "Group": ["UEFA", "CONMEBOL"],
    "n": [n1, n2],
    "Mean": [g1.mean(), g2.mean()],
    "Std": [g1.std(ddof=1), g2.std(ddof=1)],
}).round(4).to_string(index=False))

# Levene's test decides Student's vs Welch's t-test
lev_s, lev_p = stats.levene(g1, g2)
eq = lev_p > ALPHA
print(f"\nLevene: W = {lev_s:.4f}, p = {lev_p:.4f} -> "
      f"{'equal variances, Student t-test' if eq else 'unequal variances, Welch t-test'}")

t_stat, p_val = stats.ttest_ind(g1, g2, equal_var=eq)
sp = np.sqrt(((n1-1)*g1.var(ddof=1) + (n2-1)*g2.var(ddof=1)) / (n1+n2-2))
d = (g1.mean() - g2.mean()) / sp
dsz = "small" if abs(d) < .5 else "medium" if abs(d) < .8 else "large"
rej = p_val < ALPHA

print(f"""
t = {t_stat:.4f}   p = {p_val:.4f}   Cohen's d = {d:.4f} ({dsz})
Mean difference = {g1.mean()-g2.mean():+.4f}

CONCLUSION
  Statistical : p {'<' if rej else '>'} {ALPHA} -> {'REJECT H0' if rej else 'CANNOT REJECT H0'}
  Plain       : {'' if rej else 'No '}statistical evidence of a difference between
                European and South American players.
  Football    : UEFA {g1.mean():.3f} vs CONMEBOL {g2.mean():.3f}.""")

if rej:
    print("""                Higher tackle counts reflect playing style rather than
                defensive quality - sides that control possession
                contest fewer defensive duels.""")
else:
    print(f"""                The difference of {abs(g1.mean()-g2.mean()):.3f} is small relative to sample
                variability. CONMEBOL group has only n = {n2}, which
                reduces statistical power.""")

print(f"""
Note: {'Rejecting H0 does not prove H1 with certainty.'
       if rej else 'Failing to reject H0 does not prove H0 is true.'}

Assumptions
  Independence  : each player in one group only        -> MET
  Normality     : n1 = {n1}, n2 = {n2}                        -> {'MET' if min(n1,n2)>=15 else 'CAUTION'}
  Equal variance: checked with Levene                  -> HANDLED
""")

pd.DataFrame([{
    "Group_1":"UEFA", "n_1":n1, "mean_1":round(g1.mean(),4),
    "std_1":round(g1.std(ddof=1),4),
    "Group_2":"CONMEBOL", "n_2":n2, "mean_2":round(g2.mean(),4),
    "std_2":round(g2.std(ddof=1),4),
    "Levene_W":round(lev_s,4), "Levene_p":round(lev_p,4),
    "equal_variance":eq, "t_statistic":round(t_stat,4),
    "p_value":round(p_val,4), "alpha":ALPHA,
    "Cohens_d":round(d,4), "reject_H0":rej,
}]).to_csv("task2_ttest_results.csv", index=False)

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
ax[0].boxplot([g1, g2], tick_labels=["UEFA", "CONMEBOL"],
              patch_artist=True, boxprops=dict(facecolor="#FFD666"))
ax[0].set_ylabel("Tackles won per 90")
ax[0].set_title("Distribution by confederation")
ax[1].bar(["UEFA", "CONMEBOL"], [g1.mean(), g2.mean()],
          yerr=[stats.sem(g1)*stats.t.ppf(.975, max(n1-1,1)),
                stats.sem(g2)*stats.t.ppf(.975, max(n2-1,1))],
          capsize=8, color=["#5B8FF9", "#5AD8A6"], edgecolor="black")
ax[1].set_ylabel("Mean tackles won per 90")
ax[1].set_title("Group means with 95% CI")
plt.tight_layout()
plt.savefig("task2_ttest.png", dpi=150)
plt.close()

print("Saved: task2_descriptive_statistics.csv, task2_confidence_intervals.csv,")
print("       task2_ttest_results.csv, task2_histogram.png, task2_ttest.png")
