"""
HIT-140 (2026) - Darwin - Group 21
Task 4: Proportion of Successful Passes / Total Passes Attempted (per player)
Theme : Is Argentina truly the champion based on the ratio, despite the result against Spain?

Source: FIFA Official - World Cup 2026 Player Statistics (Distribution > Passes)
https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/statistics/player-statistics?group=gcp_distribution&stat=passes
"""
import pandas as pd
from scipy import stats

RAW   = 'WC2026_Player_Passing_FIFA_FULL.xlsx'
MIN_ATT = 20      # exclusion rule
N       = 40      # sample size (professor: 30-40)
SEED    = 42      # fixed for reproducibility

# ---------- 1. DATA WRANGLING ----------
raw = pd.read_excel(RAW, sheet_name='Player Passing')
print(f'Raw players (all 48 teams)          : {len(raw)}')

# ---------- 2. POPULATION ----------
pop = raw[raw['Confederation'].isin(['UEFA', 'CONMEBOL'])].copy()
print(f'UEFA + CONMEBOL                     : {len(pop)}')

pop = pop[pop['Passes_Att'] >= MIN_ATT].copy()
print(f'After exclusion (Att >= {MIN_ATT})          : {len(pop)}')

pop['Cmp_pct'] = (pop['Passes_Cmp'] / pop['Passes_Att'] * 100).round(2)
pop = pop.sort_values('FIFA_Rank').reset_index(drop=True)
pop.insert(0, 'No', range(1, len(pop) + 1))
pop = pop[['No', 'FIFA_Rank', 'Player', 'Abbr', 'Country', 'Confederation', 'Pos',
           'Passes_Att', 'Passes_Cmp', 'Cmp_pct']]
pop.to_csv('pass_population.csv', index=False, encoding='utf-8-sig')

# ---------- 3. SAMPLING ----------
smp = pop.sample(n=N, random_state=SEED).sort_values('No').reset_index(drop=True)
smp.insert(0, 'Sample_No', range(1, N + 1))
smp.to_csv('pass_sample_random.csv', index=False, encoding='utf-8-sig')

# ---------- 4. DESCRIPTIVE STATISTICS ----------
x = smp['Cmp_pct']
print('\n--- DESCRIPTIVE STATISTICS (sample, n=40) ---')
print(x.describe().round(3).to_string())
print('\nBy confederation:')
print(smp.groupby('Confederation')['Cmp_pct']
        .agg(['count', 'mean', 'std', 'median', 'min', 'max']).round(3).to_string())

# ---------- 5. CONFIDENCE INTERVAL ----------
lo, hi = stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=stats.sem(x))
print('\n--- 95% CONFIDENCE INTERVAL for population mean ---')
print(f'x-bar = {x.mean():.3f}   s = {x.std(ddof=1):.3f}   SE = {stats.sem(x):.3f}')
print(f'95% CI = [{lo:.3f}, {hi:.3f}]')
print(f'True population mean = {pop["Cmp_pct"].mean():.3f} '
      f'-> {"INSIDE" if lo <= pop["Cmp_pct"].mean() <= hi else "OUTSIDE"} the interval')

# ---------- 6. TWO-SAMPLE t-TEST ----------
u = smp[smp.Confederation == 'UEFA']['Cmp_pct']
c = smp[smp.Confederation == 'CONMEBOL']['Cmp_pct']
t, p = stats.ttest_ind(u, c, equal_var=False)          # Welch
print('\n--- TWO-SAMPLE t-TEST (Welch): UEFA vs CONMEBOL ---')
print('H0: mu_UEFA = mu_CONMEBOL      Ha: mu_UEFA != mu_CONMEBOL')
print(f'UEFA      n={len(u):2d}  mean={u.mean():.3f}  s={u.std(ddof=1):.3f}')
print(f'CONMEBOL  n={len(c):2d}  mean={c.mean():.3f}  s={c.std(ddof=1):.3f}')
print(f't = {t:.4f}    p = {p:.4f}')
print('Decision:', 'reject H0' if p < 0.05 else 'fail to reject H0 (alpha = 0.05)')

# assumption checks
print('\nAssumption checks:')
print(f'  Shapiro-Wilk UEFA      p = {stats.shapiro(u).pvalue:.4f}')
print(f'  Shapiro-Wilk CONMEBOL  p = {stats.shapiro(c).pvalue:.4f}')
print(f'  Levene equal variance  p = {stats.levene(u, c).pvalue:.4f}')

# robustness: non-parametric backup (UEFA group is not normal)
mw = stats.mannwhitneyu(u, c, alternative='two-sided')
print('\nRobustness check - Mann-Whitney U (non-parametric):')
print(f'  U = {mw.statistic:.1f}, p = {mw.pvalue:.4f} '
      f'({"significant" if mw.pvalue < 0.05 else "same conclusion as t-test"})')

# ---------- 7. CASE STUDY: ARGENTINA vs SPAIN ----------
print('\n--- CASE STUDY: Argentina vs Spain (full population) ---')
for team in ['Argentina', 'Spain']:
    d = pop[pop.Country == team]
    print(f'{team:10s} players={len(d):2d}  mean player Cmp%={d.Cmp_pct.mean():.2f}  '
          f'team total={d.Passes_Cmp.sum()}/{d.Passes_Att.sum()} = '
          f'{d.Passes_Cmp.sum()/d.Passes_Att.sum()*100:.2f}%')
a = pop[pop.Country == 'Argentina']['Cmp_pct']
s = pop[pop.Country == 'Spain']['Cmp_pct']
t2, p2 = stats.ttest_ind(a, s, equal_var=False)
print(f'Welch t-test Argentina vs Spain: t = {t2:.4f}, p = {p2:.4f} '
      f'({"significant" if p2 < 0.05 else "not significant"})')
