from pathlib import Path
import hashlib
import json
import pickle
import numpy as np
import pandas as pd
from .metrics import Reference,score,summarise,DIST,REL
from .study import clean_frame,load_study,OUTCOMES

def analyse(entries,human,study,progress=None):
    """Entries: (method integer, repetition integer, callable -> frame)."""
    ref=Reference(human,study);runs=[];variables=[];seen=set()
    for i,(method,rep,read) in enumerate(entries):
        if (method,rep) in seen:raise ValueError('Repeated method/repetition identifier.')
        seen.add((method,rep));f=clean_frame(read(),study)
        d,r,g1,g2=score(f,ref)
        runs.append(dict(method=method,replication=rep,participants=len(f),**g1,
            **{f'midus{k+2}_{m}':g2[k][m] for k in range(2) for m in REL}))
        for j,code in enumerate(ref.ps):
            variables.append(dict(method=method,replication=rep,code=code,**d.loc[code].to_dict(),
                **{f'midus{k+2}_r':r[j,k] for k in range(2)}))
        if progress and (i+1)%100==0:progress(i+1,len(entries))
    runs=pd.DataFrame(runs);raw=pd.DataFrame(variables);rows=[]
    for (method,code),g in raw.groupby(['method','code'],sort=True):
        j=ref.ps.index(code);ok=g.smd.notna();row=dict(method=method,code=code,distribution_runs=int(ok.sum()))
        for col in ['mean','sd']+DIST:row[col]=g.loc[ok,col].mean()
        for k in (2,3):
            v=g[f'midus{k}_r'].dropna();row.update({f'midus{k}_runs':len(v),f'midus{k}_mean_r':v.mean(),f'midus{k}_mae':abs(v-ref.r[j,k-2]).mean()})
        rows.append(row)
    summary,pairs=summarise(runs)
    humanstats=pd.DataFrame([dict(code=c,n=len(ref.values[j]),mean=ref.mean[j],sd=ref.sd[j],midus2_r=ref.r[j,0],midus3_r=ref.r[j,1]) for j,c in enumerate(ref.ps)])
    return dict(summary=summary,comparisons=pairs,variables=pd.DataFrame(rows),human=humanstats,runs=runs,
                metadata={'human_n':len(human),'datasets':len(entries),'reference':'Full supplied human reference',
                'ci':'Mean ± 1.96 × sample SD of repetition scores / sqrt(scorable runs)',
                'original_protocol':False,'source':'User data','fixed_human_reference':True})

