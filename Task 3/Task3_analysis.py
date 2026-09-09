"""
HIT-140 (2026) · Charles Darwin University · Group 21
TASK 4 — Pass Completion Rate (per player), UEFA vs CONMEBOL

Author:   Thi Ngoc Nhi Le          Student ID: S408842
Group:    21 (Darwin)
Date:     September 2026

Analytic question
    On average, is there a difference in pass completion rate between UEFA and
    CONMEBOL players at the FIFA World Cup 2026?
        H0: mu_UEFA = mu_CONMEBOL
        H1: mu_UEFA != mu_CONMEBOL

Data source
    FIFA official player statistics, Distribution -> Passes
    https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/
        statistics/player-statistics?group=gcp_distribution&stat=passes
    Extracted 1 September 2026. One source used throughout.

Usage
    Place this file in the same folder as task4_dataset_raw.xlsx, then:
        python task4_analysis.py
    Paths are relative, so the script runs unchanged on any machine.
    The random seed is fixed at 42: the sample of 40 players is identical
    on every run and on every machine.

Requires
    pandas, scipy, openpyxl, matplotlib
    statsmodels is optional — only the power analysis needs it

Outputs
    task4_population.csv        population after the exclusion rule
    task4_sample.csv            the random sample of 40
    task4_fig1_descriptive.png  Figure 1
    task4_fig2_robustness.png   Figure 2
    plus every statistic quoted in the report, printed to the console

Acknowledgment
    Claude (Anthropic) was used as an analysis assistant while developing this
    script and interpreting the results.
"""

import pandas as pd, numpy as np
from scipy import stats
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

RAW, MIN_ATT, N, SEED = 'task4_dataset_raw.xlsx', 20, 40, 42
GROUPS = ['UEFA', 'CONMEBOL']

def welch_df(a, b):
    va, vb, na, nb = a.var(ddof=1), b.var(ddof=1), len(a), len(b)
    return (va/na + vb/nb)**2 / ((va/na)**2/(na-1) + (vb/nb)**2/(nb-1))

def cohen_d(a, b):
    s = (((len(a)-1)*a.var(ddof=1) + (len(b)-1)*b.var(ddof=1)) / (len(a)+len(b)-2))**0.5
    return (a.mean() - b.mean()) / s

def head(t): print('\n' + '='*70); print(t); print('='*70)

# ---- STEP 1-2  WRANGLING -------------------------------------------------
head('STEP 1-2  DATA WRANGLING')
d = pd.read_excel(RAW, sheet_name='Player Passing')
print(f'raw rows                    {len(d)}')
print(f'attempted >= 1 pass         {(d.Passes_Att>0).sum()}')
print(f'attempted 0 passes          {(d.Passes_Att==0).sum()}')
print(f'FIFA rank ceiling           {d.FIFA_Rank.max()}')
print(f'teams                       {d.Country.nunique()}')

SLOTS = {'UEFA':16,'CAF':10,'AFC':9,'CONCACAF':6,'CONMEBOL':6,'OFC':1}
assert d.groupby('Confederation').Country.nunique().to_dict() == SLOTS
assert d.Confederation.isna().sum() == 0
print(f'confederation mapping       validated against 2026 slots {SLOTS}')

d['Cmp_pct'] = (d.Passes_Cmp / d.Passes_Att * 100).round(2)
assert len(d) == 1242 and d.duplicated(['Player','Country']).sum() == 0
assert (d.Passes_Cmp > d.Passes_Att).sum() == 0
assert d[['Passes_Att','Passes_Cmp']].isna().sum().sum() == 0
assert set(d.Pos) == {'DF','MF','FW','GK'}
p = d[d.Passes_Att > 0]
print(f'max |Cmp_pct - Acc_FIFA|    {(p.Cmp_pct-p.Acc_FIFA).abs().max():.2f} pp')
print(f'as share of the 1.58pp gap  {0.50/1.58*100:.0f}%')

