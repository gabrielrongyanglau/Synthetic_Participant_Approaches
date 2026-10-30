"""Researcher-first selection and input preparation. A benchmark is never a generation input."""
import hashlib
import json
import numpy as np
import pandas as pd
from .numbering import run_name
from .study import predictors,selected_fields,json_records,clean_frame,OUTCOMES
from .simulation import invent_reference,prepare_inputs
from .quotas import apportion
from .random_pilots import summarise_pilot

PURPOSES={
 'workflow':'Try the tool and practise creating or analysing a dataset',
 'distributions':'Explore average scores, score ranges and variation between people',
 'relationships':'Explore how psychological scores relate to life satisfaction',
 'outcomes':'Generate life-satisfaction scores for people whose profiles I already have'}
INFORMATION={
 'definitions':'Only the study definitions; no participant data',
 'population':'A written description of the people I want to simulate',
 'proportions':'Population percentages for demographics, such as age or sex',
 'pilot':'A small existing participant dataset with at least 50 people',
 'demographics':'One row per person with demographic values only',
 'psychology':'One row per person with demographics and psychological scores'}
METHODS_BY_INFORMATION={'definitions':[1,2],'population':[1,2,3],'proportions':[4],
 'pilot':[5,6],'demographics':[7],'psychology':[7,8]}
REQUIREMENTS={1:'Study definitions only. Every study value is generated.',
 2:'Study definitions only. Every study value is generated.',
 3:'Study definitions and a qualitative population description. Every study value is generated.',
 4:'A demographic sample of exactly 50 people. The tool constructs fixed profiles matching its proportions, then generates psychology and outcomes.',
 5:'Exactly 50 pilot rows with demographics, psychology and both outcomes. The tool computes summaries before sending records and summaries to the model.',
 6:'Exactly 50 pilot rows with demographics, psychology and both outcomes. The model receives the records and is instructed to analyse them.',
 7:'At least the requested number of demographic profiles. Psychology and outcomes are generated.',
 8:'At least the requested number of demographic and psychological profiles. Only outcomes are generated.'}

def compatible_methods(information):
    if information not in METHODS_BY_INFORMATION:raise ValueError('Unknown information category.')
    return METHODS_BY_INFORMATION[information].copy()

def purpose_guidance(purpose,methods):
    if purpose=='workflow':return 'Use this option to inspect the instructions sent to the AI and practise creating and downloading datasets. To assess whether generated values resemble human responses, you would need to compare them with observed human data.'
    if purpose=='distributions':
        if set(methods)&{5,6}:return 'In our MIDUS study, SPA5 and SPA6 reproduced average scores, variation and score distributions more closely than approaches without pilot records. SPA5 was closest among the methods that generated psychological scores. These findings do not guarantee the same accuracy for your data.'
        if 8 in methods:return 'SPA8 keeps the psychological scores you supply. Its score distributions describe those input scores, rather than the accuracy of newly generated psychological measurements.'
        return 'In our MIDUS study, these methods had substantial errors in the averages, variation or distributions of generated scores. They can help you practise the workflow; realistic-looking output still needs comparison with human data.'
    if purpose=='relationships':return 'Treat generated relationships as exploratory. In our MIDUS study, methods that generated psychological scores substantially overstated relationship strengths. SPA8 also retained errors. Use observed human evidence to test substantive research claims.'
    if purpose=='outcomes':
        if 8 in methods:return 'SPA8 uses each person’s observed demographics and psychological scores to generate life satisfaction at two assessments. Our study does not establish accurate individual predictions or show that generated scores can validly replace missing human responses.'
        return 'SPA8 is the approach for generating only life satisfaction from existing psychological and demographic values. It needs both types of information. The approaches shown here generate additional values as well.'
    raise ValueError('Unknown purpose.')

def _clean_fields(frame,study,fields):
    """Validate only the provided fixed fields, with no hidden reference or imputation."""
    if frame.columns.duplicated().any() or not set(fields)<=set(frame):raise ValueError('Missing or repeated input columns. Use the supplied template.')
    out=frame[fields].copy()
    for f in fields:
        if out[f].map(lambda v:isinstance(v,(bool,np.bool_))).any():raise ValueError('Boolean values are not valid scores in '+f)
        spec=study['variables'][study['outcomes'].get(f,f)];x=pd.to_numeric(out[f],errors='raise')
        x=x.mask(x.isin(spec['missing_codes']))
        valid=x.isin(list(spec['categories'])) if spec['kind']=='category' else x.between(spec['minimum'],spec['maximum'])
        if spec['kind']=='integer':valid &= x.mod(1).eq(0)
        if (x.notna() & (~valid | ~np.isfinite(x))).any():raise ValueError('Invalid fixed-input value in '+f)
        out[f]=x
    return out

