# Task 4 — Pass Completion Rate (per player)

**HIT-140 (2026) · Darwin · Group 21**

**Author.** Thi Ngoc Nhi Le — Student ID S408842

**Analytic question.** On average, is there a difference in pass completion rate between UEFA and CONMEBOL players at the FIFA World Cup 2026?

- H₀: μ_UEFA = μ_CONMEBOL
- H₁: μ_UEFA ≠ μ_CONMEBOL

**Variable.** `Cmp_pct` = passes completed ÷ passes attempted × 100, per player, whole tournament.

**Source.** FIFA official player statistics, Distribution → Passes, extracted 1 September 2026. One source used throughout.

---

## Files

| File | Contents |
|---|---|
| `task4_report.docx` | Main report — the full process, why each decision was made, and all results |
| `task4_dataset_raw.xlsx` | Raw extract: 1,242 squad members, 48 teams, 17 columns |
| `task4_population.csv` | Population after the exclusion rule: 383 players (282 UEFA, 101 CONMEBOL) |
| `task4_sample.csv` | Simple random sample: 40 players (29 UEFA, 11 CONMEBOL), seed 42 |
| `task4_analysis.py` | Single script: reproduces both CSVs, both figures, and every statistic in the report, from the raw file |
| `task4_fig1_descriptive.png` | Figure 1 — sample distribution by confederation; population with the confidence interval |
| `task4_fig2_robustness.png` | Figure 2 — specification curve: fourteen analytical variants |

## Reproducing the results

```
python task4_analysis.py
```

That one command regenerates `task4_population.csv`, `task4_sample.csv`, both figures, and prints every statistic quoted in the report.

Requires `pandas`, `scipy`, `openpyxl` and `matplotlib`. `statsmodels` is optional — only the power analysis in Step 6 needs it, and the script skips that section if it is absent. The random seed is fixed at 42, so the sample of forty players is identical on every run and on every machine.

## Where the six required skills appear

| Required skill | Report section |
|---|---|
| Analytic question formulation | Step 1 |
| Data wrangling | Step 2 |
| Data preparation and sampling | Step 3 |
| Descriptive statistics | Step 4 |
| Inferential statistics — confidence interval | Step 5 |
| Inferential statistics — two-sample *t*-test | Step 6 |

Steps 7 and 8 go beyond the brief and are labelled as such in the report: robustness testing of every analytical choice, and a decomposition of the variable by pass type.

### Other techniques used, and where

| Technique | Where | What it was for |
|---|---|---|
| Student's *t*-test | Step 6 | reported beside Welch's, to justify choosing Welch |
| One-way ANOVA | Step 8.4 | testing position as a confound |
| Chi-square test of independence | Step 8.4 | comparing the two groups' position mixes |
| Pearson and Spearman correlation | Step 3 | evidence that the ratio needs a denominator floor |
| Mann–Whitney *U* | Step 6 | non-parametric check after Shapiro–Wilk failed |
| Two-proportion *z*-test | Theme | Argentina vs Spain crossing accuracy |
| Bonferroni correction | Step 8 limits | three tests on the same data |
| Power analysis and minimum detectable effect | Step 6 | quantifying what "fail to reject" can support |
| Simulation (2,000 and 500 draws) | Steps 5, 7 | verifying CI coverage and the false-positive rate |

## Citations

The report uses APA 7th edition: author–date citations in the text and a matching reference list at the end. APA does **not** use footnotes for citations — footnotes are reserved for content notes — so there are none. The report says this explicitly in "Notes on sources and citation style", together with the acknowledgment of AI assistance.

## Headline results

| | |
|---|---|
| Sample (n = 40) | *M* = 84.77, *SD* = 9.02 |
| UEFA (n = 29) | *M* = 85.20, *SD* = 8.66 |
| CONMEBOL (n = 11) | *M* = 83.62, *SD* = 10.27 |
| 95% confidence interval for μ | [81.88, 87.65] — contains the true population mean of 84.70 |
| Welch's two-sample *t*-test | *t*(15.71) = 0.45, *p* = .657 — fail to reject H₀ |
| Effect size | Cohen's *d* = 0.17 (small) |
| Assumption checks | Shapiro–Wilk: UEFA *p* = .007, CONMEBOL *p* = .362; Levene *p* = .419 |
| Non-parametric backup | Mann–Whitney *U* = 171.0, *p* = .739 — same conclusion |
| Census (all 383 players) | *t* = 0.84, *p* = .404 |

**Conclusion.** No statistically significant difference in pass completion rate between European and South American players. The finding holds across fourteen alternative specifications (*p* from .133 to .989).

**Two qualifications stated in the report.** The sample of forty had only 7.6% power and could reliably detect nothing smaller than a nine-point gap; it is the census, adequately powered to detect 2.8 points, that licenses the null conclusion. And the aggregate null conceals two significant differences running in opposite directions — European players complete more defence-splitting passes (*p* = .049), South American players more switches of play (*p* = .006) — which cancel on averaging.

## A note on the data source

Re-checking the source on 9 September, FIFA had removed the `Passes Completed` column from this table; only attempted passes and an accuracy percentage rounded to a whole number remain. Every other figure re-verified as identical on that date (1,242 rows; 1,019 players with at least one pass; 383 in the population; 56,887 attempted passes). `task4_dataset_raw.xlsx` is therefore retained as the authoritative record, because the exact completed-pass counts underlying this analysis can no longer be retrieved from the live source, and deriving them from the rounded percentage introduces an error of up to half a percentage point per player.
