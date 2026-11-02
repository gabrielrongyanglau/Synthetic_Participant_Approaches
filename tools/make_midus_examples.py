"""Build the MIDUS demonstration inputs from the linked MIDUS 2 and 3 file, without publishing any participant's record.

Usage: python tools/make_midus_examples.py MIDUS2_3_linked_cleaned.csv pools/membership.csv

The MIDUS file is available to registered users through ICPSR and is never stored in this repository.

- SPA4: the observed demographic proportions of all 2,709 participants (the same rule as the original study's quota template).
- SPA5 and SPA6: 50 generated participants that reproduce the statistics of the calibration pool (542 people), the pool
  from which the original study drew its pilots.
- SPA7 and SPA8: 100 generated participants that reproduce the statistics of the evaluation pool (2,167 people). SPA7 uses
  their demographics and SPA8 their demographics and psychological scores.

Generated participants come from a Gaussian copula fitted to each pool: every variable keeps its observed distribution
(each generated value is one of the values observed in MIDUS) and the variables keep their observed rank correlations.
Spouse or partner support and strain are left blank at the rate observed for each marital status. Among many candidate
samples, the one closest to the pool's means, standard deviations and correlations is kept. No generated record matches
any real participant on every column.
"""
import sys,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.stats import norm,rankdata
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from spa.study import load_study,clean_frame,selected_fields,predictors,OUTCOMES
from spa.workflow import quota_template

SPOUSE=['B1SSPEMP','B1SSPCRI']

def scores(x):
    """Normal scores of the observed values (average ranks for ties)."""
    z=pd.Series(np.nan,index=x.index);o=x.dropna()
    z[o.index]=norm.ppf((rankdata(o)-.5)/len(o));return z

def fit(pool,fields):
    z=pd.DataFrame({f:scores(pool[f]) for f in fields})
    r=z.corr(min_periods=30).fillna(0).to_numpy();np.fill_diagonal(r,1)
    w,v=np.linalg.eigh(r);r=(v*np.clip(w,1e-6,None))@v.T;d=np.sqrt(np.diag(r));r=r/np.outer(d,d)
    observed={f:np.sort(pool[f].dropna().to_numpy()) for f in fields}
    married=pool['B1PB19']
    blank={m:{s:float(pool.loc[married.eq(m),s].isna().mean()) for s in SPOUSE} for m in married.dropna().unique()}
    return r,observed,blank

def draw(r,observed,blank,fields,n,rng):
    z=rng.multivariate_normal(np.zeros(len(fields)),r,size=n);u=norm.cdf(z)
    out=pd.DataFrame({f:np.quantile(observed[f],u[:,i],method='inverted_cdf') for i,f in enumerate(fields)})
    u=rng.random(n)  # one draw per person, so spouse support and strain are blank together, as in MIDUS
    for s in [s for s in SPOUSE if s in fields]:
        p=out['B1PB19'].map(lambda m:blank.get(m,{}).get(s,0)).to_numpy()
        out.loc[u<p,s]=np.nan
    return out

def distance(sample,pool,fields):
    num=[f for f in fields if pool[f].nunique()>12]
    sd=pool[num].std()
    mean_gap=((sample[num].mean()-pool[num].mean()).abs()/sd).mean()
    sd_gap=(sample[num].std()/sd-1).abs().mean()
    c1,c2=sample[fields].corr(min_periods=10),pool[fields].corr()
    corr_gap=float(np.nanmean(np.abs((c1-c2).to_numpy()[np.triu_indices(len(fields),1)])))
    return mean_gap+sd_gap+corr_gap,dict(mean_gap_sd=round(float(mean_gap),3),sd_ratio_gap=round(float(sd_gap),3),correlation_gap=round(corr_gap,3))

def best(pool,fields,n,seed,tries,real,key):
    r,observed,blank=fit(pool,fields);rng=np.random.default_rng(seed);chosen=None
    for _ in range(tries):
        s=draw(r,observed,blank,fields,n,rng)
        merged=s[key].round(6).merge(real[key].round(6).drop_duplicates(),how='inner')
        if len(merged):continue  # never keep a sample containing a real participant's complete record
        score,report=distance(s,pool,fields)
        if chosen is None or score<chosen[0]:chosen=(score,s,report)
    return chosen[1].reset_index(drop=True),chosen[2]

def main(data_path,membership_path):
    study=load_study();raw=pd.read_csv(data_path);ref=clean_frame(raw,study,reference=True)
    pools=pd.read_csv(membership_path).set_index(study['id_column'])['pool']
    ref['pool']=ref[study['id_column']].map(pools)
    calibration,evaluation=ref[ref.pool.eq('calibration')],ref[ref.pool.eq('evaluation')]
    out=ROOT/'data/examples';report={'source':'Linked MIDUS 2 and 3 file (registered ICPSR users); no participant records are stored here',
        'participants':len(ref),'calibration_pool':len(calibration),'evaluation_pool':len(evaluation)}
    # SPA4: observed proportions for all 2,709 participants
    table=quota_template(ref,study).rename(columns={'field':'variable'})
    def label(r):
        if r.variable=='B1PRAGE_2019' and r.category!='missing':return f'Aged {int(r.lower)} to {int(r.upper)}'
        if r.category=='missing':return 'No recorded value'
        return study['variables'][r.variable]['categories'][int(r.category)]
    table.insert(2,'category_label',table.apply(label,axis=1));table['proportion']=table.proportion.round(4)
    for v,g in table.groupby('variable'):  # rounding residue goes to the largest category, so each variable sums to exactly 1
        i=g.proportion.idxmax();table.loc[i,'proportion']=round(table.loc[i,'proportion']+1-g.proportion.sum(),4)
    for c in ('lower','upper'):table[c]=table[c].astype('Int64')
    table[['variable','category','category_label','lower','upper','proportion']].to_csv(out/'SPA4_proportions_example.csv',index=False)
    report['SPA4_male_share']=float(table.loc[(table.variable=='B1PRSEX')&(table.category=='1'),'proportion'].iloc[0])
    # SPA5 and SPA6: 50 generated participants matching the calibration pool
    fields=selected_fields(study)
    pilot,rep=best(calibration,fields,50,20261102,400,ref,fields);report['pilot_vs_calibration_pool']=rep
    for m in (5,6):pilot[fields].to_csv(out/f'SPA{m}_pilot_example.csv',index=False)
    # SPA7 and SPA8: 100 generated participants matching the evaluation pool
    base=predictors(study)
    profiles,rep=best(evaluation,base,100,20261103,400,ref,base);report['profiles_vs_evaluation_pool']=rep
    profiles[base].to_csv(out/'SPA8_profiles_example.csv',index=False)
    profiles[study['demographic_covariates']].to_csv(out/'SPA7_profiles_example.csv',index=False)
    (ROOT/'data/examples/MIDUS_examples_report.json').write_text(json.dumps(report,indent=1)+'\n')
    print(json.dumps(report,indent=1))

if __name__=='__main__':main(*sys.argv[1:3])
