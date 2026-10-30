"""Public, stateless generation. Inputs/results live only in request/browser memory.
Signed capabilities restrict polling to a response issued through this app.
They are not accounts, and are never written to files, cookies or a database.
"""
import base64,hashlib,hmac,json,os,secrets,time
from .study import load_study,json_records
from .workflow import context_bank
from .prompts import build_prompt
from .generation import output_schema,parse_records,response_text
from .simulation import quality_flags
MODEL='gpt-5.6-luna'

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,allow_nan=False,separators=(',',':')).encode()).hexdigest()
def signing_key():
    key=os.environ.get('OPENAI_API_KEY','').strip()
    if not key:raise RuntimeError('The owner has not configured OPENAI_API_KEY.')
    # Domain-separated signing key: only the derived HMAC authenticates temporary handles.
    return hmac.new(key.encode(),b'spa-public-v3-capabilities',hashlib.sha256).digest()
def b64(data):return base64.urlsafe_b64encode(data).rstrip(b'=').decode()
def unb64(text):return base64.urlsafe_b64decode(text+'='*((-len(text))%4))
def issue(claims):
    payload=b64(json.dumps(dict(claims,expires=int(time.time())+86400),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode())
    return payload+'.'+b64(hmac.new(signing_key(),payload.encode(),hashlib.sha256).digest())
def verify(token,kind):
    try:
        if len(token)>64000:raise ValueError()
        payload,signature=token.split('.')
        expected=b64(hmac.new(signing_key(),payload.encode(),hashlib.sha256).digest())
        if not hmac.compare_digest(expected,signature):raise ValueError()
        claims=json.loads(unb64(payload))
        if claims['kind']!=kind or type(claims['expires']) is not int or claims['expires']<time.time():raise ValueError()
        return claims
    except (ValueError,TypeError,KeyError,UnicodeError):raise ValueError('This temporary request handle is invalid or expired. It cannot be used to access a response.') from None

def settings(req):return dict(methods=req.methods,n=req.n,repetitions=req.repetitions,seed=req.seed,
    population=req.population,model=MODEL,reasoning_effort='medium',max_output_tokens=128000,batch_size=100)
def prepare(req,assets):
    if getattr(req,'study',None):
        from .custom import contexts
        return contexts(req,assets)
    return context_bank(load_study(),req.methods,req.n,req.repetitions,req.seed,assets,req.examples,req.population)
def plan(req,assets):
    from .service import check_run
    check_run(req)
    bank=prepare(req,assets);config=settings(req)
    if len(json.dumps(bank,allow_nan=False).encode())>3_500_000:raise ValueError('Prepared inputs are too large for one web response. Choose fewer approaches or repetitions in this run.')
    ticket=issue(dict(kind='plan',settings=config,runs={run:digest(ctx) for run,ctx in bank.items()},nonce=secrets.token_hex(16)))
    return dict(ticket=ticket,contexts=bank,settings=config,source='Fictional example inputs' if req.examples else 'Researcher-supplied inputs')

def batch(ctx,method,offset,n):
    ids=list(range(offset+1,min(n,offset+100)+1));fixed=ctx['fixed'][offset:offset+len(ids)] if ctx['fixed'] else None
    if ctx.get('custom'):
        from .custom import batch as custom_batch
        system,user,schema=custom_batch(ctx,method,ids,fixed)
        return dict(model=MODEL,instructions=system,input=user,reasoning={'effort':'medium'},max_output_tokens=128000,background=True,store=False,text={'format':{'type':'json_schema','name':'custom_participant_batch','strict':True,'schema':schema}}),fixed,ids
    system,user=build_prompt(load_study(),method,ids,fixed,ctx['pilot'],ctx['summary'],generated_only=True,
      population_guidance=ctx['provenance'].get('population_guidance',''))
    body=dict(model=MODEL,instructions=system,input=user,reasoning={'effort':'medium'},max_output_tokens=128000,
      background=True,store=False,text={'format':{'type':'json_schema','name':'participant_batch','strict':True,
      'schema':output_schema(load_study(),ids,fixed)}})
    return body,fixed,ids

def provider():
    from openai import OpenAI
    return OpenAI(api_key=os.environ['OPENAI_API_KEY'],timeout=35,max_retries=0)

def submit(ticket,run,offset,ctx,client=None):
    claims=verify(ticket,'plan')
    if run not in claims['runs'] or digest(ctx)!=claims['runs'][run]:raise ValueError('The inputs changed after preparation. Start a new run using the intended inputs.')
    from .service import check_run
    from types import SimpleNamespace
    check_run(SimpleNamespace(**claims['settings']))
    n=claims['settings']['n']
    if type(offset) is not int or offset<0 or offset>=n or offset%100:raise ValueError('Invalid batch position.')
    body,_,ids=batch(ctx,int(run[1]),offset,n)
    try:response=(client or provider()).responses.create(**body).model_dump(mode='json')
    except Exception as exc:
        code=getattr(exc,'status_code',None)
        if code and 400<=code<500:
            from .service import unavailable
            raise RuntimeError(unavailable()) from None
        raise RuntimeError('The submission could not be confirmed. It may have been accepted and charged. No automatic retry was made. Keep any completed downloads and contact the owner before starting this batch again.') from None
    handle=issue(dict(kind='response',response_id=response['id'],run=run,offset=offset,n=n,context_sha=digest(ctx)))
    return dict(handle=handle,status=response.get('status','queued'),run=run,start=ids[0],end=ids[-1])

def poll(handle,ctx,client=None):
    claims=verify(handle,'response')
    if digest(ctx)!=claims['context_sha']:raise ValueError('The supplied inputs do not match this temporary response handle.')
    try:response=(client or provider()).responses.retrieve(claims['response_id']).model_dump(mode='json')
    except Exception as exc:
        if getattr(exc,'status_code',None)==404:raise RuntimeError('OpenAI no longer has this temporary response available. It cannot be recovered from this prototype. No new paid request was submitted.') from None
        raise RuntimeError('Progress could not be retrieved. Keep this page open and choose Check again. Your current response handle remains in browser memory; no new paid request will be submitted by checking.') from None
    status=response.get('status')
    if status in ('queued','in_progress'):return dict(status=status)
    if status!='completed':
        from .service import contact
        return dict(status='error',message='The simulation could not finish. The team’s API budget or service limits may have been reached, or the response may have hit an output limit. No automatic paid retry was made. Download any completed datasets. '+contact()['text'])
    ids=list(range(claims['offset']+1,min(claims['n'],claims['offset']+100)+1))
    fixed=ctx['fixed'][claims['offset']:claims['offset']+len(ids)] if ctx['fixed'] else None
    try:
        if ctx.get('custom'):
            from .custom import parse as custom_parse
            frame=custom_parse(json.loads(response_text(response)),ctx['study'],ids,fixed)
        else:frame=parse_records(json.loads(response_text(response)),load_study(),ids,fixed)
    except (ValueError,KeyError,TypeError):return dict(status='error',message='The returned batch did not pass record-count, identifier, structure or range checks. No automatic paid retry was made.')
    if ctx.get('custom'):
        from .custom import quality
        flags=quality(frame,ctx['study'],ctx['pilot'])
    else:flags=quality_flags(frame,load_study(),ctx['pilot'])
    return dict(status='completed',run=claims['run'],records=json_records(frame),quality=flags)

def release(handle,cancel=False,client=None):
    claims=verify(handle,'response');client=client or provider()
    try:
        if cancel:client.responses.cancel(claims['response_id'])
        client.responses.delete(claims['response_id'])
        return {'released':True}
    except Exception:
        # No persistent cleanup queue. Provider retention applies if cleanup fails.
        return {'released':False}