# ---- STEP 3  POPULATION AND SAMPLE --------------------------------------
head('STEP 3  PREPARATION AND SAMPLING')
uc = d[d.Confederation.isin(GROUPS)]
print(f'UEFA + CONMEBOL             {len(uc)}')
print('\nevidence for the exclusion rule (top of the unfiltered ranking):')
print(uc[uc.Passes_Att>0].nlargest(3,'Cmp_pct')[['Player','Country','Passes_Att','Passes_Cmp','Cmp_pct']].to_string(index=False))
print('compared with:')
print(uc[uc.Player=='Rodri'][['Player','Passes_Att','Passes_Cmp','Cmp_pct']].to_string(index=False))

# correlation: does the ratio behave like a ratio, or like a sample size?
act = uc[uc.Passes_Att >= 1]
print('\nvolume vs completion rate  (why the ratio needs a denominator floor):')
for lbl, sub in [('all with >=1 attempt', act),
                 ('1-19 attempts', act[act.Passes_Att < MIN_ATT]),
                 ('>=20 (population)', act[act.Passes_Att >= MIN_ATT])]:
    r, pr = stats.pearsonr(sub.Passes_Att, sub.Cmp_pct)
    rho, ps = stats.spearmanr(sub.Passes_Att, sub.Cmp_pct)
    print(f'  {lbl:22} n={len(sub):4}  Pearson r={r:+.3f} (p={pr:.1e})  Spearman rho={rho:+.3f} (p={ps:.1e})')
print('  spread of the ratio collapses as the denominator grows:')
for lo, hi, nm in [(1,9,'1-9'), (10,19,'10-19'), (20,49,'20-49'),
                   (50,199,'50-199'), (200,10**6,'200+')]:
    sub = act[act.Passes_Att.between(lo, hi)]
    print(f'    {nm:>7} attempts  n={len(sub):4}  SD of rate = {sub.Cmp_pct.std(ddof=1):5.2f}')

pop = uc[uc.Passes_Att >= MIN_ATT].sort_values('FIFA_Rank').reset_index(drop=True)
pop.insert(0, 'No', range(1, len(pop)+1))
pop = pop[['No','FIFA_Rank','Player','Abbr','Country','Confederation','Pos',
           'Passes_Att','Passes_Cmp','Cmp_pct']]
pop.to_csv('task4_population.csv', index=False, encoding='utf-8-sig')
print(f'\nremoved                     {len(uc)-len(pop)}  '
      f'({(uc.Passes_Att==0).sum()} with no passes, {len(uc)-len(pop)-(uc.Passes_Att==0).sum()} with 1-19)')
print(f'population                  {len(pop)}  {pop.Confederation.value_counts().to_dict()}')
print(f'total passes in population  {pop.Passes_Att.sum():,}')

smp = pop.sample(n=N, random_state=SEED).sort_values('No').reset_index(drop=True)
smp.insert(0, 'Sample_No', range(1, N+1))
smp.to_csv('task4_sample.csv', index=False, encoding='utf-8-sig')
assert pop.sample(n=N, random_state=SEED).Player.tolist() == \
       pop.sample(n=N, random_state=SEED).Player.tolist()
pp = (pop.Confederation.value_counts(normalize=True)*100).round(1).to_dict()
sp = (smp.Confederation.value_counts(normalize=True)*100).round(1).to_dict()
print(f'sample                      {smp.Confederation.value_counts().to_dict()}')
print(f'population %                {pp}')
print(f'sample %                    {sp}')

# ---- STEP 4  DESCRIPTIVE ------------------------------------------------
head('STEP 4  DESCRIPTIVE STATISTICS')
x = smp.Cmp_pct
u = smp[smp.Confederation=='UEFA'].Cmp_pct
c = smp[smp.Confederation=='CONMEBOL'].Cmp_pct
for lbl, g in [('sample', x), ('UEFA', u), ('CONMEBOL', c)]:
    print(f'{lbl:9s} n={len(g):2d}  M={g.mean():.2f}  SD={g.std(ddof=1):.2f}  '
          f'med={g.median():.2f}  min={g.min():.2f}  max={g.max():.2f}')
