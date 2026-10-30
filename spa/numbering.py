"""Approach numbering. The toolkit uses SPA1-SPA8 as defined in the revised proposal (Table 3):
SPA7 = demographic-only profiles; SPA8 = demographic and psychological profiles.

The original study's prompt bank (prompts/methods.json), verified aggregate results
(data/original_study/) and offline archives used the earlier numbering, in which 7 and 8 were
the other way round. Those source files are kept byte-identical; this module is the only place
that translates them, at load time.
"""
import re

ORIGINAL_TO_SPA={1:1,2:2,3:3,4:4,5:5,6:6,7:8,8:7}
SPA_TO_ORIGINAL={v:k for k,v in ORIGINAL_TO_SPA.items()}
RUN_PATTERN=r'SPA[1-8]_R[0-9]{4}'

def run_name(spa,repetition):return f'SPA{int(spa)}_R{int(repetition):04d}'

def run_parts(run):
    match=re.fullmatch(r'SPA([1-8])_R([0-9]{4})',str(run))
    if not match:raise ValueError('Invalid dataset name.')
    return int(match.group(1)),int(match.group(2))

def run_spa(run):return run_parts(run)[0]

def original_frame(frame):
    """Relabel method columns of a source result table from the original numbering to SPA numbering."""
    frame=frame.copy()
    for column in ('method','first','second'):
        if column in frame:frame[column]=frame[column].map(lambda m:ORIGINAL_TO_SPA[int(m)])
    return frame
