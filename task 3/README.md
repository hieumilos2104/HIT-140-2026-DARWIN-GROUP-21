# UEFA vs CONMEBOL Disciplinary Rates — FIFA World Cup 2026

This project analyses whether players representing UEFA and CONMEBOL teams exhibited different disciplinary characteristics at the 2026 FIFA World Cup.

## Research question

Do players representing UEFA and CONMEBOL teams differ in their mean disciplinary rate, measured as cards received per 100 fouls committed, at the 2026 FIFA World Cup?

## Data source

The raw data were manually extracted from the **Player Miscellaneous Statistics** table on FBref:

<https://fbref.com/en/comps/1/2026/misc/2026-World-Cup-Stats>

The following variables were retained:

- `Rk`: player ranking number
- `Player`: player name
- `Squad`: national team
- `90s`: playing time expressed as 90-minute periods
- `CrdY`: yellow cards
- `CrdR`: red cards
- `2CrdY`: dismissals caused by a second yellow card
- `Fls`: fouls committed

The analysis script does not download data from the internet. The manually extracted raw CSV must be stored in the same directory as the script.

## Files

```text
assignment2/
├── README.md
├── task3_complete.py
└── fbref_wc2026_player_misc_raw_manual.csv
```

Running the script creates the following files:

```text
fbref_wc2026_player_misc_cleaned.csv
task3_eligible_players.csv
task3_player_random_sample_50.csv
task3_descriptive_statistics.csv
task3_confidence_intervals.csv
task3_ttest_results.csv
task3_disciplinary_rate_visualisation.png
```

## Software requirements

- Python 3
- pandas
- NumPy
- SciPy
- Matplotlib

Using Conda, the required packages can be installed with:

```bash
conda install pandas numpy scipy matplotlib
```

Activate the relevant Conda environment before running the analysis. For example:

```bash
conda activate hit140env
```

## How to run the project

1. Place `task3_complete.py` and `fbref_wc2026_player_misc_raw_manual.csv` in the same directory.
2. Open a terminal in that directory.
3. Activate the Conda environment.
4. Run:

```bash
python task3_complete.py
```

The script prints the statistical results and saves the processed data, result tables and visualisation in the same directory.

## Method

### Population and eligibility

The source dataset contains 1,039 player records from the 2026 FIFA World Cup. The target population is all players representing UEFA and CONMEBOL teams.

Players were eligible for analysis if they:

1. represented a UEFA or CONMEBOL team; and
2. committed at least one foul (`Fls > 0`).

The eligible population contains 358 players:

- UEFA: 258 players
- CONMEBOL: 100 players

Players with no fouls were excluded because a cards-per-foul rate cannot be calculated when the denominator is zero.

### Outcome variable

Cards received are calculated as:

```text
Cards received = yellow cards + red cards
```

`2CrdY` is not added separately because it identifies a red card caused by a second yellow and would otherwise duplicate an already recorded disciplinary outcome.

The disciplinary rate is calculated for every eligible player as:

```text
Cards per 100 fouls = (cards received / fouls committed) × 100
```

### Sampling

A simple random sample of 50 players is selected from the eligible population. A fixed random seed of `140` makes the sample reproducible.

The resulting sample contains:

- UEFA: 34 players
- CONMEBOL: 16 players

### Statistical analysis

The project performs:

- descriptive statistics for each confederation;
- 95% confidence intervals for each population mean;
- a Welch two-sample t-test;
- a 95% confidence interval for the difference in means; and
- histogram and boxplot visualisations.

Welch's test is used because the two groups have unequal sample sizes and equal population variances are not assumed.

The hypotheses are:

```text
H0: The mean disciplinary rates of UEFA and CONMEBOL players are equal.
H1: The mean disciplinary rates of UEFA and CONMEBOL players are different.
```

The significance level is `α = 0.05`.

## Results

| Confederation | Sample size | Mean | Median | Standard deviation | 95% CI for mean |
|---|---:|---:|---:|---:|---:|
| UEFA | 34 | 17.49 | 0.00 | 30.04 | [7.01, 27.97] |
| CONMEBOL | 16 | 29.14 | 7.14 | 38.86 | [8.43, 49.84] |

Welch two-sample t-test results:

```text
t(23.77) = -1.06
p = 0.300
Mean difference (UEFA − CONMEBOL) = -11.65
95% CI for the mean difference = [-34.35, 11.06]
```

At the 5% significance level, the null hypothesis is not rejected because the p-value is greater than 0.05. Although the CONMEBOL sample has a higher mean disciplinary rate, the sample provides insufficient evidence that the population means differ.

## Limitations

- The simple random sample is unbalanced, with 34 UEFA players and 16 CONMEBOL players.
- The disciplinary-rate distributions are right-skewed and contain many zero values.
- Rates can be unstable for players who committed only a small number of fouls.
- Players from the same team may not be completely independent because they share tactics, opponents and match conditions.
- The findings apply to eligible players from UEFA and CONMEBOL teams at this tournament and should not be generalised to every football competition.

## Academic use

This repository was prepared for an academic data-analysis assignment. FBref is the source of the football statistics and should be acknowledged in the report and presentation.
