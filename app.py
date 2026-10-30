"""Vercel entrypoint: static interface plus short, public server requests without application storage."""
import os
from pathlib import Path
from urllib.parse import urlsplit
import pandas as pd
from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import FileResponse,Response,JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel,ConfigDict,Field
from dotenv import load_dotenv
from spa.study import load_study,NAMES,json_records,selected_fields,clean_frame
from spa.content import INTRO,SCOPE,METHODS,TERMS,METRICS,variable_guide,readable_results,readable_records
from spa.workflow import PURPOSES,INFORMATION,METHODS_BY_INFORMATION,purpose_guidance,evaluation_reference,illustrative_generation,generated_metadata
from spa.io import read_csv
from spa import public_jobs as jobs
ROOT=Path(__file__).parent;load_dotenv(ROOT/'.env',override=False)
app=FastAPI(title='Synthetic Participant Research Toolkit',docs_url=None,redoc_url=None,openapi_url=None)

class Run(BaseModel):
    model_config=ConfigDict(extra='forbid')
    methods:list[int]=Field(min_length=1,max_length=1)
    n:int=Field(default=100,ge=100,le=100,multiple_of=100)
    repetitions:int=Field(default=1,ge=1,le=1)
    seed:int=Field(default=1,ge=0,le=2147483647)
    examples:bool=True
    population:str=Field(default='Middle-aged and older adults in the specified US longitudinal cohort.',max_length=4000)
    assets:dict[str,str]=Field(default_factory=dict)
    consent:bool=False
    study:dict|None=None
    goal:str="workflow"
    supporting:dict=Field(default_factory=dict)

@app.middleware('http')
async def guard(request,call_next):
    if request.method in ('POST','DELETE'):
        origin=request.headers.get('origin')
        same=not origin or urlsplit(origin).netloc==request.headers.get('host')
        if request.headers.get('x-spa-request')!='1' or not same or request.headers.get('sec-fetch-site')=='cross-site':
            return JSONResponse({'detail':'Open the toolkit directly to make this request.'},status_code=403)
        # Bound JSON bodies before parsing. Uploads travel inside this JSON, never as local files.
        body=bytearray()
        async for part in request.stream():
            body.extend(part)
            if len(body)>3_000_000:return JSONResponse({'detail':'Inputs exceed 3 MB. Supply a smaller CSV pool.'},status_code=413)
        request._body=bytes(body)
    try:response=await call_next(request)
    except Exception:
        # Do not expose the API key or provider error bodies.
        return JSONResponse({'detail':'The service could not complete this request. Keep this page open and download any completed datasets. Ask the owner to check the service configuration.'},status_code=503)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='same-origin'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    if request.url.path.startswith('/api/'):response.headers['Cache-Control']='no-store'
    return response

@app.exception_handler(RequestValidationError)
async def invalid_request(request,exc):
    return JSONResponse({'detail':'Check the simulation settings and required fields. Select one approach and 100 participants. Use the supplied input templates; prompt editing and model changes are unavailable.'},status_code=422)

@app.exception_handler(ValueError)
async def bad_value(request,exc):return JSONResponse({'detail':str(exc)},status_code=400)
@app.exception_handler(PermissionError)
async def denied(request,exc):return JSONResponse({'detail':str(exc)},status_code=403)
@app.exception_handler(LookupError)
async def missing(request,exc):return JSONResponse({'detail':str(exc)},status_code=404)

def assets(req):
    if len(set(req.methods))!=len(req.methods) or any(m not in range(1,9) for m in req.methods):raise ValueError('Select distinct approaches M1–M8.')
    allowed={'proportions','pilot_M5','pilot_M6','profiles_M7','profiles_M8'}
    if set(req.assets)-allowed:raise ValueError('Unknown upload type.')
    try:return {k:read_csv(v.encode('utf-8')) for k,v in req.assets.items()}
    except (ValueError,TypeError,StopIteration,UnicodeError):raise ValueError('A CSV could not be read. Save it as UTF-8 comma-separated CSV, use the template headers once, and check that all data values are numeric or blank.') from None

def display_results(frame,key):
    d=readable_results(frame)
    if key=='human':d=d.rename(columns={'Datasets included':'Human participants with observed scores',
      'Average across datasets':'Human mean','Average score SD':'Human score SD',
      'midus2_r':'Human baseline correlation','midus3_r':'Human follow-up correlation'})
    return d


def download(content,name,typ='application/zip'):
    return Response(content,media_type=typ,headers={'Content-Disposition':f'attachment; filename="{name}"','Cache-Control':'no-store'})

