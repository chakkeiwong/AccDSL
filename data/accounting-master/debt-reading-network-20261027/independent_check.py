"""Exact Fraction checks on original temporal records, no production imports."""
from fractions import Fraction as Q
def check(definition,witness):
 obs=definition['observations'];assert set(witness)==set(obs),'witness coverage'
 values={k:Q(v) for k,v in witness.items()}
 for key,item in obs.items():
  r=item['interval'];assert r is not None,'unresolved interval'
  lo,hi=Q(r['lower']),Q(r['upper']);x=values[key]
  assert (x>=lo if r['lower_inclusive'] else x>lo),'lower bound:'+key
  assert (x<=hi if r['upper_inclusive'] else x<hi),'upper bound:'+key
 for relation in definition['relations']:
  if relation['kind']=='same_time':
   lhs=sum((Q(t['coefficient'])*values[t['observation']] for t in relation['terms']),Q(0));rhs=Q(relation['rhs'])
  else:
   assert relation['kind']=='stock_flow'
   lhs=values[relation['opening']]+sum((Q(t['coefficient'])*values[t['observation']] for t in relation['movements']),Q(0));rhs=values[relation['closing']]
  assert lhs==rhs,'relation:'+relation['id']
 return dict(complete_values=len(values),checked_intervals=len(obs),checked_equations=len(definition['relations']))
