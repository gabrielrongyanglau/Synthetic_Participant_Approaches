"""Checks that run before generation and explain problems precisely (column, row, value, what is allowed).
The scientific engine's own validation still runs afterwards as a backstop."""
import csv,io,re
import numpy as np
import pandas as pd
from .errors import AppError,warning

LABELS={'proportions_SPA4':'The SPA4 proportions file','pilot_SPA5':'The SPA5 pilot sample','pilot_SPA6':'The SPA6 pilot sample',
        'profiles_SPA7':'The SPA7 profile file','profiles_SPA8':'The SPA8 profile file'}
IDENTIFIER_COLUMN=re.compile(r'(^|_|\b)(first_?name|last_?name|surname|full_?name|name|e-?mail|email_?address|phone|mobile|telephone|address|street|postcode|post_code|zip_?code|nric|ssn|social_security|passport|national_id|date_?of_?birth|dob|birth_?date|ip_?address)(_|\b|$)',re.I)
EMAIL=re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')
PHONE=re.compile(r'^\+?[\d\s()-]{9,}$')
NATIONAL_ID=re.compile(r'^([STFGM]\d{7}[A-Z]|\d{3}-\d{2}-\d{4}|[A-Z]{2}\d{6}[A-D])$',re.I)

def sniff(text,label):
    """Reject non-CSV content early with a specific explanation. Returns the parsed rows (header first)."""
    if text is None or not str(text).strip():raise AppError('file_empty',label=label)
    head=str(text)[:4096]
    if head.startswith('PK\x03\x04'):raise AppError('not_csv',label=label,kind='an Excel workbook (.xlsx)')
    if head.startswith('%PDF'):raise AppError('not_csv',label=label,kind='a PDF')
    if '\x00' in head or head.startswith('￾') or head.startswith('\xff\xfe'):raise AppError('not_csv',label=label,kind='a binary or UTF-16 file')
    if re.match(r'\s*<(!doctype|html|\?xml)',head,re.I):raise AppError('not_csv',label=label,kind='a web page or XML file')
    first=head.lstrip('﻿').splitlines()[0] if head.strip() else ''
    if ',' not in first:
        for d,name in ((';','semicolons'),('\t','tabs'),('|','vertical bars')):
            if d in first:raise AppError('wrong_delimiter',label=label,delimiter=name)
    rows=list(csv.reader(io.StringIO(str(text).lstrip('﻿'))))
    while rows and not any(c.strip() for c in rows[-1]):rows.pop()  # trailing blank lines
    if len(rows)<2:raise AppError('file_empty',label=label)
    header=[h.strip() for h in rows[0]]
    dups=sorted({h for h in header if header.count(h)>1})
    if dups:raise AppError('duplicate_columns',label=label,columns=', '.join(dups))
    for i,r in enumerate(rows[1:],start=2):
        if len(r)!=len(header) and any(c.strip() for c in r):raise AppError('ragged_rows',label=label,row=i,found=len(r),expected=len(header))
    return rows

def identifiers(rows,label,allowed=()):
    header=[h.strip() for h in rows[0]]
    bad=[h for h in header if h not in allowed and h!='participant_id' and IDENTIFIER_COLUMN.search(h)]
    if bad:raise AppError('identifier_columns',label=label,columns=', '.join(bad))
    for i,r in enumerate(rows[1:],start=2):
        for h,v in zip(header,r):
            v=v.strip()
            if not v:continue
            if EMAIL.search(v):raise AppError('identifier_values',label=label,row=i,column=h,kind='an email address')
            if NATIONAL_ID.match(v):raise AppError('identifier_values',label=label,row=i,column=h,kind='an identity number')
            if PHONE.match(v) and len(re.sub(r'\D','',v))>=9 and not re.fullmatch(r'-?\d+(\.\d+)?',v):raise AppError('identifier_values',label=label,row=i,column=h,kind='a phone number')

