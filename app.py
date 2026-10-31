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
from spa.workflow import PURPOSES,INFORMATION,METHODS_BY_INFORMATION,purpose_guidance
from spa.io import read_csv
from spa import public_jobs as jobs
from spa import public as names
from spa.numbering import RUN_PATTERN,run_spa,run_parts,original_frame
from spa.errors import AppError,CATALOGUE
import json
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
    midus_fields:dict|None=None
    goal:str="distributions"
    sensitive_ack:bool=False

@app.middleware('http')
async def guard(request,call_next):
    if request.method in ('POST','DELETE'):
        origin=request.headers.get('origin')
        same=not origin or urlsplit(origin).netloc==request.headers.get('host')
        if request.headers.get('x-spa-request')!='1' or not same or request.headers.get('sec-fetch-site')=='cross-site':
            return error_response(AppError('blocked_request'))
        # Bound JSON bodies before parsing. Uploads travel inside this JSON, never as local files.
        body=bytearray()
        async for part in request.stream():
            body.extend(part)
            if len(body)>3_000_000:return error_response(AppError('request_too_large'))
        request._body=bytes(body)
    try:response=await call_next(request)
    except Exception:
        # Do not expose the API key or provider error bodies.
        return JSONResponse(dict(detail='The toolkit hit an unexpected problem while handling this request.',code='server_error',title='Something went wrong on the server',
          advice='Your inputs and any datasets are still in this tab. Try again in a moment. If it happens again, download completed datasets and contact the research team with the time of the error.',auto='none'),status_code=503)
    if request.url.path.startswith('/api/') and not custom_request(request):response=await publicise(response)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='same-origin'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
    if request.url.path.startswith('/api/'):response.headers['Cache-Control']='no-store'
    return response

def custom_request(request):
    """Custom studies contain only researcher-defined names, so they are never translated."""
    try:data=json.loads(getattr(request,'_body',b'') or b'{}')
    except ValueError:return False
    return isinstance(data,dict) and bool(data.get('study') or (isinstance(data.get('context'),dict) and data['context'].get('custom')))

async def publicise(response):
    """Translate MIDUS source codes to public variable names in every API response and download."""
    kind=response.headers.get('content-type','')
    if not (kind.startswith('application/json') or kind.startswith('text/csv')):return response
    body=b''.join([chunk async for chunk in response.body_iterator])
    if kind.startswith('application/json'):content=json.dumps(names.outbound(json.loads(body)),ensure_ascii=False,allow_nan=False).encode()
    else:content=names.text(body.decode('utf-8')).encode('utf-8')
    headers={k:v for k,v in response.headers.items() if k.lower()!='content-length'}
    return Response(content,status_code=response.status_code,headers=headers,media_type=kind)

def error_response(exc):return JSONResponse(exc.payload(),status_code=exc.status)

@app.exception_handler(AppError)
async def app_error(request,exc):return error_response(exc)

@app.exception_handler(RequestValidationError)
async def invalid_request(request,exc):
    return error_response(AppError('run_limits'))

@app.exception_handler(ValueError)
async def bad_value(request,exc):return error_response(AppError('invalid_input',detail=str(exc)))
@app.exception_handler(PermissionError)
async def denied(request,exc):return JSONResponse({'detail':str(exc)},status_code=403)
@app.exception_handler(LookupError)
async def missing(request,exc):return JSONResponse({'detail':str(exc)},status_code=404)

