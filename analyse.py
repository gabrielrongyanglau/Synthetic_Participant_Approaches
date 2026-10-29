"""Private command-line analysis. Generated results stay outside version control."""
import argparse
from spa.analysis import analyse_archive
from spa.verify import verify

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--output',default='private/analysis')
    p.add_argument('--original',action='store_true');p.add_argument('--verify',help='Reference Excel workbook')
    a=p.parse_args();b=analyse_archive(a.input,a.output,a.original)
    if a.verify:print(verify(b,a.verify,a.output))
    print('Complete:',a.output)