def describe(spec):
    if spec['kind']=='category':return 'one of the codes '+', '.join(f'{k} ({v.title()})' for k,v in list(spec['categories'].items())[:8])+(' …' if len(spec['categories'])>8 else '')
    unit='whole numbers' if spec['kind'] in ('integer',) else 'numbers'
    return f"{unit} from {spec['minimum']:g} to {spec['maximum']:g}"

MISSING_TOKENS={'na','n/a','#n/a','nan','null','none','missing','-','.','<na>','#null!'}

def values(rows,label,specs,public=lambda f:f):
    """Validate every cell of the known columns. specs: {column:{kind,minimum,maximum,categories,missing_codes}}."""
    header=[h.strip() for h in rows[0]];idx={h:i for i,h in enumerate(header)};warn=[];coded=0;tokens=0
    for col,spec in specs.items():
        if col not in idx:continue
        for n,r in enumerate(rows[1:],start=2):
            raw=r[idx[col]].strip() if idx[col]<len(r) else ''
            if raw=='':continue
            if raw.lower() in MISSING_TOKENS:r[idx[col]]='';tokens+=1;continue
            if re.fullmatch(r'-?\d+,\d+',raw):raise AppError('decimal_comma',label=label,row=n,column=public(col),value=raw)
            try:x=float(raw)
            except ValueError:raise AppError('non_numeric_value',label=label,row=n,column=public(col),value=raw[:40],allowed=describe(spec)) from None
            if not np.isfinite(x):raise AppError('non_numeric_value',label=label,row=n,column=public(col),value=raw[:40],allowed=describe(spec))
            if x in spec.get('missing_codes',[]):coded+=1;continue
            if spec['kind']=='category':
                cats=[float(k) for k in spec['categories']]
                if x%1:raise AppError('not_whole_number',label=label,row=n,column=public(col),value=raw,allowed=describe(spec))
                if x not in cats:raise AppError('value_out_of_range',label=label,row=n,column=public(col),value=raw,allowed=describe(spec))
            else:
                if not spec['minimum']<=x<=spec['maximum']:raise AppError('value_out_of_range',label=label,row=n,column=public(col),value=raw,allowed=describe(spec))
                if spec['kind']=='integer' and x%1:raise AppError('not_whole_number',label=label,row=n,column=public(col),value=raw,allowed=describe(spec))
    if coded:warn.append(warning('missing_codes',label=label,count=coded))
    if tokens:warn.append(warning('missing_tokens',label=label,count=tokens))
    return warn

def frame_of(rows):
    header=[h.strip() for h in rows[0]]
    f=pd.DataFrame([r+['']*(len(header)-len(r)) for r in rows[1:]],columns=header,dtype=object)
    return f.mask(f.isin(['','null']))

def structure(rows,label,required,public=lambda f:f,complete=(),complete_reason='',duplicates='strict'):
    """Required columns, required values, duplicates and degenerate columns. Returns warnings."""
    header=[h.strip() for h in rows[0]];warn=[]
    missing=[c for c in required if c not in header]
    if missing:raise AppError('missing_columns',label=label,count=len(missing),columns=', '.join(public(c) for c in missing[:12])+(' …' if len(missing)>12 else ''))
    extra=[h for h in header if h not in required and h!='participant_id']
    if extra:warn.append(warning('ignored_columns',label=label,columns=', '.join(extra[:10])))
    f=frame_of(rows)[list(required)].apply(pd.to_numeric,errors='coerce')
    for c in complete:
        blank=[i+2 for i in np.flatnonzero(f[c].isna().to_numpy())]
        if blank:raise AppError('missing_required_value',label=label,column=public(c),rows=', '.join(map(str,blank[:10]))+(' …' if len(blank)>10 else ''),reason=complete_reason)
    n=len(f);unique=len(f.round(6).drop_duplicates());dup=n-unique
    if duplicates=='strict' and (unique==1 or dup>=max(2,int(np.ceil(.2*n)))):raise AppError('duplicate_participants',label=label,unique=unique,rows=n,duplicates=dup)
    if duplicates=='demographic' and unique<min(5,n):raise AppError('duplicate_participants',label=label,unique=unique,rows=n,duplicates=dup)
    if duplicates=='strict' and dup:warn.append(warning('duplicate_rows',label=label,count=dup))
    if n>1:
        for c in required:
            col=f[c].dropna()
            if col.empty:warn.append(warning('empty_column',column=public(c),label=label))
            elif col.nunique()==1 and duplicates=='strict':warn.append(warning('constant_column',column=public(c),value=f'{col.iloc[0]:g}',label=label))
    return warn

