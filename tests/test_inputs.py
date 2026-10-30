import io
from zipfile import ZipFile
import numpy as np
import pandas as pd
import pytest
from spa.study import clean_frame,selected_fields,json_records
from spa.simulation import local_demo,prepare_inputs,quality_flags
from spa.generation import output_schema,parse_records
from spa.labels import field_map
from spa.prompts import build_prompt
from spa.io import archive,read_csv

@pytest.mark.parametrize('n',range(100,1001,100))
def test_all_sizes_and_methods(n,study,reference):
    for m in range(1,9):
        f,ctx=local_demo(reference,study,m,n,30)
        assert len(f)==n and f.participant_id.tolist()==list(range(1,n+1))
        if ctx['fixed']:
            for i,row in enumerate(ctx['fixed']):
                for field,value in row.items():
                    assert (pd.isna(f.iloc[i][field]) and value is None) or f.iloc[i][field]==value

def test_independent_pilots_and_summary(study,reference):
    a=prepare_inputs(reference,study,5,100,2);b=prepare_inputs(reference,study,6,100,2)
    assert a['pilot']!=b['pilot'];assert a['summary'];assert b['summary'] is None
    assert len(a['summary']['pairwise_relationships'])==780
    assert a['pilot']!=prepare_inputs(reference,study,5,100,2,2)['pilot']

def test_fixed_null_and_precision(study,reference):
    ctx=prepare_inputs(reference,study,8,100,3);ids=list(range(1,101));mapping=field_map(study)
    ctx['fixed'][0][study['psychological_predictors'][0]]=None
    rows=[dict(participant_id=i,life_satisfaction_wave1=6.123456,life_satisfaction_wave2=7.543219) for i in ids]
    parsed=parse_records({'participants':rows},study,ids,ctx['fixed'])
    assert pd.isna(parsed.iloc[0][study['psychological_predictors'][0]])
    assert parsed.life_satisfaction_MIDUS2.iloc[0]==6.1235
    props=output_schema(study,ids,ctx['fixed'])['properties']['participants']['items']['properties']
    assert len(props)==3
    system,user=build_prompt(study,8,ids,ctx['fixed'],generated_only=True)
    assert 'Return only the generated fields' in user and 'participant_id' in user

def test_duplicates_are_flags(study,reference):
    f,_=local_demo(reference,study,6);f.iloc[1,1:]=f.iloc[0,1:].values
    flags=quality_flags(f,study,json_records(f.iloc[:1]))
    assert flags['repeated_complete_profiles']>=1 and flags['pilot_record_matches']>=2
    clean_frame(f,study,expected_n=100)

def test_archive_safety_and_windows_paths():
    a=io.BytesIO()
    with ZipFile(a,'w') as z:z.writestr('../bad','x')
    with pytest.raises(ValueError):archive(a.getvalue())
    a=io.BytesIO()
    with ZipFile(a,'w') as z:z.writestr('data\\reference.csv','x')
    z,ms=archive(a.getvalue());assert 'data/reference.csv' in ms;z.close()
    with pytest.raises(ValueError):read_csv(b'x,x\n1,2\n')
