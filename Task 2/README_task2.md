# Task 2 — Tackles Won per 90 Minutes

**Analytic task 2 of 4 · 2026 FIFA World Cup**
Europe (UEFA) vs South America (CONMEBOL)

---

## Focal point

This task examines **regaining possession through tackling**. It is
distinct from the other three tasks in the group:

| Task | Phase of play | Metric |
|---|---|---|
| 1 | Attacking efficiency | Goals / shots |
| **2 (this one)** | **Regaining possession** | **Tackles won per 90** |
| 3 | Discipline | Cards / fouls |
| 4 | Retaining possession | Pass completion % |

Tasks 2 and 4 are complementary rather than overlapping: pass accuracy
measures how well a team **keeps** the ball, tackles won measures how
effectively it **gets it back**.

---

## Skill 1 — Analytic question formulation

> On average, how many tackles does a player win per 90 minutes at the
> 2026 World Cup, and does this differ between European and South
> American players? Only players with at least 180 minutes are included.

**Variable**

```
TklW_90 = TklW / 90s
```

`TklW` = tackles won — tackles after which the player's team regained
possession. `90s` = minutes played divided by 90.

**Why this metric.** A tackle won marks the moment a team turns defence
into attack. It captures the half of the possession story that pass
accuracy does not.

**Why normalise per 90 minutes.** A player who appeared in eight matches
accumulates more tackles than one who played two. Dividing by 90-minute
equivalents compares intensity rather than opportunity.

**Why Europe vs South America.** Two football cultures with contrasting
reputations, and both 2026 finalists came from them.

**Expectation.** South American players were expected to record higher
values, on the assumption that European sides control possession more
and therefore contest fewer defensive duels.

---

## Skill 2 — Data wrangling

**Source:** FBref — *Player Miscellaneous Stats*, 2026 World Cup,
exported through the table's "Get table as CSV" function.
1039 players across all 48 teams.

FBref provides no confederation column, so the team-to-confederation
mapping was added in `task2_filter.py` from the official tournament
draw. The `Squad` field is written as `us United States`, so the country
name is split off before matching.

### Cleaning log

| Step | Condition | Remaining | Removed | Reason |
|---|---|---|---|---|
| 0 | raw export | 1039 | — | — |
| 1 | `drop_duplicates()` | 1039 | 0 | avoid double counting |
| 2 | UEFA or CONMEBOL only | 483 | 556 | scope of the study |
| 3 | `Pos` does not contain `GK` | 456 | 27 | goalkeepers rarely tackle |
| 4 | `90s >= 2.0` | 247 | 209 | small denominators distort the rate |
| 5 | `dropna(TklW, 90s)` | 247 | 0 | rate not computable |

Also written to `task2_cleaning_log.csv`.

### Justification of the 180-minute threshold

`TklW_90` is a ratio, so a small denominator makes it unstable:

| Minutes played | One tackle shifts the rate by |
|---|---|
| 18 | 5.00 |
| 90 | 1.00 |
| **180** | **0.50** |
| 360 | 0.25 |

A player appearing for 18 minutes and winning one tackle would score
5.0 per 90 — higher than anyone in the sample. That reflects chance,
not ability.

### What was deliberately **not** removed

51 players in the population recorded `TklW = 0`. These were kept.
Zero is a valid observation — typically a forward in a
possession-dominant side — not missing data. Removing them would
inflate the mean and bias the estimate.

---

## Skill 3 — Data preparation and sampling

**Variables retained:** `Player`, `Country`, `Confederation`, `Pos`,
`90s`, `TklW`, and the derived `TklW_90`.

**Population.** All outfield players from the 22 UEFA and CONMEBOL teams
at the 2026 World Cup who played at least 180 minutes.

```
N     = 247        (UEFA 179, CONMEBOL 68)
mu    = 0.925 tackles won per 90
sigma = 0.683
```

**Sample.**

```
n     = 40         (16.2% of the population)
x_bar = 1.0675
s     = 0.8245
```

**Technique:** simple random sampling via
`pandas.DataFrame.sample(n=40, random_state=42)`.

Every player in the population has an equal probability of selection, so
the sample is not biased towards any team or confederation. The fixed
seed makes the result reproducible — re-running the script returns the
same 40 players.

**Sample size justification.** n = 40 ≥ 30 satisfies the Central Limit
Theorem, so the sampling distribution of the mean is approximately
normal even though the underlying data are right-skewed. This permits
the use of the t-distribution for interval estimation and hypothesis
testing.

---

## Skill 4 — Descriptive statistics

