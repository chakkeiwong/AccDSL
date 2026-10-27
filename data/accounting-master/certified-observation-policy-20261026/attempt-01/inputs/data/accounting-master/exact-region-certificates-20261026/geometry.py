"""Two-variable rational elimination producer. Consumers must verify proofs."""
from fractions import Fraction as F

def qrow(h,i):return ([F(x) for x in h['f']],bool(h['strict']),{i:F(1)})
def merge(a,b):
 out=dict(a)
 for k,v in b.items():out[k]=out.get(k,F(0))+v
 return {k:v for k,v in out.items() if v}
def scale(row,k):
 a,s,w=row
 return ([x*k for x in a],s and k>0,{i:v*k for i,v in w.items()})
def unique(rows):
 out={}
 for row in rows:
  a,s,w=row;k=tuple(a)
  if k not in out or (s and not out[k][1]):out[k]=row
 return list(out.values())
def eliminate(rows,axis):
 plus=[r for r in rows if r[0][axis]>0];minus=[r for r in rows if r[0][axis]<0]
 out=[r for r in rows if r[0][axis]==0]
 for p in plus:
  for m in minus:
   a=scale(p,1/p[0][axis]);b=scale(m,-1/m[0][axis])
   out.append(([x+y for x,y in zip(a[0],b[0])],a[1] or b[1],merge(a[2],b[2])))
 return unique(out)
def contradiction(rows):
 for a,s,w in rows:
  if a[0]==a[1]==0 and (a[2]>0 or (a[2]==0 and s)):return w
 return None
def scalar_point(rows,axis,fixed=None):
 low=[];high=[]
 for a,s,_ in rows:
  k=a[axis];c=a[2]+(a[1-axis]*fixed if fixed is not None else 0)
  if k>0:high.append((-c/k,s))
  elif k<0:low.append((-c/k,s))
  elif c>0 or (c==0 and s):raise ValueError('inconsistent_back_substitution')
 lo=max((x for x,_ in low),default=None);hi=min((x for x,_ in high),default=None)
 if lo is None and hi is None:return F(0)
 if lo is None:return hi-1
 if hi is None:return lo+1
 if lo>hi:raise ValueError('empty_interval_without_certificate')
 if lo==hi:
  if any(s for x,s in low+high if x==lo):raise ValueError('strict_empty_interval')
  return lo
 return (lo+hi)/2

def produce(hs):
 rows=unique([qrow(h,i) for i,h in enumerate(hs)])
 stages=[rows,eliminate(rows,0)]
 stages.append(eliminate(stages[1],1))
 for stage in stages:
  w=contradiction(stage)
  if w is not None:return {'kind':'empty','weights':{str(i):str(v) for i,v in sorted(w.items())}}
 y=scalar_point(stages[1],1);x=scalar_point(rows,0,y)
 return {'kind':'witness','point':[str(x),str(y)]}
