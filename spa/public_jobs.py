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
from .numbering import run_spa
MODEL='gpt-5.6-luna'

def batch_size():
    """Participants per AI request. Requests for one dataset run in parallel, so smaller batches finish sooner.
    SPA_BATCH_SIZE may be 25, 50 or 100; 100 reproduces the single-request protocol of the original MIDUS evaluation."""
    raw=os.environ.get('SPA_BATCH_SIZE','25').strip()
    return int(raw) if raw in ('25','50','100') else 25

def canonical(value):
    """Browsers serialise whole-number decimals (3.0) as integers (3); normalise so signatures survive the round trip."""
    if isinstance(value,dict):return {k:canonical(v) for k,v in value.items()}
    if isinstance(value,list):return [canonical(v) for v in value]
    if isinstance(value,float) and value.is_integer():return int(value)
    return value
def digest(value):return hashlib.sha256(json.dumps(canonical(value),sort_keys=True,allow_nan=False,separators=(',',':')).encode()).hexdigest()
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
    except (ValueError,TypeError,KeyError,UnicodeError):raise ValueError('This temporary request handle is invalid or expired.') from None

def settings(req):return dict(methods=req.methods,n=req.n,repetitions=req.repetitions,seed=req.seed,
    population=req.population,model=MODEL,reasoning_effort='medium',max_output_tokens=128000,batch_size=batch_size())
def prepare(req,assets):
    from .evidence import clean
    evidence=clean(getattr(req,'supporting',{}))
    if not getattr(req,'study',None) and evidence['reviewed']:
        raise ValueError('Supporting papers and research context are available in Use your own study. The MIDUS demonstration keeps the original study prompts.')
    if getattr(req,'study',None):
        from .custom import contexts
        bank=contexts(req,assets)
    else:bank=context_bank(load_study(),req.methods,req.n,req.repetitions,req.seed,assets,req.examples,req.population)
    for ctx in bank.values():
        if evidence['reviewed']:ctx['supporting']=evidence
        from .study import PROJECT_ROOT
        ctx['provenance']['method_prompt_bank_sha256']=hashlib.sha256((PROJECT_ROOT/'prompts/methods.json').read_bytes()).hexdigest()
        ctx['provenance']['prompt_mode']='Literature-informed custom adaptation' if evidence['reviewed'] else ('Custom measurement adaptation' if ctx.get('custom') else 'Original MIDUS method template')
    return bank
def plan(req,assets):
    from .service import check_run
    check_run(req)
    bank=prepare(req,assets);config=settings(req)
    if len(json.dumps(bank,allow_nan=False).encode())>3_500_000:raise ValueError('Prepared inputs are too large for one web response. Choose fewer approaches or repetitions in this run.')
    ticket=issue(dict(kind='plan',settings=config,runs={run:digest(ctx) for run,ctx in bank.items()},nonce=secrets.token_hex(16)))
    return dict(ticket=ticket,contexts=bank,settings=config,source='Fictional example inputs' if req.examples else 'Researcher-supplied inputs')

def batch(ctx,method,offset,n,size=None):
    size=size or batch_size()
    ids=list(range(offset+1,min(n,offset+size)+1));fixed=ctx['fixed'][offset:offset+len(ids)] if ctx['fixed'] else None
    if ctx.get('custom'):
        from .custom import batch as custom_batch
        system,user,schema=custom_batch(ctx,method,ids,fixed)
        from .evidence import system_extension
        system+=system_extension(ctx.get('supporting',{}))
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

MAX_PROMPT_CHARS=900_000
_sleep=time.sleep

def check_size(body):
    from .errors import AppError
    if len(body['instructions'])+len(body['input'])>MAX_PROMPT_CHARS:raise AppError('inputs_too_large_for_model')

def provider_error(exc):
    """Map an OpenAI SDK exception to a catalogue error without exposing provider messages."""
    from .errors import AppError
    status=getattr(exc,'status_code',None);body=getattr(exc,'body',None)
    detail=body.get('error',body) if isinstance(body,dict) else {}
    code=str(getattr(exc,'code',None) or (detail.get('code') if isinstance(detail,dict) else '') or '')
    text=(str(getattr(exc,'message','') or '')+' '+code).lower()
    if status==429:
        if 'insufficient_quota' in text or 'quota' in text or 'billing' in text or 'credit' in text:return AppError('budget_exhausted')
        return AppError('service_busy')
    if status==401:return AppError('service_key_invalid')
    if status in (403,404):return AppError('service_access_denied')
    if status==400 and ('context_length' in text or 'too long' in text or 'maximum context' in text or 'too large' in text):return AppError('inputs_too_large_for_model')
    if status in (400,409,413,422):return AppError('request_rejected',reason='its format or content was not accepted by OpenAI.')
    if status and status>=500:return AppError('service_unavailable')
    return AppError('submission_uncertain')

