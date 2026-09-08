"""
Task 4 - addendum requested by the lecturer:
 (A) robustness: does the FIFA-vs-FBref source/count difference change the conclusion?
 (B) exploration: what else do the passing + crossing columns reveal?
"""
import pandas as pd, numpy as np
from scipy import stats

d = pd.read_excel('WC2026_Player_Passing_FIFA_FULL.xlsx', sheet_name='Player Passing')
d = d[d.Confederation.isin(['UEFA', 'CONMEBOL'])].copy()
d = d[d.Passes_Att >= 20].copy()
d['Cmp_pct'] = d.Passes_Cmp / d.Passes_Att * 100

def welch(pop, n=40, seed=42):
    s = pop.sample(n=min(n, len(pop)), random_state=seed)
    u = s[s.Confederation == 'UEFA'].Cmp_pct
    c = s[s.Confederation == 'CONMEBOL'].Cmp_pct
    if len(u) < 3 or len(c) < 3: return None
    return stats.ttest_ind(u, c, equal_var=False)

# ---------- A. ROBUSTNESS ----------
print('A1. exclusion threshold')
full = pd.read_excel('WC2026_Player_Passing_FIFA_FULL.xlsx', sheet_name='Player Passing')
full = full[full.Confederation.isin(['UEFA', 'CONMEBOL'])].copy()
full['Cmp_pct'] = full.Passes_Cmp / full.Passes_Att * 100
for thr in [10, 20, 50, 100, 150, 200]:
    r = welch(full[full.Passes_Att >= thr])
    print(f'   Att>={thr:<4} p={r.pvalue:.4f}  {"reject" if r.pvalue < .05 else "fail to reject"}')

print('A2. population shrunk to FBref size (247)')
r = welch(full.nlargest(247, 'Passes_Att'));  print(f'   p={r.pvalue:.4f}')

print('A3. census - no sampling')
u, c = d[d.Confederation == 'UEFA'].Cmp_pct, d[d.Confederation == 'CONMEBOL'].Cmp_pct
t, p = stats.ttest_ind(u, c, equal_var=False);  print(f'   p={p:.4f}')

print('A4. 500 different random seeds')
ps = np.array([welch(d, seed=s).pvalue for s in range(500)])
print(f'   median p={np.median(ps):.4f}   reject rate={(ps < .05).mean() * 100:.1f}%')

# ---------- B. EXPLORATION ----------
def wacc(vol, rate):
    m = d[vol] > 0
    return (d.loc[m, vol] * d.loc[m, rate]).sum() / d.loc[m, vol].sum()

print('\nB1. risk gradient')
print(f'   all passes {d.Passes_Cmp.sum()/d.Passes_Att.sum()*100:.1f}% | '
      f'switches {wacc("Switches_Att","Switches_Acc"):.1f}% | '
      f'linebreaks {wacc("DefLinebreaks_Att","DefLinebreaks_Acc"):.1f}% | '
      f'crosses {wacc("Crosses","Cross_Acc"):.1f}%')

print('B2. position effect')
f, p = stats.f_oneway(*[g.Cmp_pct.values for _, g in d.groupby('Pos')])
print(f'   ANOVA F={f:.2f} p={p:.2e}')
print(d.groupby('Pos').Cmp_pct.agg(['count', 'mean']).round(2).to_string())

print('B3. confederation gap by pass type')
for lbl, vol, rate, mn in [('crossing', 'Crosses', 'Cross_Acc', 5),
                           ('linebreaks', 'DefLinebreaks_Att', 'DefLinebreaks_Acc', 5),
                           ('switches', 'Switches_Att', 'Switches_Acc', 3)]:
    s = d[d[vol] >= mn]
    u, c = s[s.Confederation == 'UEFA'][rate], s[s.Confederation == 'CONMEBOL'][rate]
    t, pv = stats.ttest_ind(u, c, equal_var=False)
    print(f'   {lbl:11s} UEFA {u.mean():5.1f}% vs CONMEBOL {c.mean():5.1f}%  t={t:6.3f} p={pv:.4f}')

print('B4. volume vs accuracy')
r, pv = stats.pearsonr(d.Passes_Att, d.Cmp_pct);  print(f'   Pearson r={r:.3f} p={pv:.2e}')
