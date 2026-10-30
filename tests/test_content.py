"""Display changes must preserve the scientific data and exported values."""
import json
from pathlib import Path
import pandas as pd
from spa.content import INTRO,METHODS,METRICS,variable_guide,readable_records,readable_results
from spa.study import PROJECT_ROOT,selected_fields
from spa.analysis import load_bundle

def test_readable_record_display_preserves_raw_export(study):
    raw=pd.read_csv(PROJECT_ROOT/'data/examples/M1_R0001.csv',float_precision='round_trip')
    before=raw.copy(deep=True);display=readable_records(raw,study)
    pd.testing.assert_frame_equal(raw,before)
    assert len(display)==100 and display.shape==raw.shape
    assert not display.columns.duplicated().any()
    for f in study['psychological_predictors']:
        from spa.study import label
        pd.testing.assert_series_equal(display[label(study,f)],raw[f],check_names=False)

def test_result_display_keeps_values():
    bundle=load_bundle(PROJECT_ROOT/'data/original_study');raw=bundle['summary'];copy=raw.copy(deep=True)
    display=readable_results(raw)
    pd.testing.assert_frame_equal(raw,copy)
    assert display['Average across datasets'].equals(raw['mean'])
    assert display['Lower 95% confidence limit'].equals(raw['lower'])
    assert display['Upper 95% confidence limit'].equals(raw['upper'])

def test_guides_and_filled_templates_match_study(study):
    guide=variable_guide(study)
    assert set(guide['CSV column name'])==set(selected_fields(study))
    for m in (5,6):
        frame=pd.read_csv(PROJECT_ROOT/f'data/examples/M{m}_pilot_example.csv')
        assert len(frame)==50 and set(frame)==set(selected_fields(study))
    for m in (7,8):
        frame=pd.read_csv(PROJECT_ROOT/f'data/examples/M{m}_profiles_example.csv')
        assert len(frame)==100 and not set(study['outcomes'])&set(frame)

def test_method_and_measure_explanations():
    assert 'synthetic participant approach (SPA)' in INTRO
    assert set(METHODS)==set(range(1,9))
    assert all(all(item.get(k) for k in ('input','procedure','output')) for item in METHODS.values())
    assert 'toolkit' in METHODS[5]['procedure'] and 'itself' in METHODS[6]['procedure']
    assert len(METRICS)==8 and all(len(item)==3 and all(item) for item in METRICS.values())
