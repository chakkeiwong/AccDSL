"""Exact finite counterexample; no accounting selector is admitted."""
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import sys
UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
INPUTS={'A':(F(975),F(1000)),'B':(F(10),F(20)),'C':(F(10),F(199,10))}
EXPECTED={
 '':('90','0','18','72','178'), 'A':('1065','965/2','233/2','466','1178'),
 'B':('100','0','20','80','198'), 'C':('100','0','20','80','1979/10'),
 'AB':('1075','975/2','235/2','470','1198'), 'AC':('1075','975/2','235/2','470','11979/10'),
 'BC':('110','5','21','84','2179/10'), 'ABC':('1085','985/2','237/2','474','12179/10')}

def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def read(name):return json.loads((UNIT/name).read_text())
def write(name,data):
 with (UNIT/name).open('x') as f:json.dump(data,f,indent=2);f.write(chr(10))
def key(s):return ''.join(sorted(s))
def world(s,q=F(1,2),n=F(178)):
 interest=sum((INPUTS[i][0] for i in s),F(0));x=90+interest
 bonus=q*max(x-100,0);tax=(x-bonus)/5;N=x-bonus-tax
 D=n+sum((INPUTS[i][1] for i in s),F(0))
 assert D>0
 return {'pretax':x,'bonus':bonus,'tax':tax,'N':N,'D':D,'r':N/D}
def ratio_increment(s,i,q):return (world(s|{i},q)['N']-world(s,q)['N'])/INPUTS[i][1]
def trace(mode,q=F(1,2),order=None):
 accepted=set();remaining=set(INPUTS);steps=[]
 fixed=sorted(INPUTS,key=lambda i:(ratio_increment(set(),i,q),i)) if order is None else list(order)
 while remaining:
  ranking=sorted(remaining,key=lambda i:(ratio_increment(accepted,i,q),i)) if mode=='marginal' else [i for i in fixed if i in remaining]
  ratios={i:ratio_increment(accepted,i,q) for i in ranking}
  i=ranking[0];current=world(accepted,q);trial=world(accepted|{i},q)
  cross=trial['N']*current['D']-current['N']*trial['D'];take=cross<0
  steps.append({'before':key(accepted),'remaining_order':ranking,'marginal_ratios':{j:str(ratios[j]) for j in ranking},
                'trial':i,'current_ratio':str(current['r']),'trial_ratio':str(trial['r']),
                'cross_difference':str(cross),'accepted':take})
  if take:accepted.add(i)
  remaining.remove(i)
 return {'mode':mode,'accepted':key(accepted),'ratio':str(world(accepted,q)['r']),'steps':steps}

