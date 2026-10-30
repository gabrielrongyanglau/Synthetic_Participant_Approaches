"""Public variable names for everything the website shows or exports.

MIDUS source codes remain the internal identifiers of the preserved scientific engine
(config/study.yaml, metrics, workflow). They never leave the server: app.py translates
every API response and download to these readable names, and translates uploaded files
and returned records back. This file is the only mapping between the two.
"""
import csv,io,re

PUBLIC={
 # Psychological scores used as predictors
 'B1SORIEN':'optimism_overall','B1SPESSI':'pessimism','B1SMASTE':'personal_mastery','B1SCONST':'perceived_constraints',
 'B1SCTRL':'sense_of_control','B1SESTEE':'self_esteem','B1SEXTRA':'extraversion','B1SOPEN':'openness',
 'B1SCONS2':'conscientiousness','B1SAGREE':'agreeableness','B1SNEURO':'neuroticism','B1SACTIV':'active_coping',
 'B1SPLAN':'planning_coping','B1SREINT':'positive_reinterpretation','B1SPRCOP':'problem_focused_coping',
 'B1SDENIA':'denial_coping','B1SDISEN':'behavioural_disengagement','B1SFDCOP':'food_coping',
 'B1SPOSAF':'positive_affect','B1SNEGAF':'negative_affect','B1PANXIE':'anxiety_symptoms',
 'B1SKINPO':'family_support','B1SFDSPO':'friend_support','B1SSPEMP':'partner_support',
 'B1SKINNE':'family_strain','B1SFDSNE':'friend_strain','B1SSPCRI':'partner_strain','B1SGENER':'generativity',
 'B1SSWBMS':'society_meaningfulness','B1SSWBSI':'social_integration','B1SSWBAO':'social_acceptance',
 'B1SSWBSC':'social_contribution','B1SSWBSA':'social_actualisation','B1SDAYDI':'daily_discrimination',
 'B1SNEGWF':'work_to_family_spillover','B1SNEGFW':'family_to_work_spillover',
 'B1SPWBU2':'purpose_in_life','B1SPWBS2':'self_acceptance',
 # Demographics
 'B1PRAGE_2019':'age','B1PRSEX':'sex','B1PB1':'education','B1PB19':'marital_status',
 'B1PF7A':'racial_origin','B1SN1A':'religious_preference',
 # Defined in the study configuration but not used as predictors
 'B1SOPTIM':'optimism','B1SCONS1':'conscientiousness_4item','B1SPOSPA':'positive_affect_panas',
 'B1SNEGPA':'negative_affect_panas','B1SLFEDI':'lifetime_discrimination','B1SPWBU1':'purpose_in_life_3item',
 'B1SPWBS1':'self_acceptance_3item',
 # Source outcome scores (the generated outcomes are named life_satisfaction_MIDUS2/3)
 'B1SSATIS':'life_satisfaction_5item_wave1','C1SSATIS':'life_satisfaction_5item_wave2',
 'B1SSATIS2':'life_satisfaction_6item_wave1','C1SSATIS2':'life_satisfaction_6item_wave2',
 'B1SQ1':'life_overall_rating_wave1','C1SQ1':'life_overall_rating_wave2',
 # Identifiers and status flags in real reference files
 'M2ID':'source_participant_id','M2FAMNUM':'source_family_id','B1STATUS':'wave1_status','C1STATUS':'wave2_status',
}
CODE={v:k for k,v in PUBLIC.items()}
assert len(CODE)==len(PUBLIC),'Public names must be unique.'
_PATTERN=re.compile(r'(?<![A-Za-z0-9_])('+'|'.join(sorted(map(re.escape,PUBLIC),key=len,reverse=True))+r')(?![A-Za-z0-9_])')
SKIP_KEYS={'ticket','handle'}  # signed opaque tokens are never rewritten

# Source labels refer to the MIDUS 1 wave as "M1"; spell it out so it cannot be read as an approach number.
LABELS={'(Parallel M1 items)':'(MIDUS 1 parallel items)','(M1 items + 1 additional)':'(MIDUS 1 items plus one)'}

def text(value):
    """Replace every source code in a string (free text, CSV or JSON text) with its public name."""
    for old,new in LABELS.items():value=value.replace(old,new)
    return _PATTERN.sub(lambda m:PUBLIC[m.group(1)],value)

def outbound(value):
    """Recursively translate keys and strings in a JSON-like value for the browser."""
    if isinstance(value,dict):
        return {(PUBLIC[k] if k in PUBLIC else text(k) if isinstance(k,str) else k):(v if k in SKIP_KEYS else outbound(v)) for k,v in value.items()}
    if isinstance(value,list):return [outbound(v) for v in value]
    if isinstance(value,str):return text(value)
    return value

def inbound(value):
    """Reverse outbound() for structured values: keys and exact string values only, never free text."""
    if isinstance(value,dict):
        return {(CODE.get(k,k) if isinstance(k,str) else k):(v if k in SKIP_KEYS else inbound(v)) for k,v in value.items()}
    if isinstance(value,list):return [inbound(v) for v in value]
    if isinstance(value,str):return CODE.get(value,value)
    return value

def inbound_csv(content):
    """Translate public column names (and exact-match cells such as proportion field names) in an uploaded CSV."""
    if not isinstance(content,str) or not any(name in content for name in CODE):return content
    rows=list(csv.reader(io.StringIO(content.lstrip('﻿'))))
    out=io.StringIO();csv.writer(out,lineterminator='\n').writerows([[CODE.get(c.strip(),c) for c in row] for row in rows])
    return out.getvalue()

def contains_code(value):
    """True if any source code survives in a string; used by tests and the response guard."""
    return bool(_PATTERN.search(value))