@app.get('/')
def index():return FileResponse(ROOT/'web/index.html')
@app.get('/app.js')
def js():return FileResponse(ROOT/'web/app.js',media_type='text/javascript')
@app.get('/study-charts.js')
def study_charts_script():return FileResponse(ROOT/'web/study-charts.js',media_type='text/javascript')
@app.get('/supporting.js')
def supporting_script():return FileResponse(ROOT/'web/supporting.js',media_type='text/javascript')

@app.get('/research.js')
def research_script():return FileResponse(ROOT/'web/research.js',media_type='text/javascript')
@app.get('/zip.js')
def zip_script():return FileResponse(ROOT/'web/zip.js',media_type='text/javascript')
@app.get('/style.css')
def css():return FileResponse(ROOT/'web/style.css',media_type='text/css')

@app.get('/api/config')
def config():
    study=load_study()
    from spa.recommendations import PUBLIC_ID,PUBLIC_NAMES
    from spa.service import service_info
    return dict(service=service_info(),public_ids=PUBLIC_ID,public_names=PUBLIC_NAMES,intro=INTRO,scope=SCOPE,methods={m:dict(name=NAMES[m],**METHODS[m]) for m in NAMES},
      purpose_help={k:purpose_guidance(k,list(NAMES)) for k in PURPOSES},purposes=PURPOSES,information=INFORMATION,compatible=METHODS_BY_INFORMATION,terms=TERMS,metrics=METRICS,
      variable_guide=json_records(variable_guide(study)),model=jobs.MODEL,reasoning='medium',
      configured=bool(os.environ.get('OPENAI_API_KEY','').strip()))

@app.get('/api/guide.csv')
def guide():return download(variable_guide(load_study()).to_csv(index=False),'variable_guide.csv','text/csv')

@app.get('/api/example/{name}')
def example(name:str):
    allowed={'pilot.csv':'templates/pilot.csv','M7_profiles.csv':'templates/M7_profiles.csv','M8_profiles.csv':'templates/M8_profiles.csv',
      'demographic_proportions.csv':'templates/demographic_proportions.csv',**{f'M{m}_inputs.csv':f'examples/M{m}_{"pilot" if m in (5,6) else "profiles"}_example.csv' for m in (5,6,7,8)}}
    if name not in allowed:raise HTTPException(404,'Example not found.')
    return download((ROOT/'data'/allowed[name]).read_bytes(),name,'text/csv')

@app.post('/api/preview')
def preview(req:Run):
    bank=jobs.prepare(req,assets(req));run=next(iter(bank));ctx=bank[run]
    body,_,_=jobs.batch(ctx,int(run[1]),0,req.n)
    return dict(run=run,system=body['instructions'],user=body['input'],provenance={k:c['provenance'] for k,c in bank.items()},
                note='This preview is the first batch of the first selected approach. Each later batch receives its own participant IDs and fixed profiles.')

@app.post('/api/demo')
def demo(req:Run):
    if not req.examples:raise ValueError('The free demonstration uses fictional examples. Choose AI generation to use your own data.')
    if req.repetitions!=1 or len(req.methods)!=1:raise ValueError('Request one approach and one repetition at a time for the demonstration.')
    bank=jobs.prepare(req,assets(req));study=load_study();frames={}
    if req.study:
        from spa.custom import demo,quality
        for run,ctx in bank.items():frames[run]=demo(ctx,int(run[1]),req.n,req.seed)
        return dict(datasets={run:json_records(f) for run,f in frames.items()},metadata=dict(input_provenance={run:c['provenance'] for run,c in bank.items()},quality_flags={run:quality(f,ctx['study'],bank[run]['pilot']) for run,f in frames.items()}))
    for run,ctx in bank.items():
        m=int(run[1]);r=int(run.split('_R')[1]);frames[(m,r)]=illustrative_generation(study,m,req.n,req.seed,r,ctx)
    meta=generated_metadata(frames,bank,study,jobs.settings(req),'Invented numerical demonstration — no AI calls','workflow')
    return dict(datasets={f'M{m}_R{r:04d}':json_records(f) for (m,r),f in frames.items()},metadata=meta)

class Submit(BaseModel):
    model_config=ConfigDict(extra='forbid')
    ticket:str=Field(max_length=64000)
    run:str=Field(pattern=r'^M[1-8]_R[0-9]{4}$')
    offset:int=Field(ge=0,le=900,multiple_of=100)
    context:dict

class Poll(BaseModel):
    model_config=ConfigDict(extra='forbid')
    handle:str=Field(max_length=64000)
    context:dict

