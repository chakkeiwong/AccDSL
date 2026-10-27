"""Independent arithmetic proof checking; never calls the elimination producer."""
from fractions import Fraction as Q

def verify(hs,proof):
 if proof.get('kind')=='witness':
  if set(proof)!={'kind','point'} or len(proof['point'])!=2:raise ValueError('witness_shape')
  x,y=map(Q,proof['point'])
  for h in hs:
   a,b,c=map(Q,h['f']);v=a*x+b*y+c
   if not (v<0 if h['strict'] else v<=0):raise ValueError('invalid_witness')
  return 'nonempty'
 if proof.get('kind')=='empty':
  if set(proof)!={'kind','weights'} or not proof['weights']:raise ValueError('certificate_shape')
  total=[Q(0),Q(0),Q(0)];has_strict=False
  for key,value in proof['weights'].items():
   if str(int(key))!=key or not 0<=int(key)<len(hs):raise ValueError('multiplier_index')
   w=Q(value)
   if w<=0:raise ValueError('nonpositive_multiplier')
   h=hs[int(key)];total=[a+w*Q(b) for a,b in zip(total,h['f'])]
   has_strict=has_strict or h['strict']
  if total[:2]!=[0,0]:raise ValueError('variables_not_eliminated')
  if not (total[2]>0 or (total[2]==0 and has_strict)):raise ValueError('no_contradiction')
  return 'empty'
 raise ValueError('unknown_proof')
