"""MIDUS demonstration: choosing demographics and psychological predictors on the Questionnaire step."""
import json
import pytest
from fastapi.testclient import TestClient
from app import app,Run
from spa import public_jobs as jobs
from spa.public import PUBLIC,outbound,inbound,contains_code
from spa.selection import choices,parse,subset
from spa.study import load_study,selected_fields
from test_public import H

DEMOS=['age','sex']
PREDS=['optimism_overall','self_esteem','neuroticism','family_support']

@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','fake-key-for-tests-only')
    return TestClient(app)

def test_choices_use_public_names_in_study_order():
    c=choices(load_study())
    assert len(c['demographics'])==6 and len(c['predictors'])==38
    assert not contains_code(json.dumps(c)) and c['predictors'][0]['label'].startswith('Optimism')

def test_full_selection_is_the_evaluated_study():
    s=load_study();c=choices(s)
    full={'demographics':[x['name'] for x in c['demographics']],'predictors':[x['name'] for x in c['predictors']]}
    assert parse(full,s) is None and parse(None,s) is None
    ctx=jobs.prepare(Run(methods=[2],midus_fields=full),{})['SPA2_R0001']
    assert 'fields' not in ctx

def test_selection_errors():
    s=load_study()
    for bad in [{'predictors':[]},{'predictors':['not_a_variable']},{'demographics':['age','age'],'predictors':['pessimism']},{'other':[]},'all']:
        with pytest.raises(ValueError):parse(bad,s)

@pytest.mark.parametrize('method',range(1,9))
def test_subset_runs_for_every_approach(method,client):
    fields={'demographics':DEMOS,'predictors':PREDS}
    r=client.post('/api/check-inputs',json={'methods':[method],'consent':True,'midus_fields':fields},headers=H)
    assert r.status_code==200,r.text
    expected=len(PREDS)+len(DEMOS)+2-{4:len(DEMOS),7:len(DEMOS),8:len(DEMOS)+len(PREDS)}.get(method,0)
    assert r.json()['generated_fields']==expected
    preview=client.post('/api/preview',json={'methods':[method],'consent':True,'midus_fields':fields},headers=H).json()
    assert preview['user'].count('psychological_05_wave1')==0 and 'psychological_04_wave1' in preview['user']

def test_signed_context_keeps_the_selection_and_round_trips():
    ctx=jobs.prepare(Run(methods=[5],midus_fields={'demographics':DEMOS,'predictors':PREDS}),{})['SPA5_R0001']
    assert ctx['fields']['predictors']==['B1SORIEN','B1SESTEE','B1SNEURO','B1SKINPO']
    assert set(ctx['pilot'][0])==set(selected_fields(subset(load_study(),ctx['fields'])))
    public=outbound(ctx);assert not contains_code(json.dumps(public)) and jobs.digest(inbound(public))==jobs.digest(ctx)
    body,_,_=jobs.batch(ctx,5,0,100)
    props=body['text']['format']['schema']['properties']['participants']['items']['properties']
    assert len(props)==1+len(PREDS)+len(DEMOS)+2

def test_fixed_demographics_need_at_least_one(client):
    for m in (4,7,8):
        r=client.post('/api/check-inputs',json={'methods':[m],'consent':True,'midus_fields':{'demographics':[],'predictors':PREDS}},headers=H)
        assert r.status_code==400 and 'demographic' in r.json()['detail']
    r=client.post('/api/check-inputs',json={'methods':[2],'consent':True,'midus_fields':{'demographics':[],'predictors':PREDS}},headers=H)
    assert r.status_code==200

def test_dataset_with_selection(client):
    from spa.workflow import illustrative_generation
    from spa.study import json_records
    fields={'demographics':DEMOS,'predictors':PREDS}
    ctx=jobs.prepare(Run(methods=[2],midus_fields=fields),{})['SPA2_R0001']
    full=load_study()
    frame=illustrative_generation(full,2,100,1,1,{'pilot':None,'fixed':None})
    cols=['participant_id']+selected_fields(subset(full,ctx['fields']))
    rows=outbound(json_records(frame[cols]))
    r=client.post('/api/dataset',json={'name':'SPA2_R0001','records':rows,'midus_fields':fields},headers=H)
    assert r.status_code==200,r.text
    header=r.json()['csv'].splitlines()[0].split(',')
    assert header==['participant_id']+[PUBLIC.get(c,c) for c in cols[1:]]
    assert len(r.json()['codebook'])==len(cols)
