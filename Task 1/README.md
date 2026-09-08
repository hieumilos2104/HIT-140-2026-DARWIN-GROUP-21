# Task 1 — Goals per Shot

**Analytic task 1 of 4 · 2026 FIFA World Cup**
Europe (UEFA) vs South America (CONMEBOL)

---

## Focal point

This task examines **attacking efficiency through shot conversion**. It is distinct from the other three tasks in the group because it focuses on how effectively players convert their shooting opportunities into goals.

| Task             | Phase of play            | Metric             |
| ---------------- | ------------------------ | ------------------ |
| **1 (this one)** | **Attacking efficiency** | **Goals / shots**  |
| 2                | Regaining possession     | Tackles won per 90 |
| 3                | Discipline               | Cards / fouls      |
| 4                | Retaining possession     | Pass completion %  |

The metric measures the proportion of a player's recorded shots that resulted in goals. Unlike total goals, which are strongly influenced by the number of opportunities a player receives, goals per shot measures **efficiency in converting those opportunities**.

---

## Skill 1 — Analytic question formulation

> **On average, what proportion of shots taken by players from UEFA and CONMEBOL result in goals during the 2026 FIFA World Cup, and is there a statistically significant difference in shot-conversion efficiency between the two confederations?**

**Variable**

```text
Conversion_Ratio = Goals / Shots
```

`Goals` = goals scored by the player during the tournament.
`Shots` = total shots attempted by the player, regardless of whether the shot was on or off target.

**Why this metric.** Goals alone do not necessarily indicate shooting efficiency. A player may score several goals because they take many shots, while another player may score fewer goals but convert a larger proportion of their attempts. Dividing goals by total shots provides a measure of how efficiently shooting opportunities are converted.

**Why include both UEFA and CONMEBOL.** UEFA and CONMEBOL represent the two major European and South American football confederations. Comparing players from these groups provides a meaningful cross-confederation comparison of attacking efficiency.

**Expectation.** UEFA players were expected to have a higher average conversion ratio because European teams may provide players with more structured attacking opportunities and potentially higher-quality shooting situations. However, the analysis tests whether any observed difference is statistically significant rather than assuming that the difference is meaningful.

---

## Skill 2 — Data wrangling

The raw FIFA World Cup 2026 player data were first collected and then filtered to retain players belonging to **UEFA and CONMEBOL**.

The analysis focuses on two variables required to calculate shooting efficiency:

* `Goals`
* `Shots`

The conversion ratio was then calculated for each player:

```text
Conversion_Ratio = Goals / Shots
```

The resulting ratio represents the proportion of total shots that resulted in goals.

Players from confederations other than UEFA and CONMEBOL were excluded because the purpose of this analysis is to compare European and South American players.

The data were also checked so that the variables required for the calculation were available before the conversion ratio was analysed.

### Why total shots were used

The analysis uses **all shots taken**, rather than only shots on target. Therefore, both shots on target and shots off target contribute to the denominator.

This is important because the research question concerns overall **shooting conversion efficiency**. Restricting the denominator to shots on target would answer a different question and would exclude unsuccessful attempts that are part of a player's overall shooting performance.

---

## Skill 3 — Data preparation and sampling

The variables retained for the analysis were:

```text
Player
Confederation
Goals
Shots
Conversion_Ratio
```

### Population

The population consists of players from **UEFA and CONMEBOL** represented in the FIFA World Cup 2026 dataset and for whom the goals-to-shots conversion ratio could be calculated.

### Sample

A random sample of **40 players** was selected from the filtered UEFA and CONMEBOL dataset.

```text
n = 40
UEFA = 20
CONMEBOL = 20
```

The sample was therefore evenly divided between the two confederations, allowing the average conversion ratios of UEFA and CONMEBOL players to be compared directly.

A random sampling approach was used so that individual players were not deliberately selected based on their performance. This reduces selection bias and makes the sample more representative of the filtered population.

Because the sample contains 40 players, it provides a reasonable basis for estimating the population mean and conducting the required inferential statistical tests.

---

## Skill 4 — Descriptive statistics

The descriptive statistics for the two confederations are:

| Statistic          | CONMEBOL |   UEFA |
| ------------------ | -------: | -----: |
| n                  |       20 |     20 |
| Mean               |   0.0764 | 0.1192 |
| Median             |   0.0000 | 0.0000 |
| Standard deviation |   0.1599 | 0.2511 |
| Minimum            |   0.0000 | 0.0000 |
| Maximum            |   0.5000 | 1.0000 |
| IQR                |   0.0278 | 0.1250 |

### Mean

The mean conversion ratio for **CONMEBOL players was 0.0764**, meaning that the average player in the sample converted approximately **7.64% of their shots into goals**.

The corresponding mean for **UEFA players was 0.1192**, or approximately **11.92%**.

Therefore, the UEFA sample had a higher average shot-conversion ratio than the CONMEBOL sample.

The difference between the two sample means was:

```text
0.1192 − 0.0764 = 0.0428
```

