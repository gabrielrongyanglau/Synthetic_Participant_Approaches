"""MIDUS source codes never leave the server, and AI generation runs as parallel batches."""
import io,json
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app import app
from spa import public_jobs as jobs
from spa.public import PUBLIC,CODE,outbound,inbound,contains_code,inbound_csv
from spa.study import load_study,selected_fields
from conftest import local_rows
from test_public import FakeProvider,H

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','fake-key-for-tests-only')
    return TestClient(app)

def test_every_study_variable_has_a_unique_public_name():
    s=load_study()
    assert set(s['variables'])|{s['id_column'],s['family_column']}<=set(PUBLIC)
    assert len(set(PUBLIC.values()))==len(PUBLIC) and not any(contains_code(v) for v in PUBLIC.values())

@pytest.mark.parametrize('method',range(1,9))
def test_contexts_round_trip_exactly(method):
    from app import Run
    ctx=jobs.prepare(Run(methods=[method]),{})[f'SPA{method}_R0001']
    public=outbound(ctx)
    assert not contains_code(json.dumps(public))
    assert inbound(public)==ctx and jobs.digest(inbound(public))==jobs.digest(ctx)

def test_no_source_codes_in_any_page_or_download(client):
    responses=[client.get(p) for p in ['/','/app.js','/research.js','/study-charts.js','/supporting.js','/api/config','/api/evidence','/api/guide.csv']]
    responses+=[client.get(f'/api/template/{m}') for m in (4,5,6,7,8)]
    responses+=[client.get(f'/api/example/{n}') for n in [f'SPA{m}_template.csv' for m in (4,5,6,7,8)]]
    for m in range(1,9):
        body={'methods':[m],'consent':True}
        responses+=[client.post('/api/preview',json=body,headers=H),client.post('/api/check-inputs',json=body,headers=H),client.post('/api/prepare',json=body,headers=H)]
    rows=local_rows(5)['SPA5_R0001']
    responses.append(client.post('/api/dataset',json={'name':'SPA5_R0001','records':rows},headers=H))
    from spa.simulation import invent_reference
    responses.append(client.post('/api/compare',json={'csv':invent_reference(load_study()).to_csv(index=False),'datasets':local_rows(1)},headers=H))
    for r in responses:
        assert r.status_code==200,(r.request.url,r.text[:200])
        assert not contains_code(r.text),(r.request.url,next(m for m in PUBLIC if m in r.text))

def test_dataset_csv_and_codebook_use_public_names(client):
    r=client.post('/api/dataset',json={'name':'SPA2_R0001','records':local_rows(2)['SPA2_R0001']},headers=H).json()
    frame=pd.read_csv(io.StringIO(r['csv']));book=pd.read_csv(io.StringIO(r['codebook_csv'].lstrip('﻿')))
    s=load_study()
    assert list(frame)==['participant_id']+[PUBLIC.get(f,f) for f in selected_fields(s)]
    assert book.column.tolist()==list(frame)

@pytest.mark.parametrize('method',[4,5,6,7,8])
def test_uploads_with_public_names_are_accepted(client,method):
    example=f'SPA{method}_template.csv'
    key={4:'proportions_SPA4',5:'pilot_SPA5',6:'pilot_SPA6',7:'profiles_SPA7',8:'profiles_SPA8'}[method]
    csv=client.get('/api/example/'+example).text
    assert not contains_code(csv)
    r=client.post('/api/check-inputs',json={'methods':[method],'examples':False,'assets':{key:csv}},headers=H)
    assert r.status_code==200,r.text

def test_inbound_csv_only_changes_exact_public_names():
    text='age,sex,notes\n50,1,"age and sex"\n'
    assert inbound_csv(text).splitlines()[0]=='B1PRAGE_2019,B1PRSEX,notes'
    assert '"age and sex"' in inbound_csv(text) or 'age and sex' in inbound_csv(text)

@pytest.mark.parallel
@pytest.mark.parametrize('method',[2,5,7])
def test_parallel_batches_assemble_one_dataset(client,monkeypatch,method):
    fake=FakeProvider();monkeypatch.setattr(jobs,'provider',lambda:fake)
    plan=client.post('/api/prepare',json={'methods':[method],'consent':True},headers=H).json()
    size=plan['settings']['batch_size'];assert size==25
    run=f'SPA{method}_R0001';ctx=plan['contexts'][run]
    handles=[client.post('/api/submit',json=dict(ticket=plan['ticket'],run=run,offset=o,context=ctx),headers=H).json()['handle'] for o in range(0,100,size)]
    assert len(fake.created)==4
    for body in fake.created:assert len(body['text']['format']['schema']['properties']['participants']['items']['properties']['participant_id']['enum'])==25
    rows=[]
    for h in handles:
        r=client.post('/api/poll',json={'handle':h,'context':ctx},headers=H).json();assert r['status']=='completed';rows+=r['records']
    assert [r['participant_id'] for r in rows]==list(range(1,101))
    if ctx['fixed']:
        for row,fixed in zip(rows,ctx['fixed']):
            for f,v in fixed.items():assert row[f]==v
    result=client.post('/api/dataset',json=dict(name=run,records=rows,pilot=ctx['pilot']),headers=H)
    assert result.status_code==200 and not contains_code(result.text)
    assert client.post('/api/submit',json=dict(ticket=plan['ticket'],run=run,offset=10,context=ctx),headers=H).status_code==400

