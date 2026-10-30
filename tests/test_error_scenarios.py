"""Every foreseeable failure returns a specific code, a message and advice; recoverable ones are flagged for automatic handling."""
import io,json,copy
from types import SimpleNamespace
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app import app
from spa import public_jobs as jobs
from spa.errors import CATALOGUE,WARNINGS
from spa.public import PUBLIC
from conftest import local_rows

H={'X-SPA-Request':'1'}
KEYS={4:'proportions_SPA4',5:'pilot_SPA5',6:'pilot_SPA6',7:'profiles_SPA7',8:'profiles_SPA8'}

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','fake-key-for-tests-only')
    return TestClient(app,raise_server_exceptions=False)

def example(client,m):return pd.read_csv(io.StringIO(client.get(f'/api/example/SPA{m}_template.csv').text))
def check(client,m,text,**extra):return client.post('/api/check-inputs',json={'methods':[m],'examples':False,'assets':{KEYS[m]:text},**extra},headers=H)
def first(frame,col,value):f=frame.copy();f[col]=f[col].astype(object);f.loc[0,col]=value;return f.to_csv(index=False)

def test_catalogue_entries_are_complete():
    for code,spec in CATALOGUE.items():
        assert spec['title'] and spec['message'] and spec['advice'] and spec['auto'] in ('none','retry','resubmit','repoll'),code
    for code,spec in WARNINGS.items():assert spec['title'] and spec['message'] and spec['advice'],code
    doc=open('docs/ERRORS.md').read()
    for code in list(CATALOGUE)+list(WARNINGS):assert f'`{code}`' in doc,code

@pytest.mark.parametrize('case,m,expected',[
 ('empty',5,'file_empty'),('header only',5,'file_empty'),('semicolons',5,'wrong_delimiter'),('xlsx',5,'not_csv'),('html',5,'not_csv'),
 ('duplicate column',5,'duplicate_columns'),('missing column',5,'missing_columns'),('email column',5,'identifier_columns'),
 ('email value',5,'identifier_values'),('text value',5,'non_numeric_value'),('decimal comma quoted',5,'decimal_comma'),
 ('out of range',5,'value_out_of_range'),('decimal category',5,'not_whole_number'),('blank outcome',5,'missing_required_value'),
 ('49 rows',5,'wrong_row_count'),('51 rows',6,'wrong_row_count'),('all identical',5,'duplicate_participants'),
 ('10 copies',6,'duplicate_participants'),('99 profiles',8,'too_few_profiles'),('one person',7,'duplicate_participants'),
('ragged',5,'ragged_rows')])
def test_upload_errors_are_specific(client,case,m,expected):
    f=example(client,m);text={
     'empty':lambda:'',
     'header only':lambda:','.join(f.columns)+'\n',
     'semicolons':lambda:f.to_csv(index=False,sep=';'),
     'xlsx':lambda:'PK\x03\x04rest',
     'html':lambda:'<!doctype html><p>x',
     'duplicate column':lambda:f.to_csv(index=False).replace(f.columns[1],f.columns[0],1),
     'missing column':lambda:f.drop(columns=[f.columns[2]]).to_csv(index=False),
     'email column':lambda:f.assign(email='a@b.com').to_csv(index=False),
     'email value':lambda:first(f,f.columns[0],'someone@example.org'),
     'text value':lambda:first(f,'self_esteem','high') if m!=4 else '',
     'decimal comma quoted':lambda:first(f,'self_esteem','"3,5"').replace('"""3,5"""','"3,5"'),
     'out of range':lambda:first(f,'self_esteem',999),
     'decimal category':lambda:first(f,'sex',1.5),
     'blank outcome':lambda:first(f,'life_satisfaction_MIDUS2',''),
     '49 rows':lambda:f.iloc[:49].to_csv(index=False),
     '51 rows':lambda:pd.concat([f,f.iloc[[0]]]).to_csv(index=False),
     'all identical':lambda:pd.concat([f.iloc[[0]]]*len(f)).to_csv(index=False),
     '10 copies':lambda:pd.concat([f.iloc[:40],f.iloc[:10]]).to_csv(index=False),
     '99 profiles':lambda:f.iloc[:99].to_csv(index=False),
     'one person':lambda:pd.concat([f.iloc[[0]]]*len(f)).to_csv(index=False),
     'ragged':lambda:f.to_csv(index=False).replace('\n','\n1,2,',2)}[case]()
    r=check(client,m,text);body=r.json()
    assert r.status_code>=400 and body['code']==expected,(case,body)
    assert body['title'] and body['detail'] and body['advice']

