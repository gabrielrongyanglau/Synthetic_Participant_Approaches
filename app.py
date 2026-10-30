"""Vercel entrypoint: static interface plus short, public server requests without application storage."""
import os
from pathlib import Path
from urllib.parse import urlsplit
import pandas as pd
from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import FileResponse,Response,JSONResponse
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
    methods:list[int]=Field(min_length=1,max_length=8)
    n:int=Field(default=100,ge=100,le=1000,multiple_of=100)
    repetitions:int=Field(default=1,ge=1,le=5)
    seed:int=Field(default=1,ge=0,le=2147483647)
    examples:bool=True
    population:str=Field(default='Middle-aged and older adults in the specified US longitudinal cohort.',max_length=4000)
    assets:dict[str,str]=Field(default_factory=dict)
    consent:bool=False

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
    return {k:read_csv(v.encode('utf-8')) for k,v in req.assets.items()}

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
@app.get('/zip.js')
def zip_script():return FileResponse(ROOT/'web/zip.js',media_type='text/javascript')
@app.get('/style.css')
def css():return FileResponse(ROOT/'web/style.css',media_type='text/css')

@app.get('/api/config')
def config():
    study=load_study()
    return dict(intro=INTRO,scope=SCOPE,methods={m:dict(name=NAMES[m],**METHODS[m]) for m in NAMES},
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
    frame=clean_dataset(data.get('records'))
    pilot=data.get('pilot')
    if pilot is not None:
        if not isinstance(pilot,list) or len(pilot)!=50:raise ValueError('Expected 50 pilot records.')
        pilot=json_records(clean_frame(pd.DataFrame(pilot),load_study(),expected_n=50))
    from spa.simulation import quality_flags
    return dict(name=name,csv=frame.to_csv(index=False),preview=json_records(readable_records(frame.head(10),load_study())),
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
    data=await request.json();human=evaluation_reference(read_csv(str(data.get('csv','')).encode()),load_study())
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
        'human':json_records(raw['human']),'method_names':NAMES,
        'variable_labels':{code:study['variables'][code]['label'] for code in study['psychological_predictors']},
        'reference_n':2709,'planned_repetitions':1000,'participants_per_dataset':100}}


