import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from spa.study import load_study
from spa.simulation import invent_reference

@pytest.fixture(scope='session')
def study():return load_study()
@pytest.fixture(scope='session')
def reference(study):return invent_reference(study)


def local_rows(method):
    """Fictional 100-person MIDUS dataset generated locally (no AI), keyed by internal source codes."""
    from spa.workflow import context_bank,illustrative_generation
    from spa.study import json_records
    s=load_study();ctx=context_bank(s,[method],100,1,1,examples=True,population='Adults')[f'SPA{method}_R0001']
    return {f'SPA{method}_R0001':json_records(illustrative_generation(s,method,100,1,1,ctx))}