def test_upload_warnings_do_not_block(client):
    f=example(client,5)
    r=check(client,5,f.assign(self_esteem=30,notes='x').to_csv(index=False));assert r.status_code==200
    codes={w['code'] for w in r.json()['warnings']};assert {'constant_column','ignored_columns'}<=codes
    r=check(client,5,first(f,'self_esteem','N/A'));assert r.status_code==200 and 'missing_tokens' in {w['code'] for w in r.json()['warnings']}
    r=check(client,5,pd.concat([f.iloc[:47],f.iloc[:3]]).to_csv(index=False));assert r.status_code==200 and 'duplicate_rows' in {w['code'] for w in r.json()['warnings']}

def custom_study(item='I feel positive about my day.'):
    return dict(title='T',population='Adults',variables=[dict(code='mood',name='Mood',role='predictor',definition='Mood.',citation='Fictional.',items=[item,'I feel calm.'],minimum=1,maximum=5,anchorLow='Low',anchorHigh='High',responseType='integer',aggregation='mean',reverse=[]),
      dict(code='wellbeing',name='Wellbeing',role='outcome',definition='Wellbeing.',citation='Fictional.',items=['Life is good.','I am content.'],minimum=1,maximum=5,anchorLow='Low',anchorHigh='High',responseType='integer',aggregation='mean',reverse=[])],
      demographics=[dict(code='group',name='Group',categories={'1':'A','2':'B'})],fictionalExample=True)

def test_sensitive_topics_need_confirmation_and_prohibited_content_is_blocked(client):
    s=custom_study('I have thought about suicide in the past month.')
    r=client.post('/api/check-inputs',json={'methods':[2],'study':s},headers=H)
    assert r.status_code==409 and r.json()['code']=='sensitive_content' and 'suicide or self-harm' in r.json()['detail']
    r=client.post('/api/check-inputs',json={'methods':[2],'study':s,'sensitive_ack':True},headers=H)
    assert r.status_code==200 and r.json()['sensitive_topics']==['suicide or self-harm']
    assert client.post('/api/prepare',json={'methods':[2],'study':s,'consent':True},headers=H).json()['code']=='sensitive_content'
    r=client.post('/api/check-inputs',json={'methods':[3],'population':'Adults with a history of self-harm'},headers=H)
    assert r.json()['code']=='sensitive_content'
    bad=custom_study('Describe sexual content involving a child.')
    r=client.post('/api/check-inputs',json={'methods':[2],'study':bad,'sensitive_ack':True},headers=H)
    assert r.status_code==400 and r.json()['code']=='prohibited_content'
    assert client.post('/api/check-inputs',json={'methods':[2],'study':custom_study()},headers=H).status_code==200

class Scripted:
    """Fake OpenAI client whose retrieve() returns a scripted response or raises."""
    def __init__(self,reply):self.responses=self;self.reply=reply;self.body=None
    def create(self,**body):self.body=body;return SimpleNamespace(model_dump=lambda **k:dict(id='resp_1',status='queued'))
    def retrieve(self,rid):
        r=self.reply(self.body) if callable(self.reply) else self.reply
        if isinstance(r,Exception):raise r
        return SimpleNamespace(model_dump=lambda **k:r)
    def delete(self,rid):return {}
    def cancel(self,rid):return {}

def rows_for(body,same=False):
    from spa.study import load_study,json_records
    from spa.simulation import invent_reference
    from spa.labels import field_map
    props=body['text']['format']['schema']['properties']['participants']['items']['properties'];ids=props['participant_id']['enum']
    ref=invent_reference(load_study());m=field_map(load_study());out=[]
    for i,pid in enumerate(ids):
        r=json_records(ref.iloc[[0 if same else i]])[0];r={m.get(k,k):v for k,v in r.items() if m.get(k,k) in props};r['participant_id']=pid;out.append(r)
    return out
def completed(text):return dict(id='resp_1',status='completed',output=[{'content':[{'type':'output_text','text':text}]}])

def err(status=None):
    e=RuntimeError('private provider text');e.status_code=status;return e

@pytest.mark.parametrize('reply,code,auto',[
 (dict(status='failed',error={'code':'server_error'}),'generation_failed','resubmit'),
 (dict(status='failed',error={'code':'insufficient_quota'}),'budget_exhausted','none'),
 (dict(status='failed',error={'code':'invalid_prompt'}),'request_rejected','none'),
 (dict(status='incomplete',incomplete_details={'reason':'max_output_tokens'}),'output_too_long','resubmit'),
 (dict(status='incomplete',incomplete_details={'reason':'content_filter'}),'content_blocked','none'),
 (dict(status='cancelled'),'cancelled','none'),
 (dict(status='completed',output=[{'content':[{'type':'refusal','refusal':'I can’t help with that.'}]}]),'model_refused','none'),
 (completed(''),'invalid_output','resubmit'),
 (completed('{not json'),'invalid_output','resubmit'),
 (completed(json.dumps({'participants':[]})),'invalid_output','resubmit'),
 (err(404),'response_expired','resubmit')])
