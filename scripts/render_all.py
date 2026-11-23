import json,sys,os
sys.path.insert(0,'scripts')
from multiprocessing import Pool
from render import render
L=json.load(open('data/levels.json'))
def job(x):
    g=x['global_id']
    render(x,f'docs/img/{g:04d}.webp')
    render(x,f'docs/thumb/{g:04d}.webp',long_side=240,thumb=True)
    return g
if __name__=='__main__':
    with Pool(8) as p: r=p.map(job,L,chunksize=8)
    print(len(r))
