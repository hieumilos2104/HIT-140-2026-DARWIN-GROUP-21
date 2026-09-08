# Task 4 — Pass Completion Rate at the FIFA World Cup 2026

**HIT-140 (2026), Darwin, Group 21**

**Variable:** proportion of successful passes to total passes attempted, per player
**Theme:** Is Argentina truly the champion based on the ratio, despite the actual result against Spain?

---

## 1. Background and research question

Argentina won the 2026 FIFA World Cup, beating Spain in the final. The scoreline is the official answer to the question of who was the better side, and it is unambiguous — but it is also a single number produced by a single match. Football is decided by a handful of moments, and a tournament's worth of quality can be overturned by one deflection.

That gap between **outcome** and **process** is what this task set out to examine. A result records who lifted the trophy. A process measure — how reliably a team moved the ball, across every match it played — is closer to a description of how well the team actually played. If Argentina were genuinely the superior side, the process data should agree with the scoreline; if it does not, the trophy came from something other than sustained superiority.

Pass completion rate was chosen as that process measure. Passing is the highest-volume action in football: the population analysed here attempted 56,887 passes. High volume yields a stable, low-noise statistic, in contrast to goals, where an entire tournament may give a single player only two or three events.

### 1.1 Why the statistical comparison is UEFA versus CONMEBOL

A two-sample *t*-test requires two groups. Testing Argentina against Spain directly would be the literal reading of the theme, but two squads supply roughly forty players between them, and a two-team comparison can only ever describe those two teams.

The final, however, was not only Argentina against Spain. It was **CONMEBOL against UEFA** — a South American side defeating a European one. This allows the question to be widened without abandoning it:

> Was the final's result reflective of a broader difference between European and South American football, or was it specific to that match?

This is the hypothesis tested inferentially. If European players complete passes at a significantly higher rate across the tournament, Spain's defeat reads as an upset against the grain; if the two confederations are statistically indistinguishable, the final was decided by something other than a regional advantage in ball control, and Argentina's victory requires a different explanation. Argentina and Spain are then examined directly as a case study (Section 9), preserving the original theme while inference is conducted at a scale where inference is meaningful.

- H₀: μ_UEFA = μ_CONMEBOL
- H₁: μ_UEFA ≠ μ_CONMEBOL

---

## 2. Data source and acquisition

### 2.1 Source

All data were obtained from the official FIFA statistics portal for the tournament (FIFA, 2026a), specifically the player-level distribution table reporting passes attempted and passes completed. Team-level totals used for validation were taken from the same portal's team statistics table (FIFA, 2026b). Football Reference (2026) was the source used by the other three tasks in this group and is referenced here only for the cross-source comparison in Section 7.1.

A single source was used throughout the analysis. Mixing sources mid-analysis is how a dataset acquires two conflicting values for the same player, and source consistency was identified as a design decision requiring defence in the unit's worked example.

### 2.2 What was learned obtaining the data

Acquiring the data was not a download, and each obstacle revealed something about the dataset that would not have been apparent had it come easily.

**Football Reference blocks automated access.** Attempts to retrieve data programmatically returned a bot-verification challenge rather than data. This explains why this task used FIFA while the remainder of the group used Football Reference: a technical constraint, not a preference. It is also a substantive lesson — data being *published* is not the same as data being *accessible*, and a design that assumes access to a particular source can fail for reasons unrelated to the research question.

**The FIFA table is not present in the page source.** The statistics portal is a JavaScript application; the visible table is assembled in the browser, and only the fifty rows currently rendered can be copied from the screen. The complete table is delivered through a paginated data feed of twenty-five pages. The practical consequence is important: **any approach based on copying the visible screen would have silently captured a fraction of the data**, and the result would not have looked wrong. A fifty-row extract consisting of the tournament's highest-volume passers would have produced a plausible mean and a badly biased one.

**There are two distinct passing tables.** The first extraction returned forty-eight rows and appeared complete; it was the squad-level table, one row per team. The required player-level table sits further down the same page with over a thousand rows. This mattered beyond lost time: working with the forty-eight-row version is what exposed the unit-of-analysis problem described in Section 3.1. The dead end was the mechanism by which the group discovered that the task as originally worded could not be completed.

**The visible player count is misleading.** The rank column terminates at 1,023, implying roughly a thousand players; the actual row count is 1,242. The explanation is informative: 223 squad members attempted zero passes — unused substitutes and reserve goalkeepers — and FIFA assigns all of them the same bottom rank. The rank ceiling therefore reflects players who recorded an action, while the row count includes everyone named in a squad. The number of players attempting at least one pass is 1,019.

