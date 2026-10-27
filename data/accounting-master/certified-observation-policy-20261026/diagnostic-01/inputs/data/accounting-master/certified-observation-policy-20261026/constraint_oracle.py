"""Independent forbidden-pair formulation and finite SAT solver.

A literal (v,b) is satisfied when Boolean decision variable v equals b.
False means pay and True draw. No candidate policy enumeration is imported.
"""

def formula(rows,view):
 clauses=set();variables=set();reaches=set()
 for r in rows:
  first=tuple(r['obs1']) if view=='refined' else (r['obs1'][0],)
  x=('first',first);a=r['a1']=='draw';variables.add(x)
  if r['status']=='refused1':clauses.add(((x,not a),));continue
  second=first+(r['a1'],bool(r['obs2'][-2]),bool(r['obs2'][-1]))
  y=('second',second);variables.add(y);reaches.add((x,a,y))
  if r['status']=='refused2':
   b=r['a2']=='draw';clauses.add(tuple(sorted(((x,not a),(y,not b)),key=repr)))
 return sorted(variables,key=repr),sorted(clauses,key=repr),reaches

def assignments(variables,clauses,current=None):
 current={} if current is None else dict(current)
 while True:
  remaining=[];units=[]
  for clause in clauses:
   if any(v in current and current[v]==b for v,b in clause):continue
   rest=[(v,b) for v,b in clause if v not in current]
   if not rest:return
   remaining.append(rest)
   if len(rest)==1:units.append(rest[0])
  if not units:break
  for v,b in units:
   if v in current and current[v]!=b:return
   current[v]=b
 missing=[v for v in variables if v not in current]
 if not missing:yield current;return
 # Branch on the first unassigned variable, retaining complete assignments.
 v=missing[0]
 for b in (False,True):yield from assignments(variables,remaining,{**current,v:b})

def solve(rows,view):
 variables,clauses,reaches=formula(rows,view);policies=set();count=0
 for solution in assignments(variables,clauses):
  count+=1;first={v[1]:'draw' if solution[v] else 'pay' for v in variables if v[0]=='first'}
  live={y for x,a,y in reaches if solution[x]==a}
  second={y[1]:'draw' if solution[y] else 'pay' for y in live}
  policies.add((tuple(sorted(first.items(),key=repr)),tuple(sorted(second.items(),key=repr))))
 return policies,{'variables':variables,'clauses':clauses,'satisfying_total_assignments':count,'reachable_policy_count':len(policies)}