class Release(BaseModel):
    model_config=ConfigDict(extra='forbid')
    handle:str=Field(max_length=64000)
    cancel:bool=False

@app.exception_handler(RuntimeError)
async def service_error(request,exc):return JSONResponse({'detail':str(exc)},status_code=503)

@app.post('/api/prepare')
def prepare_ai(req:Run):
    if not os.environ.get('OPENAI_API_KEY','').strip():raise RuntimeError('The owner must configure OPENAI_API_KEY in Vercel before AI generation is available.')
    if not req.consent:raise ValueError('Confirm that inputs may be sent to OpenAI and that generation incurs charges for the owner.')
    return jobs.plan(req,assets(req))

@app.post('/api/submit')
def submit(req:Submit):return jobs.submit(req.ticket,req.run,req.offset,req.context)

@app.post('/api/poll')
def poll(req:Poll):return jobs.poll(req.handle,req.context)

@app.post('/api/release')
def release(req:Release):return jobs.release(req.handle,req.cancel)

@app.post('/api/dataset')
async def dataset_details(request:Request):
    data=await request.json();name=str(data.get('name',''))
    import re
    if not re.fullmatch(r'M[1-8]_R[0-9]{4}',name):raise ValueError('Invalid dataset name.')
    if data.get('study'):
        from spa.custom import definition,clean_dataset as custom_clean,quality
        s=definition(data['study']);frame=custom_clean(data.get('records'),s,int(name[1]))
        from spa.codebook import build,csv
        book=build(list(frame.columns),int(name[1]),s)
        return dict(name=name,csv=frame.to_csv(index=False),codebook=book,codebook_csv=csv(book),preview=json_records(frame.head(10).rename(columns={r['column']:r['name']+' ['+r['column']+']' for r in book})),quality=quality(frame,s,data.get('pilot')))
    frame=clean_dataset(data.get('records'))
    pilot=data.get('pilot')
    if pilot is not None:
        if not isinstance(pilot,list) or len(pilot)!=50:raise ValueError('Expected 50 pilot records.')
        pilot=json_records(clean_frame(pd.DataFrame(pilot),load_study(),expected_n=50))
    from spa.simulation import quality_flags
    from spa.codebook import build,csv
    book=build(list(frame.columns),int(name[1]))
    return dict(name=name,csv=frame.to_csv(index=False),codebook=book,codebook_csv=csv(book),preview=json_records(readable_records(frame.head(10),load_study())),
                quality=quality_flags(frame,load_study(),pilot))

def clean_dataset(rows):
    from spa.study import clean_frame
    if not isinstance(rows,list) or len(rows) not in range(100,1001,100):raise ValueError('Provide 100–1,000 records in steps of 100.')
    frame=clean_frame(pd.DataFrame(rows),load_study(),expected_n=len(rows))
    if frame.participant_id.tolist()!=list(range(1,len(rows)+1)):raise ValueError('Participant identifiers must run from 1 to the dataset size, in order.')
    return frame

@app.post('/api/compare')
async def compare(request:Request):
    from spa.analysis import analyse
    import re
    data=await request.json()
    if data.get('study'):return compare_custom(data)
    human=evaluation_reference(read_csv(str(data.get('csv','')).encode()),load_study())
    raw=data.get('datasets',{})
    if not isinstance(raw,dict) or not 1<=len(raw)<=40:raise ValueError('Provide 1–40 completed datasets.')
    entries=[]
    for run,rows in raw.items():
        if not re.fullmatch(r'M[1-8]_R[0-9]{4}',run):raise ValueError('Invalid dataset name.')
        frame=clean_dataset(rows);entries.append((int(run[1]),int(run.split('_R')[1]),lambda f=frame:f))
    b=analyse(entries,human,load_study())
    return {**{k:json_records(display_results(b[k],k)) for k in ['summary','comparisons','variables','human']},
      'metadata':b['metadata'],'csv_exports':{k:b[k].to_csv(index=False) for k in ['summary','comparisons','variables','human','runs']}}

@app.get('/api/evidence')
def evidence():
    raw={k:read_csv(ROOT/'data/original_study'/f'{k}.csv') for k in ['summary','comparisons','variables','human']}
    study=load_study()
    return {**{k:json_records(display_results(frame,k)) for k,frame in raw.items()},
      'charts':{'summary':json_records(raw['summary']),'variables':json_records(raw['variables']),
        'human':json_records(raw['human']),'method_names':{m:__import__('spa.recommendations',fromlist=['PUBLIC_ID','PUBLIC_NAMES']).PUBLIC_NAMES[__import__('spa.recommendations',fromlist=['PUBLIC_ID']).PUBLIC_ID[m]] for m in NAMES},
        'variable_labels':{code:study['variables'][code]['label'] for code in study['psychological_predictors']},
        'reference_n':2709,'planned_repetitions':1000,'participants_per_dataset':100}}



