import builtins,copy,json,os
from types import SimpleNamespace
from pathlib import Path
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app import app
from spa import public_jobs as jobs
from spa.study import load_study,json_records
from spa.simulation import invent_reference
from spa.labels import field_map
from conftest import local_rows
H={'X-SPA-Request':'1'}

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','fake-key-for-tests-only')
    monkeypatch.delenv('DATABASE_URL',raising=False);monkeypatch.delenv('SPA_INVITES_JSON',raising=False)
    return TestClient(app)

class FakeProvider:
    def __init__(self,fail_submit=False):self.responses=self;self.requests={};self.created=[];self.deleted=[];self.fail_submit=fail_submit
    def create(self,**body):
        self.created.append(body)
        if self.fail_submit:raise ConnectionError('private provider message never displayed')
        rid='resp_mock_'+str(len(self.created));self.requests[rid]=body
        return SimpleNamespace(model_dump=lambda **k:dict(id=rid,status='in_progress'))
    def retrieve(self,rid):
        props=self.requests[rid]['text']['format']['schema']['properties']['participants']['items']['properties']
        ids=props['participant_id']['enum'];s=load_study();row=json_records(invent_reference(s).iloc[:1])[0];mapping=field_map(s)
        row={mapping.get(k,k):v for k,v in row.items() if mapping.get(k,k) in props}
        rows=[dict(row,participant_id=i) for i in ids]
        return SimpleNamespace(model_dump=lambda **k:dict(id=rid,status='completed',output=[{'content':[{'type':'output_text','text':json.dumps({'participants':rows})}]}]))
    def delete(self,rid):self.deleted.append(rid);return {'deleted':True}
    def cancel(self,rid):return {'status':'cancelled'}

def test_no_accounts_database_or_secret_exposure(client):
    assert client.get('/api/config').json()['configured'] is True
    for path in ['/','/app.js','/zip.js','/style.css','/api/config','/api/evidence','/api/guide.csv','/api/example/SPA5_template.csv']:
        r=client.get(path);assert r.status_code==200;assert 'fake-key-for-tests-only' not in r.text;assert 'set-cookie' not in r.headers
    for path in ['/api/jobs','/api/me','/.env','/db/schema.sql']:assert client.get(path).status_code==404
    assert client.post('/api/login',json={},headers=H).status_code==404

