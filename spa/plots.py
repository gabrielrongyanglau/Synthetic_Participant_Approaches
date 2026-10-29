import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import textwrap
from .metrics import METRIC_LABELS

COLORS=['#0072B2','#E69F00','#009E73','#CC79A7','#D55E00','#56B4E9','#332288','#666666']
def performance(summary,metric,wave,metric_label=None):
    d=summary[(summary.metric==metric)&(summary.wave==wave)].sort_values('method')
    fig,ax=plt.subplots(figsize=(8,4));x=np.arange(len(d))
    for i,(_,r) in enumerate(d.iterrows()):
        ax.scatter(i,r['mean'],color=COLORS[int(r.method)-1],s=45,zorder=3)
        if np.isfinite(r.lower) and np.isfinite(r.upper):ax.vlines(i,r.lower,r.upper,color=COLORS[int(r.method)-1],linewidth=2)
    ax.set_xticks(x,['M'+str(int(m)) for m in d.method]);ax.set_ylabel(textwrap.fill(metric_label or METRIC_LABELS[metric],36));ax.spines[['top','right']].set_visible(False)
    if metric=='sd_ratio':ax.axhline(1,color='gray',ls='--',lw=1)
    ax.set_title('Average across generated datasets'+(' — life satisfaction at MIDUS '+str(wave) if wave else ''));fig.tight_layout();return fig

def correlations(variables,human,methods,wave,study,show_labels=False):
    fig,ax=plt.subplots(figsize=(8,5));d=variables.merge(human[['code',f'midus{wave}_r']],on='code')
    d=d[d.code!='B1PANXIE']
    ax.plot([-1,1],[-1,1],color='gray',ls='--',lw=1,label='Equal human and generated correlations')
    for m in methods:
        g=d[d.method==m];ax.scatter(g[f'midus{wave}_r'],g[f'midus{wave}_mean_r'],s=24,alpha=.8,color=COLORS[m-1],label=f'M{m}')
        if show_labels and len(methods)==1:
            for _,r in g.iterrows():ax.annotate(study['variables'][r.code].get('construct',r.code),(r[f'midus{wave}_r'],r[f'midus{wave}_mean_r']),fontsize=6,xytext=(3,2),textcoords='offset points')
    ax.set(xlim=(-1.05,1.05),ylim=(-1.05,1.05),xlabel='Human correlation with life satisfaction',ylabel='Average generated correlation with life satisfaction',title=f'Life satisfaction at MIDUS {wave}')
    ax.legend(fontsize=8,ncol=3,loc='upper center',bbox_to_anchor=(.5,-.16));ax.spines[['top','right']].set_visible(False);fig.tight_layout();return fig

def figure_bytes(fig,format):
    b=io.BytesIO();fig.savefig(b,format=format,dpi=180,bbox_inches='tight');return b.getvalue()
