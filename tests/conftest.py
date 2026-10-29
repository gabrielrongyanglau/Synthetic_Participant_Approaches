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
