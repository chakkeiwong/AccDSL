"""Independent binary forbidden-action model; imports no enumerator/key builder."""
from itertools import product

def solve(rows,actions1,actions2,reveal):
 # Both action sets have at most two choices in this selected profile.
 assert len(actions1)<=2 and len(actions2)<=2
 variables=set();clauses=set();reach=set();domains={}
 for row in rows:
  observed=('known',row['mechanism'],row['message1']) if reveal=='first' else ('unknown',row['message1'])
  x=('first',observed);variables.add(x);domains[x]=actions1;first_action=row['a1']
  if row['status']=='refused1':clauses.add(((x,first_action),));continue
  memory=(observed,row['a1'],None if reveal=='never' else row['mechanism'],tuple(row['message2']))
  y=('second',memory);variables.add(y);domains[y]=actions2;reach.add((x,first_action,y))
  if row['status']=='refused2':clauses.add(tuple(sorted(((x,first_action),(y,row['a2'])),key=repr)))
 # Each clause forbids its listed simultaneous equalities. Unit propagation removes forbidden values.
 def enumerate_assignments(current,remaining):
  allowed={v:set(domains[v]) for v in variables if v not in current}
  while True:
   updated=False;pending=[]
   for clause in remaining:
    if any(v in current and current[v]!=a for v,a in clause):continue
    rest=[(v,a) for v,a in clause if v not in current]
    if not rest:return
    if len(rest)==1:
     v,a=rest[0];allowed[v].discard(a)
     if not allowed[v]:return
    pending.append(tuple(rest))
   for v,options in list(allowed.items()):
    if len(options)==1:current={**current,v:next(iter(options))};del allowed[v];updated=True
   remaining=pending
   if not updated:break
  missing=sorted((v for v in variables if v not in current),key=repr)
  if not missing:yield current;return
  v=missing[0]
  for a in sorted(allowed[v]):yield from enumerate_assignments({**current,v:a},remaining)
 result=set();assignments=0
 for assignment in enumerate_assignments({},sorted(clauses,key=repr)):
  assignments+=1;first={v[1]:a for v,a in assignment.items() if v[0]=='first'}
  reached={y for x,a,y in reach if assignment[x]==a};second={y[1]:assignment[y] for y in reached}
  result.add((tuple(sorted(first.items(),key=repr)),tuple(sorted(second.items(),key=repr))))
 return result,{'variables':len(variables),'forbidden_clauses':len(clauses),'total_assignments':assignments,'reachable_policies':len(result)}
