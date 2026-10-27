"""Synthetic guarded coupon methods over unchanged common typed engines."""
from pathlib import Path
from fractions import Fraction as F
from copy import deepcopy as cp
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import declared_company_program_v2 as rt
import declared_financing_methods_v1 as h
TEXT={'kind':'text','context':{}}
DATE={'kind':'date','context':{}}
BOOL=rt.core.BOOL
CLASSES={'cash':'asset','other_assets':'asset','old_debt':'liability','facility_debt':'liability','interest_payable':'liability','capital':'equity','income':'income','interest_expense':'expense','fee_expense':'expense'}
SCOPE='Supplied capped-coupon and once-only facility; no actual source or accounting admission.'
DATES={1:'2027-06-30',2:'2027-12-31'}
def fmt(x):return h.fmt(F(x))
def logical(op,*args):return {'op':op,'args':list(args)}
def not_(x):return {'op':'not','arg':x}
def coupon(mode,r):
 r=F(r)
 if mode not in ('fixed','floating') or not F(1,50)<=r<=F(2,25):raise ValueError('outside_declared_family')
 return F(5) if mode=='fixed' else 100*min(F(3,50),max(F(3,100),r))
def build(mode='floating',right=True,r1='3/50',r2='3/50',receipt='7',a1='draw',a2='pay',chart='alpha'):
 if type(right)!=bool or F(receipt) not in (6,7) or a1 not in ('pay','draw') or a2 not in ('pay','draw'):raise ValueError('scope')
 values={'I1':coupon(mode,r1),'I2':coupon(mode,r2),'R':F(receipt)}
 mapping={k:k if chart=='alpha' else 'acct'+str(90-i*7) for i,k in enumerate(CLASSES)}
 context={'entity':'Guarded-'+chart,'book':'legal-'+chart,'currency':'USD','case_id':'selected-two-date-'+chart,'mode':'synthetic'}
 book={'profile':rt.engine.BOOK,'context':context,'period':{'start':'2027-01-01','end_exclusive':'2028-01-01'},'date':'2027-01-01','accounts':{mapping[k]:{'classification':v} for k,v in CLASSES.items()},'balances':{mapping[k]:fmt({'cash':F(11,2),'other_assets':F(189,2),'old_debt':-100}.get(k,0)) for k in CLASSES},'cash_account':mapping['cash'],'seen':[],'flows':[]}
 money=rt.engine.money_type(book)
 types={'mode':TEXT,'right':BOOL,'used':BOOL,'phase':TEXT,'action1':TEXT,'action2':TEXT,'source':TEXT,'clause':TEXT,**{x:money for x in ('due1','due2','paid1','paid2')}}
 mem={'mode':mode,'right':right,'used':False,'phase':'opening','action1':'none','action2':'none','source':'synthetic-source-v1','clause':'once-only-v1',**{x:'0/1' for x in ('due1','due2','paid1','paid2')}}
 shape=h.record({k:{'type':'boolean'} if t['kind']=='boolean' else h.scalar(t['kind']) for k,t in types.items()})
 book.update(memory=mem,memory_schema=rt.digest(shape),memory_types={'/'+k:v for k,v in types.items()})
 schemas={rt.digest(shape):shape};entries={}
 zero=h.constant(money,'0/1');one=h.constant(money,'1/1');fee=h.constant(money,'1/4')
 const=lambda typ,x:h.constant(typ,x)
 eq=lambda x,y:h.binary('eq',x,y)
 neg=lambda x:h.binary('sub',zero,x)
 knownphase={'accrue1':('opening','due1',1),'pay1':('due1','settled1',1),'draw1':('due1','settled1',1),'receipt2':('settled1','receipt2',2),'repay2':('receipt2','repaid2',2),'accrue2':('repaid2','due2',2),'pay2':('due2','settled2',2),'draw2':('due2','settled2',2)}
 for key,(before,after,t) in knownphase.items():
  ident='synthetic.guarded-memory.'+key
  bindings={k:(typ,h.memory('/'+k)) for k,typ in types.items()}
  bindings.update({k:(money,h.account(k)) for k in ('cash','facility_debt','interest_payable')})
  bindings['event_date']=(DATE,h.event('event_date'))
  pre=[];post=[]
  def row(dest,name,expr,deps):dest.append((name,expr,deps,'invalid'))
  row(pre,'phase',eq(h.ref('phase'),const(TEXT,before)),['phase'])
  row(pre,'dated',eq(h.ref('event_date'),const(DATE,DATES[t])),['event_date'])
  for label,value in [('mode',mode),('source','synthetic-source-v1'),('clause','once-only-v1')]:
   row(pre,label,eq(h.ref(label),const(TEXT,value)),[label])
  used_expr=logical('any',eq(h.ref('action1'),const(TEXT,'draw')),eq(h.ref('action2'),const(TEXT,'draw')))
  for target in (pre,post):
   row(target,'used_matches_history',eq(h.ref('used'),used_expr),['used','action1','action2'])
   due=h.binary('add',h.binary('sub',h.ref('due1'),h.ref('paid1')),h.binary('sub',h.ref('due2'),h.ref('paid2')))
   row(target,'payable_matches_history',eq(neg(h.ref('interest_payable')),due),['interest_payable','due1','paid1','due2','paid2'])
   row(target,'cash_nonnegative',h.binary('le',zero,h.ref('cash')),['cash'])
  row(post,'phase',eq(h.ref('phase'),const(TEXT,after)),['phase'])
  numeric={};evtypes={};postings=[];flows=[];changes={'phase':{'kind':'literal','value':after}}
  def bind_numeric(name,source):
   numeric[name]=(money,source);bindings[name]=(money,source)
  def add(role,expression,requires):postings.append({'id':role,'account':role,'expression':expression,'requires':requires})
  def flow(name,activity,expression,requires):flows.append({'id':name,'origin':name,'activity':activity,'expression':expression,'requires':requires})
  def store(field,name):changes[field]={'kind':'read','source':'inputs','pointer':'/'+name}
  if key.startswith('accrue'):
   evtypes['amount']=money;bind_numeric('amount',h.event('amount'))
   row(pre,'coupon_range',logical('all',h.binary('le',const(money,'3/1'),h.ref('amount')),h.binary('le',h.ref('amount'),const(money,'6/1'))),['amount'])
   # The wrapper binds the coupon formula to rate/mode; the registry additionally
   # binds the amount to the declared selected request, not caller discretion.
   row(pre,'selected_coupon',eq(h.ref('amount'),const(money,fmt(values['I'+str(t)]))),['amount'])
   add('interest_expense',h.ref('amount'),['amount']);add('interest_payable',neg(h.ref('amount')),['amount'])
   store('due'+str(t),'amount')
  elif key=='receipt2':
   evtypes['amount']=money;bind_numeric('amount',h.event('amount'))
   row(pre,'selected_receipt',eq(h.ref('amount'),const(money,fmt(values['R']))),['amount'])
   add('cash',h.ref('amount'),['amount']);add('income',neg(h.ref('amount')),['amount'])
   flow('operating_receipt','operating',h.ref('amount'),['amount'])
  elif key=='repay2':
   bind_numeric('loan',h.account('facility_debt'))
   row(pre,'repayment_cash',h.binary('le',neg(h.ref('loan')),h.ref('cash')),['loan','cash'])
   add('cash',h.ref('loan'),['loan']);add('facility_debt',neg(h.ref('loan')),['loan'])
   flow('facility_repayment','financing',h.ref('loan'),['loan'])
  else:
   bind_numeric('coupon',h.memory('/due'+str(t)))
   row(pre,'amount_due',eq(h.ref('coupon'),neg(h.ref('interest_payable'))),['coupon','interest_payable'])
   store('paid'+str(t),'coupon');changes['action'+str(t)]={'kind':'literal','value':key[:-1]}
   if key.startswith('draw'):
    row(pre,'right',h.ref('right'),['right']);row(pre,'unused',not_(h.ref('used')),['used'])
    row(pre,'strict_trigger',h.binary('lt',const(money,'11/2'),h.ref('coupon')),['coupon'])
    row(pre,'cash_after_draw',h.binary('le',h.ref('coupon'),h.binary('add',h.ref('cash'),const(money,'3/4'))),['coupon','cash'])
    add('cash',h.binary('sub',const(money,'3/4'),h.ref('coupon')),['coupon']);add('facility_debt',neg(one),[])
    add('fee_expense',fee,[]);changes['used']={'kind':'literal','value':True}
    flow('facility_draw','financing',one,[]);flow('facility_fee','operating',neg(fee),[])
   else:
    row(pre,'cash_to_pay',h.binary('le',h.ref('coupon'),h.ref('cash')),['coupon','cash'])
    add('cash',neg(h.ref('coupon')),['coupon'])
   add('interest_payable',h.ref('coupon'),['coupon']);flow('interest_payment','operating',neg(h.ref('coupon')),['coupon'])
  if key not in ('receipt2','repay2'):
   row(pre,'facility_zero',eq(h.ref('facility_debt'),zero),['facility_debt'])
  else:
   debt_ok=logical('any',logical('all',eq(h.ref('action1'),const(TEXT,'draw')),eq(h.ref('facility_debt'),const(money,'-1/1'))),logical('all',eq(h.ref('action1'),const(TEXT,'pay')),eq(h.ref('facility_debt'),zero)))
   row(pre,'facility_matches_first_order',debt_ok,['action1','facility_debt'])
  prekeys=sorted({k for _,_,ds,_ in pre for k in ds});postkeys=sorted({k for _,_,ds,_ in post for k in ds})
  meminputs={x['pointer'][1:] for x in changes.values() if x['kind']=='read'}
  ishape=h.record({k:h.scalar('rational') for k in sorted(meminputs)})
  local={**schemas,rt.digest(ishape):ishape};schemas.update(local)
  method={'profile':rt.engine.METHOD,'id':ident,'version':'1','context':cp(context),'account_map':cp(mapping),
   'preconditions':{'manifest':h.conditions(ident,{k:bindings[k][0] for k in prekeys},pre),'bindings':{k:bindings[k][1] for k in prekeys}},
   'postconditions':{'manifest':h.conditions(ident,{k:bindings[k][0] for k in postkeys},post),'bindings':{k:bindings[k][1] for k in postkeys}},
   'monetary':{'definition':{'profile':rt.engine.monetary.PROFILE,'method_id':ident,'version':'1','inputs':{k:h.declaration(typ,k) for k,(typ,_) in numeric.items()},'calculations':[],'accounts':{k:money for k in CLASSES},'cash_account':'cash','postings':postings,'flows':flows},'bindings':{k:b for k,(_,b) in numeric.items()}},
   'memory':{'definition':{'profile':rt.engine.memory.PROFILE,'state_schema':book['memory_schema'],'input_schema':rt.digest(ishape),'operations':[{'id':'write.'+k,'op':'replace','path':[k],'value':v} for k,v in changes.items()]},'input_bindings':{k:{'kind':'monetary_input','name':k} for k in meminputs}},
   'residual_prerequisites':[SCOPE]}
  entries[key]={'method_sha256':rt.digest(method),'method':method,'schemas':local,'account_classes':cp(CLASSES),'event_inputs':evtypes,'metadata_bindings':{'event_date':'date'},'clock':{'kind':'direct_event_date'}}
 commands=[]
 for key in ('accrue1',a1+'1','receipt2','repay2','accrue2',a2+'2'):
  inputs={}
  if key in ('accrue1','accrue2','receipt2'):
   amount=values['R' if key=='receipt2' else 'I'+key[-1]]
   inputs={'amount':{'type':money,'value':rt.engine.known(fmt(amount)),'provenance':SCOPE}}
  commands.append({'kind':'event','method_key':key,'event':{'id':key,'date':DATES[int(key[-1])],'inputs':inputs}})
 mappingdef={'profile':rt.reports.MAP,'context':cp(context),'lines':[{'id':k,'label':k,'classification':v,'accounts':[mapping[k]]} for k,v in CLASSES.items()]}
 body={'profile':rt.PROFILE,'name':'selected-two-date-memory','opening':book,'schemas':schemas,'registry':{'profile':rt.methods.REGISTRY,'context':cp(context),'entries':entries},'mapping':mappingdef,'commands':commands}
 return body,mapping
def report(body,current):
 return rt.reports.report(rt.reports.request(body['opening'],current,body['schemas'],body['mapping']))
