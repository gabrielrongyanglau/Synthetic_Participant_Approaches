"""Convert the verified R package's CSV outputs into an Explorer analysis bundle."""
import argparse
from pathlib import Path
import pandas as pd
from spa.analysis import save_bundle
from spa.metrics import summarise
from spa.io import read_csv

def convert(source,output):
    root=Path(source);runs=read_csv(root/'per_run_metrics.csv')
    variables=read_csv(root/'by_variable_results.csv')
    human=read_csv(root/'human_reference_statistics.csv').rename(columns={'human_n':'n','human_mean':'mean','human_sd':'sd',
        'human_r_midus2':'midus2_r','human_r_midus3':'midus3_r'})
    summary,comparisons=summarise(runs)
    counts=runs.groupby('method').size()
    if set(counts.index)!=set(range(1,9)) or not counts.eq(1000).all():raise ValueError('Expected the verified original R export: 1,000 runs per method.')
    if human['n'].max()!=2709:raise ValueError('Human statistics do not match the full-reference R export.')
    b=dict(runs=runs,variables=variables,human=human,summary=summary,comparisons=comparisons,
        metadata={'human_n':2709,'datasets':len(runs),'original_protocol':True,'source':'Original MIDUS study — imported R outputs',
        'reference':'Full 2,709-person human reference','ci':'Mean ± 1.96 × sample SD / sqrt(scorable runs)',
        'fixed_human_reference':True,'imported_from':'Verified R package CSV schema'})
    save_bundle(b,output);return b

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    convert(a.input,a.output);print('R analysis bundle saved:',a.output)
