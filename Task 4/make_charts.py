"""Descriptive-statistics figures for Task 4 (pass completion %)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
from scipy import stats

# --- design tokens ---
SURFACE='#fcfcfb'; INK='#0b0b0b'; INK2='#52514e'; MUTED='#898781'
GRID='#e1e0d9'; BASE='#c3c2b7'
UEFA_C='#2a78d6'; CONM_C='#eb6834'          # validated categorical slots 1 & 2

pop=pd.read_csv('pass_population.csv'); smp=pd.read_csv('pass_sample_random.csv')
u=smp[smp.Confederation=='UEFA']['Cmp_pct'].values
c=smp[smp.Confederation=='CONMEBOL']['Cmp_pct'].values
x=smp['Cmp_pct']
lo,hi=stats.t.interval(0.95,len(x)-1,loc=x.mean(),scale=stats.sem(x))

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,
    'axes.edgecolor':BASE,'axes.labelcolor':INK2,'text.color':INK,
    'xtick.color':MUTED,'ytick.color':MUTED,'axes.facecolor':SURFACE,
    'figure.facecolor':SURFACE,'axes.linewidth':0.8})

fig,(ax1,ax2)=plt.subplots(1,2,figsize=(10,4.2))

# ---- Panel 1: boxplot + jitter (sample, n=40) ----
data=[u,c]; cols=[UEFA_C,CONM_C]; labs=[f'UEFA\n(n={len(u)})',f'CONMEBOL\n(n={len(c)})']
bp=ax1.boxplot(data,widths=0.45,patch_artist=True,showfliers=False,
               medianprops=dict(color=INK,linewidth=2),
               whiskerprops=dict(color=BASE,linewidth=1.2),
               capprops=dict(color=BASE,linewidth=1.2))
for patch,col in zip(bp['boxes'],cols):
    patch.set_facecolor(col); patch.set_alpha(0.16)
    patch.set_edgecolor(col); patch.set_linewidth(2)
rng=np.random.default_rng(7)
for i,(d,col) in enumerate(zip(data,cols),start=1):
    ax1.scatter(rng.normal(i,0.055,len(d)),d,s=26,color=col,alpha=0.85,
                edgecolors=SURFACE,linewidths=1.2,zorder=3)
for i,(d,col) in enumerate(zip(data,cols),start=1):
    ax1.annotate(f'mean {d.mean():.1f}%',xy=(i,d.mean()),xytext=(i+0.30,d.mean()),
                 color=col,fontsize=8.5,fontweight='bold',va='center')
    ax1.plot([i-0.225,i+0.225],[d.mean()]*2,color=col,lw=1.4,ls=(0,(3,2)),zorder=4)
ax1.set_xticks([1,2]); ax1.set_xticklabels(labs,color=INK2,fontsize=9)
ax1.set_ylabel('Pass completion (%)')
ax1.set_title('Sample distribution by confederation',fontsize=10.5,color=INK,
              fontweight='bold',loc='left',pad=10)
ax1.yaxis.grid(True,color=GRID,lw=0.8); ax1.set_axisbelow(True)
for s in ('top','right'): ax1.spines[s].set_visible(False)

# ---- Panel 2: population histogram + sample mean & 95% CI ----
ax2.hist(pop['Cmp_pct'],bins=24,color=MUTED,alpha=0.35,edgecolor=SURFACE,linewidth=1)
ax2.axvspan(lo,hi,color=UEFA_C,alpha=0.14,zorder=2)
ax2.axvline(x.mean(),color=UEFA_C,lw=2,zorder=3)
ax2.axvline(pop['Cmp_pct'].mean(),color=INK,lw=1.6,ls=(0,(4,2)),zorder=3)
ymax=ax2.get_ylim()[1]; ax2.set_ylim(0,ymax*1.20)
ax2.annotate(f'95% CI  [{lo:.1f}, {hi:.1f}]',xy=(lo,ymax*1.14),xytext=(-6,0),
             textcoords='offset points',ha='right',va='center',
             fontsize=8.5,color=UEFA_C,fontweight='bold')
ax2.annotate(f'sample {x.mean():.1f}%  ·  population {pop["Cmp_pct"].mean():.1f}%',
             xy=(0.985,0.86),xycoords='axes fraction',
             ha='right',va='center',fontsize=8.5,color=INK2)
ax2.set_xlabel('Pass completion (%)'); ax2.set_ylabel('Number of players')
ax2.set_title(f'Population (n={len(pop)}) with 95% CI from the sample',
              fontsize=10.5,color=INK,fontweight='bold',loc='left',pad=10)
ax2.yaxis.grid(True,color=GRID,lw=0.8); ax2.set_axisbelow(True)
for s in ('top','right'): ax2.spines[s].set_visible(False)

fig.suptitle('FIFA World Cup 2026 — pass completion rate, UEFA vs CONMEBOL players',
             fontsize=11.5,color=INK,fontweight='bold',x=0.008,ha='left',y=0.99)
fig.tight_layout(rect=[0,0,1,0.94])
fig.savefig('task4_descriptive_stats.png',dpi=200,facecolor=SURFACE)
print('saved task4_descriptive_stats.png')
