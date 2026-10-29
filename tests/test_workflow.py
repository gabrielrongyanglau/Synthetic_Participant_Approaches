import numpy as np
import pandas as pd
import pytest
from spa.workflow import (compatible_methods,prepare_context,context_bank,input_digest,quota_template,
                           illustrative_generation,profiles_from_proportions,PURPOSES,purpose_guidance)
from spa.study import predictors,selected_fields

@pytest.mark.parametrize('information,methods',[
 ('definitions',[1,2]),('population',[1,2,3]),('proportions',[4]),('pilot',[5,6]),
 ('demographics',[8]),('psychology',[7,8])])
def test_compatibility(information,methods):assert compatible_methods(information)==methods

@pytest.mark.parametrize('method',range(1,9))
def test_own_inputs_need_no_benchmark(method,study,reference):
    assets={'proportions':quota_template(reference,study),'pilot_M5':reference.iloc[:75],
      'pilot_M6':reference.iloc[75:150],'profiles_M7':reference[predictors(study)].iloc[:100],
      'profiles_M8':reference[study['demographic_covariates']].iloc[:100]}
    context=prepare_context(study,method,100,assets=assets,population='Middle-aged and older adults.')
    assert context['provenance']['reference_required'] is False
    assert (context['summary'] is not None)==(method==5)
    assert (context['pilot'] is not None)==(method in (5,6))
    if method>=7:assert len(context['fixed'])==100
    frame=illustrative_generation(study,method,100,3,1,context)
    assert len(frame)==100
    if context['fixed']:
        for i,row in enumerate(context['fixed']):
            for key,value in row.items():
                assert (pd.isna(frame.iloc[i][key]) and value is None) or frame.iloc[i][key]==value

def test_insufficient_inputs_explained(study):
    for method in (4,5,6,7,8):
        with pytest.raises(ValueError):prepare_context(study,method,100,assets={})
    with pytest.raises(ValueError):prepare_context(study,3,100)

def test_quota_marginals_and_errors(study,reference):
    table=quota_template(reference,study);f,audit=profiles_from_proportions(table,study,1000,np.random.default_rng(1))
    assert len(f)==1000 and set(f)==set(study['demographic_covariates'])
    for field,info in audit.items():assert sum(info['allocated_counts'])==1000
    field=study['demographic_covariates'][1]
    sub=table[table.field==field]
    for i,(_,r) in enumerate(sub.iterrows()):
        assert f[field].eq(float(r.category)).sum()==audit[field]['allocated_counts'][i]
    invalid=table.copy();invalid.loc[0,'proportion']+=.1
    with pytest.raises(ValueError):profiles_from_proportions(invalid,study,100,np.random.default_rng(1))
    invalid=pd.concat([table,table.iloc[[6]]],ignore_index=True)
    with pytest.raises(ValueError):profiles_from_proportions(invalid,study,100,np.random.default_rng(1))

def test_profile_pool_and_pilot_drawing(study,reference):
    assets={'pilot_M5':reference.iloc[:100],'pilot_M6':reference.iloc[:100]}
    bank=context_bank(study,[5,6],100,2,7,assets)
    assert bank['M5_R0001']['pilot']!=bank['M5_R0002']['pilot']
    assert bank['M5_R0001']['pilot']!=bank['M6_R0001']['pilot']
    assert input_digest(bank)==input_digest(bank)
    assets={'profiles_M8':reference[study['demographic_covariates']].iloc[:100]}
    a=prepare_context(study,8,100,assets=assets)
    for f in study['demographic_covariates']:assert a['fixed'][0][f]==reference.iloc[0][f]

def test_purpose_is_not_a_ranking():
    assert 'hypothetical' not in purpose_guidance('workflow',[1]).lower()
    assert 'overstated' in purpose_guidance('relationships',[5,6])
    assert 'individual' in purpose_guidance('outcomes',[7])

def test_optional_validation_uses_only_required_scores(study,reference):
    from spa.workflow import evaluation_reference
    from spa.analysis import analyse
    ref=evaluation_reference(reference[study['psychological_predictors']+list(study['outcomes'])],study)
    context=prepare_context(study,1,100)
    frame=illustrative_generation(study,1,100,1,1,context)
    result=analyse([(1,1,lambda:frame)],ref,study)
    assert result['metadata']['human_n']==2709
    assert len(result['summary'])==12
    assert result['comparisons'].empty

