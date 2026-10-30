import json,copy
import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient
from app import app,Run
from spa import custom,public_jobs
from spa.recommendations import suggest,PUBLIC_ID

HEAD={'X-SPA-Request':'1'}
@pytest.fixture
def study():
    return dict(title='Fictional test',population='Adults',fictionalExample=True,demographics=[dict(code='group',name='Group',categories={'1':'A','2':'B'})],variables=[dict(code=c,name=c,role='outcome' if c=='outcome' else 'predictor',definition='Fictional test measure',citation='Fictional test; not a validated scale',items=['Item one','Item two'],minimum=1,maximum=5,responseType='integer',anchorLow='Low',anchorHigh='High',aggregation='mean',reverse=[2]) for c in ['a','b','c','outcome']])

def test_scoring_reverse_missing_and_sum(study):
    s=custom.definition(study);f=custom.fake(s,5)
    for v in s['variables']:
        x=f[v['code']+'__i1'];y=f[v['code']+'__i2']
        np.testing.assert_allclose(f[v['code']],(x+6-y)/2)
    f.loc[0,'a__i1']=np.nan;assert pd.isna(custom.scored(f,s).loc[0,'a'])
    s['variables'][0]['aggregation']='sum';assert custom.scored(f,s).loc[1,'a']==f.loc[1,'a__i1']+6-f.loc[1,'a__i2']

def test_all_methods_schema_and_fixed_inputs(study):
    bank={}
    for m in range(1,9):
        req=Run(study=study,methods=[m],examples=True,population='Adults')
        bank.update(public_jobs.prepare(req,{}))
    for run,ctx in bank.items():
        m=int(run[1]);f=custom.demo(ctx,m,100,9)
        assert len(f)==100
        custom.clean_dataset(json.loads(f.to_json(orient='records')),ctx['study'],m)
        if ctx['fixed']:
            fixed=pd.DataFrame(ctx['fixed'])
            for c in fixed:np.testing.assert_allclose(f[c],fixed[c],rtol=0,atol=0,equal_nan=True)
        body,_,ids=public_jobs.batch(ctx,m,0,100)
        assert len(ids)==100 and body['reasoning']['effort']=='medium'
        assert ('precomputed_summary": null' in body['input'])==(m!=5)
        props=body['text']['format']['schema']['properties']['participants']['items']['properties']
        if m==7:assert 'a__i1' not in props and 'outcome__i1' in props
        if m==8:assert 'a__i1' in props and 'group' not in props

def test_identical_reference_zero_errors_and_perfect_agreement(study):
    s=custom.definition(study);f=custom.fake(s,100);f.insert(0,'participant_id',range(1,101))
    summary,pairs,variables=custom.comparison({'M2_R0001':json.loads(f.to_json(orient='records'))},f,s,[2])
    for metric in ['smd','sd_error','wasserstein','correlation_mae']:
        assert np.allclose(summary.loc[summary.metric==metric,'mean'],0,atol=1e-12)
    for metric in ['icc','ccc','pattern_r','sign_agreement']:
        assert np.allclose(summary.loc[summary.metric==metric,'mean'],1,atol=1e-12)
    assert summary.lower.isna().all() and pairs.empty

def test_templates_and_routes(study):
    c=TestClient(app)
    r=c.post('/api/custom-tools',json={'study':study},headers=HEAD);assert r.status_code==200
    assert len(r.json()['guide'])==13
    r=c.post('/api/demo',json=dict(study=study,methods=[5],examples=True),headers=HEAD);assert r.status_code==200,r.text
    rows=r.json()['datasets']['M5_R0001']
    r=c.post('/api/dataset',json=dict(study=study,name='M5_R0001',records=rows),headers=HEAD);assert r.status_code==200,r.text
    bad=copy.deepcopy(rows);bad[0]['a']=9
    assert c.post('/api/dataset',json=dict(study=study,name='M5_R0001',records=bad),headers=HEAD).status_code==400
    for code in ['a','b','c','outcome']:assert code in r.json()['csv']
    assert c.get('/research.js').status_code==200

def test_recommendations_mapping():
    assert PUBLIC_ID[7]==8 and PUBLIC_ID[8]==7
    assert suggest('distributions',['pilot','psychology'])['primary']==5
    assert suggest('strengths',['pilot'])['primary']==6
    assert suggest('patterns',['psychology'])['primary']==7
    assert {5,6,7,8}<=set(suggest('patterns',['pilot','psychology'])['feasible'])
    assert not suggest('outcomes',[])['task_supported']

