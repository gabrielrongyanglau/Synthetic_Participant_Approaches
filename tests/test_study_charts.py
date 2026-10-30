"""Charts expose original verified aggregates, not session results."""
import json,shutil,subprocess
import pytest
from fastapi.testclient import TestClient
from app import app
from spa.study import PROJECT_ROOT,json_records
from spa.io import read_csv
from spa.public import outbound
from spa.numbering import original_frame

@pytest.fixture(scope='module')
def chart_data():
    with TestClient(app) as client:
        response=client.get('/api/evidence');assert response.status_code==200
        return response.json()['charts']

def test_full_precision_chart_sources(chart_data):
    for key in ['summary','variables','human']:
        assert chart_data[key]==outbound(json_records(original_frame(read_csv(PROJECT_ROOT/'data/original_study'/f'{key}.csv'))))
    assert len(chart_data['summary'])==96 and len(chart_data['variables'])==304 and len(chart_data['human'])==38
    assert chart_data['reference_n']==2709 and chart_data['planned_repetitions']==1000
    assert len(chart_data['variable_labels'])==38

def test_story_is_supported_at_both_waves(chart_data):
    rows=chart_data['summary'];generated={1,2,3,4,5,6,7}
    for metric in ['wasserstein','smd','sd_error']:
        values=[r for r in rows if r['metric']==metric and r['wave']==0 and r['method'] in generated]
        assert min(values,key=lambda r:r['mean'])['method']==5
    for wave in [2,3]:
        values=[r for r in rows if r['metric']=='correlation_mae' and r['wave']==wave]
        assert min(values,key=lambda r:r['mean'])['method']==8
        assert min((r for r in values if r['method'] in generated),key=lambda r:r['mean'])['method']==6
        pattern=[r for r in rows if r['metric']=='pattern_r' and r['wave']==wave]
        assert all(.93<r['mean']<.98 for r in pattern)

@pytest.mark.skipif(not shutil.which('node'),reason='Optional Node.js check of browser chart selection')
def test_chart_selectors_and_scale_use_source_values(chart_data):
    script=(PROJECT_ROOT/'web/study-charts.js').read_text()
    script+='\nconst d='+json.dumps(chart_data)+';const outputs=[];'
    script+="for(const metric of ['smd','sd_error','wasserstein'])outputs.push({metric,wave:0,rows:StudyCharts.dataFor(d,metric,0),scale:StudyCharts.intervalSpec(StudyCharts.dataFor(d,metric,0))});"
    script+="for(const wave of [2,3])for(const metric of ['correlation_mae','icc','ccc','pattern_r'])outputs.push({metric,wave,rows:StudyCharts.dataFor(d,metric,wave),scale:StudyCharts.intervalSpec(StudyCharts.dataFor(d,metric,wave),metric!=='correlation_mae')});"
    script+="const scatter=[];for(const wave of [2,3])for(let m=1;m<=8;m++)scatter.push({m,wave,rows:StudyCharts.scatterFor(d,m,wave)});process.stdout.write(JSON.stringify({outputs,scatter}));"
    result=json.loads(subprocess.run(['node'],input=script.encode(),capture_output=True,check=True).stdout)
    for out in result['outputs']:
        expected=sorted((r for r in chart_data['summary'] if r['metric']==out['metric'] and r['wave']==out['wave']),key=lambda r:r['method'])
        assert out['rows']==expected and out['scale']['min']==0
        assert out['scale']['max']>=max(r['upper'] for r in expected)
        if out['metric'] in ['icc','ccc','pattern_r']:assert out['scale']['max']==1
    human={r['code']:r for r in chart_data['human']}
    for out in result['scatter']:
        assert len(out['rows'])==37 and all(r['code']!='anxiety_symptoms' for r in out['rows'])
        source={r['code']:r for r in chart_data['variables'] if r['method']==out['m']}
        for r in out['rows']:
            assert r['human']==human[r['code']][f'midus{out["wave"]}_r']
            assert r['generated']==source[r['code']][f'midus{out["wave"]}_mean_r']
            assert r['n']==source[r['code']][f'midus{out["wave"]}_runs']
            assert r['label']==chart_data['variable_labels'][r['code']]

def test_charts_are_public_and_no_key_needed(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    with TestClient(app) as client:
        assert client.get('/study-charts.js').status_code==200
        assert client.get('/api/evidence').status_code==200
        page=client.get('/').text
        for field in ['studyWave','studyDistribution','studyScatterMethod','distributionChart','relationshipChart','agreementChart','correlationChart']:assert f'id="{field}"' in page
        assert '95% confidence interval' in page and 'actual psychological' in page


def test_spa_numbering_matches_revised_proposal(chart_data):
    """Proposal Tables 3-5: SPA7 = demographic-only profiles, SPA8 = demographic and psychological profiles."""
    get=lambda metric,wave,m:next(r['mean'] for r in chart_data['summary'] if r['metric']==metric and r['wave']==wave and r['method']==m)
    assert round(get('smd',0,8),4)==.0802 and round(get('wasserstein',0,8),4)==.1174
    assert round(get('correlation_mae',2,8),4)==.1927 and round(get('correlation_mae',3,8),4)==.2445
    assert round(get('smd',0,7),4)==.5822 and round(get('wasserstein',0,7),4)==.6648
    assert round(get('correlation_mae',2,7),4)==.6574 and round(get('correlation_mae',3,7),4)==.7114
    assert chart_data['method_names']['7']=='Demographic-only profiles' and chart_data['method_names']['8']=='Demographic and psychological profiles'
