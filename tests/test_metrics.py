import numpy as np
import pytest
from scipy.stats import wasserstein_distance,ttest_ind
from spa.metrics import Reference,safe_cor,relationship,mean_ci,welch,score

def test_undefined():
    assert np.isnan(safe_cor([1,1],[1,2]))
    assert np.isnan(safe_cor([1,np.nan],[2,3]))

def test_agreement_and_inflation():
    x=np.linspace(-.4,.5,37)
    perfect=relationship(x,x)
    assert perfect['correlation_mae']==0
    for k in ('icc','ccc','pattern_r'):assert perfect[k]==pytest.approx(1)
    inflated=relationship(x,x*1.5+.2)
    assert inflated['pattern_r']==pytest.approx(1)
    assert inflated['icc']<1 and inflated['ccc']<1 and inflated['correlation_mae']>0

def test_icc_anova():
    x=np.array([-.3,.1,.2,.4,.6]);y=np.array([-.5,.2,.6,.7,.9]);a=np.column_stack([x,y]);n,k=a.shape
    msr=k*np.var(a.mean(axis=1),ddof=1);msc=n*np.var(a.mean(axis=0),ddof=1)
    residual=a-a.mean(axis=1)[:,None]-a.mean(axis=0)[None,:]+a.mean()
    mse=(residual**2).sum()/((n-1)*(k-1))
    icc=(msr-mse)/(msr+(k-1)*mse+k*(msc-mse)/n)
    assert relationship(x,y)['icc']==pytest.approx(icc,abs=1e-14)

@pytest.mark.parametrize('s',[[0,1],[1,1],[0,2,3],[.2,.4,.8,.9,.92]])
def test_wasserstein(reference,study,s):
    ref=Reference(reference,study);v=np.sort(s)
    assert ref.wasserstein(v,0)==pytest.approx(wasserstein_distance(ref.values[0],v)/ref.sd[0],abs=1e-13)

def test_welch_and_ci():
    a=np.array([1,2,4,8,10]);b=np.array([1,3,3,4,5,6])
    w=welch(a,b);direct=ttest_ind(a,b,equal_var=False)
    assert w['p_adjusted']==pytest.approx(min(1,direct.pvalue*28))
    assert w['welch_df']==pytest.approx(direct.df)
    ci=mean_ci(a);assert ci['upper']==pytest.approx(a.mean()+1.96*a.std(ddof=1)/np.sqrt(len(a)))
    assert np.isnan(mean_ci([1])['upper'])

def test_constant_synthetic_and_missing(reference,study):
    f=reference.iloc[:100].copy();f[study['psychological_predictors'][0]]=10
    ref=Reference(reference,study);d,r,g1,g2=score(f,ref)
    assert d.iloc[0].sd_ratio==0
    assert np.isnan(g2[0]['icc'])
    f[study['psychological_predictors'][1]]=np.nan
    assert np.isnan(score(f,ref)[2]['smd'])