# ---------------- Sensitive and prohibited content in free text
SENSITIVE={
 'suicide or self-harm':r'suicid|self[- ]?harm|self[- ]?injur|kill(ing)? (my|them|him|her)sel(f|ves)|end(ing)? (my|their|his|her) (own )?life|take (my|their) own life|overdos|want(ed)? to die|cutting (my|them)sel',
 'sexual violence or abuse':r'sexual(ly)? (abuse|assault|violence|exploit)|\brape|molest|incest|child abuse|grooming',
 'violence or weapons':r'homicid|murder|\bweapons?\b|firearm|explosive|bomb|terroris|mass shooting',
 'illegal drug use':r'cocaine|heroin|methamphetamine|fentanyl|illegal drug|illicit drug',
 'eating disorders':r'anorexi|bulimi|binge[- ]?eating|purging',
}
PROHIBITED={'sexual content involving minors':r'(child|minor|under[- ]?(18|age)|underage|teen)\w*\W+(\w+\W+){0,6}(sexual|sex|porn|nude|explicit)|(sexual|sex|porn|nude|explicit)\w*\W+(\w+\W+){0,6}(child|minor|underage)'}

def texts_from(req):
    out=[]
    if getattr(req,'population',None):out.append(('the population description',req.population))
    s=getattr(req,'study',None)
    if isinstance(s,dict):
        for k in ('title','population'):
            if isinstance(s.get(k),str):out.append(('the study '+k,s[k]))
        for v in s.get('variables') or []:
            if not isinstance(v,dict):continue
            name=v.get('name') or v.get('code') or 'a measure'
            for k in ('name','definition','citation','anchorLow','anchorHigh'):
                if isinstance(v.get(k),str):out.append((f'measure "{name}"',v[k]))
            for item in v.get('items') or []:
                if isinstance(item,str):out.append((f'items of "{name}"',item))
        for v in s.get('demographics') or []:
            if isinstance(v,dict):
                out.append(('demographic definitions',str(v.get('name',''))))
                for lab in (v.get('categories') or {}).values():out.append(('demographic categories',str(lab)))
    sup=getattr(req,'supporting',None) or {}
    if isinstance(sup,dict):
        if isinstance(sup.get('question'),str):out.append(('the research context',sup['question']))
        for src in sup.get('sources') or []:
            if isinstance(src,dict):out.append((f'source "{str(src.get("title",""))[:60]}"',str(src.get('title',''))+'\n'+str(src.get('text',''))))
    return out

def content(req):
    """Block prohibited content; require acknowledgement for sensitive topics."""
    found={};blocked={}
    for where,text in texts_from(req):
        low=text.lower()
        for topic,rx in PROHIBITED.items():
            if re.search(rx,low):blocked.setdefault(topic,where)
        for topic,rx in SENSITIVE.items():
            if re.search(rx,low):found.setdefault(topic,where)
    if blocked:raise AppError('prohibited_content',topics=' and '.join(blocked),where=', '.join(sorted(set(blocked.values()))))
    if found and not getattr(req,'sensitive_ack',False):
        raise AppError('sensitive_content',topics=' and '.join(found),where=', '.join(sorted(set(found.values()))))
    return sorted(found)

ROWS={'pilot_SPA5':('exact',50),'pilot_SPA6':('exact',50),'profiles_SPA7':('min',100),'profiles_SPA8':('min',100)}

def midus_specs(study):
    specs={}
    for f in list(study['variables']):
        v=study['variables'][f];specs[f]={k:v.get(k) for k in ('kind','minimum','maximum','categories','missing_codes')}
    for out,src in study['outcomes'].items():specs[out]=specs[src]
    return specs