def assets(req,collect=None):
    if len(set(req.methods))!=len(req.methods) or any(m not in range(1,9) for m in req.methods):raise ValueError('Select one approach, SPA1–SPA8.')
    allowed={'proportions_SPA4','pilot_SPA5','pilot_SPA6','profiles_SPA7','profiles_SPA8'}
    if set(req.assets)-allowed:raise ValueError('Unknown upload type.')
    from spa import checks
    custom=None
    if req.study:
        from spa.custom import definition
        custom=definition(req.study)
    out={};warnings=[]
    for k,v in req.assets.items():
        text=v if req.study else names.inbound_csv(v)
        warn,text=checks.check_upload(k,text,custom);warnings+=warn
        try:out[k]=read_csv(text.lstrip('\ufeff').encode('utf-8'))
        except (ValueError,TypeError,StopIteration,UnicodeError):raise AppError('not_csv',label=checks.LABELS.get(k,'The file'),kind='an unreadable file') from None
    if collect is not None:collect.extend(warnings)
    return out

def display_results(frame,key):
    d=readable_results(frame)
    if key=='human':d=d.rename(columns={'Datasets included':'Human participants with observed scores',
      'Average across datasets':'Human mean','Average score SD':'Human score SD',
      'midus2_r':'Human baseline correlation','midus3_r':'Human follow-up correlation'})
    return d


def download(content,name,typ='application/zip'):
    # CSV files start with a UTF-8 byte order mark so Excel shows characters such as en dashes correctly.
    if typ=='text/csv':
        if isinstance(content,str):content=content.encode('utf-8')
        if not content.startswith(b'\xef\xbb\xbf'):content=b'\xef\xbb\xbf'+content
        typ='text/csv; charset=utf-8'
    return Response(content,media_type=typ,headers={'Content-Disposition':f'attachment; filename="{name}"','Cache-Control':'no-store'})

@app.get('/')
def index():return FileResponse(ROOT/'web/index.html')
@app.get('/app.js')
def js():return FileResponse(ROOT/'web/app.js',media_type='text/javascript')
@app.get('/study-charts.js')
def study_charts_script():return FileResponse(ROOT/'web/study-charts.js',media_type='text/javascript')

@app.get('/research.js')
def research_script():return FileResponse(ROOT/'web/research.js',media_type='text/javascript')
@app.get('/zip.js')
def zip_script():return FileResponse(ROOT/'web/zip.js',media_type='text/javascript')
@app.get('/style.css')
def css():return FileResponse(ROOT/'web/style.css',media_type='text/css')
@app.get('/console.js',include_in_schema=False)
def console_script():return FileResponse(ROOT/'web/console.js',media_type='text/javascript')
FONTS={'plexsans-var.woff2'}
@app.get('/fonts/{name}',include_in_schema=False)
def font(name:str):
    if name not in FONTS:raise HTTPException(404,'Font not found.')
    return FileResponse(ROOT/'web/fonts'/name,media_type='font/woff2',headers={'Cache-Control':'public, max-age=31536000, immutable'})

@app.get('/api/config')
def config():
    study=load_study()
    from spa.recommendations import PUBLIC_ID,PUBLIC_NAMES
    from spa.service import service_info
    return dict(service=service_info(),public_ids=PUBLIC_ID,public_names=PUBLIC_NAMES,intro=INTRO,scope=SCOPE,methods={m:dict(name=NAMES[m],**METHODS[m]) for m in NAMES},
      purpose_help={k:purpose_guidance(k,list(NAMES)) for k in PURPOSES},purposes=PURPOSES,information=INFORMATION,compatible=METHODS_BY_INFORMATION,terms=TERMS,metrics=METRICS,
      variable_guide=json_records(variable_guide(study)),midus_choices=__import__('spa.selection',fromlist=['choices']).choices(study),model=jobs.MODEL,reasoning='medium',batch_size=jobs.batch_size(),
      configured=bool(os.environ.get('OPENAI_API_KEY','').strip()))

@app.get('/api/guide.csv')
def guide():return download(variable_guide(load_study()).to_csv(index=False),'variable_guide.csv','text/csv')

@app.get('/api/example/{name}')
def example(name:str):
    from spa.workflow import EXAMPLE_FILES
    allowed={f'SPA{m}_template.csv':'examples/'+f for m,f in EXAMPLE_FILES.items()}
    if name not in allowed:raise HTTPException(404,'Example not found.')
    return download((ROOT/'data'/allowed[name]).read_bytes(),name,'text/csv')

