"""Matches the supplied R computation; sample variance for ICC, population for CCC."""
import itertools
import numpy as np
import pandas as pd
from scipy import stats

DIST = ['smd','sd_ratio','sd_error','wasserstein']
REL = ['correlation_mae','icc','ccc','pattern_r']
METRIC_LABELS = {'smd':'Mean |SMD|','sd_ratio':'Mean SD ratio','sd_error':'Mean |SD ratio − 1|',
 'wasserstein':'Normalised Wasserstein','correlation_mae':'Correlation MAE','icc':'ICC(A,1)',
 'ccc':'Lin’s CCC','pattern_r':'Pearson pattern r'}
GUIDE = {
 'smd':'Mean absolute gap in means divided by the root mean of the two variances. Lower is closer.',
 'sd_ratio':'Synthetic sample SD divided by human sample SD, averaged across variables. Target 1.',
 'sd_error':'Mean absolute deviation of each SD ratio from 1. Lower is closer.',
 'wasserstein':'Empirical Wasserstein-1 distance divided by the human sample SD. Lower is closer.',
 'correlation_mae':'Mean absolute gap between corresponding human and synthetic correlations. Lower is closer.',
 'icc':'Single-measure absolute-agreement ICC across corresponding coefficients. Higher is closer; target 1.',
 'ccc':'Lin’s concordance using population moments across corresponding coefficients. Higher is closer; target 1.',
 'pattern_r':'Pearson correlation across the coefficient vectors. Higher means closer pattern correspondence, not necessarily magnitude agreement.'}

def safe_cor(x,y):
    x,y=np.asarray(x,float),np.asarray(y,float)
    ok=np.isfinite(x)&np.isfinite(y);x,y=x[ok],y[ok]
    if len(x)<2 or np.ptp(x)==0 or np.ptp(y)==0:return np.nan
    return float(np.corrcoef(x,y)[0,1])

def relationship(x,y):
    x,y=np.asarray(x,float),np.asarray(y,float);j=len(x)
    if j<2 or not (np.isfinite(x).all() and np.isfinite(y).all()):return dict.fromkeys(REL,np.nan)
    vx,vy=np.var(x,ddof=1),np.var(y,ddof=1);cv=np.cov(x,y,ddof=1)[0,1];d=(x.mean()-y.mean())**2
    di=(1-1/j)*(vx+vy)+2*cv/j+d;dc=(vx+vy)*(j-1)/j+d
    return dict(zip(REL,[np.mean(abs(x-y)),2*cv/di if di else np.nan,
                         2*cv*(j-1)/j/dc if dc else np.nan,safe_cor(x,y)]))

class Reference:
    def __init__(self,human,study):
        self.ps=study['psychological_predictors'];self.os=list(study['outcomes']);self.n=len(human)
        self.values=[np.sort(human[f].dropna().to_numpy(float)) for f in self.ps]
        if any(len(v)<2 or np.std(v,ddof=1)==0 for v in self.values):
            raise ValueError('Each reference psychological variable needs at least two observed, varying values.')
        self.mean=np.array([v.mean() for v in self.values]);self.sd=np.array([v.std(ddof=1) for v in self.values])
        self.r=np.array([[safe_cor(human[f],human[o]) for o in self.os] for f in self.ps])
        self.main=np.array([f!='B1PANXIE' for f in self.ps]);self._weights={}
        if not np.isfinite(self.r[self.main]).all():raise ValueError('Reference needs all 37 primary correlations at both waves.')

    def wasserstein(self,s,j):
        h=self.values[j];key=(len(h),len(s))
        if key not in self._weights:
            cuts=np.unique(np.r_[np.arange(len(h)+1)/len(h),np.arange(len(s)+1)/len(s)])
            w=np.diff(cuts);mid=cuts[:-1]+w/2
            self._weights[key]=(w,np.minimum(len(h)-1,np.ceil(mid*len(h)).astype(int)-1),np.minimum(len(s)-1,np.ceil(mid*len(s)).astype(int)-1))
        w,hi,si=self._weights[key]
        return float(np.sum(w*np.abs(h[hi]-s[si]))/self.sd[j])

def score(frame,ref):
    d=[];rs=[]
    for j,f in enumerate(ref.ps):
        v=np.sort(frame[f].dropna().to_numpy(float));n=len(v)
        row=dict(n=n,mean=np.nan,sd=np.nan,**dict.fromkeys(DIST,np.nan))
        if n>=2:
            avg=v.mean();s=v.std(ddof=1);ratio=s/ref.sd[j]
            row.update(mean=avg,sd=s,smd=abs(avg-ref.mean[j])/np.sqrt((s*s+ref.sd[j]**2)/2),
                       sd_ratio=ratio,sd_error=abs(ratio-1),wasserstein=ref.wasserstein(v,j))
        d.append(row);rs.append([safe_cor(frame[f],frame[o]) for o in ref.os])
    d=pd.DataFrame(d,index=ref.ps);rs=np.array(rs)
    g1={f:float(d[f].mean()) for f in DIST} if d.smd.notna().all() else dict.fromkeys(DIST,np.nan)
    g2=[relationship(ref.r[ref.main,k],rs[ref.main,k]) for k in range(2)]
    return d,rs,g1,g2

def mean_ci(v):
    v=np.asarray(v,float);v=v[np.isfinite(v)];n=len(v)
    m=float(v.mean()) if n else np.nan;se=float(v.std(ddof=1)/np.sqrt(n)) if n>=2 else np.nan
    return dict(n=n,mean=m,lower=m-1.96*se,upper=m+1.96*se)

def welch(a,b,family=28):
    a,b=np.asarray(a,float),np.asarray(b,float);a=a[np.isfinite(a)];b=b[np.isfinite(b)]
    if min(len(a),len(b))<2:return None
    va,vb=a.var(ddof=1)/len(a),b.var(ddof=1)/len(b);se=np.sqrt(va+vb)
    if se==0:return None
    df=(va+vb)**2/(va*va/(len(a)-1)+vb*vb/(len(b)-1));delta=a.mean()-b.mean()
    q=stats.t.ppf(1-.05/(2*family),df);p=min(1.,family*2*stats.t.sf(abs(delta/se),df))
    return dict(difference=delta,lower=delta-q*se,upper=delta+q*se,p_adjusted=p,
                welch_df=df,se=se,n_first=len(a),n_second=len(b),significant=bool(p<.05))

def summarise(runs,method_ids=None):
    methods=sorted(runs.method.unique()) if method_ids is None else sorted(method_ids)
    families=[('distribution',0,m,m) for m in DIST]+[('relationship',k,m,f'midus{k}_{m}') for k in (2,3) for m in REL]
    summaries=[];pairs=[];family=max(1,len(methods)*(len(methods)-1)//2)
    for domain,wave,metric,col in families:
        for method in methods:
            summaries.append(dict(domain=domain,wave=wave,metric=metric,method=method,**mean_ci(runs.loc[runs.method==method,col])))
        for a,b in itertools.combinations(methods,2):
            result=welch(runs.loc[runs.method==a,col],runs.loc[runs.method==b,col],family)
            if result:pairs.append(dict(domain=domain,wave=wave,metric=metric,first=a,second=b,family_size=family,**result))
    columns=['domain','wave','metric','first','second','family_size','difference','lower','upper','p_adjusted','welch_df','se','n_first','n_second','significant']
    return pd.DataFrame(summaries),pd.DataFrame(pairs,columns=columns)
