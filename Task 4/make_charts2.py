"""Addendum figure: risk gradient + confederation gap by pass type."""
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd, numpy as np
from scipy import stats

SURFACE='#fcfcfb'; INK='#0b0b0b'; INK2='#52514e'; MUTED='#898781'
GRID='#e1e0d9'; BASE='#c3c2b7'
UEFA_C='#2a78d6'; CONM_C='#eb6834'; SEQ='#2a78d6'

d=pd.read_excel('WC2026_Player_Passing_FIFA_FULL.xlsx', sheet_name='Player Passing')
d=d[d.Confederation.isin(['UEFA','CONMEBOL'])]; d=d[d.Passes_Att>=20].copy()
d['Cmp_pct']=d.Passes_Cmp/d.Passes_Att*100
def wacc(vol,rate):
    m=d[vol]>0; return (d.loc[m,vol]*d.loc[m,rate]).sum()/d.loc[m,vol].sum()

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,
    'axes.edgecolor':BASE,'axes.labelcolor':INK2,'text.color':INK,
    'xtick.color':MUTED,'ytick.color':MUTED,'axes.facecolor':SURFACE,
    'figure.facecolor':SURFACE,'axes.linewidth':0.8})
fig,(ax1,ax2)=plt.subplots(1,2,figsize=(10.5,4.3))

# ---- Panel 1: risk gradient (single measure, one hue) ----
labs=['All passes','Switches\nof play','Defensive\nlinebreaks','Crosses']
vals=[d.Passes_Cmp.sum()/d.Passes_Att.sum()*100, wacc('Switches_Att','Switches_Acc'),
      wacc('DefLinebreaks_Att','DefLinebreaks_Acc'), wacc('Crosses','Cross_Acc')]
vols=[int(d.Passes_Att.sum()),int(d.Switches_Att.sum()),
      int(d.DefLinebreaks_Att.sum()),int(d.Crosses.sum())]
y=np.arange(len(labs))[::-1]
ax1.barh(y,vals,height=0.6,color=SEQ,alpha=0.85,edgecolor=SURFACE,linewidth=2)
for yi,v,vol in zip(y,vals,vols):
    ax1.text(v+1.5,yi,f'{v:.1f}%',va='center',fontsize=9.5,fontweight='bold',color=INK)
    ax1.text(1.5,yi,f'n={vol:,}',va='center',fontsize=7.8,color=SURFACE)
ax1.set_yticks(y); ax1.set_yticklabels(labs,color=INK2,fontsize=9)
ax1.set_xlim(0,104); ax1.set_xlabel('Completion rate (%)')
ax1.set_title('Not all passes are equal',fontsize=10.5,fontweight='bold',color=INK,loc='left',pad=10)
ax1.xaxis.grid(True,color=GRID,lw=0.8); ax1.set_axisbelow(True)
for s in ('top','right','left'): ax1.spines[s].set_visible(False)

# ---- Panel 2: UEFA vs CONMEBOL by pass type (2 series) ----
types=[('All passes','Cmp_pct',None,0),('Crossing','Cross_Acc','Crosses',5),
       ('Def. linebreaks','DefLinebreaks_Acc','DefLinebreaks_Att',5),
       ('Switches','Switches_Acc','Switches_Att',3)]
um,cm,pv=[],[],[]
for lbl,rate,vol,mn in types:
    s=d if vol is None else d[d[vol]>=mn]
    u=s[s.Confederation=='UEFA'][rate]; c=s[s.Confederation=='CONMEBOL'][rate]
    um.append(u.mean()); cm.append(c.mean()); pv.append(stats.ttest_ind(u,c,equal_var=False).pvalue)
xp=np.arange(len(types)); w=0.36
ax2.bar(xp-w/2-0.01,um,w,label='UEFA',color=UEFA_C,alpha=0.9,edgecolor=SURFACE,linewidth=2)
ax2.bar(xp+w/2+0.01,cm,w,label='CONMEBOL',color=CONM_C,alpha=0.9,edgecolor=SURFACE,linewidth=2)
for i,(a,b,p) in enumerate(zip(um,cm,pv)):
    top=max(a,b)
    if p<0.05:
        ax2.text(i,top+7,f'p = {p:.3f}',ha='center',fontsize=8.5,fontweight='bold',color=INK)
        ax2.plot([i-w/2,i+w/2],[top+5.2]*2,color=INK,lw=1.2)
    else:
        ax2.text(i,top+5,'n.s.',ha='center',fontsize=8.5,color=MUTED)
ax2.set_xticks(xp); ax2.set_xticklabels([t[0] for t in types],color=INK2,fontsize=8.6)
ax2.set_ylabel('Completion rate (%)'); ax2.set_ylim(0,108)
ax2.set_title('Identical overall — different where it is risky',
              fontsize=10.5,fontweight='bold',color=INK,loc='left',pad=10)
ax2.yaxis.grid(True,color=GRID,lw=0.8); ax2.set_axisbelow(True)
for s in ('top','right'): ax2.spines[s].set_visible(False)
ax2.legend(frameon=False,fontsize=9,loc='upper center',ncol=2,
           bbox_to_anchor=(0.5,-0.13),labelcolor=INK2,handlelength=1.4,
           columnspacing=2.2)

fig.suptitle('World Cup 2026 — what the passing and crossing columns reveal',
             fontsize=11.5,fontweight='bold',color=INK,x=0.008,ha='left',y=0.99)
fig.tight_layout(rect=[0,0.045,1,0.94])
fig.savefig('task4_exploration.png',dpi=200,facecolor=SURFACE)
print('saved')