This distinction is not cosmetic. It is precisely the population question the task requires: is the population *players at the World Cup*, or *players who played at the World Cup*? The structure of the data is what surfaced the choice; Section 3.2 records the decision.

**Internal validation exposed three small inconsistencies in FIFA's own data.** Summing every player's passes and comparing the totals against FIFA's separate team statistics table, 45 of 48 teams matched exactly on both attempted and completed passes. Three did not: Japan (−5 attempts), Morocco (−4) and Bosnia and Herzegovina (−27). These discrepancies are all below 2%, but their existence is the point — an official source is not necessarily internally exact, and knowing the magnitude of the inconsistency establishes how much precision the analysis is entitled to claim.

**The dataset contained more than was requested.** The passing feed also returns crosses, defence-splitting passes and switches of play, each with its own completion rate — categories for which this task had no plan. Those columns made Section 8 possible, and produced the most substantial finding in the task.

---

## 3. Population and sample

### 3.1 Unit of analysis: players rather than teams

The task was originally worded "per team", and was changed. The practical reason is arithmetic: the population comprises European and South American teams — sixteen UEFA and six CONMEBOL, **twenty-two teams in total** — and a sample of 30 to 40 cannot be drawn from a population of twenty-two.

The substantive reason is that a team-level completion rate is a single weighted average concealing who did the passing. Spain's 90.40% and Argentina's 89.53% appear nearly identical; at player level the distribution behind those figures becomes visible — its spread, whether it is driven by a few dominant passers, and how goalkeepers and forwards pull it in opposite directions. Aggregation to one figure per team discards all of this. Moving to player level cost nothing and yielded 383 observations rather than 22.

### 3.2 Population definition and exclusion rule

| | |
|---|---|
| **Population** | Players of UEFA (16 countries) and CONMEBOL (6 countries) teams at the 2026 FIFA World Cup |
| **Unit of observation** | One player |
| **Variable of interest** | `Cmp_pct` = passes completed ÷ passes attempted × 100 |
| **Exclusion rule** | Players attempting fewer than 20 passes are removed |
| **Funnel** | 1,242 squad members → 571 UEFA/CONMEBOL → **383 after exclusion** (282 UEFA, 101 CONMEBOL) |

The exclusion rule is the most consequential judgement in the task. The variable is a **ratio**, and ratios destabilise as the denominator shrinks. A substitute introduced late who attempted two passes and completed both records a completion rate of 100% — arithmetically superior to Rodri's 93.49% across 799 passes. He is not the better passer; he has a denominator of two. Retained in the data, such players occupy the top of the distribution and inflate the mean while carrying no information about passing ability.

A distinct group sits at the other extreme: the 223 squad members with zero passes. Their ratio is not low but **undefined** (0 ÷ 0). Including them as zeros would treat "never played" as "played and failed", depressing the mean for reasons unconnected to football.

The threshold of twenty attempted passes is a judgement rather than a rule, so its influence was tested rather than asserted (Section 7.2).

### 3.3 Sampling

**Simple random sampling, n = 40**, drawn with `pandas.DataFrame.sample(random_state = 42)` (McKinney, 2010). The realised split was 29 UEFA and 11 CONMEBOL.

Stratification to a balanced 20/20 was considered and rejected. The imbalance is real: UEFA sent sixteen teams to this tournament and CONMEBOL six, so 282 of the 383 players in the population are European. A simple random sample reproduces that proportion faithfully, whereas forcing balance would over-represent South American players relative to the defined population — and the confidence interval in Section 5 is an estimate *for that population*. The approach also matches the sampling method in the unit's worked example.

The sample size sits at the upper end of the permitted 30–40 range. With a ratio variable carrying substantial variance (*SD* ≈ 9 percentage points), the larger end of the range was preferred.

The random seed is fixed so that any group member executing `task4_analysis.py` obtains the identical forty players. Without a fixed seed the sample changes on each run, reported statistics cease to match the code, and the work cannot be checked.

---

## 4. Descriptive statistics (n = 40)

| Statistic | Value |
|---|---|
| *M* | 84.77 |
| *SD* | 9.02 |
| Median | 87.96 |
| Minimum / Maximum | 66.67 / 96.77 |
| Q1 / Q3 | 77.66 / 91.69 |