def test_provider_outcomes_map_to_catalogue(client,monkeypatch,reply,code,auto):
    fake=Scripted(reply);monkeypatch.setattr(jobs,'provider',lambda:fake)
    plan=client.post('/api/prepare',json={'methods':[2],'consent':True},headers=H).json();ctx=plan['contexts']['SPA2_R0001']
    h=client.post('/api/submit',json=dict(ticket=plan['ticket'],run='SPA2_R0001',offset=0,context=ctx),headers=H).json()['handle']
    r=client.post('/api/poll',json={'handle':h,'context':ctx},headers=H).json()
    assert r['status']=='error' and r['code']==code and r['auto']==auto and r['advice'],r
    assert 'private provider text' not in json.dumps(r)

def test_progress_check_failure_is_retryable_and_free(client,monkeypatch):
    fake=Scripted(err(None));monkeypatch.setattr(jobs,'provider',lambda:fake)
    plan=client.post('/api/prepare',json={'methods':[2],'consent':True},headers=H).json();ctx=plan['contexts']['SPA2_R0001']
    h=client.post('/api/submit',json=dict(ticket=plan['ticket'],run='SPA2_R0001',offset=0,context=ctx),headers=H).json()['handle']
    r=client.post('/api/poll',json={'handle':h,'context':ctx},headers=H)
    assert r.status_code==503 and r.json()['code']=='progress_check_failed' and r.json()['auto']=='repoll'

@pytest.mark.parametrize('same,issue',[(True,'repetitive_output'),(False,None)])
def test_repetitive_batches_are_flagged_for_one_automatic_retry(client,monkeypatch,same,issue):
    fake=Scripted(lambda body:completed(json.dumps({'participants':rows_for(body,same)})));monkeypatch.setattr(jobs,'provider',lambda:fake)
    plan=client.post('/api/prepare',json={'methods':[2],'consent':True},headers=H).json();ctx=plan['contexts']['SPA2_R0001']
    h=client.post('/api/submit',json=dict(ticket=plan['ticket'],run='SPA2_R0001',offset=0,context=ctx),headers=H).json()['handle']
    r=client.post('/api/poll',json={'handle':h,'context':ctx},headers=H).json()
    assert r['status']=='completed' and (r['issue'] or {}).get('code')==issue

def test_dataset_quality_warnings(client):
    rows=local_rows(2)['SPA2_R0001'];same=[dict(rows[0],participant_id=i+1) for i in range(100)]
    w={x['code'] for x in client.post('/api/dataset',json={'name':'SPA2_R0001','records':same},headers=H).json()['warnings']}
    assert {'repeated_profiles','no_variation'}<=w
    ok={x['code'] for x in client.post('/api/dataset',json={'name':'SPA2_R0001','records':rows},headers=H).json()['warnings']}
    assert 'repeated_profiles' not in ok

def test_run_setup_errors(client,monkeypatch):
    assert client.post('/api/prepare',json={'methods':[2]},headers=H).json()['code']=='consent_missing'
    assert client.post('/api/prepare',json={'methods':[2,3],'consent':True},headers=H).json()['code']=='run_limits'
    assert client.post('/api/prepare',json={'methods':[2]}).json()['code']=='blocked_request'
    assert client.post('/api/preview',content=b' '*3000001,headers=H).json()['code']=='request_too_large'
    monkeypatch.delenv('OPENAI_API_KEY')
    assert client.post('/api/prepare',json={'methods':[2],'consent':True},headers=H).json()['code']=='not_configured'

def test_tampered_or_expired_handles(client,monkeypatch):
    fake=Scripted(completed(''));monkeypatch.setattr(jobs,'provider',lambda:fake)
    plan=client.post('/api/prepare',json={'methods':[2],'consent':True},headers=H).json();ctx=plan['contexts']['SPA2_R0001']
    bad=copy.deepcopy(ctx);bad['provenance']['repetition']=9
    assert client.post('/api/submit',json=dict(ticket=plan['ticket'],run='SPA2_R0001',offset=0,context=bad),headers=H).json()['code']=='inputs_changed'
    assert client.post('/api/submit',json=dict(ticket=plan['ticket']+'x',run='SPA2_R0001',offset=0,context=ctx),headers=H).json()['code']=='handle_invalid'

