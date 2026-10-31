"""Approach labels and suggestions, using SPA1-SPA8 numbering from the revised proposal."""
PUBLIC_ID={m:m for m in range(1,9)}  # SPA numbering is used throughout
PUBLIC_NAMES={1:'Persona prompted',2:'Direct generation',3:'Population guided',4:'Quota matched',5:'Pilot calibrated',6:'Pilot analysis guided',7:'Demographic-only profiles',8:'Demographic and psychological profiles'}
def public_label(m):return f'SPA{PUBLIC_ID[int(m)]} · {PUBLIC_NAMES[PUBLIC_ID[int(m)]]}'
def public_run(run):return run

GOALS={'distributions':'Goal 1: reproduce psychological variables',
 'relationships':'Goal 2: reproduce relationships among variables'}
# Earlier interface versions offered finer-grained choices; they map onto the proposal's two goals.
LEGACY_GOALS={'patterns':'relationships','strengths':'relationships','outcomes':'relationships','workflow':'distributions'}
STAGES={'none':'No participant data yet','description':'A general population description','proportions':'Target demographic proportions','pilot':'A pilot sample of 50 participants',
 'demographics':'Individual demographic profiles','psychology':'Individual demographic and psychological scores'}
PATTERN='In the study, every approach reproduced the direction and overall pattern of relationships closely (pattern r .94 to .97).'
STRENGTH='Approaches that generated psychological scores made relationships about three times stronger than in the human data (average correlation with life satisfaction about .95, against .31).'
CAUTION='These suggestions follow the proposal’s recommendations (its Table 6), which are based on one comparison with MIDUS data. Your own measures, population and outcomes need their own check against human data. No evaluated approach is validated for effect sizes or power calculations.'

def suggest(goal,information):
    """Recommended approach for a goal and the information a researcher has (Table 6 of the proposal)."""
    goal=LEGACY_GOALS.get(goal,goal)
    if goal not in GOALS:raise ValueError('Unknown research goal.')
    info={i for i in information if i in STAGES or i=='population'}
    feasible={1,2,3}
    for key,ms in {'proportions':[4],'pilot':[5,6],'demographics':[7],'psychology':[7,8]}.items():
        if key in info:feasible.update(ms)
    rel=goal=='relationships'
    if 'psychology' in info:
        primary=8
        reason=('SPA8 generates outcomes from each person’s supplied demographics and psychological scores. In the study, it came closest to human relationship strengths (average correlation error .19 at MIDUS 2 and .24 at MIDUS 3, against .63 to .72 for the other approaches), although it still overstated them.' if rel else
                'Psychological scores already exist for every participant, so there is nothing for Goal 1 to generate. SPA8 keeps those scores and generates the outcomes. To try generating psychological scores instead, choose a small human pilot dataset: 50 participants with every variable, outcomes included, used with SPA5.')
    elif 'pilot' in info:
        primary=5
        reason=('SPA5 uses the pilot records and their summary statistics. '+PATTERN+' Relationship strengths stayed inflated, and SPA6 reduced strength errors only slightly.' if rel else
                'The proposal recommends SPA5 for a 50-person pilot. SPA6 is an alternative in which the AI analyses the pilot records itself. In the study, SPA5 produced the closest psychological scores: averages differed from human data by 0.21 standard deviations, against 0.53 to 0.58 for approaches without pilot data.')
    elif 'demographics' in info:
        primary=7;reason='SPA7 keeps each person’s supplied demographics and generates their psychological scores and outcomes. In the study, keeping real demographics did not bring scores or relationships closer to human data than SPA2.'
    elif 'proportions' in info:
        primary=4;reason='SPA4 builds profiles that match the demographic proportions and generates the remaining scores. In the study, matching demographics did not bring scores or relationships closer to human data than SPA2.'
    elif 'description' in info:
        primary=3
        reason=('SPA3 adds the population description to the instructions. In the study, it reproduced relationship patterns about as well as SPA1 and SPA2 (pattern r .94), and relationship strengths stayed inflated (correlation error .66 at MIDUS 2, against .65 for SPA2).' if rel else
                'SPA3 uses a description of the people to simulate. In the study, its average scores differed from human data by 0.53 standard deviations, close to SPA1 and SPA2. A 50-person pilot with SPA5 roughly halves this.')
    else:
        primary=2
        reason=('The proposal recommends SPA2 before human data are collected. SPA1 and SPA3 are alternatives that showed no meaningful advantage. '+PATTERN+' '+STRENGTH if rel else
                'Without human data, SPA2 is the simplest starting point. In the study, its average scores differed from human data by about half a standard deviation. A 50-person pilot with SPA5 roughly halves this.')
    return dict(primary=primary,feasible=sorted(feasible,key=lambda m:PUBLIC_ID[m]),reason=reason,caution=CAUTION,task_supported=True,goal_label=GOALS[goal],strength_note=STRENGTH if rel else '')