| Confederation | *n* | *M* | *SD* | Median | Min | Max |
|---|---|---|---|---|---|---|
| UEFA | 29 | 85.20 | 8.66 | 89.47 | 68.18 | 96.77 |
| CONMEBOL | 11 | 83.62 | 10.27 | 82.91 | 66.67 | 95.82 |

Figure 1 (`task4_descriptive_stats.png`) presents the sample distribution by confederation with every sampled observation displayed, alongside the population distribution with the confidence interval overlaid. Figures were produced with Matplotlib (Hunter, 2007).

---

## 5. Confidence interval

The 95% confidence interval for the population mean, with σ unknown and therefore estimated from the sample:

x̄ ± t*(s / √n) → **95% CI [81.88, 87.65]**

Because the whole population is available, the estimate can be checked directly: the population mean is 84.70, which falls inside the interval. The sample estimated the population correctly.

---

## 6. Two-sample *t*-test

Welch's *t*-test (Welch, 1947) was used rather than Student's, implemented as `scipy.stats.ttest_ind(..., equal_var = False)` (Virtanen et al., 2020). The groups are unequal in size (29 versus 11); Student's test assumes equal variances, Welch's does not, and with unbalanced groups the more conservative test costs almost nothing while protecting against a violated assumption.

**Result:** *t*(15.71) = 0.45, ***p* = .657** → **fail to reject H₀** at α = .05.

There is no statistically significant difference in pass completion rate between UEFA and CONMEBOL players.

### 6.1 Assumption checks

| Check | Statistic | Interpretation |
|---|---|---|
| Shapiro–Wilk, UEFA (Shapiro & Wilk, 1965) | *p* = .007 | departs from normality |
| Shapiro–Wilk, CONMEBOL | *p* = .363 | consistent with normality |
| Levene's test (Levene, 1960) | *p* = .419 | variances comparable |

The UEFA group departs from normality. This is reported rather than omitted, for two reasons. First, an assumption that is never checked is not an assumption but a hope. Second, it permits a demonstration that the conclusion does not depend on it: a Mann–Whitney *U* test (Mann & Whitney, 1947), which assumes no particular distribution, returns *U* = 171.0, ***p* = .739** — the same conclusion as the *t*-test. When two tests resting on different assumptions agree, the finding stands on its own rather than on the choice of test.

---

## 7. Robustness

A single *p*-value from a single sample is a fragile basis for a conclusion: a different forty players yields a different number. Robustness was therefore assessed in four ways. This section also answers the question raised in supervision — whether the difference in data source between this task and the rest of the group changes the finding.

### 7.1 The two sources agree on who played

The FIFA passing table returns 1,242 rows, but this is every squad member, including the 223 who never attempted a pass. The count of players attempting at least one pass is 1,019.

| Source | Players | Basis |
|---|---|---|
| FIFA — attempted ≥ 1 pass | 1,019 | passing table, zero-pass squad members removed |
| Football Reference — minutes played > 0 | 1,037 | as reported by group members |
| **Difference** | **18 (1.7%)** | |

The two sources therefore agree to within 1.7% on how many players took the field, across the identical twenty-two nations. The remaining eighteen are most plausibly players credited with minutes who never attempted a pass — a late substitute, or a goalkeeper introduced with no recorded distribution.

Had the 1,242 figure been accepted at face value and compared against 1,037, an apparent discrepancy of over two hundred players would have been inferred. That discrepancy is an artefact of comparing two different definitions of "player", not a disagreement between the sources.

The remaining difference in population size — 383 here against 247 for the group member analysing tackles — reflects the **exclusion rule**, not the source: a twenty-pass threshold is less restrictive than Football Reference's 180-minute threshold. Section 7.2 tests this directly.

### 7.2 Sensitivity to the exclusion threshold

| Exclusion rule | Population | *p* | Decision |
|---|---|---|---|
| ≥ 10 passes | 429 | .706 | fail to reject H₀ |
| **≥ 20 passes (adopted)** | **383** | **.657** | **fail to reject H₀** |
| ≥ 50 passes | 302 | .882 | fail to reject H₀ |
| ≥ 100 passes | 211 | .309 | fail to reject H₀ |
| ≥ 150 passes | 142 | .423 | fail to reject H₀ |
| ≥ 200 passes | 100 | .522 | fail to reject H₀ |

### 7.3 Population matched to the group's size

Restricting the population to the 247 highest-volume passers — matching the size used by the group member working from Football Reference — returns *p* = .415: fail to reject H₀.

### 7.4 Census, with no sampling

