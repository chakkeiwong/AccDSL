"""Independent finite representatives of weak orders for zero-difference clocks.

For n variables, n distinct interior positions per endpoint gap realize every
strict ordering. This checks the solver, not a substitute for its certificates.
"""
from fractions import Fraction as F
from itertools import product

def exists(variables,edges):
 points={F(0)}
 for e in edges:
  if e['u']=='zero':points.add(F(e['bound']))
  elif e['v']=='zero':points.add(-F(e['bound']))
  elif F(e['bound'])!=0:raise ValueError('oracle_nonzero_cross_difference')
 ends=sorted(points);grid=set(ends);n=len(variables)
 for a,b in zip(ends,ends[1:]):
  for i in range(1,n+1):grid.add(a+(b-a)*F(i,n+1))
 # Include exterior positions when a caller leaves a clock unbounded.
 for i in range(1,n+1):grid.add(ends[0]-i);grid.add(ends[-1]+i)
 for xs in product(sorted(grid),repeat=n):
  vals={'zero':F(0),**dict(zip(variables,xs))}
  if all((vals[e['v']]-vals[e['u']]<F(e['bound'])) if e['strict'] else (vals[e['v']]-vals[e['u']]<=F(e['bound'])) for e in edges):return True
 return False