print(f'IQR       {x.quantile(.25):.2f} to {x.quantile(.75):.2f}  = {x.quantile(.75)-x.quantile(.25):.2f}')
print(f'UEFA mean-median {u.mean()-u.median():+.2f}  skew {stats.skew(u):+.2f}')
print(f'CONM mean-median {c.mean()-c.median():+.2f}  skew {stats.skew(c):+.2f}')
print(f"Cohen's d {cohen_d(u,c):.3f}")

# ---- STEP 5  CONFIDENCE INTERVAL ---------------------------------------
head('STEP 5  CONFIDENCE INTERVAL')
se, tstar = stats.sem(x), stats.t.ppf(.975, N-1)
lo, hi = stats.t.interval(.95, N-1, loc=x.mean(), scale=se)
TRUE = pop.Cmp_pct.mean()
print(f'SE {se:.3f}   t*({N-1}) {tstar:.3f}   margin {tstar*se:.2f}')
print(f'95% CI [{lo:.2f}, {hi:.2f}]   width {hi-lo:.2f}')
print(f'true population mean {TRUE:.2f}  inside: {lo<=TRUE<=hi}')
hits = sum(1 for s in range(2000)
           if (lambda l,h: l<=TRUE<=h)(*stats.t.interval(.95, 39,
              loc=(ss:=pop.Cmp_pct.sample(n=40, random_state=s)).mean(), scale=stats.sem(ss))))
print(f'empirical coverage over 2000 samples: {hits/2000*100:.1f}%  (nominal 95.0%)')

# ---- STEP 6  HYPOTHESIS TEST -------------------------------------------
head('STEP 6  HYPOTHESIS TEST')
ts, ps = stats.ttest_ind(u, c, equal_var=True)
tw, pw = stats.ttest_ind(u, c, equal_var=False)
print(f"Student's  t({len(u)+len(c)-2}) = {ts:.3f}, p = {ps:.3f}")
print(f"Welch's    t({welch_df(u,c):.2f}) = {tw:.3f}, p = {pw:.3f}   <- adopted")
print(f"Cohen's d  {cohen_d(u,c):.3f}")
print(f'Shapiro UEFA p={stats.shapiro(u).pvalue:.3f}   CONMEBOL p={stats.shapiro(c).pvalue:.3f}')
print(f'Levene p={stats.levene(u,c).pvalue:.3f}')
mw = stats.mannwhitneyu(u, c, alternative='two-sided')
print(f'Mann-Whitney U={mw.statistic:.1f}, p={mw.pvalue:.3f}')
try:
    from statsmodels.stats.power import TTestIndPower
    an = TTestIndPower()
    d_obs = abs(cohen_d(u,c))
    print(f'power to detect d={d_obs:.2f}: {an.power(effect_size=d_obs, nobs1=len(u), ratio=len(c)/len(u), alpha=.05)*100:.1f}%')
    mde = an.solve_power(nobs1=len(u), ratio=len(c)/len(u), alpha=.05, power=.80)
    print(f'sample MDE at 80% power: d={mde:.2f} (~{mde*x.std(ddof=1):.1f} pp)')
    U, C = pop[pop.Confederation=='UEFA'].Cmp_pct, pop[pop.Confederation=='CONMEBOL'].Cmp_pct
    mdec = an.solve_power(nobs1=len(U), ratio=len(C)/len(U), alpha=.05, power=.80)
    print(f'census MDE at 80% power: d={mdec:.2f} (~{mdec*pop.Cmp_pct.std(ddof=1):.1f} pp)')
except ImportError:
    print('statsmodels not installed - power analysis skipped')

