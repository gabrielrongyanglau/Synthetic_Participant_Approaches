"""Approach labels and suggestions, using SPA1-SPA8 numbering from the revised proposal."""
PUBLIC_ID={m:m for m in range(1,9)}  # SPA numbering is used throughout
PUBLIC_NAMES={1:'Persona prompted',2:'Direct generation',3:'Population guided',4:'Quota matched',5:'Pilot calibrated',6:'Pilot analysis guided',7:'Demographic-only profiles',8:'Demographic and psychological profiles'}
def public_label(m):return f'SPA{PUBLIC_ID[int(m)]} · {PUBLIC_NAMES[PUBLIC_ID[int(m)]]}'
def public_run(run):return run

def suggest(goal,information):
    info=set(information);feasible={1,2}
    for key,ms in {'population':[3],'proportions':[4],'pilot':[5,6],'demographics':[7],'psychology':[7,8]}.items():
        if key in info:feasible.update(ms)
    if goal not in ('distributions','patterns','strengths','outcomes','workflow'):raise ValueError('Unknown research goal.')
    reason='Direct generation is the simplest starting point without participant records. Its MIDUS fidelity was limited.'
    primary=2
    if goal=='distributions' and 'pilot' in info:primary=5;reason='Pilot-calibrated generation had the closest generated psychological-score distributions in MIDUS. Pilot analysis guided generation is an alternative.'
    elif goal in ('strengths','outcomes','patterns') and 'psychology' in info:primary=8;reason='Generate hypothetical outcomes conditional on observed psychological and demographic scores. This had much smaller relationship errors in MIDUS, although errors remained.'
    elif goal in ('patterns','strengths') and 'pilot' in info:primary=6;reason='Pilot analysis guided generation had smaller relationship errors than pilot calibrated generation in MIDUS. Both substantially exaggerated strengths, so treat their effect sizes as unvalidated.'
    elif 'demographics' in info or 'psychology' in info:primary=7;reason='Use actual demographic profiles when retaining those profiles matters. Demographics alone did not produce substantially closer psychological scores or relationships.'
    elif 'proportions' in info:primary=4;reason='Use constructed profiles when matching demographic proportions is part of the task. Matching demographics did not establish psychological fidelity.'
    elif 'population' in info:primary=3;reason='Use a qualitative population description to guide generation. This is compatible with your inputs, with uncertain gains in fidelity.'
    if goal=='outcomes' and 'psychology' not in info:reason='Generating outcomes only requires observed demographics and psychological scores. Available alternatives also generate predictors and address a different task.'
    return dict(primary=primary,feasible=sorted(feasible,key=lambda m:PUBLIC_ID[m]),reason=reason,
      caution='Recommendations are informed by one MIDUS comparison. Custom questionnaires, populations and outcomes require their own validation. Treat generated strengths as exploratory. Effect sizes, forecasts, imputations and power calculations need validated human data.',
      task_supported=goal!='outcomes' or 'psychology' in info)
