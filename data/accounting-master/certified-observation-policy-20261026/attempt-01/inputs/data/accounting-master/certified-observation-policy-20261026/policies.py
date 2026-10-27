"""Robust policies on reachable information cells; no probabilities or ranking."""
from itertools import product

def key1(row,view):return tuple(row['obs1']) if view=='refined' else tuple(row['obs1'][:1])
def key2(row,view):return key1(row,view)+(row['a1'],)+tuple(row['obs2'][-2:])
def canonical(first,second):return (tuple(sorted(first.items(),key=repr)),tuple(sorted(second.items(),key=repr)))
def enumerate_policies(rows,view):
 signals=sorted({key1(r,view) for r in rows},key=repr);out=set();decisions=[]
 for actions in product(('pay','draw'),repeat=len(signals)):
  first=dict(zip(signals,actions));selected=[r for r in rows if first[key1(r,view)]==r['a1']]
  early=[r for r in selected if r['status']=='refused1']
  if early:
   decisions.append({'first':list(first.items()),'status':'refused1','witness_row':early[0]['row_id']});continue
  allowed={}
  for row in selected:
   k=key2(row,view);allowed.setdefault(k,{'pay','draw'})
   if row['status']!='accepted':allowed[k].discard(row['a2'])
  empty=[k for k,v in allowed.items() if not v]
  if empty:
   witnesses=[r['row_id'] for r in selected if key2(r,view)==empty[0] and r['status']!='accepted']
   decisions.append({'first':list(first.items()),'status':'no_second_action','cell':empty[0],'witness_rows':witnesses});continue
  keys=sorted(allowed,key=repr)
  for actions2 in product(*(sorted(allowed[k]) for k in keys)):out.add(canonical(first,dict(zip(keys,actions2))))
  decisions.append({'first':list(first.items()),'status':'feasible','allowed':[(k,sorted(allowed[k])) for k in keys]})
 return out,decisions