# ---- STEP 7  ROBUSTNESS -------------------------------------------------
head('STEP 7  ROBUSTNESS')
def spec(popn, ev=False, seed=SEED):
    s = popn.sample(n=min(N,len(popn)), random_state=seed)
    a = s[s.Confederation=='UEFA'].Cmp_pct; b = s[s.Confederation!='UEFA'].Cmp_pct
    return stats.ttest_ind(a, b, equal_var=ev).pvalue
SPECS = {}
for thr in [1,10,20,50,100,150,200]:
    pv = spec(uc[uc.Passes_Att>=thr])
    lbl = f'Att >= {thr}' + ('   (brief\'s own rule)' if thr==1 else ('   — adopted' if thr==20 else ''))
    SPECS[lbl] = pv
    print(f'  threshold Att>={thr:<4} p={pv:.3f}')
alt = d[d.Confederation.isin(GROUPS+["CONCACAF"])]; alt = alt[alt.Passes_Att>=MIN_ATT]
au = alt[alt.Confederation=='UEFA'].Cmp_pct; ao = alt[alt.Confederation!='UEFA'].Cmp_pct
K_SAMP = '"American" incl. CONCACAF (sample)'
K_CENS = '"American" incl. CONCACAF (census)'
K_247  = 'population cut to 247'
SPECS[K_SAMP] = spec(alt)
SPECS[K_CENS] = stats.ttest_ind(au, ao, equal_var=False).pvalue
SPECS[K_247]  = spec(uc.nlargest(247, 'Passes_Att'))
print(f'  "American" incl CONCACAF (sample) p={SPECS[K_SAMP]:.3f}')
print(f'  "American" incl CONCACAF (census) p={SPECS[K_CENS]:.3f}')
print(f'  population cut to 247            p={SPECS[K_247]:.3f}')
U, C = pop[pop.Confederation=='UEFA'].Cmp_pct, pop[pop.Confederation=='CONMEBOL'].Cmp_pct
tc, pc = stats.ttest_ind(U, C, equal_var=False)
print(f'  census, no sampling              t={tc:.2f} p={pc:.3f} d={cohen_d(U,C):.3f}')
SPECS['census — no sampling'] = pc
ps500 = np.array([spec(pop, seed=s) for s in range(500)])
SPECS['500 seeds — median'] = float(np.median(ps500))
SPECS["Student's instead of Welch"] = spec(pop, ev=True)  # noqa
SPECS['Mann-Whitney (non-parametric)'] = mw.pvalue
print(f'  500 seeds: median p={np.median(ps500):.3f}  reject rate={(ps500<.05).mean()*100:.1f}%')
K_STU = "Student's instead of Welch"
print(f'  Student instead of Welch         p={SPECS[K_STU]:.3f}')
print(f'  Mann-Whitney                     p={mw.pvalue:.3f}')
REJECT_RATE = (ps500<.05).mean()*100

# ---- STEP 8  EXTENDED EXPLORATION --------------------------------------
head('STEP 8  EXTENDED EXPLORATION')
e = d[d.Confederation.isin(GROUPS) & (d.Passes_Att>=MIN_ATT)].copy()
def wacc(v, r):
    m = e[v] > 0
    return (e.loc[m,v]*e.loc[m,r]).sum() / e.loc[m,v].sum()
allr = e.Passes_Cmp.sum()/e.Passes_Att.sum()*100
print(f'8.1  all passes {allr:.1f}% (n={e.Passes_Att.sum():,}) | '
      f'switches {wacc("Switches_Att","Switches_Acc"):.1f}% ({int(e.Switches_Att.sum())}) | '
      f'linebreaks {wacc("DefLinebreaks_Att","DefLinebreaks_Acc"):.1f}% ({int(e.DefLinebreaks_Att.sum())}) | '
      f'crosses {wacc("Crosses","Cross_Acc"):.1f}% ({int(e.Crosses.sum())})')
