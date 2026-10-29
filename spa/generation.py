"""Pure schema and record validation. No storage, credentials or network calls."""
import pandas as pd
from .study import selected_fields,OUTCOMES,clean_frame
from .labels import field_map

def output_schema(study,ids,fixed=None):
    mapping=field_map(study);props={'participant_id':{'type':'integer','enum':ids}}
    for f in selected_fields(study):
        if fixed and f in fixed[0]:continue
        spec=study['variables'][study['outcomes'].get(f,f)];nullable=f not in OUTCOMES
        typ='integer' if spec['kind'] in ('category','integer') else 'number'
        p={'type':[typ,'null'] if nullable else typ}
        if spec['kind']=='category':p['enum']=list(spec['categories'])+([None] if nullable else [])
        else:p.update(minimum=spec['minimum'],maximum=spec['maximum'])
        props[mapping[f]]=p
    return {'type':'object','properties':{'participants':{'type':'array','minItems':len(ids),'maxItems':len(ids),
       'items':{'type':'object','properties':props,'required':list(props),'additionalProperties':False}}},
       'required':['participants'],'additionalProperties':False}

def parse_records(data,study,ids,fixed=None):
    if set(data)!={'participants'} or not isinstance(data['participants'],list):raise ValueError('Incorrect response structure.')
    reverse={v:k for k,v in field_map(study).items()};fields=set(selected_fields(study))
    expected={'participant_id'}|{k for k,v in reverse.items() if not (fixed and v in fixed[0])}
    rows=data['participants']
    if len(rows)!=len(ids):raise ValueError('Incorrect participant count.')
    output=[]
    for i,(row,pid) in enumerate(zip(rows,ids)):
        if not isinstance(row,dict) or set(row)!=expected or type(row['participant_id']) is not int or row['participant_id']!=pid:raise ValueError('Incorrect fields or participant IDs.')
        merged={reverse.get(k,k):v for k,v in row.items()}
        if any(v is not None and type(v) not in (int,float) for k,v in row.items() if k!='participant_id'):raise ValueError('Scores must be numbers or null.')
        if fixed:merged.update(fixed[i])
        output.append(merged)
    frame=clean_frame(pd.DataFrame(output),study,expected_n=len(ids))
    for f in fields:
        if not (fixed and f in fixed[0]):frame[f]=frame[f].round(4)
    return frame

def response_text(response):
    return ''.join(c.get('text','') for item in response.get('output',[]) for c in item.get('content',[]) if c.get('type')=='output_text')

