"""MIDUS demonstration: the demographics and psychological predictors a visitor chooses on the Questionnaire step.

The preserved engine (config/study.yaml, prompts, workflow) works from the study's lists of demographic
covariates and psychological predictors. A selection is applied by passing a copy of the study with
shorter lists, so the method templates and scoring rules stay unchanged. Both life-satisfaction outcomes
are always generated. With every variable selected, the study is the one evaluated in the proposal.
"""
import copy
from .public import PUBLIC,CODE

# Plain names shown on the Questionnaire step, in the study's order.
LABELS={
 'B1PRAGE_2019':'Age','B1PRSEX':'Sex','B1PB1':'Highest educational attainment','B1PB19':'Current marital status',
 'B1PF7A':'Racial origin','B1SN1A':'Religious preference',
 'B1SORIEN':'Optimism (Life Orientation Test)','B1SPESSI':'Pessimism','B1SMASTE':'Personal mastery','B1SCONST':'Perceived constraints',
 'B1SCTRL':'Overall sense of control','B1SESTEE':'Self-esteem','B1SEXTRA':'Extraversion','B1SOPEN':'Openness to experience',
 'B1SCONS2':'Conscientiousness','B1SAGREE':'Agreeableness','B1SNEURO':'Neuroticism','B1SACTIV':'Active coping','B1SPLAN':'Planning',
 'B1SREINT':'Positive reinterpretation and growth','B1SPRCOP':'Problem-focused coping (overall)','B1SDENIA':'Denial',
 'B1SDISEN':'Behavioural disengagement','B1SFDCOP':'Use of food to cope','B1SPOSAF':'Positive affect','B1SNEGAF':'Negative affect',
 'B1PANXIE':'Anxiety symptoms','B1SKINPO':'Support from family','B1SFDSPO':'Support from friends','B1SSPEMP':'Support from spouse or partner',
 'B1SKINNE':'Strain from family','B1SFDSNE':'Strain from friends','B1SSPCRI':'Strain from spouse or partner','B1SGENER':'Generativity',
 'B1SSWBMS':'Meaningfulness of society','B1SSWBSI':'Social integration','B1SSWBAO':'Acceptance of others','B1SSWBSC':'Social contribution',
 'B1SSWBSA':'Social actualisation','B1SDAYDI':'Daily discrimination','B1SNEGWF':'Negative work-to-family spillover',
 'B1SNEGFW':'Negative family-to-work spillover','B1SPWBU2':'Purpose in life','B1SPWBS2':'Self-acceptance'}

def choices(study):
    """Variables offered on the Questionnaire step, using public names only."""
    pair=lambda codes:[dict(name=PUBLIC[c],label=LABELS[c]) for c in codes]
    return dict(demographics=pair(study['demographic_covariates']),predictors=pair(study['psychological_predictors']))

def parse(raw,study):
    """Translate a visitor's selection (public names) to source codes. None means the full study."""
    if raw is None:return None
    if not isinstance(raw,dict) or set(raw)-{'demographics','predictors'}:raise ValueError('Choose the MIDUS measures on the Questionnaire step.')
    chosen={}
    for key,allowed in (('demographics',study['demographic_covariates']),('predictors',study['psychological_predictors'])):
        names=raw.get(key,[])
        if not isinstance(names,list) or any(not isinstance(n,str) for n in names) or len(set(names))!=len(names):
            raise ValueError('Choose the MIDUS measures on the Questionnaire step.')
        codes={CODE.get(n,'') for n in names}
        unknown=[n for n,c in zip(names,[CODE.get(n,'') for n in names]) if c not in allowed]
        if unknown:raise ValueError('Unknown MIDUS variable: '+', '.join(unknown[:3])+'.')
        chosen[key]=[c for c in allowed if c in codes]
    if not chosen['predictors']:raise ValueError('Choose at least one psychological predictor on the Questionnaire step.')
    if chosen['demographics']==study['demographic_covariates'] and chosen['predictors']==study['psychological_predictors']:return None
    return chosen

def subset(study,fields):
    """A copy of the study limited to the chosen variables. The full study is returned unchanged when fields is None."""
    if not fields:return study
    s=copy.deepcopy(study)
    s['demographic_covariates']=[c for c in study['demographic_covariates'] if c in fields['demographics']]
    s['psychological_predictors']=[c for c in study['psychological_predictors'] if c in fields['predictors']]
    return s

def needs_demographics(method,fields):
    if fields is not None and method in (4,7,8) and not fields['demographics']:
        raise ValueError(f'SPA{method} keeps demographic details fixed, so it needs at least one demographic characteristic. Choose some on the Questionnaire step.')