Testing the entire population (282 UEFA versus 101 CONMEBOL) rather than a sample: *t*(148.01) = 0.84, *p* = .404 — fail to reject H₀.

### 7.5 Five hundred independent samples

Drawing 500 samples of n = 40 with 500 different seeds gave a median *p*-value of .493, and **5.8% of samples would have rejected H₀**.

That figure is not a weakness but a confirmation: it is approximately the 5% false-positive rate an α = .05 criterion *predicts* when the null hypothesis is true. The occasional significant sample is the noise the method is designed to tolerate, not a signal being overlooked.

---

## 8. Extended exploration: beyond the original variable

A null result is an unsatisfying place to stop, and potentially a misleading one, because it admits two very different readings: there is genuinely no difference, or there are differences that cancel. The FIFA data reports several categories of passing separately, which allows these to be distinguished.

### 8.1 Not all passes are equally difficult

Weighting each player's rate by that player's own volume, across the 383-player population:

| Pass type | Completion rate | Volume |
|---|---|---|
| All passes | 87.5% | 56,887 |
| Switches of play | 84.7% | 563 |
| Defensive linebreaks | 54.3% | 2,208 |
| **Crosses** | **23.4%** | 1,995 |

A cross is approximately four times harder to complete than an average pass. This reframes the original variable: an overall completion rate of 90% may indicate accuracy or merely caution, and the headline figure cannot distinguish them.

### 8.2 Position matters more than confederation

| Position | *n* | *M* |
|---|---|---|
| DF | 138 | 87.65 |
| MF | 130 | 86.76 |
| FW | 90 | 80.58 |
| GK | 25 | 72.47 |

A one-way analysis of variance across positions gives *F*(3, 379) = 41.50, *p* < .001 — a far stronger effect than anything observed between confederations.

This raises the possibility that position mix was confounding the main comparison. It was not: the two groups have almost identical composition (UEFA 36.5% DF, 33.7% MF, 23.0% FW, 6.7% GK; CONMEBOL 34.7%, 34.7%, 24.8%, 5.9%). The null result in Section 6 is therefore not a positional artefact — a check worth reporting precisely because it returned negative.

### 8.3 Identical overall, different where risk is involved

Testing each pass type separately across the population:

| Pass type | UEFA | CONMEBOL | *t* | *p* | |
|---|---|---|---|---|---|
| All passes | 84.9% | 84.0% | *t*(148.01) = 0.84 | .404 | *n.s.* |
| Crossing accuracy | 22.8% | 24.4% | *t*(58.58) = −0.48 | .633 | *n.s.* |
| Defensive linebreaks | 55.9% | 48.7% | *t*(82.27) = 2.00 | **.049** | UEFA higher |
| Switches of play | 82.5% | 93.9% | *t*(67.35) = −2.81 | **.006** | CONMEBOL higher |

The two confederations are indistinguishable on passing overall, yet differ **in opposite directions** on the riskier categories: European players complete more passes through a defensive line, South American players complete more switches of play. Averaged into a single figure the two effects cancel — which is precisely why the aggregate test detected nothing. The null result of Section 6 is not an absence of difference but a **masking effect**.

Figure 2 (`task4_exploration.png`) presents both the difficulty gradient and the confederation comparison by pass type.

**Limitations.** The linebreak result (*p* = .049) sits on the significance boundary and should be read as suggestive rather than established. Three tests were conducted; under a Bonferroni correction (Dunn, 1961) at α = .017, only the switches result survives. Switch-of-play volume is small (563 attempts across 70 qualifying players), so that estimate is correspondingly noisy.

### 8.4 Volume and accuracy

Passes attempted and completion rate are moderately positively correlated: *r*(381) = .39, *p* < .001 (Spearman ρ = .42). Players who receive the ball more often complete a higher proportion of their passes. The data alone cannot separate two plausible readings: stronger players both receive the ball more and pass more accurately, or high-volume players are predominantly defenders and midfielders recycling low-risk possession, consistent with Section 8.2.

---

## 9. Case study: Argentina versus Spain

| | All passes | Crossing | Def. linebreaks | Crosses attempted |
|---|---|---|---|---|
| Argentina | 89.53% | **31.4%** | 56.9% | 111 |
| Spain | **90.40%** | 20.2% | **65.4%** | 178 |

At player level the two squads are statistically indistinguishable on pass completion: *t*(39.64) = 0.18, *p* = .860. On the raw figures **Spain were marginally the better passing side** — higher overall accuracy, more effective line-breaking, and substantially greater crossing volume. By this process measure, the losing finalists controlled the ball better.

