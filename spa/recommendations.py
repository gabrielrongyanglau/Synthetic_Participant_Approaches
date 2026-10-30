"""Approach labels and suggestions, using SPA1-SPA8 numbering from the revised proposal."""
PUBLIC_ID={m:m for m in range(1,9)}  # SPA numbering is used throughout
PUBLIC_NAMES={1:'Persona prompted',2:'Direct generation',3:'Population guided',4:'Quota matched',5:'Pilot calibrated',6:'Pilot analysis guided',7:'Demographic-only profiles',8:'Demographic and psychological profiles'}
def public_label(m):return f'SPA{PUBLIC_ID[int(m)]} · {PUBLIC_NAMES[PUBLIC_ID[int(m)]]}'
def public_run(run):return run

GOALS={'distributions':'Goal 1: reproduce psychological scores',
 'patterns':'Goal 2: explore the direction and pattern of relationships',
 'strengths':'Goal 2: estimate the strength of relationships',
 'outcomes':'Goal 2: generate a later outcome from baseline scores',
 'workflow':'Try the toolkit'}
STAGES={'none':'No participant data yet','proportions':'Target demographic proportions','pilot':'A pilot sample of 50 participants',
 'demographics':'Individual demographic profiles','psychology':'Individual demographic and psychological scores'}
PATTERN='In the study, every approach reproduced the direction and overall pattern of relationships closely (pattern r .94 to .97).'
STRENGTH='Approaches that generated psychological scores made relationships about three times stronger than in the human data (average correlation with life satisfaction about .95, against .31).'
CAUTION='These suggestions follow Table 6 of the proposal, which is based on one comparison with MIDUS data. Your own measures, population and outcomes need their own check against human data. No evaluated approach is validated for effect sizes or power calculations.'

def suggest(goal,information):
    """Recommended approach for a goal and the information a researcher has (Table 6 of the proposal)."""
    if goal not in GOALS:raise ValueError('Unknown research goal.')
    info={i for i in information if i in STAGES or i=='population'}
    feasible={1,2,3}
    for key,ms in {'proportions':[4],'pilot':[5,6],'demographics':[7],'psychology':[7,8]}.items():
        if key in info:feasible.update(ms)
    if 'psychology' in info:
        primary=8
        reason={'distributions':'Your psychological scores are already observed, so SPA8 keeps them and generates the outcomes. To generate new psychological scores, use 50 complete records, outcomes included, as a pilot sample with SPA5.',
                'workflow':'SPA8 keeps each person’s real demographics and psychological scores and generates only life satisfaction.'}.get(goal,
                'Table 6 recommends SPA8 when baseline demographics and psychological scores are available. In the study, SPA8 came closest to human relationship strengths (average correlation error .19 at MIDUS 2 and .24 at MIDUS 3, against .63 to .72 for the other approaches), although it still overstated them.')
    elif 'pilot' in info:
        primary=6 if goal=='strengths' else 5
        reason={'strengths':'With a pilot sample, SPA6 had slightly smaller relationship errors than SPA5. '+STRENGTH,
                'patterns':'SPA5 uses your pilot records and their summary statistics. '+PATTERN}.get(goal,
                'Table 6 recommends SPA5 for a 50-person pilot, with SPA6 when you cannot compute summary statistics. In the study, SPA5 produced the closest psychological scores: averages differed from human data by 0.21 standard deviations, against 0.53 to 0.58 for approaches without pilot data.')
    elif 'demographics' in info:
        primary=7;reason='SPA7 keeps each person’s real demographics and generates their psychological scores and outcomes. In the study, real demographics did not bring scores or relationships closer to human data than SPA2.'
    elif 'proportions' in info:
        primary=4;reason='SPA4 builds profiles that match your demographic proportions and generates the remaining scores. In the study, matching demographics did not bring scores or relationships closer to human data than SPA2.'
    else:
        primary=2
        reason={'distributions':'Without human data, SPA2 is the simplest starting point. In the study, its average scores differed from human data by about half a standard deviation. A 50-person pilot with SPA5 roughly halves this.',
                'strengths':'Table 6 recommends SPA2 before human data are collected. '+STRENGTH}.get(goal,
                'Table 6 recommends SPA2 before human data are collected, with SPA1 and SPA3 as alternatives that showed no meaningful advantage. '+PATTERN)
    supported=goal!='outcomes' or 'psychology' in info
    if not supported:reason='Generating a later outcome needs each person’s baseline demographics and psychological scores (SPA8). With your current information, the approaches below generate psychological scores as well.'
    return dict(primary=primary,feasible=sorted(feasible,key=lambda m:PUBLIC_ID[m]),reason=reason,caution=CAUTION,task_supported=supported,
      goal_label=GOALS[goal],strength_note=STRENGTH if goal=='strengths' else '')