Thus, the UEFA mean was approximately **4.28 percentage points higher** than the CONMEBOL mean.

### Median

Both groups had a median conversion ratio of **0.0000**.

This indicates that at least half of the sampled players in each confederation had a conversion ratio of zero. In practical terms, these players did not score from their recorded shots.

The difference between the mean and median is therefore important. The means are above zero while the medians are zero, indicating that a relatively small number of players with successful goal conversions have a substantial influence on the average.

### Variability

The UEFA sample had a standard deviation of **0.2511**, compared with **0.1599** for CONMEBOL.

This indicates greater variation in shooting conversion among the sampled UEFA players.

The maximum value also demonstrates this difference. The highest CONMEBOL conversion ratio was **0.5000**, whereas the highest UEFA value was **1.0000**.

The UEFA IQR of **0.1250** was also larger than the CONMEBOL IQR of **0.0278**, showing greater spread in the middle 50% of UEFA observations.

Overall, the descriptive statistics suggest that UEFA players had a higher average conversion ratio, but there was considerable variation within both groups.

---

## Skill 5 — Confidence interval

A 95% confidence interval was calculated separately for the mean conversion ratio of each confederation.

### CONMEBOL

```text
x̄ = 0.0764
95% CI = [0.0015 ; 0.1512]
```

We are **95% confident that the population mean conversion ratio for CONMEBOL players lies between 0.0015 and 0.1512**.

Expressed as percentages, this corresponds to approximately:

```text
0.15% to 15.12%
```

### UEFA

```text
x̄ = 0.1192
95% CI = [0.0016 ; 0.2367]
```

We are **95% confident that the population mean conversion ratio for UEFA players lies between 0.0016 and 0.2367**.

Expressed as percentages, this corresponds to approximately:

```text
0.16% to 23.67%
```

### Interpretation

The UEFA sample mean of **0.1192** is higher than the CONMEBOL sample mean of **0.0764**. However, both confidence intervals are relatively wide and overlap substantially.

This indicates that there is considerable uncertainty around the estimated population means. The confidence intervals therefore do not, by themselves, provide sufficient evidence to conclude that UEFA players have a genuinely higher conversion ratio than CONMEBOL players.

The two-sample t-test is used to formally test whether the observed difference is statistically significant.

---

## Skill 6 — Two-sample t-test

A **two-sample t-test** was conducted to determine whether the mean conversion ratio differs between UEFA and CONMEBOL players.

### Hypotheses

```text
H₀: μ_CONMEBOL = μ_UEFA

H₁: μ_CONMEBOL ≠ μ_UEFA

α = 0.05
```

The null hypothesis states that there is **no difference in the population mean conversion ratio** between CONMEBOL and UEFA players.

The alternative hypothesis states that the population mean conversion ratios are different.

### Group statistics

| Group    |  n |   Mean | Standard deviation |
| -------- | -: | -----: | -----------------: |
| CONMEBOL | 20 | 0.0764 |             0.1599 |
| UEFA     | 20 | 0.1192 |             0.2511 |

### Result

```text
t = -0.6425
p = 0.5251
```

The p-value of **0.5251** is greater than the significance level of **0.05**:

```text
p = 0.5251 > α = 0.05
```

Therefore, we **fail to reject the null hypothesis**.

### Statistical conclusion

There is **no statistically significant evidence of a difference in mean shot-conversion ratio between UEFA and CONMEBOL players** in the sample.

Although UEFA players recorded a higher sample mean conversion ratio (**0.1192**) than CONMEBOL players (**0.0764**), the observed difference is not large enough relative to the variation in the data to be considered statistically significant at the 5% significance level.

### Plain-language conclusion

UEFA players appeared to be more efficient at converting shots into goals in this sample, with an average conversion ratio of **11.92% compared with 7.64% for CONMEBOL players**. However, the statistical test indicates that this observed difference could reasonably be due to sampling variation.

Therefore, the analysis does **not provide sufficient evidence to conclude that UEFA players are genuinely more efficient shooters than CONMEBOL players**.

Failing to reject H₀ does not prove that the two confederations have exactly the same conversion efficiency. Rather, it means that the sample provides insufficient statistical evidence to establish a difference.

---

## Overall finding

The descriptive analysis suggests a difference in shooting efficiency:

```text
UEFA       = 11.92%
CONMEBOL   =  7.64%
Difference =  4.28 percentage points
```

However, the inferential analysis does not support this difference as statistically significant:

```text
t = -0.6425
p = 0.5251
```

Consequently, the most appropriate conclusion is:

> **Although UEFA players had a higher observed average goals-per-shot ratio than CONMEBOL players, there is insufficient statistical evidence to conclude that the two groups differ in their population-level shooting conversion efficiency.**

This finding is useful for the group's broader FIFA World Cup analysis because it suggests that **shot-conversion efficiency alone may not explain differences in tournament performance**. Other aspects of performance investigated by the remaining tasks may provide stronger evidence for differences between players or teams.
