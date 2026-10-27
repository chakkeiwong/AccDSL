"""Refine certified financial leaves with current actor observations."""
from fractions import Fraction as F
from copy import deepcopy as cp
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'exact-region-certificates-20261026'))
import regions as r
import geometry as g
import proofcheck as pc

def sign_on_atom(mode,axis,index):
 lo,hi=r.atoms()[index]
 # Atom boundaries include 11/200; fixed coupon5 never triggers.
 if mode=='fixed':return False
 if hi<=F(11,200):return False
 if lo>=F(11,200) and lo<hi:return True
 if lo>F(11,200):return True
 raise ValueError('atom_crosses_trigger')
def coverage_guard(steps,job):
 mode,right,ix,iy,a1,a2,R=job
 v={'I1':r.coupon(mode,0,ix),'I2':r.coupon(mode,1,iy),'R':[0,0,R]}
 # Second accrual has occurred; payment has not. State comes from certified path.
 before=steps[5]['before'];cash=list(map(F,r.affine(before['book']['cash'],v)))
 I2=r.coupon(mode,1,iy)
 return r.H(*(x-y for x,y in zip(I2,cash)))
def inspect_leaf(leaf,steps,job,index):
 mode,right,ix,iy,a1,a2,R=job
 lo,hi=r.atoms()[ix]
 if lo<F(1,25)<hi:raise ValueError('atom_crosses_first_signal')
 signal='low' if hi<=F(1,25) else 'high'
 o1=(signal,sign_on_atom(mode,0,ix))
 common={'job':list(job),'job_id':r.job_id(job),'leaf_index':index,'mode':mode,'right':right,'receipt':R,'a1':a1,'a2':a2,'obs1':o1}
 if leaf['kind']=='refused' and leaf['event_index']==1:
  return [{**common,'row_id':r.job_id(job)+'/'+str(index)+'/early','obs2':None,'status':'refused1','witness':leaf['witness']}],None
 if leaf['kind']=='refused' and leaf['event_index']!=5:raise ValueError('unexpected_refusal')
 h=coverage_guard(steps,job);proofs=[];rows=[]
 for covers,predicate in ((True,h),(False,r.opposite(h))):
  hs=leaf['constraints']+[predicate];proof=g.produce(hs);verdict=pc.verify(hs,proof)
  proofs.append({'covers':covers,'predicate':predicate,'proof':proof})
  if verdict=='nonempty':
   o2=o1+(a1,sign_on_atom(mode,1,iy),covers)
   rows.append({**common,'row_id':r.job_id(job)+'/'+str(index)+'/'+str(covers),'obs2':o2,'status':'accepted' if leaf['kind']=='accepted' else 'refused2','witness':proof['point']})
 return rows,{'job':list(job),'leaf_index':index,'constraints':leaf['constraints'],'coverage_guard':h,'children':proofs}
