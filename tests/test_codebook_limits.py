import io,json
from types import SimpleNamespace
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app import app,Run
from spa import service,public_jobs,codebook
from spa.study import load_study,selected_fields
from spa.simulation import invent_reference

H={'X-SPA-Request':'1'}

@pytest.mark.parametrize('settings',[dict(n=200),dict(n=1000),dict(repetitions=2),dict(methods=[1,2])])
def test_public_limit_before_any_provider_call(settings,monkeypatch):
    def prohibited():raise AssertionError('A disallowed run reached the provider')
    monkeypatch.setattr(public_jobs,'provider',prohibited)
    c=TestClient(app)
    for path in ['/api/preview','/api/demo','/api/prepare']:
        r=c.post(path,json=dict(methods=[2],consent=True,**{k:v for k,v in settings.items() if k!='methods'}) if 'methods' not in settings else dict(methods=settings['methods'],consent=True),headers=H)
        assert r.status_code==422


def test_original_columns_have_complete_codebook():
    s=load_study();columns=['participant_id']+selected_fields(s)
    book=codebook.build(columns,7)
    assert [r['column'] for r in book]==columns
    for r in book:assert all(r[k] for k in ['name','definition','role','allowed_values','scoring','missing_values','source','provenance'])
    lookup={r['column']:r for r in book}
    assert 'anxiety' in lookup['B1PANXIE']['definition']
    assert 'worth' in lookup['B1SESTEE']['definition']
    assert 'everyday' in lookup['B1SDAYDI']['definition']
    assert 'family demands' in lookup['B1SNEGFW']['definition']
    assert lookup['B1SESTEE']['provenance']=='Retained from supplied profiles'
    assert lookup['life_satisfaction_MIDUS3']['provenance']=='Generated'
    assert codebook.build(['B1PRSEX'],4)[0]['provenance'].startswith('Constructed')


def test_dataset_response_includes_codebook_and_requested_fields():
    c=TestClient(app)
    demo=c.post('/api/demo',json=dict(methods=[2]),headers=H).json()
    rows=demo['datasets']['M2_R0001']
    r=c.post('/api/dataset',json=dict(name='M2_R0001',records=rows),headers=H)
    assert r.status_code==200
    f=pd.read_csv(io.StringIO(r.json()['csv']));book=pd.read_csv(io.StringIO(r.json()['codebook_csv']))
    assert list(f)==book.column.tolist()
    s=load_study()
    assert set(s['demographic_covariates'])<=set(f) and set(s['psychological_predictors'])<=set(f)


def test_contact_and_estimate_have_safe_defaults_and_optional_email(monkeypatch):
    monkeypatch.delenv('SPA_CONTACT_EMAIL',raising=False)
    assert service.contact()['email'] is None
    assert 'person who shared' in service.contact()['text']
    monkeypatch.setenv('SPA_CONTACT_EMAIL','team@example.org')
    monkeypatch.setenv('SPA_ESTIMATED_MINUTES','7–25')
    info=service.service_info()
    assert info['contact']['email']=='team@example.org' and info['estimated_minutes']=='7–25'
    assert 'provisional' in info['estimate_note'].lower()
    monkeypatch.setenv('SPA_CONTACT_EMAIL','<script>alert(1)</script>')
    assert service.contact()['email'] is None
    monkeypatch.setenv('SPA_ESTIMATED_MINUTES','untrusted text')
    assert service.estimate()=='5–20'


def test_budget_error_gives_contact_without_exposing_provider_details(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','fake-test-key')
    monkeypatch.setenv('SPA_CONTACT_EMAIL','team@example.org')
    class Provider:
        responses=None
        def __init__(self):self.responses=self;self.calls=0
        def create(self,**kwargs):
            self.calls+=1
            error=RuntimeError('Private provider error');error.status_code=429;raise error
    client=Provider();req=Run(methods=[2]);p=public_jobs.plan(req,{})
    with pytest.raises(RuntimeError) as e:public_jobs.submit(p['ticket'],'M2_R0001',0,p['contexts']['M2_R0001'],client)
    assert 'team@example.org' in str(e.value) and 'Private provider' not in str(e.value) and client.calls==1


def test_old_larger_signed_plans_cannot_generate_new_batches(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','fake-test-key')
    ctx=public_jobs.prepare(Run(methods=[2]),{})['M2_R0001']
    ticket=public_jobs.issue(dict(kind='plan',runs={'M2_R0001':public_jobs.digest(ctx)},settings=dict(methods=[2],n=200,repetitions=1)))
    with pytest.raises(ValueError):public_jobs.submit(ticket,'M2_R0001',0,ctx)
