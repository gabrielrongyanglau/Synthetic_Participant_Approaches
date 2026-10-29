"""Bounded ZIP reads, including the historical nested archive and backslash paths."""
from pathlib import Path, PurePosixPath
from zipfile import ZipFile
import io
import re
import pandas as pd

MAX_UNCOMPRESSED=1_500_000_000
def members(z):
    out={};total=0
    for info in z.infolist():
        name=info.filename.replace('\\','/');p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or re.match(r'^[A-Za-z]:',name):raise ValueError('Unsafe ZIP path.')
        if info.is_dir():continue
        if name in out:raise ValueError('Repeated ZIP member.')
        total+=info.file_size
        if total>MAX_UNCOMPRESSED or info.file_size>500_000_000:raise ValueError('Archive exceeds the extraction allowance.')
        out[name]=info
    return out

def archive(path_or_bytes):
    z=ZipFile(io.BytesIO(path_or_bytes) if isinstance(path_or_bytes,bytes) else path_or_bytes)
    ms=members(z)
    nested=[n for n in ms if n.endswith('MIDUS_Analysis_Upload.zip')]
    if nested:
        if len(nested)!=1:raise ValueError('Expected one nested analysis archive.')
        data=z.read(ms[nested[0]]);z.close();z=ZipFile(io.BytesIO(data));ms=members(z)
    return z,ms

def read_csv(data):
    if isinstance(data,bytes):data=io.BytesIO(data)
    # pandas otherwise silently renames duplicate CSV headers.
    import csv
    if hasattr(data,'read'):
        content=data.read();data=io.BytesIO(content) if isinstance(content,bytes) else io.StringIO(content)
        first=next(csv.reader(io.StringIO(content.decode('utf-8-sig') if isinstance(content,bytes) else content)))
    else:
        with open(data,encoding='utf-8-sig',newline='') as f:first=next(csv.reader(f))
    if len(first)!=len(set(first)):raise ValueError('Repeated CSV headers.')
    return pd.read_csv(data,float_precision='round_trip',na_values=['null'])

def dataset_source(path):
    """Return reference, [(method, run, lazy reader)], source fingerprint inputs."""
    if Path(path).is_dir():
        root=Path(path);fs=list(root.rglob('*'));human=[p for p in fs if p.name=='MIDUS2_3_linked_cleaned.csv']
        datasets=[p for p in fs if re.fullmatch(r'M[1-8]_R\d{4}\.csv',p.name)]
        if len(human)!=1:raise ValueError('Expected one human reference CSV.')
        entries=[(int(p.name[1]),int(p.stem.split('_R')[1]),lambda p=p:read_csv(p)) for p in datasets]
        return read_csv(human[0]),sorted(entries,key=lambda a:a[:2]),None
    z,ms=archive(path)
    human=[n for n in ms if n.endswith('MIDUS2_3_linked_cleaned.csv')]
    if len(human)!=1:z.close();raise ValueError('Expected one human reference CSV.')
    entries=[]
    for n in ms:
        match=re.fullmatch(r'M([1-8])_R(\d{4})\.csv',PurePosixPath(n).name)
        if match:entries.append((int(match[1]),int(match[2]),lambda n=n:read_csv(z.read(ms[n]))))
    return read_csv(z.read(ms[human[0]])),sorted(entries,key=lambda a:a[:2]),z
