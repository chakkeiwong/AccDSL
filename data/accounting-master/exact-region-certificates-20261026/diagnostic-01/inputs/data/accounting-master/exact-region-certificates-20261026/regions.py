"""Exact certificate tree for a fixed selected rate-domain/order obligation."""
from fractions import Fraction as F
from copy import deepcopy as cp
from itertools import product
import hashlib,json
import geometry
import proofcheck
ROOTS=tuple(map(F,('1/50','3/100','1/25','11/200','3/50','2/25')))
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def atoms():
 out=[]
 for i,p in enumerate(ROOTS):
  out.append((p,p))
  if i+1<len(ROOTS):out.append((p,ROOTS[i+1]))
 return out
def H(a,b,c,strict=False):return {'f':[str(F(a)),str(F(b)),str(F(c))],'strict':strict}
def domain(ix,iy):
 lo,hi=atoms()[ix];bot,top=atoms()[iy]
 return [H(-1,0,lo,lo!=hi),H(1,0,-hi,lo!=hi),H(0,-1,bot,bot!=top),H(0,1,-top,bot!=top)]
def coupon(mode,axis,index):
 lo,hi=atoms()[index]
 if mode=='fixed':return [F(0),F(0),F(5)]
 if hi<=F(3,100):return [F(0),F(0),F(3)]
 if lo>=F(3,50):return [F(0),F(0),F(6)]
 return [F(100) if axis==0 else F(0),F(100) if axis==1 else F(0),F(0)]
def affine(form,variables):
 if form[0]!='linear':raise ValueError('nonlinear')
 out=[F(0),F(0),F(form[2])]
 for k,v in form[1]:out=[x+F(v)*y for x,y in zip(out,variables[k])]
 return [str(x) for x in out]
def predicates(form,variables):
 op=form[0]
 if op=='literal' and form[1]=='boolean':return [bool(form[2])]
 if op=='all':return [g for x in form[1] for g in predicates(x,variables)]
 if op in ('le','lt') and len(form)==2:
  a=affine(form[1],variables)
  if F(a[0])==F(a[1])==0:return [F(a[2])<0 if op=='lt' else F(a[2])<=0]
  return [{'f':a,'strict':op=='lt'}]
 if op=='eq' and len(form)==2:
  row=affine(form[1],variables)
  if F(row[0])==F(row[1])==0:return [F(row[2])==0]
  return [{'f':row,'strict':False},{'f':[str(-F(x)) for x in row],'strict':False}]
 raise ValueError('unsupported_symbolic_predicate:'+repr(form))
def instructions(steps,job):
 mode,right,ix,iy,a1,a2,R=job
 v={'I1':coupon(mode,0,ix),'I2':coupon(mode,1,iy),'R':[F(0),F(0),F(R)]}
 result=[]
 for i,step in enumerate(steps):
  for phase in ('pre','post'):
   for name,p in step[phase].items():
    for j,h in enumerate(predicates(p,v)):result.append({'event_index':i,'phase':phase,'guard':name,'part':j,'predicate':h})
 return result

def opposite(h):return {'f':[str(-F(x)) for x in h['f']],'strict':not h['strict']}
def build(hs,ins,cursor=0):
 if cursor<len(ins) and ins[cursor]['predicate'] is True:
  return {'cursor':cursor,'instruction':cp(ins[cursor]),'kind':'constant_true','child':build(hs,ins,cursor+1)}
 proof=geometry.produce(hs);verdict=proofcheck.verify(hs,proof)
 if verdict=='empty':return {'kind':'empty','proof':proof}
 if cursor==len(ins):return {'kind':'accepted','proof':proof}
 pred=ins[cursor]['predicate'];base={'cursor':cursor,'instruction':cp(ins[cursor])}
 if type(pred)==bool:
  if pred:return {**base,'kind':'constant_true','child':build(hs,ins,cursor+1)}
  return {**base,'kind':'refused','event_index':ins[cursor]['event_index'],'proof':proof}
 yes=hs+[pred];no=hs+[opposite(pred)]
 np=geometry.produce(no);nv=proofcheck.verify(no,np)
 negative={'kind':'empty','proof':np} if nv=='empty' else {'kind':'refused','event_index':ins[cursor]['event_index'],'proof':np}
 return {**base,'kind':'split','yes':build(yes,ins,cursor+1),'no':negative}

def verify_tree(hs,ins,tree,cursor=0,leaves=None):
 if leaves is None:leaves=[]
 kind=tree.get('kind')
 if kind=='empty':
  if set(tree)!={'kind','proof'}:raise ValueError('empty_fields')
  if proofcheck.verify(hs,tree['proof'])!='empty':raise ValueError('empty_without_proof')
  leaves.append({'kind':'empty'});return leaves
 if cursor==len(ins):
  if set(tree)!={'kind','proof'} or kind!='accepted' or proofcheck.verify(hs,tree['proof'])!='nonempty':raise ValueError('completion_without_witness')
  leaves.append({'kind':'accepted','witness':tree['proof']['point'],'constraints':hs});return leaves
 item=ins[cursor];pred=item['predicate']
 if tree.get('cursor')!=cursor or tree.get('instruction')!=item:raise ValueError('instruction_binding')
 if type(pred)==bool:
  if pred:
   if set(tree)!={'kind','cursor','instruction','child'} or kind!='constant_true':raise ValueError('constant_true_branch')
   return verify_tree(hs,ins,tree['child'],cursor+1,leaves)
  if set(tree)!={'kind','cursor','instruction','event_index','proof'} or kind!='refused' or tree['event_index']!=item['event_index']:raise ValueError('constant_false_branch')
  if proofcheck.verify(hs,tree['proof'])!='nonempty':raise ValueError('refusal_witness')
  leaves.append({'kind':'refused','event_index':item['event_index'],'witness':tree['proof']['point'],'constraints':hs});return leaves
 if set(tree)!={'kind','cursor','instruction','yes','no'} or kind!='split':raise ValueError('missing_split_child')
 verify_tree(hs+[pred],ins,tree['yes'],cursor+1,leaves)
 n=tree['no'];nh=hs+[opposite(pred)]
 if n.get('kind')=='empty':
  if set(n)!={'kind','proof'} or proofcheck.verify(nh,n['proof'])!='empty':raise ValueError('negative_empty_proof')
  leaves.append({'kind':'empty'})
 else:
  if set(n)!={'kind','event_index','proof'} or n.get('kind')!='refused' or n['event_index']!=item['event_index']:raise ValueError('negative_refusal')
  if proofcheck.verify(nh,n['proof'])!='nonempty':raise ValueError('negative_refusal_witness')
  leaves.append({'kind':'refused','event_index':item['event_index'],'witness':n['proof']['point'],'constraints':nh})
 return leaves

def roster():return list(product(('fixed','floating'),(False,True),range(11),range(11),('pay','draw'),('pay','draw'),(6,7)))
def job_id(job):return '|'.join(map(str,job))
