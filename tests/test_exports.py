import json
import numpy as np
import pandas as pd
from spa.analysis import load_bundle
from spa.export import bundle_zip,provenance
from spa.study import PROJECT_ROOT

def test_bundle_roundtrip(study):
    b=load_bundle(PROJECT_ROOT/'data/examples/analysis');raw=bundle_zip(b);again=load_bundle(raw)
    pd.testing.assert_frame_equal(b['summary'],again['summary'])
    rec=provenance(b,study);json.dumps(rec,allow_nan=False)
    assert 'original_prompt_templates' in rec
    assert 'OPENAI_API_KEY' not in json.dumps(rec)

def test_original_summary():
    b=load_bundle(PROJECT_ROOT/'data/original_study')
    assert len(b['summary'])==96 and len(b['comparisons'])==336
    assert len(b['variables'])==304 and len(b['human'])==38
    assert b['metadata']['human_n']==2709 and b['metadata']['datasets']==8000
    assert b['comparisons'].significant.sum()==265
    row=b['summary'].query('method==5 and metric=="wasserstein"').iloc[0]
    assert round(row['mean'],4)==.3213

def test_r_output_converter(tmp_path):
    from import_r import convert
    from spa.metrics import DIST,REL
    rng=np.random.default_rng(1);b=load_bundle(PROJECT_ROOT/'data/original_study')
    runs=pd.DataFrame({'method':np.repeat(np.arange(1,9),1000),'replication':np.tile(np.arange(1,1001),8)})
    for name in DIST+[f'midus{k}_{m}' for k in (2,3) for m in REL]:runs[name]=rng.normal(size=8000)
    runs.to_csv(tmp_path/'per_run_metrics.csv',index=False)
    b['variables'].to_csv(tmp_path/'by_variable_results.csv',index=False)
    b['human'].rename(columns={'n':'human_n','mean':'human_mean','sd':'human_sd','midus2_r':'human_r_midus2','midus3_r':'human_r_midus3'}).to_csv(tmp_path/'human_reference_statistics.csv',index=False)
    converted=convert(tmp_path,tmp_path/'bundle')
    assert len(converted['summary'])==96 and len(converted['comparisons'])==336

def test_generation_export_needs_no_benchmark(study):
    from spa.workflow import context_bank,illustrative_generation,generated_metadata
    from spa.export import dataset_zip
    from zipfile import ZipFile
    import io
    bank=context_bank(study,[1],100,1,1)
    frames={(1,1):illustrative_generation(study,1,100,1,1,bank['M1_R0001'])}
    record=generated_metadata(frames,bank,study,{'n':100},'Local demonstration','Try the workflow')
    data=dataset_zip(frames,provenance({'metadata':record},study))
    with ZipFile(io.BytesIO(data)) as z:
        assert set(z.namelist())=={'M1_R0001.csv','run_record.json'}
        rec=json.loads(z.read('run_record.json'))
        assert rec['validation_status'].startswith('Not evaluated')
        assert rec['schema_version']=='1.1'
