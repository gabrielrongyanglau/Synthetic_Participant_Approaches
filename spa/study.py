from pathlib import Path
import json
import numpy as np
import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTCOMES = ('life_satisfaction_MIDUS2', 'life_satisfaction_MIDUS3')
NAMES = {1:'Persona prompted',2:'Ungrounded random',3:'Population guided',4:'Quota matched',
         5:'Pilot calibrated',6:'Pilot analysis guided',7:'Demographic-only profiles',8:'Demographic and psychological profiles'}
DESCRIPTIONS = {
 1:'Imagine a distinct person for each generated record. All study values are generated.',
 2:'Generate records directly. All study values are generated; this is not a probability sample of humans.',
 3:'Use qualitative target-population guidance. All study values are generated.',
 4:'Construct demographic profiles matching marginal proportions. Generate psychology and outcomes.',
 5:'Use 50 pilot records with precomputed descriptive statistics, correlations and covariances.',
 6:'Analyse 50 pilot records, then generate using that analysis. No precomputed summaries are supplied.',
 7:'Retain supplied demographics. Generate psychology and life-satisfaction outcomes.',
 8:'Retain supplied demographics and psychology. Generate only life-satisfaction outcomes.'}

def load_study():
    return yaml.safe_load((PROJECT_ROOT/'config/study.yaml').read_text())

def predictors(study):
    return study['psychological_predictors'] + study['demographic_covariates']

def selected_fields(study):
    return predictors(study) + list(OUTCOMES)

def json_records(frame):
    return [
        {k:(None if pd.isna(v) else v.item() if hasattr(v,'item') else v) for k,v in r.items()}
        for r in frame.to_dict('records')]

def clean_frame(frame, study, *, reference=False, expected_n=None):
    frame = frame.copy()
    if frame.columns.duplicated().any():
        raise ValueError('Repeated column names.')
    for output, source in study['outcomes'].items():
        if output not in frame and source in frame: frame[output] = frame[source]
    fields = selected_fields(study)
    absent = set(fields)-set(frame.columns)
    if absent: raise ValueError('Missing fields: '+', '.join(sorted(absent)))
    if expected_n is not None and len(frame) != expected_n: raise ValueError('Incorrect participant count.')
    for f in fields:
        spec = study['variables'][study['outcomes'].get(f,f)]
        x = pd.to_numeric(frame[f], errors='raise')
        x = x.mask(x.isin(spec['missing_codes']))
        if spec['kind']=='category': valid = x.isin(list(spec['categories']))
        else:
            valid = x.between(spec['minimum'],spec['maximum'])
            if spec['kind']=='integer': valid &= x.mod(1).eq(0)
        if (x.notna() & (~valid | ~np.isfinite(x))).any(): raise ValueError('Invalid values in '+f)
        frame[f] = x
    if reference:
        if 'B1STATUS' in frame and not (frame.B1STATUS.eq(2)&frame.C1STATUS.isin([4,5,6])).all():
            raise ValueError('Reference includes records outside the specified linked cohort.')
        if study['id_column'] in frame and (frame[study['id_column']].isna().any() or frame[study['id_column']].duplicated().any()):
            raise ValueError('Reference IDs must be unique and observed.')
        frame = frame.dropna(subset=list(OUTCOMES)).reset_index(drop=True)
    elif frame[list(OUTCOMES)].isna().any().any(): raise ValueError('Generated outcomes must be observed.')
    if 'participant_id' in frame:
        ids = pd.to_numeric(frame.participant_id,errors='raise')
        if ids.isna().any() or ids.duplicated().any() or (ids%1!=0).any(): raise ValueError('Participant IDs must be unique integers.')
    return frame

def label(study, code):
    if code in OUTCOMES: return 'Life satisfaction at MIDUS '+('2' if code==OUTCOMES[0] else '3')
    return study['variables'][code].get('label',code)