| Statistic | Value |
|---|---|
| n | 40 |
| Mean | 1.0675 |
| Median | 0.9410 |
| Mode | 0.0000 |
| Standard deviation | 0.8245 |
| Variance | 0.6798 |
| Minimum | 0.0000 |
| Q1 | 0.4330 |
| Q3 | 1.4595 |
| Maximum | 3.5000 |
| Range | 3.5000 |
| IQR | 1.0265 |
| Skewness | 0.8733 |
| Kurtosis | 0.8590 |

**Shape.** The mean exceeds the median and skewness is 0.873 — the
distribution is right-skewed. Most players tackle at a low rate while a
small group of defensive midfielders and full-backs record much higher
values.

**Outliers.** Using the 1.5 × IQR rule the bounds are [−1.107 ; 3.000].
One observation (3.500) lies above the upper bound. It was retained: the
value is genuine and reflects a high-duel role, not a data-entry error.

**Visualisation.** `task2_histogram.png` — histogram with mean and median
marked, alongside a boxplot for outlier detection.

Also written to `task2_descriptive_statistics.csv`.

---

## Skill 5 — Confidence interval

The t-distribution is used because the population standard deviation is
unknown and estimated from the sample.

```
x_bar = 1.0675    s = 0.8245    n = 40    df = 39
SE = s / sqrt(n) = 0.1304
CI = x_bar  ±  t(alpha/2, 39) × SE
```

| Confidence | t critical | Margin of error | Interval |
|---|---|---|---|
| 90% | 1.6849 | 0.2196 | [0.8479 ; 1.2872] |
| **95%** | **2.0227** | **0.2637** | **[0.8038 ; 1.3312]** |
| 99% | 2.7079 | 0.3530 | [0.7145 ; 1.4205] |

**Interpretation.** We are 95% confident that the mean number of tackles
won per 90 minutes across all outfield players from the 22 UEFA and
CONMEBOL teams lies between 0.804 and 1.331. The margin of error is
±0.264, or 24.7% of the sample mean.

**Correct reading.** If the sampling process were repeated many times,
approximately 95% of the intervals produced would contain the true
population mean. It is *not* correct to say there is a 95% probability
that μ lies in this interval — μ is a fixed constant; the interval is
what varies from sample to sample.

**Trade-off.** Raising confidence from 90% to 99% widens the interval
from 0.44 to 0.71 units. Greater confidence costs precision.

**Validation.** The true population mean (μ = 0.925) falls inside the
95% interval, as expected.

Also written to `task2_confidence_intervals.csv`.

---

## Skill 6 — Two-sample t-test

**Hypotheses**

```
H0: mu_UEFA  =  mu_CONMEBOL
H1: mu_UEFA !=  mu_CONMEBOL        (two-tailed)
alpha = 0.05
```

**Group statistics**

| Group | n | Mean | Std |
|---|---|---|---|
| UEFA (Europe) | 31 | 1.0338 | 0.8699 |
| CONMEBOL (South America) | 9 | 1.1838 | 0.6758 |

**Equality of variances.** Levene's test gives W = 0.3341, p = 0.5667.
Since p > 0.05 the assumption of equal variances holds, so Student's
t-test is used rather than Welch's.

**Result**

```
t = -0.4757
p =  0.6370
Mean difference = -0.1500
Cohen's d = -0.1801    (small effect)
```

**Conclusion**

*Statistical.* p = 0.637 > α = 0.05 → cannot reject H₀.

*Plain language.* There is no statistical evidence that European and
South American players differ in tackles won per 90 minutes.

*Football context.* South American players averaged 1.18 against
Europe's 1.03, but this difference of 0.15 is small relative to the
variability within each group (standard deviations of 0.87 and 0.68).
The result does not support the expectation stated in Skill 1.

Failing to reject H₀ does not prove that H₀ is true — with only nine
players in the CONMEBOL group, the test may simply lack the power to
detect a real difference.

**Assumptions**

| Assumption | Status |
|---|---|
| Independence | Met — each player belongs to one confederation only |
| Normality | Acceptable — n₁ = 31; n₂ = 9 is small, noted as a limitation |
| Equal variances | Checked with Levene's test |

**Visualisation.** `task2_ttest.png` — boxplots by confederation and
group means with 95% error bars. The heavily overlapping error bars are
the visual counterpart of p = 0.637.

Also written to `task2_ttest_results.csv`.

---

## Contribution to the group question

*Did Argentina deserve the 2026 World Cup title?*

| | Value | Position relative to 95% CI |
|---|---|---|
| 95% CI | [0.804 ; 1.331] | — |
| Spain | 1.111 | within |
| Argentina | 1.076 | within |

Comparing the two finalists directly: t = 0.153, p = 0.880 —
statistically indistinguishable.

**Both finalists were typical of the population on this measure. The
title was not decided in this phase of play.** For a group narrative
that asks whether the result was statistically deserved, this is a
meaningful negative finding: it rules out ball recovery as the
differentiating factor and directs attention to the phases covered by
the other three tasks.

---