def custom_specs(s):
    from .custom import bounds
    return {c:dict(kind='category' if cats else 'integer' if integer else 'number',minimum=lo,maximum=hi,categories={k:str(k) for k in cats} if cats else None,missing_codes=[])
            for c,(lo,hi,integer,cats) in bounds(s).items()}

def check_upload(key,text,custom=None):
    """Validate one uploaded CSV (text already translated to internal names). Returns a list of warnings."""
    from .public import PUBLIC
    from .study import load_study,selected_fields,predictors,OUTCOMES
    label=LABELS.get(key,'The uploaded file');public=lambda c:PUBLIC.get(c,c)
    rows=sniff(text,label)
    if key=='proportions_SPA4':
        from . import proportions
        spec=proportions.midus_spec(load_study()) if custom is None else proportions.custom_spec(custom)
        warn,table=proportions.check(rows,label,spec,public if custom is None else (lambda c:c))
        return warn,table.rename(columns={'field':'variable'}).to_csv(index=False)
    if custom is None:
        study=load_study();specs=midus_specs(study);allowed=()
    else:
        from .custom import demographics
        study=None;specs=custom_specs(custom);allowed=tuple(specs)
    identifiers(rows,label,allowed)
    if key in ROWS:
        rule,n=ROWS[key];found=len(rows)-1
        if rule=='exact' and found!=n:raise AppError('wrong_row_count',label=label,expected=n,found=found)
        if rule=='min' and found<n:raise AppError('too_few_profiles',label=label,expected=n,found=found)
    header=[h.strip() for h in rows[0]]
    if custom is None:
        demo=study['demographic_covariates']
        required={'profiles_SPA7':demo,'profiles_SPA8':predictors(study),'pilot_SPA5':selected_fields(study),'pilot_SPA6':selected_fields(study)}.get(key)
        if required is None:required=[c for c in header if c in specs]
        complete=list(OUTCOMES) if key.startswith('pilot') else ()
        reason='Both life-satisfaction outcomes must be observed for every pilot participant.'
    else:
        demo=demographics(custom);required=[c for c in header if c in specs]
        missing=[c for c in demo if c not in header]
        if missing:raise AppError('missing_columns',label=label,count=len(missing),columns=', '.join(missing))
        complete=[c for c in required if key.startswith('pilot')];reason='Every cell of a custom pilot sample needs a value.'
    # Missing columns are reported before cell values, so the most important problem comes first.
    missing=[c for c in required if c not in header]
    if missing:raise AppError('missing_columns',label=label,count=len(missing),columns=', '.join(public(c) for c in missing[:12])+(' …' if len(missing)>12 else ''))
    warn=values(rows,label,{c:specs[c] for c in required if c in specs},public)
    mode='demographic' if key=='profiles_SPA7' else 'strict'
    warn+=structure(rows,label,required,public,complete,reason,mode) if required else []
    out=io.StringIO();csv.writer(out,lineterminator='\n').writerows(rows)
    return warn,out.getvalue()


def dataset_warnings(frame,quality,generated,specs,public=lambda c:c):
    """Quality warnings for a finished dataset. Never blocks the download."""
    n=len(frame);out=[]
    rep=int(quality.get('repeated_complete_profiles',0))
    if rep>=max(2,int(.05*n)):out.append(warning('repeated_profiles',count=rep,n=n))
    if quality.get('pilot_record_matches',0):out.append(warning('pilot_copies',count=quality['pilot_record_matches']))
    for c in generated:
        x=pd.to_numeric(frame[c],errors='coerce').dropna()
        if len(x)<2:continue
        if x.nunique()==1:out.append(warning('no_variation',column=public(c)));continue
        spec=specs.get(c) or {}
        if spec.get('kind')=='number' and spec.get('minimum') is not None:
            for end,value in (('maximum',spec['maximum']),('minimum',spec['minimum'])):
                share=float((x==value).mean())
                if share>=.5:out.append(warning('floor_ceiling',share=f'{share:.0%}',column=public(c),end=end,value=f'{value:g}'));break
    return out
