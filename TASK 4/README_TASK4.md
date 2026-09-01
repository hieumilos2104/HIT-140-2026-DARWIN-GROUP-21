# Task 4 — Pass Completion Rate (UEFA vs CONMEBOL players)

**Variable:** `Cmp_pct` = Passes Completed ÷ Passes Attempted × 100, per player
**Theme:** Is Argentina truly the champion based on the ratio, despite the actual result against Spain?

---

## 1. Analytic question

On average, is there a difference in pass completion rate between players of UEFA (European) teams and players of CONMEBOL (South American) teams at the FIFA World Cup 2026?

- H₀: μ_UEFA = μ_CONMEBOL
- Hₐ: μ_UEFA ≠ μ_CONMEBOL

## 2. Data wrangling

Single source: **FIFA Official — World Cup 2026 Player Statistics (Distribution → Passes)**
`https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/statistics/player-statistics?group=gcp_distribution&stat=passes`

1242 players across all 48 teams were extracted, then labelled by confederation.
No other source was mixed in.

**Data validation:** summing passes per player and comparing against FIFA's own team-statistics page, **45 of 48 teams match exactly** on both attempted and completed passes. Three differ slightly — Japan (−5 attempts), Morocco (−4), Bosnia & Herzegovina (−27) — all under 2%, most likely players absent from the player table.

## 3. Population & sample

| | |
|---|---|
| **Population** | Players of UEFA (16 countries) and CONMEBOL (6 countries) teams at WC 2026. Unit of observation: **one player**. |
| **Exclusion rule** | Players with fewer than **20 attempted passes** are removed — those with 0 never took the field, and a handful of passes gives an unstable ratio (2/2 = 100%). |
| **Funnel** | 1242 total → 571 UEFA/CONMEBOL → **383 after exclusion** (282 UEFA, 101 CONMEBOL) |
| **Sample** | **Simple random sample, n = 40**, `pandas.sample(random_state=42)`. Natural split 29 UEFA / 11 CONMEBOL — no stratification, so the split reflects the population proportion. The fixed seed lets any group member reproduce the identical sample. |

## 4. Descriptive statistics (n = 40)

| | Cmp_pct |
|---|---|
| mean | 84.77 |
| sd | 9.02 |
| median | 87.96 |
| min / max | 66.67 / 96.77 |
| Q1 / Q3 | 77.67 / 91.69 |

| Confederation | n | mean | sd | median | min | max |
|---|---|---|---|---|---|---|
| UEFA | 29 | 85.20 | 8.66 | 89.47 | 68.18 | 96.77 |
| CONMEBOL | 11 | 83.62 | 10.27 | 82.91 | 66.67 | 95.82 |

Figure: `task4_descriptive_stats.png` — boxplot with every sampled player shown, plus the population distribution with the confidence interval overlaid.

## 5. Confidence interval

x̄ ± t*(s/√n), 95%, σ unknown → **[81.88, 87.65]**

The true population mean is 84.70, which falls inside the interval — the sample estimated the population correctly.

## 6. Two-sample t-test (Welch)

| | |
|---|---|
| t | 0.4522 |
| p | **0.6573** |
| Decision | **Fail to reject H₀** at α = 0.05 |

There is no statistically significant difference in pass completion rate between UEFA and CONMEBOL players.

**Assumption checks**

| Check | p | Reading |
|---|---|---|
| Shapiro–Wilk, UEFA | 0.0070 | not normal — flagged honestly |
| Shapiro–Wilk, CONMEBOL | 0.3625 | normal |
| Levene (equal variance) | 0.4190 | variances comparable |

Because the UEFA group departs from normality, a non-parametric backup was run: **Mann–Whitney U = 171.0, p = 0.7390** — the same conclusion. Welch's t-test was used throughout (it does not assume equal variances), and n = 29 gives some central-limit protection.

## 7. Case study — Argentina vs Spain

| Team | Players | Mean player Cmp% | Team total |
|---|---|---|---|
| Argentina | 23 | 88.84 | 4697 / 5246 = **89.53%** |
| Spain | 19 | 88.51 | 4933 / 5457 = **90.40%** |

Welch t-test Argentina vs Spain: t = 0.1778, **p = 0.8598** — not significant.

**Reading against the theme:** Spain passed marginally more accurately than the eventual champions (90.40% vs 89.53% at team level), and at player level the two squads are statistically indistinguishable. On passing accuracy alone, Argentina were **not** measurably the better side — whatever won them the trophy, it was not superior distribution.

## 8. Files

| File | Contents |
|---|---|
| `pass_population.csv` | 383 players — the population after exclusion |
| `pass_sample_random.csv` | 40 players — the random sample |
| `task4_analysis.py` | Wrangling → population → sampling → descriptives → CI → t-test |
| `make_charts.py` | Generates the figure |
| `task4_descriptive_stats.png` | Descriptive-statistics figure |
| `WC2026_Player_Passing_FIFA_FULL.xlsx` | Raw source data (1242 players, 48 teams) |

## 9. Column notes

`No, FIFA_Rank, Player, Abbr, Country, Confederation, Pos, Passes_Att, Passes_Cmp, Cmp_pct`

- `Passes_Att` / `Passes_Cmp` — attempted / completed passes for the whole tournament
- `Cmp_pct` — recomputed to 2 decimals (FIFA publishes it rounded to an integer)
- `FIFA_Rank` — the player's rank on FIFA's passes table; ties share a rank

**Note on scope:** the task was originally written as "per Team". At team level the population is only 22 teams (16 UEFA + 6 CONMEBOL), which cannot support a sample of 30–40, so the analysis is done **per player** — consistent with the professor's worked example (n = 40 players) and with the rest of the group's tasks.