def submit(ticket,run,offset,ctx,client=None):
    from .errors import AppError
    try:claims=verify(ticket,'plan')
    except ValueError:raise AppError('handle_invalid') from None
    if run not in claims['runs'] or digest(ctx)!=claims['runs'][run]:raise AppError('inputs_changed')
    from .service import check_run
    from types import SimpleNamespace
    check_run(SimpleNamespace(**claims['settings']))
    n=claims['settings']['n'];size=claims['settings'].get('batch_size',100)
    if type(offset) is not int or offset<0 or offset>=n or offset%size:raise ValueError('Invalid batch position.')
    body,_,ids=batch(ctx,run_spa(run),offset,n,size);check_size(body)
    client=client or provider()
    for attempt in range(3):
        try:
            response=client.responses.create(**body).model_dump(mode='json');break
        except Exception as exc:
            error=provider_error(exc)
            # Declined requests (rate limit, server error) were not accepted, so retrying cannot double-charge.
            if error.code in ('service_busy','service_unavailable') and attempt<2:_sleep((1.5,4)[attempt]);continue
            raise error from None
    handle=issue(dict(kind='response',response_id=response['id'],run=run,offset=offset,n=n,size=size,context_sha=digest(ctx)))
    return dict(handle=handle,status=response.get('status','queued'),run=run,start=ids[0],end=ids[-1])

def failed(code,**params):
    from .errors import AppError
    return dict(status='error',**AppError(code,**params).payload())

def poll(handle,ctx,client=None):
    from .errors import AppError
    try:claims=verify(handle,'response')
    except ValueError:raise AppError('handle_invalid') from None
    if digest(ctx)!=claims['context_sha']:raise AppError('inputs_changed')
    try:response=(client or provider()).responses.retrieve(claims['response_id']).model_dump(mode='json')
    except Exception as exc:
        if getattr(exc,'status_code',None)==404:return failed('response_expired')
        raise AppError('progress_check_failed') from None
    status=response.get('status')
    if status in ('queued','in_progress'):return dict(status=status)
    if status=='cancelled':return failed('cancelled')
    if status=='failed':
        code=str((response.get('error') or {}).get('code') or '')
        if 'quota' in code:return failed('budget_exhausted')
        if code=='invalid_prompt':return failed('request_rejected',reason='OpenAI flagged the instructions as invalid.')
        return failed('generation_failed',reason={'rate_limit_exceeded':'service rate limit','server_error':'temporary server error'}.get(code,code.replace('_',' ') or 'no reason given'))
    if status=='incomplete':
        reason=str((response.get('incomplete_details') or {}).get('reason') or '')
        if reason=='content_filter':return failed('content_blocked')
        if reason=='max_output_tokens':return failed('output_too_long')
        return failed('generation_failed',reason='the response was incomplete')
    if status!='completed':return failed('generation_failed',reason=f'unexpected status "{status}"')
    refusal=' '.join(c.get('refusal','') for item in response.get('output',[]) for c in item.get('content',[]) if c.get('type')=='refusal').strip()
    if refusal:return failed('model_refused',reason=refusal[:300])
    ids=list(range(claims['offset']+1,min(claims['n'],claims['offset']+claims.get('size',100))+1))
    fixed=ctx['fixed'][claims['offset']:claims['offset']+len(ids)] if ctx['fixed'] else None
    text=response_text(response)
    if not text.strip():return failed('invalid_output',reason='no data was returned')
    try:data=json.loads(text)
    except ValueError:return failed('invalid_output',reason='the reply was not valid JSON')
    try:
        if ctx.get('custom'):
            from .custom import parse as custom_parse
            frame=custom_parse(data,ctx['study'],ids,fixed)
        else:frame=parse_records(data,load_study(),ids,fixed)
    except (ValueError,KeyError,TypeError) as exc:return failed('invalid_output',reason=str(exc).rstrip('.')[:120] or 'structure check failed')
    if ctx.get('custom'):
        from .custom import quality
        flags=quality(frame,ctx['study'],ctx['pilot'])
    else:flags=quality_flags(frame,load_study(),ctx['pilot'])
    generated=[c for c in frame.columns if c!='participant_id' and not (fixed and c in fixed[0])]
    repeats=int(frame[generated].round(4).duplicated().sum()) if generated else 0
    issue=None
    if repeats>=max(2,int(.1*len(frame))):issue=AppError('repetitive_output',count=repeats,size=len(frame)).payload()
    elif flags.get('pilot_record_matches',0)>=2:issue=AppError('copied_pilot',count=flags['pilot_record_matches']).payload()
    return dict(status='completed',run=claims['run'],records=json_records(frame),quality=flags,issue=issue)

def release(handle,cancel=False,client=None):
    claims=verify(handle,'response');client=client or provider()
    try:
        if cancel:client.responses.cancel(claims['response_id'])
        client.responses.delete(claims['response_id'])
        return {'released':True}
    except Exception:
        # No persistent cleanup queue. Provider retention applies if cleanup fails.
        return {'released':False}
