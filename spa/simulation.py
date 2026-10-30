"""Invented local demonstrations and independently drawn method-specific inputs."""
import numpy as np
import pandas as pd
from .study import selected_fields,predictors,OUTCOMES,json_records,clean_frame
from .quotas import demographic_profiles
from .random_pilots import summarise_pilot

def invent_reference(study,n=2709,seed=20261029):
    rng=np.random.default_rng(seed);latent=rng.normal(size=(n,3));data={}
    for j,f in enumerate(study['psychological_predictors']):
        spec=study['variables'][f];lo,hi=spec['minimum'],spec['maximum'];sign=-1 if j%3==1 else 1
        z=sign*.45*latent[:,0]+.25*latent[:,1]+rng.normal(size=n)*.9
        x=lo+(hi-lo)*np.clip(.5+.17*z,0,1)
        if spec['kind']=='integer':x=np.round(x)
        if f=='B1PANXIE':x=np.maximum(lo,np.round(x));x[rng.random(n)<.94]=np.nan
        data[f]=np.round(x,4)
    for f in study['demographic_covariates']:
        spec=study['variables'][f]
        data[f]=rng.choice(list(spec['categories']),n) if spec['kind']=='category' else rng.integers(28,85,n)
    data[OUTCOMES[0]]=np.round(np.clip(6+.8*latent[:,0]+rng.normal(size=n),0,10),4)
    data[OUTCOMES[1]]=np.round(np.clip(6+.5*latent[:,0]+rng.normal(size=n)*1.2,0,10),4)
    return pd.DataFrame(data)

def prepare_inputs(reference,study,method,n,seed=1,replication=1,pilot_override=None,profiles_override=None):
    if method not in range(1,9) or n not in range(100,1001,100):raise ValueError('Choose SPA1–SPA8 and 100–1,000 participants in steps of 100.')
    if len(reference)<50:raise ValueError('Reference needs at least 50 rows for sampling.')
    rng=np.random.default_rng(np.random.SeedSequence([seed,method,replication]))
    context=dict(fixed=None,pilot=None,summary=None,quota_audit=None)
    # Deterministic participant split is only for drawing inputs; scoring uses the full reference.
    pool_rng=np.random.default_rng(seed);order=pool_rng.permutation(len(reference));cut=round(.2*len(reference))
    if method==4:
        profiles,audit=demographic_profiles(reference,study,n,rng)
        context.update(fixed=[dict(participant_id=i+1,**r) for i,r in enumerate(json_records(profiles))],quota_audit=audit)
    if method in (5,6):
        pool=reference.iloc[order[:cut]]
        if pilot_override is not None:
            chosen=clean_frame(pilot_override,study)
            if len(chosen)!=50:raise ValueError('Pilot must have exactly 50 rows.')
        else:
            if len(pool)<50:raise ValueError('The 20% pilot pool needs at least 50 participants; upload a 50-record pilot or use ≥250 reference rows.')
            chosen=pool.iloc[rng.choice(len(pool),50,replace=False)]
        context['pilot']=json_records(chosen[selected_fields(study)])
        if method==5:context['summary']=summarise_pilot(chosen,study)
    if method in (7,8):
        fields=predictors(study) if method==8 else study['demographic_covariates']
        if profiles_override is not None:
            chosen=profiles_override
            if len(chosen)!=n or not set(fields)<=set(chosen):raise ValueError('Profile file has incorrect rows or missing fixed fields.')
            # Validate fixed fields with temporary legal values for other fields.
            dummy=reference.iloc[np.resize(np.arange(len(reference)),n)].copy().reset_index(drop=True)
            for f in fields:dummy[f]=chosen[f].to_numpy()
            chosen=clean_frame(dummy,study)
        else:
            pool=reference.iloc[order[cut:]]
            if n>len(pool):raise ValueError('Profile sample exceeds the 80% profile pool; upload profiles or a larger reference.')
            chosen=pool.iloc[rng.choice(len(pool),n,replace=False)]
        context['fixed']=[dict(participant_id=i+1,**r) for i,r in enumerate(json_records(chosen[fields]))]
    return context

def local_demo(reference,study,method,n=100,seed=1,replication=1):
    """Illustrative rules, not outputs of the LLM prompts or estimates of SPA performance."""
    ctx=prepare_inputs(reference,study,method,n,seed,replication)
    rng=np.random.default_rng(np.random.SeedSequence([seed,method,replication,91]))
    if method in (5,6):base=pd.DataFrame(ctx['pilot'])
    else:base=reference
    frame=base.iloc[rng.choice(len(base),n,replace=True)].copy().reset_index(drop=True)
    if method not in (5,6,7):
        for f in selected_fields(study):frame[f]=rng.permutation(frame[f].to_numpy())
    for f in study['psychological_predictors']:
        if method==8:continue
        spec=study['variables'][f];span=spec['maximum']-spec['minimum']
        frame[f]=(frame[f]+rng.normal(0,span*(.025 if method in (5,6) else .1),n)).clip(spec['minimum'],spec['maximum']).round(4)
        if spec['kind']=='integer':frame[f]=frame[f].round()
    if ctx['fixed'] is not None:
        for f in ctx['fixed'][0]:
            if f!='participant_id':frame[f]=[r[f] for r in ctx['fixed']]
    # Demonstrates an outcome model with residual variation; not a claim about LLM behaviour.
    z=(frame[study['psychological_predictors'][0]]-reference[study['psychological_predictors'][0]].mean())/reference[study['psychological_predictors'][0]].std()
    for k,o in enumerate(OUTCOMES):frame[o]=np.clip(6+(.6 if k==0 else .4)*z.fillna(0)+rng.normal(0,1.2,n),0,10).round(4)
    frame=frame[selected_fields(study)];frame.insert(0,'participant_id',np.arange(1,n+1))
    return clean_frame(frame,study,expected_n=n),ctx

def quality_flags(frame,study,pilot=None):
    fields=selected_fields(study);base=predictors(study)
    flags={'repeated_complete_profiles':int(frame[fields].round(4).duplicated().sum()),
           'repeated_baseline_profiles':int(frame[base].round(4).duplicated().sum()),'pilot_record_matches':0}
    if pilot:
        def key(r):return tuple(None if pd.isna(v) else round(float(v),4) for v in r)
        keys={key(r) for r in pd.DataFrame(pilot)[fields].itertuples(index=False,name=None)}
        flags['pilot_record_matches']=sum(key(r) in keys for r in frame[fields].itertuples(index=False,name=None))
    return flags