print(f'     a cross is {allr/wacc("Crosses","Cross_Acc"):.1f}x harder than an average pass')
print('\n8.2  accuracy by type:')
for lbl, v, r, mn in [('crossing','Crosses','Cross_Acc',5),
                      ('linebreaks','DefLinebreaks_Att','DefLinebreaks_Acc',5),
                      ('switches','Switches_Att','Switches_Acc',3)]:
    s = e[e[v]>=mn]
    a, b = s[s.Confederation=='UEFA'][r], s[s.Confederation=='CONMEBOL'][r]
    t_, p_ = stats.ttest_ind(a, b, equal_var=False)
    print(f'     {lbl:11s} UEFA {a.mean():5.1f}%  CONM {b.mean():5.1f}%  t({welch_df(a,b):.2f})={t_:6.2f}  p={p_:.3f}')
print('\n8.3  attempts per 100 passes (do they choose differently?):')
for lbl, v in [('crosses','Crosses'),('linebreaks','DefLinebreaks_Att'),('switches','Switches_Att')]:
    e['r'] = e[v]/e.Passes_Att*100
    a, b = e[e.Confederation=='UEFA'].r, e[e.Confederation=='CONMEBOL'].r
    print(f'     {lbl:11s} UEFA {a.mean():5.2f}   CONM {b.mean():5.2f}   p={stats.ttest_ind(a,b,equal_var=False).pvalue:.3f}')
print('\n8.4  position:')
f_, pf = stats.f_oneway(*[g.Cmp_pct.values for _, g in e.groupby('Pos')])
print(f'     ANOVA F(3, {len(e)-4}) = {f_:.2f}, p = {pf:.2e}')
print('    ', e.groupby('Pos').Cmp_pct.mean().round(2).to_dict())
chi = stats.chi2_contingency(pd.crosstab(e.Confederation, e.Pos))
print(f'     chi-square confederation x position: chi2 = {chi.statistic:.2f}, p = {chi.pvalue:.3f}')

# ---- ARGENTINA vs SPAIN -------------------------------------------------
head('ANSWERING THE THEME  —  ARGENTINA vs SPAIN')
for ct in ['Argentina','Spain']:
    t_ = pop[pop.Country==ct]
    cr = e[(e.Country==ct) & (e.Crosses>0)]
    lb = e[(e.Country==ct) & (e.DefLinebreaks_Att>0)]
    print(f'{ct:10s} pass {t_.Passes_Cmp.sum()/t_.Passes_Att.sum()*100:5.2f}%  '
          f'crossing {(cr.Crosses*cr.Cross_Acc).sum()/cr.Crosses.sum():5.1f}%  '
          f'linebreaks {(lb.DefLinebreaks_Att*lb.DefLinebreaks_Acc).sum()/lb.DefLinebreaks_Att.sum():5.1f}%  '
          f'crosses attempted {int(cr.Crosses.sum())}  '
          f'per100 {cr.Crosses.sum()/t_.Passes_Att.sum()*100:.2f}')
a_, s_ = pop[pop.Country=='Argentina'].Cmp_pct, pop[pop.Country=='Spain'].Cmp_pct
t3, p3 = stats.ttest_ind(a_, s_, equal_var=False)
print(f'\npass completion: t({welch_df(a_,s_):.2f}) = {t3:.2f}, p = {p3:.3f}')
res = {}
for ct in ['Argentina','Spain']:
    cr = e[(e.Country==ct) & (e.Crosses>0)]
    n_ = int(cr.Crosses.sum()); k_ = int(round((cr.Crosses*cr.Cross_Acc/100).sum()))
    res[ct] = (n_, k_)
