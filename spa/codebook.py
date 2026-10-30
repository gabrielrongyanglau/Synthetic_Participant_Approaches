"""Download dictionaries follow the actual exported columns and input provenance."""
import json
import pandas as pd
from .study import load_study,OUTCOMES
from .custom import guide as custom_guide,demographics,predictor_fields,item_fields,bounds

DEFINITIONS={
 'B1SORIEN':'General expectations that future events will have favourable rather than unfavourable outcomes, measured by the overall Life Orientation Test score.',
 'B1SPESSI':'General expectations of unfavourable future outcomes.',
 'B1SMASTE':'Belief in one’s ability to achieve goals and influence important outcomes.',
 'B1SCONST':'Perceived obstacles and limits on one’s ability to influence events.',
 'B1SCTRL':'Overall perceived ability to influence one’s life, combining mastery and constraints.',
 'B1SESTEE':'Overall evaluation of one’s worth and positive regard for oneself.',
 'B1SEXTRA':'Tendency toward sociability, activity and engagement with other people.',
 'B1SOPEN':'Openness to new ideas, experiences and imaginative thinking.',
 'B1SCONS2':'Tendency toward organization, responsibility and dependability.',
 'B1SAGREE':'Tendency toward warmth, cooperation and consideration of others.',
 'B1SNEURO':'Tendency to experience emotional instability and distress.',
 'B1SACTIV':'Taking direct action to address a source of stress.',
 'B1SPLAN':'Thinking through steps and strategies for dealing with stress.',
 'B1SREINT':'Finding positive meaning or opportunities for growth in stressful experiences.',
 'B1SPRCOP':'Use of active coping, planning and positive reinterpretation to address stress.',
 'B1SDENIA':'Coping by refusing to acknowledge or accept a stressful situation.',
 'B1SDISEN':'Reducing or giving up efforts to deal with a stressful situation.',
 'B1SFDCOP':'Use of eating or food to manage distress.',
 'B1SPOSAF':'Frequency of positive emotional experiences during the past 30 days.',
 'B1SNEGAF':'Frequency of negative emotional experiences during the past 30 days.',
 'B1PANXIE':'Count of anxiety symptoms experienced most days over the past 12 months, subject to source screening rules. Zero is a valid score; this is not a binary diagnosis.',
 'B1SKINPO':'Perceived emotional support and understanding from family members.',
 'B1SFDSPO':'Perceived emotional support and understanding from friends.',
 'B1SSPEMP':'Perceived emotional support and understanding from a spouse or partner.',
 'B1SKINNE':'Perceived demands, criticism or interpersonal strain involving family members.',
 'B1SFDSNE':'Perceived demands, criticism or interpersonal strain involving friends.',
 'B1SSPCRI':'Perceived demands, criticism or interpersonal strain involving a spouse or partner.',
 'B1SGENER':'Concern for and perceived contribution to the welfare of other people and future generations.',
 'B1SSWBMS':'Perception that society and the social world are understandable and meaningful.',
 'B1SSWBSI':'Sense of belonging to and connection with a community or society.',
 'B1SSWBAO':'Positive attitudes toward other people and acceptance of human differences.',
 'B1SSWBSC':'Perception that one’s activities make a useful contribution to society.',
 'B1SSWBSA':'Belief that society has potential for positive development.',
 'B1SDAYDI':'Reported frequency of unfair or disrespectful treatment in everyday interactions.',
 'B1SNEGWF':'Interference from work demands or experiences with family life.',
 'B1SNEGFW':'Interference from family demands or experiences with work life.',
 'B1SPWBU2':'Sense of direction, goals and meaning in life.',
 'B1SPWBS2':'Positive evaluation and acceptance of oneself and one’s past life.',
 'B1PRAGE_2019':'Age in completed years at the MIDUS 2 telephone interview, using the corrected source age variable.',
 'B1PRSEX':'Sex recorded for the respondent in the source data; use the category labels supplied below.',
 'B1PB1':'Highest level of formal education completed.',
 'B1PB19':'Current marital status at MIDUS 2.',
 'B1PF7A':'First reported racial-origin category. This field does not represent every reported racial origin.',
 'B1SN1A':'First reported religious preference. This field does not represent every reported preference.',
 'life_satisfaction_MIDUS2':'Existing source life-satisfaction composite at MIDUS 2, summarizing ratings across life domains.',
 'life_satisfaction_MIDUS3':'Existing source life-satisfaction composite at MIDUS 3, summarizing ratings across life domains.'}