def calculations():
 checks=0;worlds={}
 for length in range(4):
  for s in itertools.combinations(INPUTS,length):
   w=world(set(s));k=key(s)
   for f,e in zip(('pretax','bonus','tax','N','D'),EXPECTED[k]):assert w[f]==F(e),(k,f);checks+=1
   assert w['pretax']-w['bonus']-w['tax']==w['N'];checks+=1
   I=sum((INPUTS[i][0] for i in s),F(0));assert w['N']==(72 if not s else 76+F(2,5)*I);checks+=1
   worlds[k]={f:str(v) for f,v in w.items()}
 marginal=trace('marginal');fixed=trace('fixed');alternate=trace('fixed',order='BCA')
 assert marginal['accepted']==fixed['accepted']=='ABC';checks+=1
 assert alternate['accepted']=='BC';checks+=1
 assert marginal['ratio']=='4740/12179';checks+=1
 assert alternate['ratio']=='840/2179';checks+=1
 for t in (marginal,fixed,alternate):
  for step in t['steps']:
   assert F(step['cross_difference'])!=0;checks+=1
   assert (F(step['trial_ratio'])<F(step['current_ratio']))==step['accepted'];checks+=1
 for step in marginal['steps']:
  rank=[F(step['marginal_ratios'][i]) for i in step['remaining_order']]
  assert all(a<b for a,b in zip(rank,rank[1:]));checks+=1
 gap=world(set('ABC'))['r']-world(set('BC'))['r'];assert gap==F(98100,26538041);checks+=1
 removals={i:str(world(set('ABC'))['r']-world(set('ABC')-{i})['r']) for i in INPUTS}
 assert F(removals['A'])>0 and all(F(removals[i])<0 for i in 'BC');checks+=1
 minimum=min(F(w['r']) for w in worlds.values());assert [k for k,w in worlds.items() if F(w['r'])==minimum]==['BC'];checks+=1
 additive={name:trace(name,F(0)) for name in ('marginal','fixed')}
 assert all(t['accepted']=='BC' and t['ratio']=='880/2179' for t in additive.values());checks+=1
 for t in additive.values():
  for step in t['steps']:
   assert F(step['cross_difference'])!=0;checks+=1
 # Exact analytic conditions for first A and removable final A.
 n=F(178)
 assert n<F(36000,197);checks+=1
 # BC ratio below A's final-context increment 390/1000 = 39/100.
 assert F(840,2179)<F(39,100)<F(197,500)<F(36,89);checks+=1
 assert F(39,100)*(n+F(399,10))>84;checks+=1
 # Derive correct final-removal threshold: n > 8400/39 - 399/10.
 deletion_threshold=F(8400,39)-F(399,10)
 assert deletion_threshold==F(22813,130) and n>deletion_threshold;checks+=1
 # Check the cross-multiplication identity in every admissible one-step world.
 for length in range(3):
  for s0 in itertools.combinations(INPUTS,length):
   s=set(s0);w=world(s)
   for i in INPUTS.keys()-s:
    t=world(s|{i});a=t['N']-w['N'];b=INPUTS[i][1]
    assert t['r']-w['r']==(a*w['D']-w['N']*b)/(w['D']*(w['D']+b));checks+=1
 rejections=[]
 for label,bad in [('numerator',F(475)),('denominator',F(1218)),('bonus',F(492)),('tax',F(118))]:
  actual=world(set('ABC'))[{'numerator':'N','denominator':'D','bonus':'bonus','tax':'tax'}[label]]
  assert actual!=bad;rejections.append(label)
 assert trace('marginal')['accepted']!='BC';rejections.append('pretend_marginal_deletes_A')
 assert trace('fixed',order='BCA')['steps'][0]['trial']!='A';rejections.append('pretend_alternate_initial_ranking')
 return {'worlds':worlds,'marginal':marginal,'fixed':fixed,'alternate_prescribed_BCA':alternate,
         'final_deletion_improvement':removals,'ABC_minus_BC':str(gap),'subset_minimum':'BC',
         'subset_minimum_accounting_admitted':False,'additive_control':additive,
         'analytic_A_initial_threshold':str(F(36000,197)),
         'analytic_A_deletion_threshold':str(deletion_threshold),
         'explicit_assertions':checks,'rejected_corruptions':rejections}

def check():
 d=calculations();assert d==read('calculations.json')
 for b in read('source-ledger.json')['bindings']:assert bind(ROOT/b['path'])==b
 assert read('source-ledger.json')['new_acquisitions']==0
 return {'status':'exact marginal final-context instability checked','worlds':8,'traces':5,
         'assertions':d['explicit_assertions'],'rejected_corruptions':d['rejected_corruptions'],
         'marginal_final':d['marginal']['ratio'],'deleting_A':d['alternate_prescribed_BCA']['ratio'],
         'strict_difference':d['ABC_minus_BC'],'accounting_selectors_admitted':0,'whole_rows_closed':0}

if __name__=='__main__':
 if sys.argv[1:]==['--calculate']:
  d=calculations();write('calculations.json',d)
  prior=ROOT/'data/accounting-master/r03-eps-order-discriminator-20261018'
  write('source-ledger.json',{'new_acquisitions':0,'status':'exact project derivation, no new accounting interpretation',
                            'bindings':[bind(prior/f) for f in ('source-boundary.md','derivation.md','result.md','checks.json','completion.json')],
                            'source_role':'Prior historical paragraphs and P80 boundary retained; no current-law or issuer applicability conclusion.'})
  print(json.dumps({'assertions':d['explicit_assertions'],'marginal':d['marginal'],'alternate':d['alternate_prescribed_BCA'],'gap':d['ABC_minus_BC'],'additive':d['additive_control']}))
 else:print(json.dumps(check()))