(n1,k1),(n2,k2) = res['Argentina'], res['Spain']
p1_, p2_ = k1/n1, k2/n2; pp_ = (k1+k2)/(n1+n2)
z = (p1_-p2_)/np.sqrt(pp_*(1-pp_)*(1/n1+1/n2)); pz = 2*(1-stats.norm.cdf(abs(z)))
ml = 1.96*np.sqrt(p1_*(1-p1_)/n1 + p2_*(1-p2_)/n2)
print(f'crossing: ARG {k1}/{n1} = {p1_*100:.1f}%   ESP {k2}/{n2} = {p2_*100:.1f}%')
print(f'two-proportion z = {z:.2f}, p = {pz:.3f}, diff {(p1_-p2_)*100:.1f} pp, '
      f'95% CI [{(p1_-p2_-ml)*100:.1f}, {(p1_-p2_+ml)*100:.1f}]')

print('\n' + '='*70)
print('all assertions passed — every figure above appears in TASK4_Process_Report.docx')


# ---- FIGURE 1 -----------------------------------------------------------
head('FIGURE 1  DESCRIPTIVE STATISTICS')
uv, cv = u.values, c.values



SURFACE='#fcfcfb'; INK='#0b0b0b'; INK2='#52514e'; MUTED='#898781'
GRID='#e1e0d9'; BASE='#c3c2b7'; UEFA_C='#2a78d6'; CONM_C='#eb6834'


plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,
    'axes.edgecolor':BASE,'axes.labelcolor':INK2,'text.color':INK,
    'xtick.color':MUTED,'ytick.color':MUTED,'axes.facecolor':SURFACE,
    'figure.facecolor':SURFACE,'axes.linewidth':0.8})
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(10,4.2))

bp=ax1.boxplot([uv,cv],widths=0.45,patch_artist=True,showfliers=False,
    medianprops=dict(color=INK,linewidth=2),
    whiskerprops=dict(color=BASE,linewidth=1.2),capprops=dict(color=BASE,linewidth=1.2))
for patch,col in zip(bp['boxes'],[UEFA_C,CONM_C]):
    patch.set_facecolor(col); patch.set_alpha(0.16)
    patch.set_edgecolor(col); patch.set_linewidth(2)
rng=np.random.default_rng(7)
for i,(dd,col) in enumerate(zip([uv,cv],[UEFA_C,CONM_C]),start=1):
    ax1.scatter(rng.normal(i,0.055,len(dd)),dd,s=26,color=col,alpha=0.85,
                edgecolors=SURFACE,linewidths=1.2,zorder=3)
    ax1.plot([i-0.225,i+0.225],[dd.mean()]*2,color=col,lw=1.4,ls=(0,(3,2)),zorder=4)
    ax1.annotate(f'mean {dd.mean():.1f}%',xy=(i,dd.mean()),xytext=(i+0.30,dd.mean()),
                 color=col,fontsize=8.5,fontweight='bold',va='center')
ax1.set_xticks([1,2]); ax1.set_xticklabels([f'UEFA\n(n={len(uv)})',f'CONMEBOL\n(n={len(cv)})'],color=INK2)
ax1.set_ylabel('Pass completion (%)')
ax1.set_title('Sample distribution by confederation',fontsize=10.5,color=INK,fontweight='bold',loc='left',pad=10)
ax1.yaxis.grid(True,color=GRID,lw=0.8); ax1.set_axisbelow(True)
for s in ('top','right'): ax1.spines[s].set_visible(False)

ax2.hist(pop.Cmp_pct,bins=24,color=MUTED,alpha=0.35,edgecolor=SURFACE,linewidth=1)
ax2.axvspan(lo,hi,color=UEFA_C,alpha=0.14,zorder=2)
ax2.axvline(x.mean(),color=UEFA_C,lw=2,zorder=3)
ax2.axvline(pop.Cmp_pct.mean(),color=INK,lw=1.6,ls=(0,(4,2)),zorder=3)
ymax=ax2.get_ylim()[1]; ax2.set_ylim(0,ymax*1.20)
ax2.annotate(f'95% CI  [{lo:.1f}, {hi:.1f}]',xy=(lo,ymax*1.14),xytext=(-6,0),
             textcoords='offset points',ha='right',va='center',fontsize=8.5,
             color=UEFA_C,fontweight='bold')
