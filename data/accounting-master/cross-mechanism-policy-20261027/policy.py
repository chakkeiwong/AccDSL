"""Finite robust policies sharing only declared actor messages and own-action memory."""
from itertools import product

def need(ok,msg):
 if not ok:raise ValueError(msg)
def canonical(first,second):return tuple(sorted(first.items(),key=repr)),tuple(sorted(second.items(),key=repr))
def keys(row,reveal):
 first=('known',row['mechanism'],row['message1']) if reveal=='first' else ('unknown',row['message1'])
 second=(first,row['a1'],row['mechanism'] if reveal in ('first','second') else None,tuple(row['message2'])) if row['message2'] is not None else None
 return first,second

def validate(rows,actions1,actions2,reveal):
 need(reveal in ('first','second','never'),'revelation_regime')
 need(type(rows) is list and rows,'nonempty_row_domain');need(len({r['id'] for r in rows})==len(rows),'unique_support_rows')
 need(len(set(actions1))==len(actions1)>0 and len(set(actions2))==len(actions2)>0,'action_domains')
 for r in rows:
  need(set(r)=={'id','support','mechanism','a1','a2','message1','message2','status'},'row_fields')
  need(isinstance(r['id'],str) and isinstance(r['support'],str) and isinstance(r['mechanism'],str),'row_identities')
  need(r['a1'] in actions1 and r['a2'] in actions2 and isinstance(r['message1'],str),'typed_actions_messages')
  need(r['status'] in ('accepted','refused1','refused2'),'row_status')
  need((r['message2'] is None)==(r['status']=='refused1'),'second_message_reachability')
  if r['message2'] is not None:need(type(r['message2']) is list and all(type(x) in (str,bool,int) for x in r['message2']),'second_message_tokens')

 # Complete action tables are required per observable cell; missing actions are not implicitly safe.
 first_cells={keys(r,reveal)[0] for r in rows}
 for k in first_cells:need({r['a1'] for r in rows if keys(r,reveal)[0]==k}==set(actions1),'first_action_coverage')
 second_cells={keys(r,reveal)[1] for r in rows if r['status']!='refused1'}
 for k in second_cells:need({r['a2'] for r in rows if r['status']!='refused1' and keys(r,reveal)[1]==k}==set(actions2),'second_action_coverage')

def solve(rows,actions1,actions2,reveal):
 validate(rows,actions1,actions2,reveal);cells=sorted({keys(r,reveal)[0] for r in rows},key=repr);result=set()
 for choices in product(actions1,repeat=len(cells)):
  first=dict(zip(cells,choices));chosen=[r for r in rows if first[keys(r,reveal)[0]]==r['a1']]
  if any(r['status']=='refused1' for r in chosen):continue
  allowed={}
  for r in chosen:
   k=keys(r,reveal)[1];allowed.setdefault(k,set(actions2))
   if r['status']=='refused2':allowed[k].discard(r['a2'])
  if any(not x for x in allowed.values()):continue
  ks=sorted(allowed,key=repr)
  for second in product(*(sorted(allowed[k]) for k in ks)):result.add(canonical(first,dict(zip(ks,second))))
 return result
