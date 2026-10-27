"""Conditional symbolic composition of accepted known-valued method forms."""
from copy import deepcopy as cp
from fractions import Fraction as F

def lin(d=None,c=0):return ('linear',tuple(sorted((k,str(F(v))) for k,v in (d or {}).items() if F(v))),str(F(c)))
def plus(a,b):
 if a[0]!=b[0] or a[0]!='linear':raise ValueError('nonaffine_add')
 d={k:F(v) for k,v in a[1]}
 for k,v in b[1]:d[k]=d.get(k,F(0))+F(v)
 return lin(d,F(a[2])+F(b[2]))
def scaled(a,k):return lin({s:F(v)*k for s,v in a[1]},F(a[2])*k)
def value(form,env):
 op=form[0]
 if op=='linear':
  out=lin(c=form[2])
  for key,k in form[1]:
   if key not in env:raise ValueError('unbound:'+key)
   out=plus(out,scaled(env[key],F(k)))
  return out
 if op=='symbol':
  if form[2] not in env:raise ValueError('unbound:'+form[2])
  return env[form[2]]
 if op=='literal':return form
 if op in ('eq','le','lt'):
  a=value(form[1],env)
  if len(form)==2:
   if a[0]!='linear':raise ValueError('comparison_form')
   if a[1]:return (op,a)
   n=F(a[2]);return ('literal','boolean',n==0 if op=='eq' else n<=0 if op=='le' else n<0)
  z=value(form[2],env)
  if a[0]==z[0]=='literal':
   if a[1]!=z[1]:raise ValueError('comparison_type')
   return ('literal','boolean',a[2]==z[2] if op=='eq' else a[2]<=z[2] if op=='le' else a[2]<z[2])
  return (op,a,z)
 if op in ('all','any'):
  xs=[value(x,env) for x in form[1]]
  if all(x[0]=='literal' and x[1]=='boolean' for x in xs):return ('literal','boolean',(all if op=='all' else any)(x[2] for x in xs))
  return (op,tuple(sorted(xs,key=repr)))
 if op=='not':
  x=value(form[1],env)
  return ('literal','boolean',not x[2]) if x[0]=='literal' and x[1]=='boolean' else ('not',x)
 raise ValueError('unsupported:'+str(op))

def initial(mode,right):
 roles=('cash','other_assets','old_debt','facility_debt','interest_payable','capital','income','interest_expense','fee_expense')
 book={k:lin(c={'cash':'11/2','other_assets':'189/2','old_debt':-100}.get(k,0)) for k in roles}
 memory={k:('literal','text',v) for k,v in dict(mode=mode,phase='opening',action1='none',action2='none',source='synthetic-source-v1',clause='once-only-v1').items()}
 memory.update(right=('literal','boolean',right),used=('literal','boolean',False))
 memory.update({k:lin() for k in ('due1','due2','paid1','paid2')})
 return {'book':book,'memory':memory,'flows':[]}

def environment(state,key,mode,right):
 env={**{'account/'+k:v for k,v in state['book'].items()},**{'memory/'+k:v for k,v in state['memory'].items()}}
 env.update({'parameter/I1':lin({'I1':1}),'parameter/I2':lin({'I2':1}),'parameter/R':lin({'R':1}),
   'parameter/mode':('literal','text',mode),'parameter/right':('literal','boolean',right),
   'event/event_date':('literal','date','2027-06-30' if key[-1]=='1' else '2027-12-31')})
 if key.startswith('accrue') or key=='receipt2':env['event/amount']=lin({'R' if key=='receipt2' else 'I'+key[-1]:1})
 return env

def sequence(forms,mode,right,a1,a2):
 keys=('accrue1',a1+'1','receipt2','repay2','accrue2',a2+'2')
 state=initial(mode,right);steps=[]
 for key in keys:
  m=forms[key];before=cp(state);env=environment(before,key,mode,right)
  pre={k:value(v,env) for k,v in m['pre'].items()}
  # All effects read the same pre-state. Atomicity forbids sequential rebinding.
  after=cp(before)
  for account,expr in m['postings'].items():after['book'][account]=plus(before['book'][account],value(expr,env))
  for name,expr in m['memory'].items():after['memory'][name]=value(expr,env)
  after['flows']+= [(key,name,activity,origin,value(expr,env)) for name,(activity,origin,expr) in sorted(m['flows'].items())]
  post={k:value(v,environment(after,key,mode,right)) for k,v in m['post'].items()}
  steps.append({'key':key,'before':before,'pre':pre,'after':after,'post':post});state=after
 return steps

def branch(steps,stop):
 """Store guards without feasibility inference; postconditions join acceptance."""
 count=6 if stop is None else stop
 if count not in (1,5,6):raise ValueError('selected_refusal_index')
 successes=[{'key':s['key'],'pre':s['pre'],'post':s['post']} for s in steps[:count]]
 return {'status':'accepted' if stop is None else 'refused1' if stop==1 else 'refused2',
  'current':cp(steps[count-1]['after']), 'accepted_conditions':successes,
  'refusal':None if stop is None else {'key':steps[count]['key'],'not_all':{'pre':steps[count]['pre'],'post':steps[count]['post']}},
  'remaining':[s['key'] for s in steps[count:]]}