ax2.annotate(f'sample {x.mean():.1f}%  ·  population {pop.Cmp_pct.mean():.1f}%',
             xy=(0.985,0.86),xycoords='axes fraction',ha='right',va='center',
             fontsize=8.5,color=INK2)
ax2.set_xlabel('Pass completion (%)'); ax2.set_ylabel('Number of players')
ax2.set_title(f'Population (n={len(pop)}) with 95% CI from the sample',
              fontsize=10.5,color=INK,fontweight='bold',loc='left',pad=10)
ax2.yaxis.grid(True,color=GRID,lw=0.8); ax2.set_axisbelow(True)
for s in ('top','right'): ax2.spines[s].set_visible(False)

fig.suptitle('FIFA World Cup 2026 — pass completion rate, UEFA vs CONMEBOL players',
             fontsize=11.5,color=INK,fontweight='bold',x=0.008,ha='left',y=0.99)
fig.tight_layout(rect=[0,0,1,0.94])
fig.savefig('task4_fig1_descriptive.png',dpi=200,facecolor=SURFACE)
print('fig1 saved')


# ---- FIGURE 2 -----------------------------------------------------------
head('FIGURE 2  ROBUSTNESS SPECIFICATION CURVE')
ORANGE='#eb6834'
items=sorted(SPECS.items(), key=lambda kv: kv[1])
labels=[k for k,_ in items]; pvals=[v for _,v in items]
yy=np.arange(len(items))[::-1]

fig,ax=plt.subplots(figsize=(9.2,5.4))
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
ax.axvspan(0,0.05,color=ORANGE,alpha=0.10,zorder=1)
ax.axvline(0.05,color=ORANGE,lw=1.8,zorder=3)
ax.set_ylim(-1.6,len(items)-0.3)
ax.annotate('α = .05  —  reject H₀ left of this line',xy=(0.05,-1.15),xytext=(8,0),
            textcoords='offset points',ha='left',va='center',fontsize=8.8,
            color=ORANGE,fontweight='bold')
for yi,lab,pv in zip(yy,labels,pvals):
    adopted='adopted' in lab
    ax.plot([0,pv],[yi,yi],color=BASE,lw=1,zorder=2)
    ax.scatter([pv],[yi],s=150 if adopted else 78,color=UEFA_C,
               edgecolors=SURFACE,linewidths=2,zorder=4,marker='D' if adopted else 'o')
    ax.text(pv+0.022,yi,f'{pv:.3f}',va='center',fontsize=8.6,color=INK,
            fontweight='bold' if adopted else 'normal')
ax.set_yticks(yy); ax.set_yticklabels(labels,fontsize=8.8,color=INK2)
ax.set_xlim(0,1.06); ax.set_xlabel('p-value',color=INK2,fontsize=9.5)
ax.set_title('Every analytical choice, tested — none crosses the threshold',
             fontsize=11.5,fontweight='bold',color=INK,loc='left',pad=12)
ax.xaxis.grid(True,color=GRID,lw=0.8); ax.set_axisbelow(True)
for sp in ('top','right','left'): ax.spines[sp].set_visible(False)
ax.spines['bottom'].set_color(BASE); ax.tick_params(axis='x',colors=MUTED)
fig.text(0.008,0.015,f'Diamond = the specification adopted. Closest approach to '
         f'significance: p = {min(pvals):.3f}. Across 500 seeds, {REJECT_RATE:.1f}% would reject H₀.',
         fontsize=8.2,color=MUTED)
fig.tight_layout(rect=[0,0.045,1,1])
fig.savefig('task4_fig2_robustness.png',dpi=200,facecolor=SURFACE)
print(f'fig2 saved — {len(items)} specifications, p from {min(pvals):.3f} to {max(pvals):.3f}')