@app.post('/api/preview')
def preview(req:Run):
    from spa.checks import content
    content(req);bank=jobs.prepare(req,assets(req));run=next(iter(bank));ctx=bank[run]
    body,_,_=jobs.batch(ctx,run_spa(run),0,req.n)
    return dict(run=run,system=body['instructions'],user=body['input'],provenance={k:c['provenance'] for k,c in bank.items()},
                note=f'This preview is the first of {req.n//jobs.batch_size()} requests that run at the same time. Each request receives its own participant IDs and fixed profiles.')

class Submit(BaseModel):
    model_config=ConfigDict(extra='forbid')
    ticket:str=Field(max_length=64000)
    run:str=Field(pattern='^'+RUN_PATTERN+'$')
    offset:int=Field(ge=0,le=99)
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
async def service_error(request,exc):
    return JSONResponse(dict(detail=str(exc),code='service_error',title='The AI service could not complete this step',advice='Download any completed datasets. Try again in a few minutes, or contact the research team if it continues.',auto='none'),status_code=503)

@app.post('/api/prepare')
def prepare_ai(req:Run):
    from spa.checks import content
    if not os.environ.get('OPENAI_API_KEY','').strip():raise AppError('not_configured')
    if not req.consent:raise AppError('consent_missing')
    content(req);warnings=[]
    plan=jobs.plan(req,assets(req,warnings));plan['warnings']=warnings
    return plan

@app.post('/api/submit')
def submit(req:Submit):return jobs.submit(req.ticket,req.run,req.offset,midus_context(req.context))

@app.post('/api/poll')
def poll(req:Poll):return jobs.poll(req.handle,midus_context(req.context))

def midus_context(ctx):return ctx if ctx.get('custom') else names.inbound(ctx)

@app.post('/api/release')
def release(req:Release):return jobs.release(req.handle,req.cancel)

@app.post('/api/dataset')
async def dataset_details(request:Request):
    data=await request.json();name=str(data.get('name',''))
    import re
    run_parts(name)
    if data.get('study'):
        from spa.custom import definition,clean_dataset as custom_clean,quality
        s=definition(data['study']);frame=custom_clean(data.get('records'),s,run_spa(name))
        from spa.codebook import build,csv
        book=build(list(frame.columns),run_spa(name),s)
        q=quality(frame,s,data.get('pilot'));from spa import checks
        generated=[r['column'] for r in book if r['provenance'] not in ('Retained from supplied profiles','Assigned locally','Constructed locally to match demographic proportions')]
        return dict(name=name,csv=frame.to_csv(index=False),codebook=book,codebook_csv=csv(book),preview=json_records(frame.head(10).rename(columns={r['column']:r['name']+' ['+r['column']+']' for r in book})),quality=q,
          warnings=checks.dataset_warnings(frame,q,generated,checks.custom_specs(s)))
    from spa.selection import parse,subset
    study=subset(load_study(),parse(data.get('midus_fields'),load_study()))
    frame=clean_dataset(names.inbound(data.get('records')),study)
    pilot=names.inbound(data.get('pilot'))
    if pilot is not None:
        if not isinstance(pilot,list) or len(pilot)!=50:raise ValueError('Expected 50 pilot records.')
        pilot=json_records(clean_frame(pd.DataFrame(pilot),study,expected_n=50))
    from spa.simulation import quality_flags
    from spa.codebook import build,csv
    book=build(list(frame.columns),run_spa(name))
    q=quality_flags(frame,study,pilot);from spa import checks
    generated=[r['column'] for r in book if r['provenance']=='Generated']
    return dict(name=name,csv=frame.to_csv(index=False),codebook=book,codebook_csv=csv(book),preview=json_records(readable_records(frame.head(10),study)),
                quality=q,warnings=checks.dataset_warnings(frame,q,generated,checks.midus_specs(study)))