def build(columns,method,study=None):
    result=[]
    identifier=dict(column='participant_id',name='Participant identifier',definition='Sequential record number assigned within this generated dataset. It is not an original human participant identifier.',role='identifier',assessment='',allowed_values='Whole numbers 1–100',scoring='Not a psychological score.',missing_values='Not permitted',source='Assigned by the toolkit',provenance='Assigned locally')
    if study:
        guides={r['Column']:r for r in custom_guide(study)};ds=demographics(study);ps=predictor_fields(study)
        for code in columns:
            if code=='participant_id':result.append(identifier);continue
            g=guides[code];v=next((v for v in study['variables'] if code in item_fields(v) or code==v['code']),None)
            fixed=method in (4,7,8) and code in ds or method==7 and code in ps
            if v:
                is_item=code in item_fields(v);name=v['name']+(f' item {item_fields(v).index(code)+1}' if is_item else ' score')
                definition=v['definition']+(' Item wording: '+v['items'][item_fields(v).index(code)] if is_item else '')
                score=g['Scoring']+'; reverse-coded item positions: '+json.dumps(v['reverse'])
                src='User-supplied source (not automatically verified): '+v['citation'];provenance='Retained from supplied profiles' if fixed else 'Generated raw item' if is_item else 'Calculated locally from generated items'
            else:
                v=next(v for v in study['demographics'] if v['code']==code);name=v['name'];definition='Researcher-defined demographic characteristic: '+name;score='Numeric category code; '+json.dumps(v['categories'],ensure_ascii=False);src='Researcher-defined demographic';provenance='Constructed locally to match demographic proportions' if method==4 and fixed else 'Retained from supplied profiles' if fixed else 'Generated'
            result.append(dict(column=code,name=name,definition=definition,role=g['Role'],assessment='Researcher-defined study',allowed_values=(f"{bounds(study)[code][0]} to {bounds(study)[code][1]}" if g['Allowed']=='Composite score' else g['Allowed']),scoring=score,missing_values='Blank means missing; fixed blanks are retained. Composite scores require all items.',source=src,provenance=provenance))
    else:
        s=load_study()
        for code in columns:
            if code=='participant_id':result.append(identifier);continue
            v=s['variables'][s['outcomes'].get(code,code)];ds=code in s['demographic_covariates'];out=code in OUTCOMES
            fixed=method in (4,7,8) and ds or method==7 and not out
            name=v['label'] if not out else 'Life satisfaction at MIDUS '+('2' if code==OUTCOMES[0] else '3')
            result.append(dict(column=code,name=name,definition=DEFINITIONS[code],role='demographic' if ds else 'outcome' if out else 'psychological predictor',assessment='MIDUS 3' if code==OUTCOMES[1] else 'MIDUS 2',allowed_values=json.dumps(v['categories'],ensure_ascii=False) if v['kind']=='category' else f"{v['minimum']} to {v['maximum']}",scoring=v['scoring'],missing_values='Blank means missing or not applicable; zero is a score when within the valid range. Source missing codes: '+json.dumps(v['missing_codes']),source='MIDUS source score; codebook page '+str(v.get('source_codebook_page','not specified')),provenance='Constructed locally to match demographic proportions' if method==4 and fixed else 'Retained from supplied profiles' if fixed else 'Generated'))
    return result

def csv(rows):return '\ufeff'+pd.DataFrame(rows).to_csv(index=False)