Argentina's separation lies in **efficiency rather than control**: 38% fewer crosses attempted, completed at more than one and a half times Spain's rate.

---

## 10. Conclusion

By the measure this task set out to test, there is no statistically significant difference in pass completion rate between European and South American players at the 2026 FIFA World Cup (*p* = .657 in the sample; *p* = .404 across the population), and the finding is robust to the exclusion threshold, the population size, the removal of sampling altogether, and 500 independent samples.

The answer to the theme is consequently more interesting than a simple negative. Argentina were **not** the better passing side — Spain were marginally superior on accuracy, line-breaking and volume — so the trophy did not come from out-passing Spain. It came from doing more with less in the final third.

Splitting by pass type then shows that the aggregate null result concealed two significant differences running in opposite directions, which cancel on averaging. The headline metric was hiding rather than reporting the structure in the data — which is itself an argument for examining process measures at the level at which they vary, rather than at the level at which they are most conveniently published.

---

## References

Dunn, O. J. (1961). Multiple comparisons among means. *Journal of the American Statistical Association, 56*(293), 52–64. https://doi.org/10.1080/01621459.1961.10482090

FIFA. (2026a). *Player statistics: Distribution — passes* [Data set]. FIFA World Cup 26. https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/statistics/player-statistics?group=gcp_distribution&stat=passes

FIFA. (2026b). *Team statistics* [Data set]. FIFA World Cup 26. https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/statistics/team-statistics

Football Reference. (2026). *FIFA World Cup 2026 statistics*. Sports Reference. https://fbref.com/en/

Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering, 9*(3), 90–95. https://doi.org/10.1109/MCSE.2007.55

Levene, H. (1960). Robust tests for equality of variances. In I. Olkin (Ed.), *Contributions to probability and statistics: Essays in honor of Harold Hotelling* (pp. 278–292). Stanford University Press.

Mann, H. B., & Whitney, D. R. (1947). On a test of whether one of two random variables is stochastically larger than the other. *The Annals of Mathematical Statistics, 18*(1), 50–60. https://doi.org/10.1214/aoms/1177730491

McKinney, W. (2010). Data structures for statistical computing in Python. In S. van der Walt & J. Millman (Eds.), *Proceedings of the 9th Python in Science Conference* (pp. 56–61). https://doi.org/10.25080/Majora-92bf1922-00a

Shapiro, S. S., & Wilk, M. B. (1965). An analysis of variance test for normality (complete samples). *Biometrika, 52*(3–4), 591–611. https://doi.org/10.1093/biomet/52.3-4.591

Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., Kern, R., Larson, E., … Vázquez-Baeza, Y. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods, 17*(3), 261–272. https://doi.org/10.1038/s41592-019-0686-2

Welch, B. L. (1947). The generalization of "Student's" problem when several different population variances are involved. *Biometrika, 34*(1–2), 28–35. https://doi.org/10.1093/biomet/34.1-2.28

---

## Appendix: files submitted

| File | Contents |
|---|---|
| `TASK4_REPORT.md` | This report |
| `pass_population.csv` | Population, 383 players after exclusion |
| `pass_sample_random.csv` | Random sample, 40 players |
| `task4_analysis.py` | Wrangling → population → sampling → descriptives → CI → *t*-test → assumptions |
| `robustness_and_exploration.py` | Sections 7 and 8 |
| `robustness_output.txt` | Console output of the above |
| `make_charts.py`, `make_charts2.py` | Figure generation |
| `task4_descriptive_stats.png` | Figure 1 |
| `task4_exploration.png` | Figure 2 |
| `WC2026_Player_Passing_FIFA_FULL.xlsx` | Raw source extract, 1,242 players, 48 teams |

### Variable definitions

`No, FIFA_Rank, Player, Abbr, Country, Confederation, Pos, Passes_Att, Passes_Cmp, Cmp_pct`

- `Passes_Att`, `Passes_Cmp` — passes attempted and completed across the whole tournament
- `Cmp_pct` — recomputed to two decimal places; FIFA publishes the rate rounded to an integer
- `FIFA_Rank` — rank on FIFA's passes table; tied players share a rank, and all zero-pass players share rank 1,023

### Note on reproducibility

All reported statistics can be regenerated by executing `task4_analysis.py` followed by `robustness_and_exploration.py` in a directory containing `WC2026_Player_Passing_FIFA_FULL.xlsx`. The fixed random seed (42) guarantees the identical sample of forty players.