def clean_dataset(rows,study=None):
    from spa.study import clean_frame
    study=study or load_study()
    if not isinstance(rows,list) or len(rows) not in range(100,1001,100):raise ValueError('Provide 100–1,000 records in steps of 100.')
    frame=clean_frame(pd.DataFrame(rows),study,expected_n=len(rows))
    if frame.participant_id.tolist()!=list(range(1,len(rows)+1)):raise ValueError('Participant identifiers must run from 1 to the dataset size, in order.')
    order=['participant_id']+[f for f in selected_fields(study) if f in frame]
    return frame[order+[c for c in frame.columns if c not in order]]

@app.get('/api/evidence')
def evidence():
    # Source files use the original study's numbering; relabel to SPA numbering (SPA7 demographic-only, SPA8 with psychology).
    raw={k:original_frame(read_csv(ROOT/'data/original_study'/f'{k}.csv')) for k in ['summary','comparisons','variables','human']}
    study=load_study()
    return {**{k:json_records(display_results(frame,k)) for k,frame in raw.items()},
      'charts':{'summary':json_records(raw['summary']),'variables':json_records(raw['variables']),
        'human':json_records(raw['human']),'method_names':__import__('spa.recommendations',fromlist=['PUBLIC_NAMES']).PUBLIC_NAMES,
        'variable_labels':{code:study['variables'][code]['label'] for code in study['psychological_predictors']},
        'reference_n':2709,'planned_repetitions':1000,'participants_per_dataset':100}}



@app.post('/api/recommend')
async def recommend(request:Request):
    from spa.recommendations import suggest
    d=await request.json()
    return suggest(d.get('goal','distributions'),d.get('information',[]))

@app.post('/api/custom-tools')
async def custom_tools(request:Request):
    from spa.custom import definition,guide,template
    d=await request.json();s=definition(d.get('study'))
    tables={k:template(s,k) for k in ['pilot','proportions','demographics','psychology']}
    blank={k:(f.assign(proportion=None) if k=='proportions' else f.iloc[:0]) for k,f in tables.items()}
    return dict(guide=guide(s),templates={k:f.to_csv(index=False) for k,f in tables.items()},blank_templates={k:f.to_csv(index=False) for k,f in blank.items()})

@app.post('/api/check-inputs')
def check_inputs(req:Run):
    from spa.checks import content
    topics=content(req);warnings=[]
    bank=jobs.prepare(req,assets(req,warnings))
    run=next(iter(bank));ctx=bank[run]
    body,_,_=jobs.batch(ctx,run_spa(run),0,req.n)
    jobs.check_size(body)
    # Schema/prompt construction is checked here without calling any provider.
    from spa.recommendations import public_label
    return dict(api_calls=0,approach=public_label(run_spa(run)),participants=req.n,
      input_source='Supplied fictional examples' if req.examples and not req.study else 'Your supplied study information',
      mode=ctx['provenance']['prompt_mode'],
      prompt_policy='Fixed research-team method template with a server-controlled study layer.',
      generated_fields=len(body['text']['format']['schema']['properties']['participants']['items']['required'])-1,
      note='Structural checks passed. Scientific validity needs your own review. Review the read-only instructions if needed.',
      warnings=warnings,sensitive_topics=topics)

@app.get('/api/template/{method}')
def blank_template(method:int):
    from spa.study import predictors
    if method not in (4,5,6,7,8):raise ValueError('This approach uses the study definitions only.')
    s=load_study()
    if method==4:
        from spa.proportions import blank_table,midus_spec
        return download(blank_table(midus_spec(s)).to_csv(index=False),'input_template.csv','text/csv')
    # One row per participant, one column per variable.
    frame=pd.DataFrame(columns=selected_fields(s) if method in (5,6) else predictors(s) if method==8 else s['demographic_covariates'])
    return download(frame.to_csv(index=False),'input_template.csv','text/csv')
