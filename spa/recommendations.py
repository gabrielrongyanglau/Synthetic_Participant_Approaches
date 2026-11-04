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
PATTERN='In our proposal, every approach reproduced the direction and overall pattern of relationships closely (pattern r .94 to .97).'
STRENGTH='Approaches that generated psychological scores made relationships about three times stronger than in the human data (average absolute correlation with life satisfaction .95 to .97, against .32).'
CAUTION=('These suggestions are based on our proposal’s results from one comparison with MIDUS data. Where two approaches are recommended, the first is the one '
         'our proposal recommends for that information. Where our proposal makes no recommendation, the first did better on this goal, or the results were mixed '
         'and the first uses more of your information. Your own measures, population and outcomes need their own check against human data. No evaluated approach '
         'is validated for effect sizes or power calculations.')

# Recommended approaches for each goal and the information available, first choice first. Every figure is from Tables 1 and 2 of our proposal.
GOAL1={
 'none':([2],'SPA2 generates participant records directly from your study’s definitions. Without participant data it is the simplest option, and imagining each person first (SPA1) did not help. In our proposal, average scores differed from human data by 0.54 standard deviations with SPA2 and 0.55 with SPA1. A 50-person pilot with SPA5 roughly halved this difference (0.21).'),
 'description':([3,2],'SPA3 uses your population description, and SPA2 is the simpler alternative. In our proposal, the description brought scores only slightly closer to human data: average scores differed by 0.53 standard deviations with SPA3 and 0.54 with SPA2, and the full score distributions were slightly closer too (distance 0.68 against 0.70). Both stayed about half a standard deviation from human data. A 50-person pilot with SPA5 roughly halved this difference (0.21).'),
 'proportions':([4,2],'SPA4 keeps your target demographic proportions, and SPA2 is the alternative. In our proposal, the two had different strengths. SPA4 came closest to the full human score distributions among approaches without pilot data (distance 0.65, against 0.68 to 0.70), and its participants match your demographic composition. Its average scores were slightly further from human data (0.57 standard deviations, against 0.54 for SPA2), and its scores varied less than human scores (SD ratio 0.77, where 1 means equal variation). Choose SPA4 when the demographic composition matters most, and SPA2 when average scores matter most.'),
 'pilot':([5,6],'SPA5 and SPA6 both use your 50-person pilot, and both reproduced human scores far better than approaches without pilot data. In our proposal, average scores differed from human data by 0.21 standard deviations with SPA5 and 0.25 with SPA6, against 0.53 to 0.58 without pilot data. SPA5 is recommended first because it was closer on every Goal 1 measure, for example a distribution distance of 0.32 against 0.37 for SPA6. In SPA6, the AI analyses the pilot records itself.'),
 'demographics':([7,2],'SPA7 keeps each person’s actual demographics, and SPA2 is the alternative. In our proposal, keeping actual demographics did not bring average scores closer to human data: they differed by 0.58 standard deviations with SPA7, against 0.54 with SPA2, and SPA7’s scores varied less than human scores (SD ratio 0.78). Its full score distributions were slightly closer (distance 0.66, against 0.70). Choose SPA7 when keeping each person’s actual demographics matters most, and SPA2 when average scores matter most.'),
 'psychology':([8],'SPA8 uses participants’ actual demographic characteristics and psychological scores to generate psychological outcomes, such as life satisfaction. It can therefore be used to explore the reproduction of psychological outcomes (Goal 1), but not the reproduction of psychological predictor scores already provided to AI. Our proposal evaluated SPA8’s relationship fidelity (Goal 2), but did not separately establish its ability to reproduce psychological outcomes under Goal 1.')}
GOAL2={
 'none':([2],'Our proposal recommends SPA2 before human data are collected. SPA1 and SPA3 are alternatives that showed no meaningful advantage. '+PATTERN+' '+STRENGTH),
 'description':([2,3],'SPA2 and SPA3 performed almost identically, so either is a reasonable choice. In our proposal, both reproduced the overall pattern of relationships closely (pattern r .94), and both overstated relationship strengths by similar amounts (correlation error .65 for SPA2 and .66 for SPA3 at MIDUS 2). SPA2 is listed first because it is simpler and its error was marginally lower. Choose SPA3 to apply your population description.'),
 'proportions':([2,4],'SPA2 is recommended first, with SPA4 as the alternative. In our proposal, matching demographic proportions did not improve relationships. SPA4’s correlation error was .66 at MIDUS 2, against .65 for SPA2, with the same overall pattern (pattern r .94). Choose SPA4 when your synthetic participants need to match the demographic proportions.'),
 'pilot':([5,6],'SPA5 and SPA6 both use your 50-person pilot. SPA5 is listed first, as under Goal 1, because our proposal recommends it for pilot data: it receives the pilot records together with precomputed summaries, and it reproduced human scores most closely. For relationships, the two differed only slightly. SPA6 came a little closer to human relationship strengths (correlation error .63 at MIDUS 2 and .69 at MIDUS 3, against .66 and .72 for SPA5), and its agreement with human correlations was slightly higher (ICC .58, against .56). Both reproduced the overall pattern closely (pattern r .94), and both still made relationships much stronger than in the human data.'),
 'demographics':([2,7],'SPA2 is recommended first, with SPA7 as the alternative. In our proposal, keeping actual demographics did not improve relationships. SPA7’s correlation error was .66 at MIDUS 2, against .65 for SPA2, with the same overall pattern (pattern r .94). Choose SPA7 when keeping each person’s actual demographics matters.'),
 'psychology':([8],'SPA8 generates outcomes from each person’s supplied demographics and psychological scores. In our proposal, it came closest to human relationship strengths (average correlation error .19 at MIDUS 2 and .24 at MIDUS 3, against .63 to .72 for the other approaches), although it still overstated them.')}

def suggest(goal,information):
    """Recommended approaches for a goal and the information a researcher has, with the evidence for each (Tables 1 and 2 of our proposal)."""
    goal=LEGACY_GOALS.get(goal,goal)
    if goal not in GOALS:raise ValueError('Unknown research goal.')
    info={i for i in information if i in STAGES or i=='population'}
    feasible={1,2,3}
    for key,ms in {'proportions':[4],'pilot':[5,6],'demographics':[7],'psychology':[7,8]}.items():
        if key in info:feasible.update(ms)
    rel=goal=='relationships'
    stage=next((k for k in ('psychology','pilot','demographics','proportions','description') if k in info),'none')
    recommended,reason=(GOAL2 if rel else GOAL1)[stage]
    return dict(primary=recommended[0],recommended=recommended,feasible=sorted(feasible,key=lambda m:PUBLIC_ID[m]),reason=reason,caution=CAUTION,task_supported=True,goal_label=GOALS[goal],strength_note=STRENGTH if rel else '')
