"""Independent witness/weighted original-cycle certificate checker."""
from fractions import Fraction
from collections import Counter

def verify(variables,edges,proof):
 names=set(variables)|{'zero'}
 for e in edges:
  if set(e)!={'u','v','bound','strict'} or e['u'] not in names or e['v'] not in names or type(e['strict']) is not bool:raise ValueError('edge_shape')
  Fraction(e['bound'])
 if proof.get('kind')=='nonempty':
  if set(proof)!={'kind','values'} or set(proof['values'])!=names:raise ValueError('witness_fields')
  v={k:Fraction(x) for k,x in proof['values'].items()}
  if v['zero']!=0:raise ValueError('origin')
  for e in edges:
   a=v[e['v']]-v[e['u']];b=Fraction(e['bound'])
   if not (a<b if e['strict'] else a<=b):raise ValueError('witness_inequality')
  return 'nonempty'
 if proof.get('kind')=='empty':
  if set(proof)!={'kind','cycle'} or not proof['cycle']:raise ValueError('cycle_fields')
  coeff=Counter();total=Fraction(0);strict=False
  for i in proof['cycle']:
   if type(i) is not int or i<0 or i>=len(edges):raise ValueError('edge_index')
   e=edges[i];coeff[e['v']]+=1;coeff[e['u']]-=1;total+=Fraction(e['bound']);strict|=e['strict']
  if any(coeff.values()) or not (total<0 or total==0 and strict):raise ValueError('not_a_contradiction')
  return 'empty'
 raise ValueError('proof_kind')