def analyse_archive(path,output,original=False,progress=print):
    from .io import dataset_source
    study=load_study();root=Path(output);root.mkdir(parents=True,exist_ok=True)
    human,entries,handle=dataset_source(path)
    try:
        human=clean_frame(human,study,reference=True)
        if not entries:raise ValueError('No M1_R0001.csv-style datasets found.')
        if original:
            expected={(m,r) for m in range(1,9) for r in range(1,1001)}
            if len(human)!=2709 or len(entries)!=8000 or {(m,r) for m,r,_ in entries}!=expected:
                raise ValueError('Original protocol requires all 8,000 datasets and the full 2,709-person human reference.')
        # Content hashes bind checkpoints to the actual data and computation.
        engine=hashlib.sha256(Path(__file__).read_bytes()+Path(__file__).with_name('metrics.py').read_bytes()+Path(__file__).with_name('study.py').read_bytes()+(Path(__file__).parents[1]/'config/study.yaml').read_bytes()).hexdigest()
        hhash=hashlib.sha256(human.to_csv(index=False,float_format='%.17g').encode()).hexdigest()
        bundles=[]
        for m in sorted({x[0] for x in entries}):
            subset=[];digest=hashlib.sha256((engine+hhash).encode())
            for a,r,read in entries:
                if a!=m:continue
                frame=read()
                if original:
                    from .study import selected_fields
                    if len(frame)!=100 or set(frame.columns)!={'participant_id',*selected_fields(study)} or set(frame.participant_id)!=set(range(1,101)):raise ValueError('Invalid original dataset identifiers, fields or count.')
                digest.update(f'{a}:{r}'.encode());digest.update(frame.to_csv(index=False,float_format='%.17g').encode())
                subset.append((a,r,lambda f=frame:f))
            key=digest.hexdigest();cp=root/f'checkpoint_M{m}.pkl'
            # Checkpoints are private local files created by this program, never accepted as uploads.
            saved=None
            if cp.exists():
                with cp.open('rb') as f:saved=pickle.load(f)
            if saved and saved.get('hash')==key:
                b=saved['bundle'];progress(f'M{m}: using verified checkpoint')
            else:
                b=analyse(subset,human,study,lambda i,n:progress(f'M{m}: {i}/{n} scored'))
                temp=cp.with_suffix('.tmp')
                with temp.open('wb') as f:pickle.dump({'hash':key,'bundle':b},f)
                temp.replace(cp)
            bundles.append(b)
        runs=pd.concat([b['runs'] for b in bundles],ignore_index=True);summary,pairs=summarise(runs)
        result=dict(runs=runs,summary=summary,comparisons=pairs,
           variables=pd.concat([b['variables'] for b in bundles],ignore_index=True),human=bundles[0]['human'],
           metadata={**bundles[0]['metadata'],'datasets':len(entries),'original_protocol':original,
           'source':'Original MIDUS study' if original else 'User data','engine_sha256':engine})
        save_bundle(result,root);return result
    finally:
        if handle:handle.close()

def save_bundle(bundle,path,include_runs=True):
    root=Path(path);root.mkdir(parents=True,exist_ok=True)
    for key in ['summary','comparisons','variables','human']+(['runs'] if include_runs else []):
        bundle[key].to_csv(root/f'{key}.csv',index=False)
    (root/'metadata.json').write_text(json.dumps(bundle['metadata'],indent=2,allow_nan=False))

def load_bundle(path_or_bytes):
    from .io import archive,read_csv
    if isinstance(path_or_bytes,(str,Path)) and Path(path_or_bytes).is_dir():
        root=Path(path_or_bytes)
        b={k:read_csv(root/f'{k}.csv') for k in ['summary','comparisons','variables','human']}
        b['metadata']=json.loads((root/'metadata.json').read_text());return validate_bundle(b)
    z,ms=archive(path_or_bytes)
    try:
        def one(name):
            found=[n for n in ms if n.split('/')[-1]==name]
            if len(found)!=1:raise ValueError('Analysis bundle needs exactly one '+name)
            return z.read(ms[found[0]])
        b={k:read_csv(one(f'{k}.csv')) for k in ['summary','comparisons','variables','human']}
        b['metadata']=json.loads(one('metadata.json'))
        return validate_bundle(b)
    finally:z.close()

def validate_bundle(b):
    required={'summary':{'method','domain','wave','metric','n','mean','lower','upper'},
      'variables':{'method','code','mean','sd','smd','sd_ratio','sd_error','wasserstein','midus2_mean_r','midus3_mean_r'},
      'human':{'code','n','mean','sd','midus2_r','midus3_r'}}
    for name,fields in required.items():
        if not fields<=set(b[name]):raise ValueError('Invalid analysis bundle: '+name)
    if b['summary'].duplicated(['method','domain','wave','metric']).any():raise ValueError('Repeated summary keys.')
    if not set(b['summary'].method.unique())<=set(range(1,9)):raise ValueError('Methods must be M1–M8.')
    if b['variables'].duplicated(['method','code']).any() or b['human'].code.duplicated().any():raise ValueError('Repeated variable keys.')
    for name in ['summary','comparisons','variables','human']:
        values=b[name].select_dtypes(include='number').to_numpy()
        if np.isinf(values).any():raise ValueError('Infinite statistics in '+name)
    return b
