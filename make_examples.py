"""Build only invented data, deterministically. Does not read the private MIDUS data."""
from pathlib import Path
import json
from spa.study import load_study,PROJECT_ROOT
from spa.simulation import invent_reference,local_demo
from spa.analysis import analyse,save_bundle
from spa.store import atomic_json

def main():
    study=load_study();root=PROJECT_ROOT/'data/examples';root.mkdir(parents=True,exist_ok=True)
    ref=invent_reference(study);ref.to_csv(root/'reference.csv',index=False)
    frames={}
    for m in range(1,9):
        frame,context=local_demo(ref,study,m,100,20261029,1)
        frame.to_csv(root/f'M{m}_R0001.csv',index=False);atomic_json(root/f'M{m}_inputs.json',context);frames[m,1]=frame
    b=analyse([(m,r,lambda f=f:f) for (m,r),f in frames.items()],ref,study)
    b['metadata'].update(source='Invented demonstration data — not LLM outputs or proposal findings',reference='Invented demonstration reference',
        settings={'n':100,'repetitions':1,'seed':20261029},algorithm='Local resampling, perturbation and illustrative outcome model.')
    save_bundle(b,root/'analysis');print('Invented examples ready.')

if __name__=='__main__':main()
