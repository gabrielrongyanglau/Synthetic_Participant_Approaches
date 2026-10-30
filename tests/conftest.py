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

@pytest.fixture(autouse=True)
def original_batch_size(monkeypatch,request):
    """Legacy tests check the evaluated single-request protocol (100 participants per AI request).
    Tests marked 'parallel' use the public default of several smaller concurrent requests."""
    if 'parallel' not in request.keywords:monkeypatch.setenv('SPA_BATCH_SIZE','100')
    else:monkeypatch.delenv('SPA_BATCH_SIZE',raising=False)

def local_rows(method):
    """Fictional 100-person MIDUS dataset generated locally (no AI), keyed by internal source codes."""
    from spa.workflow import context_bank,illustrative_generation
    from spa.study import json_records
    s=load_study();ctx=context_bank(s,[method],100,1,1,examples=True,population='Adults')[f'SPA{method}_R0001']
    return {f'SPA{method}_R0001':json_records(illustrative_generation(s,method,100,1,1,ctx))}

def pytest_configure(config):config.addinivalue_line('markers','parallel: use the default parallel batch size')
