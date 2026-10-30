"""Public display order is separate from historical engine and analysis IDs."""
PUBLIC_ID={1:1,2:2,3:3,4:4,5:5,6:6,7:8,8:7}
PUBLIC_NAMES={1:'Persona prompted',2:'Direct generation',3:'Population guided',4:'Quota matched',5:'Pilot calibrated',6:'Pilot analysis guided',7:'Demographic-only profiles',8:'Demographic and psychological profiles'}
def public_label(m):return f'SPA{PUBLIC_ID[int(m)]} · {PUBLIC_NAMES[PUBLIC_ID[int(m)]]}'
def public_run(run):return 'SPA'+str(PUBLIC_ID[int(run[1])])+run[2:]

def suggest(goal,information):
    info=set(information);feasible={1,2}
    for key,ms in {'population':[3],'proportions':[4],'pilot':[5,6],'demographics':[8],'psychology':[7,8]}.items():
        if key in info:feasible.update(ms)
    if goal not in ('distributions','patterns','strengths','outcomes','workflow'):raise ValueError('Unknown research goal.')
    reason='Direct generation is the simplest starting point without participant records. Its MIDUS fidelity was limited.'
    primary=2
    if goal=='distributions' and 'pilot' in info:primary=5;reason='Pilot-calibrated generation had the closest generated psychological-score distributions in MIDUS. Pilot analysis guided generation is an alternative.'
    elif goal in ('strengths','outcomes','patterns') and 'psychology' in info:primary=7;reason='Generate hypothetical outcomes conditional on observed psychological and demographic scores. This had much smaller relationship errors in MIDUS, although errors remained.'
    elif goal in ('patterns','strengths') and 'pilot' in info:primary=6;reason='Pilot analysis guided generation had smaller relationship errors than pilot calibrated generation in MIDUS. Both substantially exaggerated strengths; neither provides validated effect sizes.'
    elif 'demographics' in info or 'psychology' in info:primary=8;reason='Use actual demographic profiles when retaining those profiles matters. Demographics alone did not produce substantially closer psychological scores or relationships.'
    elif 'proportions' in info:primary=4;reason='Use constructed profiles when matching demographic proportions is part of the task. Matching demographics did not establish psychological fidelity.'
    elif 'population' in info:primary=3;reason='Use a qualitative population description to guide generation. This is compatible with your inputs, without a clear guarantee of improved fidelity.'
    if goal=='outcomes' and 'psychology' not in info:reason='Generating outcomes only requires observed demographics and psychological scores. Available alternatives also generate predictors and address a different task.'
    return dict(primary=primary,feasible=sorted(feasible,key=lambda m:PUBLIC_ID[m]),reason=reason,
      caution='Recommendations are informed by one MIDUS comparison. Custom questionnaires, populations and outcomes require their own validation. Generated strengths are not validated effect sizes, forecasts, imputations or inputs for power calculations.',
      task_supported=goal!='outcomes' or 'psychology' in info)
