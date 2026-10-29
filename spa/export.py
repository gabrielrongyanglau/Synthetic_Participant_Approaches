from zipfile import ZipFile,ZIP_DEFLATED
import io
import json
from datetime import datetime,timezone

def bundle_zip(bundle,frames=None):
    b=io.BytesIO()
    with ZipFile(b,'w',ZIP_DEFLATED) as z:
        for k in ['summary','comparisons','variables','human']:
            z.writestr(k+'.csv',bundle[k].to_csv(index=False))
        if 'runs' in bundle:z.writestr('runs.csv',bundle['runs'].to_csv(index=False))
        z.writestr('metadata.json',json.dumps(bundle['metadata'],indent=2,allow_nan=False))
        for (method,rep),frame in (frames or {}).items():z.writestr(f'datasets/M{method}_R{rep:04d}.csv',frame.to_csv(index=False))
    return b.getvalue()

def provenance(bundle,study):
    from .study import NAMES,PROJECT_ROOT
    from .metrics import GUIDE
    metadata=dict(bundle['metadata'])
    metadata.update(schema_version='1.1',created=datetime.now(timezone.utc).isoformat(),method_names=NAMES,metric_definitions=GUIDE,
        eligibility={'distribution':'At least two observed values for every psychological variable.',
          'relationship':'All 37 primary correlations defined within each repetition; anxiety excluded.',
          'variables':'Each variable uses its own available observations and scorable runs.'},
        original_prompt_templates=json.loads((PROJECT_ROOT/'prompts/methods.json').read_text()),
        prompt_adaptation='Fixed inputs are attached locally; model output schema requests only unfixed fields. Requests are independent batches.',
        variables=study['psychological_predictors'],outcomes=study['outcomes'])
    return metadata

def dataset_zip(frames,record):
    """Generation-only export has no benchmark or evaluation requirement."""
    b=io.BytesIO()
    with ZipFile(b,'w',ZIP_DEFLATED) as z:
        for (method,rep),frame in frames.items():z.writestr(f'M{method}_R{rep:04d}.csv',frame.to_csv(index=False))
        z.writestr('run_record.json',json.dumps(record,indent=2,allow_nan=False))
    return b.getvalue()