def test_no_key_needed_for_preview_and_free_demo_removed(client,monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY')
    assert client.get('/api/config').json()['configured'] is False
    assert client.post('/api/preview',json={'methods':[5]},headers=H).status_code==200
    assert client.post('/api/demo',json={'methods':[1]},headers=H).status_code==404
    assert client.post('/api/prepare',json={'methods':[1],'consent':True},headers=H).status_code==503

def test_guard_and_validation(client):
    assert client.post('/api/prepare',json={}).status_code==403
    assert client.post('/api/preview',json={'methods':[1]},headers={**H,'Origin':'https://another.invalid'}).status_code==403
    assert client.post('/api/preview',json={'methods':[1],'model':'other'},headers=H).status_code==422
    assert client.post('/api/preview',json={'methods':[1],'n':99},headers=H).status_code==422
    assert client.post('/api/prepare',json={'methods':[1]},headers=H).status_code==400
    assert client.post('/api/preview',json={'methods':[6],'examples':False},headers=H).status_code==400
    r=client.post('/api/preview',content=b' '*3000001,headers=H);assert r.status_code==413

@pytest.mark.parametrize('method',range(1,9))
def test_public_generation_and_fixed_values(client,monkeypatch,method):
    fake=FakeProvider();monkeypatch.setattr(jobs,'provider',lambda:fake)
    plan=client.post('/api/prepare',json={'methods':[method],'n':100,'consent':True},headers=H).json()
    run=f'SPA{method}_R0001';ctx=plan['contexts'][run];rows=[]
    for offset in [0]:
        r=client.post('/api/submit',json=dict(ticket=plan['ticket'],run=run,offset=offset,context=ctx),headers=H)
        assert r.status_code==200,r.text
        handle=r.json()['handle'];assert 'fake-key-for-tests-only' not in handle
        result=client.post('/api/poll',json={'handle':handle,'context':ctx},headers=H)
        assert result.status_code==200,result.text
        assert result.json()['status']=='completed';rows.extend(result.json()['records'])
        release=client.post('/api/release',json={'handle':handle},headers=H);assert release.json()['released']
    assert len(fake.created)==1 and len(fake.deleted)==1
    for req in fake.created:assert req['model']=='gpt-5.6-luna' and req['background'] is True and req['store'] is False and req['reasoning']['effort']=='medium' and req['max_output_tokens']==128000
    assert (ctx['pilot'] is not None)==(method in (5,6));assert (ctx['summary'] is not None)==(method==5)
    if ctx['fixed']:
        for row,fixed in zip(rows,ctx['fixed']):
            for f,v in fixed.items():assert row[f]==v
    result=client.post('/api/dataset',json=dict(name=run,records=rows,pilot=ctx['pilot']),headers=H)
    assert result.status_code==200,result.text
    assert len(pd.read_csv(__import__('io').StringIO(result.json()['csv'])))==100
    if method not in (4,7,8):assert result.json()['quality']['repeated_complete_profiles']==99
    assert 'fake-key-for-tests-only' not in result.text

@pytest.mark.parametrize('method',[1,7,8])
def test_thousand_person_plan_and_bounds(client,method):
    p=client.post('/api/prepare',json={'methods':[method],'n':1000,'consent':True},headers=H)
    assert p.status_code==422

def test_signed_handles_reject_tampering_other_response_and_expiry(client,monkeypatch):
    fake=FakeProvider();monkeypatch.setattr(jobs,'provider',lambda:fake)
    plan=client.post('/api/prepare',json={'methods':[8],'consent':True},headers=H).json();ctx=plan['contexts']['SPA8_R0001']
    r=client.post('/api/submit',json=dict(ticket=plan['ticket'],run='SPA8_R0001',offset=0,context=ctx),headers=H).json();handle=r['handle']
    bad=copy.deepcopy(ctx);bad['fixed'][0]['participant_id']=999
    assert client.post('/api/poll',json={'handle':handle,'context':bad},headers=H).status_code==400
    assert client.post('/api/poll',json={'handle':'resp_unrelated','context':ctx},headers=H).status_code==400
    assert client.post('/api/poll',json={'handle':handle+'x','context':ctx},headers=H).status_code==400
    monkeypatch.setattr(jobs.time,'time',lambda:99999999999)
    assert client.post('/api/poll',json={'handle':handle,'context':ctx},headers=H).status_code==400

def test_failed_submit_never_retries(client,monkeypatch):
    f=FakeProvider(fail_submit=True);monkeypatch.setattr(jobs,'provider',lambda:f)
    plan=client.post('/api/prepare',json={'methods':[1],'consent':True},headers=H).json()
    r=client.post('/api/submit',json=dict(ticket=plan['ticket'],run='SPA1_R0001',offset=0,context=plan['contexts']['SPA1_R0001']),headers=H)
    assert r.status_code==503;assert len(f.created)==1
    assert 'may have accepted and charged' in r.text and r.json()['code']=='submission_uncertain';assert 'private provider message' not in r.text

def test_read_failure_retains_handle_without_resubmission(client,monkeypatch):
    class FailReadOnce(FakeProvider):
        def __init__(self):super().__init__();self.reads=0
        def retrieve(self,rid):
            self.reads+=1
            if self.reads==1:raise ConnectionError('temporary')
            return super().retrieve(rid)
    f=FailReadOnce();monkeypatch.setattr(jobs,'provider',lambda:f)
    p=client.post('/api/prepare',json={'methods':[1],'consent':True},headers=H).json();ctx=p['contexts']['SPA1_R0001']
    h=client.post('/api/submit',json=dict(ticket=p['ticket'],run='SPA1_R0001',offset=0,context=ctx),headers=H).json()['handle']
    assert client.post('/api/poll',json={'handle':h,'context':ctx},headers=H).status_code==503
    assert client.post('/api/poll',json={'handle':h,'context':ctx},headers=H).json()['status']=='completed'
    assert len(f.created)==1

def test_no_writes_during_request(client,monkeypatch):
    f=FakeProvider();monkeypatch.setattr(jobs,'provider',lambda:f)
    def reject(*a,**k):raise AssertionError('Application attempted a filesystem write')
    original=builtins.open
    def safe_open(file,mode='r',*a,**k):
        assert not set(mode)&set('wax+'),'Application attempted a file write'
        return original(file,mode,*a,**k)
    with monkeypatch.context() as m:
        m.setattr(builtins,'open',safe_open);m.setattr(Path,'write_text',reject);m.setattr(Path,'write_bytes',reject);m.setattr(Path,'mkdir',reject)
        p=client.post('/api/prepare',json={'methods':[6],'consent':True},headers=H).json();ctx=p['contexts']['SPA6_R0001']
        h=client.post('/api/submit',json=dict(ticket=p['ticket'],run='SPA6_R0001',offset=0,context=ctx),headers=H).json()['handle']
        r=client.post('/api/poll',json={'handle':h,'context':ctx},headers=H);assert r.json()['status']=='completed'
        assert client.post('/api/dataset',json={'name':'SPA6_R0001','records':r.json()['records'],'pilot':ctx['pilot']},headers=H).status_code==200

def test_comparison_uses_browser_rows_not_database(client,reference):
    rows=local_rows(1)
    result=client.post('/api/compare',json={'csv':reference.to_csv(index=False),'datasets':rows},headers=H)
    assert result.status_code==200,result.text
    assert result.json()['metadata']['human_n']==2709 and result.json()['metadata']['datasets']==1
    assert result.json()['csv_exports']['summary']

def test_browser_uses_only_volatile_memory():
    root=Path(__file__).parents[1]
    js=(root/'web/app.js').read_text()
    for text in ['localStorage','sessionStorage','indexedDB','document.cookie','serviceWorker']:assert text not in js
    for path in ['db','spa/web_store.py','spa/store.py','spa/security.py','manage_web.py']:assert not (root/path).exists()
    assert 'psycopg' not in (root/'requirements.txt').read_text()