def quota_template(reference,study):
    rows=[]
    for f in study['demographic_covariates']:
        if f=='B1PRAGE_2019':
            for i,(lo,hi) in enumerate(study['age_quota_bins']):
                rows.append(dict(field=f,category=f'age_band_{i+1}',lower=lo,upper=hi,proportion=float(reference[f].between(lo,hi).mean())))
        else:
            for category in study['variables'][f]['categories']:
                rows.append(dict(field=f,category=str(category),lower=None,upper=None,proportion=float(reference[f].eq(category).mean())))
        if reference[f].isna().any():rows.append(dict(field=f,category='missing',lower=None,upper=None,proportion=float(reference[f].isna().mean())))
    return pd.DataFrame(rows)

def profiles_from_proportions(table,study,n,rng):
    required={'field','category','lower','upper','proportion'}
    if not required<=set(table):raise ValueError('Proportions CSV needs field, category, lower, upper and proportion.')
    if set(table.field)!=set(study['demographic_covariates']):raise ValueError('Provide proportions for all six demographic variables.')
    result={};audit={}
    for field,g in table.groupby('field',sort=False):
        g=g.reset_index(drop=True);spec=study['variables'][field]
        categories=g.category.astype(str).str.lower()
        if field!='B1PRAGE_2019':
            categories=categories.map(lambda v:'missing' if v=='missing' else str(float(v)))
        if categories.duplicated().any():raise ValueError('Repeated category for '+field)
        weights=pd.to_numeric(g.proportion,errors='raise').to_numpy(float)
        if not np.isfinite(weights).all() or (weights<0).any() or not np.isclose(weights.sum(),1,atol=1e-6,rtol=0):raise ValueError('Proportions for '+field+' must be nonnegative and sum to 1.')
        if g.category.astype(str).duplicated().any():raise ValueError('Repeated category for '+field)
        allocations=apportion({str(i):float(w) for i,w in enumerate(weights)},n);values=[];intervals=[]
        for i,row in g.iterrows():
            count=allocations[str(i)];category=str(row.category)
            if category.lower()=='missing':values.extend([np.nan]*count);continue
            if field=='B1PRAGE_2019':
                lo=float(row.lower);hi=float(row.upper)
                if not np.isfinite(lo+hi) or lo!=int(lo) or hi!=int(hi) or lo>hi or lo<spec['minimum'] or hi>spec['maximum']:raise ValueError('Invalid age interval.')
                if any(max(lo,a)<=min(hi,b) for a,b in intervals):raise ValueError('Age intervals overlap.')
                intervals.append((lo,hi));values.extend(rng.integers(int(lo),int(hi)+1,count).tolist())
            else:
                value=float(category)
                if value!=int(value) or int(value) not in spec['categories']:raise ValueError('Invalid demographic category for '+field)
                values.extend([int(value)]*count)
        rng.shuffle(values);result[field]=values
        audit[field]={'categories':g.category.astype(str).tolist(),'proportions':weights.tolist(),'allocated_counts':list(allocations.values())}
    return pd.DataFrame(result),audit

PILOT_N=50  # SPA4 demographic samples and SPA5/SPA6 pilot samples always have exactly 50 participants
ASSET_KEYS={4:'sample_SPA4',5:'pilot_SPA5',6:'pilot_SPA6',7:'profiles_SPA7',8:'profiles_SPA8'}
EXAMPLE_FILES={4:'SPA4_demographic_sample_example.csv',5:'SPA5_pilot_example.csv',6:'SPA6_pilot_example.csv',
               7:'SPA7_profiles_example.csv',8:'SPA8_profiles_example.csv'}

def example_assets(method):
    """The fictional example files offered for download (one row per participant) are the supplied examples."""
    from .study import PROJECT_ROOT
    from .io import read_csv
    return {ASSET_KEYS[method]:read_csv(PROJECT_ROOT/'data/examples'/EXAMPLE_FILES[method])}