@app.post('/api/recommend')
async def recommend(request:Request):
    from spa.recommendations import suggest
    d=await request.json()
    return suggest(d.get('goal','workflow'),d.get('information',[]))

@app.post('/api/custom-tools')
async def custom_tools(request:Request):
    from spa.custom import definition,guide,template
    d=await request.json();s=definition(d.get('study'))
    tables={k:template(s,k) for k in ['pilot','demographics','psychology','proportions','reference']}
    return dict(guide=guide(s),templates={k:f.to_csv(index=False) for k,f in tables.items()},blank_templates={k:(f.assign(proportion='') if k=='proportions' else f.iloc[:0]).to_csv(index=False) for k,f in tables.items()})

def compare_custom(data):
    import re
    from spa.custom import definition,comparison
    from spa.recommendations import public_label,public_run
    s=definition(data['study']);datasets=data.get('datasets',{})
    if not isinstance(datasets,dict) or not 1<=len(datasets)<=40 or any(not re.fullmatch(r'M[1-8]_R[0-9]{4}',r) for r in datasets):raise ValueError('Provide 1–40 completed datasets with valid names.')
    human=read_csv(str(data.get('csv','')).encode());methods=sorted({int(r[1]) for r in datasets})
    summary,pairs,variables=comparison(datasets,human,s,methods)
    if 'run' in variables:variables['run']=variables['run'].map(public_run)
    for frame in (summary,pairs):
        if 'metric' in frame:frame['metric']=frame['metric'].map(lambda m:METRICS[m][0] if m in METRICS else 'Proportion of matching correlation signs')
        if 'domain' in frame:frame['domain']=frame['domain'].map({'distribution':'Score distributions','relationship':'Psychological relationships'})
        for key in ('method','first','second'):
            if key in frame:frame[key]=frame[key].map(public_label)
    return dict(summary=json_records(summary),comparisons=json_records(pairs),variables=json_records(variables),
      metadata=dict(datasets=len(datasets),human_n=len(human),note='Custom-study extension. Scores use the declared rules; no anxiety exclusion. Pattern r requires at least three varying paired coefficients. Undefined statistics remain blank. Intervals describe mean performance across available runs against the fixed supplied reference.'),
      csv_exports={k:f.to_csv(index=False) for k,f in [('summary',summary),('comparisons',pairs),('variables',variables)]})

class Paper(BaseModel):
    model_config=ConfigDict(extra='forbid')
    filename:str=Field(max_length=300)
    data:str=Field(max_length=2_000_004)

@app.post('/api/extract-paper')
def extract_paper(req:Paper):
    from spa.evidence import extract_pdf
    return extract_pdf(req.data,req.filename)

@app.post('/api/check-inputs')
def check_inputs(req:Run):
    bank=jobs.prepare(req,assets(req))
    run=next(iter(bank));ctx=bank[run]
    body,_,_=jobs.batch(ctx,int(run[1]),0,req.n)
    # Schema/prompt construction is checked here without calling any provider.
    from spa.recommendations import public_label
    return dict(api_calls=0,approach=public_label(int(run[1])),participants=req.n,
      input_source='Supplied fictional examples' if req.examples else 'Your supplied study information',
      mode=ctx['provenance']['prompt_mode'],supporting_sources=len(ctx.get('supporting',{}).get('sources',[])),
      prompt_policy='Fixed research-team method template; server-controlled study/evidence layer; no visitor prompt editing.',
      generated_fields=len(body['text']['format']['schema']['properties']['participants']['items']['required'])-1,
      note='Structural checks passed. This does not verify source quality or scientific validity. Review the read-only instructions if needed.')

@app.get('/api/template/{method}')
def blank_template(method:int):
    from spa.study import predictors
    from spa.workflow import quota_template
    if method not in (4,5,6,7,8):raise ValueError('This approach does not need a participant-data upload.')
    s=load_study()
    if method==4:
        # Category rows and ranges are supplied; users fill in proportions.
        from spa.simulation import invent_reference
        frame=quota_template(invent_reference(s),s);frame['proportion']=''
    else:frame=pd.DataFrame(columns=selected_fields(s) if method in (5,6) else predictors(s) if method==7 else s['demographic_covariates'])
    return download(frame.to_csv(index=False),'input_template.csv','text/csv')