def test_invalid_definition(study):
    for change in [lambda s:s['variables'][0].update(reverse=[3]),lambda s:s['variables'][0].update(code='participant_id'),lambda s:s['variables'][0].update(maximum=1),lambda s:s['variables'][0].update(items=['[Enter item]'])]:
        s=copy.deepcopy(study);change(s)
        with pytest.raises(ValueError):custom.definition(s)

def test_background_custom_submission_poll_and_unchanged_fixed_values(study,monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setenv('OPENAI_API_KEY','test-only-not-a-real-key')
    s=custom.definition(study);profiles=custom.template(s,'psychology').head(100)
    profiles.loc[0,'a']=2.123456789
    req=Run(study=study,methods=[7],examples=False,consent=True)
    plan=public_jobs.plan(req,{'profiles_M7':profiles});ctx=plan['contexts']['M7_R0001']
    body,fixed,ids=public_jobs.batch(ctx,7,0,100)
    full=custom.fake(s,100);full['participant_id']=ids
    fields=list(body['text']['format']['schema']['properties']['participants']['items']['required'])
    payload={'participants':json.loads(full[fields].to_json(orient='records'))}
    response={'id':'resp_custom_test','status':'completed','output':[{'content':[{'type':'output_text','text':json.dumps(payload)}]}]}
    class Responses:
        calls=0
        def create(self,**kwargs):self.calls+=1;return SimpleNamespace(model_dump=lambda **_:dict(id='resp_custom_test',status='queued'))
        def retrieve(self,_):return SimpleNamespace(model_dump=lambda **_:response)
    client=SimpleNamespace(responses=Responses())
    submitted=public_jobs.submit(plan['ticket'],'M7_R0001',0,ctx,client)
    result=public_jobs.poll(submitted['handle'],ctx,client)
    assert result['status']=='completed' and client.responses.calls==1
    assert result['records'][0]['a']==2.123456789
    assert 'a__i1' not in result['records'][0]
    bad=copy.deepcopy(ctx);bad['study']['title']='Tampered'
    with pytest.raises(ValueError):public_jobs.poll(submitted['handle'],bad,client)


def test_custom_reference_score_only_and_mixed_items(study):
    s=custom.definition(study);f=custom.fake(s,100);f['participant_id']=range(1,101)
    rows=json.loads(f.to_json(orient='records'))
    for reference in [f[['a','b','c','outcome']],f.drop(columns=['a','group'])]:
        summary,_,_=custom.comparison({'M2_R0001':rows},reference,s,[2])
        assert summary.loc[summary.metric=='wasserstein','mean'].iloc[0]==0
    # Two coefficients do not support informative Pearson pattern correspondence.
    s['variables']=[v for v in s['variables'] if v['code']!='c'];rows=[{k:v for k,v in r.items() if not k.startswith('c')} for r in rows]
    summary,_,_=custom.comparison({'M2_R0001':rows},f,s,[2])
    assert summary.loc[summary.metric=='pattern_r','mean'].isna().all()


def test_relationship_requires_declared_predictor_and_outcome(study):
    study['variables']=[v for v in study['variables'] if v['role']=='predictor']
    with pytest.raises(ValueError):public_jobs.prepare(Run(study=study,methods=[2],goal='patterns'),{})


def test_display_mapping_attaches_correct_results():
    from spa.content import readable_results
    df=pd.DataFrame([dict(method=7,mean=.1927),dict(method=8,mean=.6574)])
    result=readable_results(df)
    assert result.iloc[0]['Method'].startswith('SPA8') and result.iloc[0]['Average across datasets']==.1927
    assert result.iloc[1]['Method'].startswith('SPA7') and result.iloc[1]['Average across datasets']==.6574


def test_custom_codebook_tracks_items_scores_and_fixed_demographics(study):
    from spa.codebook import build,csv
    req=Run(study=study,methods=[7],examples=True)
    ctx=public_jobs.prepare(req,{})['M7_R0001'];f=custom.demo(ctx,7,100,1)
    book=build(list(f),7,ctx['study']);lookup={r['column']:r for r in book}
    assert list(f)==[r['column'] for r in book]
    assert lookup['group']['provenance']=='Retained from supplied profiles'
    assert lookup['a']['provenance']=='Retained from supplied profiles'
    assert lookup['outcome__i1']['name']=='outcome item 1'
    assert lookup['outcome']['provenance']=='Calculated locally from generated items'
    assert 'reverse-coded item positions: [2]' in lookup['outcome']['scoring']
    assert pd.read_csv(__import__('io').StringIO(csv(book))).column.tolist()==list(f)


def test_custom_output_requires_demographic_definition(study):
    study['demographics']=[]
    with pytest.raises(ValueError,match='demographics'):custom.definition(study)