@pytest.mark.parallel
def test_batch_size_setting(monkeypatch):
    for raw,expected in [('25',25),('50',50),('100',100),('7',25),('',25),('abc',25)]:
        monkeypatch.setenv('SPA_BATCH_SIZE',raw);assert jobs.batch_size()==expected

@pytest.mark.parametrize('method',[4,7,8])
def test_participant_id_is_first_for_fixed_profile_datasets(client,method):
    r=client.post('/api/dataset',json={'name':f'SPA{method}_R0001','records':local_rows(method)[f'SPA{method}_R0001']},headers=H).json()
    assert r['csv'].split('\n',1)[0].split(',')[0]=='participant_id'

M_LABEL=__import__('re').compile(r'(?<![A-Za-z0-9])M[1-8](?![0-9A-Za-z])')

def test_no_m_style_approach_labels_anywhere(client):
    responses=[client.get(p) for p in ['/','/app.js','/research.js','/study-charts.js','/supporting.js','/api/config','/api/evidence','/api/guide.csv']]
    responses+=[client.get(f'/api/template/{m}') for m in (4,5,6,7,8)]+[client.get(f'/api/example/SPA{m}_template.csv') for m in (4,5,6,7,8)]
    for m in range(1,9):
        body={'methods':[m],'consent':True}
        responses+=[client.post(p,json=body,headers=H) for p in ('/api/preview','/api/check-inputs','/api/prepare')]
        responses.append(client.post('/api/check-inputs',json={'methods':[m],'examples':False},headers=H))
    responses.append(client.post('/api/dataset',json={'name':'SPA8_R0001','records':local_rows(8)['SPA8_R0001']},headers=H))
    for r in responses:
        hit=M_LABEL.search(r.text)
        assert not hit,(r.request.url,r.text[max(0,hit.start()-60):hit.end()+60])

@pytest.mark.parametrize('method,rows',[(5,50),(6,50),(7,100),(8,100)])
def test_templates_have_one_row_per_participant(client,method,rows):
    s=load_study()
    frame=pd.read_csv(io.StringIO(client.get(f'/api/example/SPA{method}_template.csv').text))
    blank=pd.read_csv(io.StringIO(client.get(f'/api/template/{method}').text))
    assert len(frame)==rows and list(frame)==list(blank) and len(blank)==0
    expected={5:selected_fields(s),6:selected_fields(s),7:s['demographic_covariates']}.get(method)
    if expected:assert list(frame)==[PUBLIC.get(f,f) for f in expected]
    else:assert set(PUBLIC[c] for c in s['demographic_covariates']+s['psychological_predictors'])==set(frame)

def test_spa8_uses_psychology_and_spa7_demographics_only():
    from app import Run
    c8=jobs.prepare(Run(methods=[8]),{})['SPA8_R0001'];c7=jobs.prepare(Run(methods=[7]),{})['SPA7_R0001']
    s=load_study()
    assert set(s['psychological_predictors'])<=set(c8['fixed'][0]) and not set(s['psychological_predictors'])&set(c7['fixed'][0])
    b8,_,_=jobs.batch(c8,8,0,100,100);b7,_,_=jobs.batch(c7,7,0,100,100)
    p8=b8['text']['format']['schema']['properties']['participants']['items']['properties'];p7=b7['text']['format']['schema']['properties']['participants']['items']['properties']
    assert set(p8)=={'participant_id','life_satisfaction_wave1','life_satisfaction_wave2'}
    assert 'psychological_01_wave1' in p7 and 'demographic_01_wave1' not in p7
    import json as _j
    bank=_j.load(open('prompts/methods.json'))['prompts']
    assert next(p for p in bank if p['method']==7)['user'] in b8['input'] or 'Predictor' in next(p for p in bank if p['method']==7)['name']

@pytest.mark.parametrize('method,key',[(4,'proportions_SPA4'),(5,'pilot_SPA5'),(6,'pilot_SPA6'),(7,'profiles_SPA7'),(8,'profiles_SPA8')])
def test_uploaded_inputs_survive_browser_number_serialisation(client,monkeypatch,method,key):
    """A browser turns 3.0 into 3; submission must still verify against the signed plan."""
    fake=FakeProvider();monkeypatch.setattr(jobs,'provider',lambda:fake)
    csv=client.get(f'/api/example/SPA{method}_template.csv').text
    plan=client.post('/api/prepare',json={'methods':[method],'consent':True,'examples':False,'assets':{key:csv}},headers=H).json()
    run=f'SPA{method}_R0001'
    def as_browser(v):
        if isinstance(v,dict):return {k:as_browser(x) for k,x in v.items()}
        if isinstance(v,list):return [as_browser(x) for x in v]
        return int(v) if isinstance(v,float) and v.is_integer() else v
    ctx=as_browser(plan['contexts'][run])
    r=client.post('/api/submit',json=dict(ticket=plan['ticket'],run=run,offset=0,context=ctx),headers=H)
    assert r.status_code==200,r.text
    assert client.post('/api/poll',json={'handle':r.json()['handle'],'context':ctx},headers=H).json()['status']=='completed'

def test_fictional_midus_reference_supports_the_comparison_step(client):
    ref=client.get('/api/example/reference.csv')
    assert ref.status_code==200 and not contains_code(ref.text) and len(ref.content)<2_200_000
    from conftest import local_rows
    r=client.post('/api/compare',json={'csv':ref.text,'datasets':local_rows(5)},headers=H)
    assert r.status_code==200,r.text