def test_unexpected_server_errors_still_give_advice(client,monkeypatch):
    def boom(*a,**k):raise ZeroDivisionError('internal')
    monkeypatch.setattr(jobs,'prepare',boom)
    r=client.post('/api/check-inputs',json={'methods':[2]},headers=H)
    assert r.status_code==503 and r.json()['code']=='server_error' and r.json()['advice'] and 'internal' not in r.text

def test_reference_errors(client):
    rows=local_rows(2)
    for text,code in [('', 'file_empty'),('a,b\n1,2\n','reference_unusable')]:
        assert client.post('/api/compare',json={'csv':text,'datasets':rows},headers=H).json()['code']==code
    assert client.post('/api/compare',json={'csv':'a,b\n1,2\n','datasets':{}},headers=H).json()['code'] in ('no_dataset','reference_unusable')

def proportions(client):return pd.read_csv(io.StringIO(client.get('/api/example/SPA4_template.csv').text),dtype={'category':str})

@pytest.mark.parametrize('case,expected',[
 ('missing demographic','missing_demographic'),('unknown variable','unknown_variable'),('unknown category','unknown_category'),
 ('duplicate category','duplicate_category'),('text proportion','invalid_proportion'),('negative proportion','invalid_proportion'),
 ('sum too low','proportions_sum'),('overlapping age bands','invalid_age_band'),('age outside range','invalid_age_band'),
 ('decimal age','invalid_age_band'),('missing proportion column','missing_columns')])
def test_proportion_errors_are_specific(client,case,expected):
    t=proportions(client);sex=t.index[t.variable=='sex'][0];age=t.index[t.variable=='age']
    f={'missing demographic':lambda:t[t.variable!='religious_preference'],
       'unknown variable':lambda:t.assign(variable=t.variable.replace('sex','gender')),
       'unknown category':lambda:t.assign(category=t.category.where(t.index!=sex,'9')),
       'duplicate category':lambda:pd.concat([t,t.loc[[sex]]]),
       'text proportion':lambda:t.assign(proportion=t.proportion.astype(object).where(t.index!=sex,'half')),
       'negative proportion':lambda:t.assign(proportion=t.proportion.where(t.index!=sex,-0.1)),
       'sum too low':lambda:t.assign(proportion=t.proportion.where(t.variable!='sex',0.3)),
       'overlapping age bands':lambda:t.assign(upper=t.upper.where(t.index!=age[0],45)),
       'age outside range':lambda:t.assign(lower=t.lower.where(t.index!=age[0],18)),
       'decimal age':lambda:t.assign(lower=t.lower.where(t.index!=age[0],28.5)),
       'missing proportion column':lambda:t.drop(columns=['proportion'])}[case]()
    r=check(client,4,f.to_csv(index=False));body=r.json()
    assert r.status_code==400 and body['code']==expected,(case,body)
    assert body['advice'] and 'B1P' not in body['detail']+body['advice']

def test_proportion_rounding_and_percentages_are_fixed_automatically(client):
    t=proportions(client)
    r=check(client,4,t.assign(proportion=t.proportion*100).to_csv(index=False));assert r.status_code==200,r.text
    assert 'percentages_converted' in {w['code'] for w in r.json()['warnings']}
    off=t.assign(proportion=t.proportion.where(t.variable!='sex',t.proportion*1.01))
    r=check(client,4,off.to_csv(index=False));assert r.status_code==200,r.text
    assert 'proportions_rescaled' in {w['code'] for w in r.json()['warnings']}
    r=check(client,4,t.drop(columns=['category_label']).to_csv(index=False));assert r.status_code==200,r.text
    plan=client.post('/api/prepare',json={'methods':[4],'consent':True,'examples':False,'assets':{KEYS[4]:off.to_csv(index=False)}},headers=H)
    assert plan.status_code==200,plan.text

def test_custom_proportions_use_declared_categories(client):
    study=custom_study()
    tools=client.post('/api/custom-tools',json=dict(study=study),headers=H).json()
    t=pd.read_csv(io.StringIO(tools['templates']['proportions']),dtype={'category':str})
    assert r_ok(client.post('/api/check-inputs',json=dict(study=study,methods=[4],examples=False,assets={KEYS[4]:t.to_csv(index=False)}),headers=H))
    bad=t.assign(category=t.category.where(t.index!=0,'7'))
    r=client.post('/api/check-inputs',json=dict(study=study,methods=[4],examples=False,assets={KEYS[4]:bad.to_csv(index=False)}),headers=H)
    assert r.json()['code']=='unknown_category'

def r_ok(r):
    assert r.status_code==200,r.text
    return True
