"""SPA4 target proportions: one row per demographic category with the share of participants in it.

Used by the MIDUS study and by custom studies. The upload checker explains each problem with a
row number, and the table it returns is what workflow.profiles_from_proportions (MIDUS) and
custom.contexts (custom studies) use to build the fixed demographic profiles.
"""
import math
import pandas as pd
from .errors import AppError,warning

COLUMNS=['variable','category','category_label','lower','upper','proportion']
TOLERANCE=0.02  # rounding differences up to this size are rescaled automatically

def midus_spec(study):
    spec={}
    for f in study['demographic_covariates']:
        v=study['variables'][f]
        if f=='B1PRAGE_2019':spec[f]=dict(kind='age',minimum=int(v['minimum']),maximum=int(v['maximum']),bins=[tuple(b) for b in study['age_quota_bins']])
        else:spec[f]=dict(kind='category',categories={str(k):str(l) for k,l in v['categories'].items()})
    return spec

def custom_spec(s):
    return {v['code']:dict(kind='category',categories={str(k):str(l) for k,l in v['categories'].items()}) for v in s['demographics']}

def _rounded(shares):
    """Round to four decimals and make each set add up to exactly 1 (the largest share absorbs the remainder)."""
    out=[round(float(x),4) for x in shares]
    if out:
        i=max(range(len(out)),key=lambda j:out[j]);out[i]=round(out[i]+1-sum(out),4)
    return out

def example_table(frame,spec):
    """A filled template: the proportions observed in a (fictional) example frame."""
    rows=[]
    for f,sp in spec.items():
        x=frame[f]
        if sp['kind']=='age':
            cats=[(f'age_band_{i+1}',f'Aged {lo} to {hi}',lo,hi,float(x.between(lo,hi).mean())) for i,(lo,hi) in enumerate(sp['bins'])]
        else:
            num=pd.to_numeric(x,errors='coerce')
            cats=[(k,lab,None,None,float(num.eq(float(k)).mean())) for k,lab in sp['categories'].items()]
        if x.isna().any():cats.append(('missing','No recorded value',None,None,float(x.isna().mean())))
        for (c,lab,lo,hi,_),p in zip(cats,_rounded([c[4] for c in cats])):rows.append(dict(variable=f,category=c,category_label=lab,lower=lo,upper=hi,proportion=p))
    table=pd.DataFrame(rows,columns=COLUMNS)
    if not any(sp['kind']=='age' for sp in spec.values()):table=table.drop(columns=['lower','upper'])
    for c in ('lower','upper'):
        if c in table:table[c]=table[c].astype('Int64')
    return table

def blank_table(spec):
    table=example_table(pd.DataFrame({f:[] for f in spec},dtype=float),spec)
    table['proportion']=None
    return table

def _number(text):
    try:value=float(str(text).strip())
    except ValueError:return None
    return value if math.isfinite(value) else None

def check(rows,label,spec,public=lambda f:f):
    """Validate an uploaded proportions table (rows: header first, internal variable names).
    Returns (warnings, cleaned DataFrame with columns field, category, lower, upper, proportion)."""
    header=[h.strip().lower() for h in rows[0]]
    needs_age=any(sp['kind']=='age' for sp in spec.values())
    required=['variable','category','proportion']+(['lower','upper'] if needs_age else [])
    missing=[c for c in required if c not in header]
    if missing:raise AppError('missing_columns',label=label,count=len(missing),columns=', '.join(missing))
    idx={h:i for i,h in enumerate(header)};get=lambda r,c:r[idx[c]].strip() if c in idx and idx[c]<len(r) else ''
    names=', '.join(public(f) for f in spec)
    seen={};records=[];bands={}
    for n,r in enumerate(rows[1:],start=2):
        if not any(c.strip() for c in r):continue
        var=get(r,'variable')
        if var not in spec:raise AppError('unknown_variable',label=label,row=n,value=var or '(blank)',allowed=names)
        sp=spec[var];shown=public(var);cat=get(r,'category')
        raw=get(r,'proportion');p=_number(raw)
        if p is None or p<0:raise AppError('invalid_proportion',label=label,row=n,value=raw or '(blank)',variable=shown,category=cat or '(blank)')
        if cat.lower()=='missing':cat='missing'
        elif sp['kind']=='category':
            code=_number(cat)
            key=str(int(code)) if code is not None and code==int(code) else None
            if key not in sp['categories']:
                allowed=', '.join(f'{k} ({v.title()})' for k,v in list(sp['categories'].items())[:12])+(' …' if len(sp['categories'])>12 else '')
                raise AppError('unknown_category',label=label,row=n,value=cat or '(blank)',variable=shown,allowed=allowed)
            cat=key
        elif not cat:raise AppError('unknown_category',label=label,row=n,value='(blank)',variable=shown,allowed='any band name, for example age_band_1')
        if (var,cat) in seen:raise AppError('duplicate_category',label=label,row=n,value=cat,variable=shown)
        seen[(var,cat)]=n;lo=hi=None
        if sp['kind']=='age' and cat!='missing':
            lo,hi=_number(get(r,'lower')),_number(get(r,'upper'))
            limits=dict(minimum=sp['minimum'],maximum=sp['maximum'])
            if lo is None or hi is None or lo!=int(lo) or hi!=int(hi):raise AppError('invalid_age_band',label=label,row=n,reason='lower and upper need whole-number ages.',**limits)
            lo,hi=int(lo),int(hi)
            if lo>hi:raise AppError('invalid_age_band',label=label,row=n,reason=f'lower ({lo}) is above upper ({hi}).',**limits)
            if lo<sp['minimum'] or hi>sp['maximum']:raise AppError('invalid_age_band',label=label,row=n,reason=f'{lo} to {hi} falls outside the eligible ages.',**limits)
            for other,(a,b) in bands.get(var,{}).items():
                if max(lo,a)<=min(hi,b):raise AppError('invalid_age_band',label=label,row=n,reason=f'{lo} to {hi} overlaps the band in row {other}.',**limits)
            bands.setdefault(var,{})[n]=(lo,hi)
        records.append(dict(field=var,category=cat,lower=lo,upper=hi,proportion=p,row=n))
    if not records:raise AppError('file_empty',label=label)
    table=pd.DataFrame(records)
    absent=[f for f in spec if f not in set(table.field)]
    if absent:raise AppError('missing_demographic',label=label,count=len(absent),columns=', '.join(public(f) for f in absent))
    warnings=[];totals=table.groupby('field',sort=False).proportion.sum()
    if all(abs(t-100)<=100*TOLERANCE for t in totals) and table.proportion.max()>1:
        table['proportion']=table.proportion/100;totals=totals/100;warnings.append(warning('percentages_converted',label=label))
    big=table[table.proportion>1]
    if len(big):
        r=big.iloc[0];raise AppError('invalid_proportion',label=label,row=int(r.row),value=f'{r.proportion:g}',variable=public(r.field),category=r.category)
    rescaled=[]
    for f,t in totals.items():
        if abs(t-1)<=1e-6:continue
        if abs(t-1)<=TOLERANCE and t>0:
            table.loc[table.field==f,'proportion']=table.loc[table.field==f,'proportion']/t;rescaled.append(public(f))
        else:raise AppError('proportions_sum',label=label,variable=public(f),total=f'{t:.4g}')
    if rescaled:warnings.append(warning('proportions_rescaled',label=label,variables=', '.join(rescaled)))
    return warnings,table.drop(columns=['row'])