def prepare_context(study,method,n,seed=1,replication=1,assets=None,examples=False,population=''):
    if method not in range(1,9) or n not in range(100,1001,100):raise ValueError('Choose SPA1–SPA8 and 100–1,000 participants in steps of 100.')
    assets=assets or {};rng=np.random.default_rng(np.random.SeedSequence([seed,method,replication]))
    ctx=dict(fixed=None,pilot=None,summary=None,quota_audit=None)
    details={'source':'Invented example inputs' if examples else 'Researcher-supplied inputs','method':method,'repetition':replication,
             'reference_required':False,'population_guidance':population if method==3 else ''}
    if method==3 and not population.strip():raise ValueError('SPA3 needs a population description.')
    if examples and method>=4:assets=example_assets(method)
    if method==4:
        sample=assets.get('sample_SPA4')
        if sample is None:raise ValueError('SPA4 needs a demographic sample: one row per participant, one column per demographic.')
        if len(sample)!=PILOT_N:raise ValueError(f'SPA4 needs a demographic sample of exactly {PILOT_N} participants (one row each); this file has {len(sample)} rows.')
        sample=_clean_fields(sample,study,study['demographic_covariates'])
        profiles,audit=profiles_from_proportions(quota_template(sample,study),study,n,rng)
        ctx.update(fixed=[dict(participant_id=i+1,**r) for i,r in enumerate(json_records(profiles))],quota_audit=audit)
        details.update(source_pool_n=PILOT_N,proportions_source=f'Observed proportions in the {PILOT_N}-person demographic sample')
    elif method in (5,6):
        pilot=assets.get(f'pilot_SPA{method}')
        if pilot is None:raise ValueError(f'SPA{method} needs a pilot sample: one row per participant, one column per variable.')
        if len(pilot)!=PILOT_N:raise ValueError(f'SPA{method} needs a pilot sample of exactly {PILOT_N} participants (one row each); this file has {len(pilot)} rows.')
        chosen=clean_frame(_clean_fields(pilot,study,selected_fields(study)),study)
        ctx['pilot']=json_records(chosen[selected_fields(study)])
        if method==5:ctx['summary']=summarise_pilot(chosen,study)
        details.update(source_pool_n=PILOT_N,pilot_n=PILOT_N,pilot_input_rows=list(range(1,PILOT_N+1)),
                       summary_source='Computed by this tool before model generation' if method==5 else 'Model instructed to analyse supplied records')
    elif method in (7,8):
        fields=predictors(study) if method==8 else study['demographic_covariates'];profiles=assets.get(f'profiles_SPA{method}')
        if profiles is None or len(profiles)<n:raise ValueError(f'SPA{method} needs at least {n} participant profiles (one row each), one for every synthetic participant.')
        profiles=_clean_fields(profiles,study,fields)
        indices=np.arange(n) if len(profiles)==n else rng.choice(len(profiles),n,replace=False)
        chosen=profiles.iloc[indices]
        ctx['fixed']=[dict(participant_id=i+1,**r) for i,r in enumerate(json_records(chosen))]
        details.update(source_pool_n=len(profiles),input_rows_in_output_order=[int(i)+1 for i in indices],
                       sampling='All supplied profiles in order' if len(profiles)==n else 'Without replacement within the draw')
    ctx['provenance']=details
    return ctx

def context_bank(study,methods,n,repetitions,seed,assets=None,examples=False,population=''):
    if not methods or len(methods)!=len(set(methods)) or not 1<=repetitions<=20:raise ValueError('Select distinct methods and 1–20 repetitions.')
    return {run_name(m,r):prepare_context(study,m,n,seed,r,assets,examples,population)
            for m in methods for r in range(1,repetitions+1)}

def input_digest(bank):
    return hashlib.sha256(json.dumps(bank,sort_keys=True,allow_nan=False,separators=(',',':')).encode()).hexdigest()

def evaluation_reference(frame,study):
    """Only scores and outcomes are used by fidelity metrics; demographics are optional."""
    frame=frame.copy()
    for field in study['demographic_covariates']:
        if field not in frame:frame[field]=np.nan
    return clean_frame(frame,study,reference=True)

def illustrative_generation(study,method,n,seed,replication,ctx):
    """Shows the mechanics only. The RNG is not an LLM or a validation benchmark."""
    from .simulation import local_demo,quality_flags
    # Reuse the existing documented local numerical rules, then attach this run's inputs.
    invented=invent_reference(study);frame,_=local_demo(invented,study,method,n,seed,replication)
    rng=np.random.default_rng(np.random.SeedSequence([seed,method,replication,51]))
    if ctx.get('pilot'):
        base=pd.DataFrame(ctx['pilot']);frame=base.iloc[rng.choice(len(base),n,replace=True)].reset_index(drop=True)
        for f in study['psychological_predictors']:
            spec=study['variables'][f];span=spec['maximum']-spec['minimum']
            frame[f]=(frame[f]+rng.normal(0,span*.03,n)).clip(spec['minimum'],spec['maximum']).round(4)
            if spec['kind']=='integer':frame[f]=frame[f].round()
        frame.insert(0,'participant_id',np.arange(1,n+1))
    if ctx.get('fixed'):
        for f in ctx['fixed'][0]:frame[f]=[p[f] for p in ctx['fixed']]
    # Outcomes are illustrative even when the fixed or pilot inputs are real.
    x=frame[study['psychological_predictors'][0]];s=x.std()
    z=(x-x.mean())/s if pd.notna(s) and s>0 else pd.Series(np.zeros(n))
    for k,o in enumerate(OUTCOMES):frame[o]=(6+(.6 if k==0 else .4)*z.fillna(0)+rng.normal(0,1.2,n)).clip(0,10).round(4)
    return clean_frame(frame,study,expected_n=n)

def generated_metadata(frames,contexts,study,settings,source,purpose):
    from .simulation import quality_flags
    return {'schema_version':'1.1','source':source,'purpose':purpose,'settings':settings,
      'validation_status':'Not evaluated against a human reference',
      'methods':sorted({m for m,r in frames}),'datasets':len(frames),'records':sum(len(f) for f in frames.values()),
      'input_provenance':{name:ctx['provenance'] for name,ctx in contexts.items()},
      'quality_flags':{run_name(m,r):quality_flags(f,study,contexts[run_name(m,r)].get('pilot')) for (m,r),f in frames.items()},
      'sampling_note':'Draws use separate method/run random streams. A supplied pool of exactly 50 pilot rows reuses those people across runs. A supplied profile file with exactly n rows retains those same profiles. Shared supplied pools can overlap; these are new user runs, not the independent-input MIDUS benchmark.'}
