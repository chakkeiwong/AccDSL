"""Independent target equations; no candidate/template/engine imports.

Credit balances are negative. A comparison stores left minus right. The inputs
are arbitrary known typed values, subject to the retained preconditions.
"""
from fractions import Fraction

def L(coeff=None, constant=0):
    return ('linear', tuple(sorted((k, str(Fraction(v))) for k,v in (coeff or {}).items() if Fraction(v))), str(Fraction(constant)))
def S(kind, name): return ('symbol', kind, name)
def V(kind, value): return ('literal', kind, value)
def B(op, *xs): return (op, tuple(sorted(xs, key=repr)))
def text_eq(field, value): return ('eq', S('text', 'memory/'+field), V('text', value))
def cmp(op, coeff=None, constant=0): return (op, L(coeff,constant))

def forms():
    phases={
      'accrue1':('opening','due1',1), 'pay1':('due1','settled1',1),
      'draw1':('due1','settled1',1), 'receipt2':('settled1','receipt2',2),
      'repay2':('receipt2','repaid2',2), 'accrue2':('repaid2','due2',2),
      'pay2':('due2','settled2',2), 'draw2':('due2','settled2',2)}
    invariant={
      'used_matches_history':('eq', S('boolean','memory/used'),
         B('any',text_eq('action1','draw'),text_eq('action2','draw'))),
      'payable_matches_history':cmp('eq',{'account/interest_payable':-1,
         'memory/due1':-1,'memory/paid1':1,'memory/due2':-1,'memory/paid2':1}),
      'cash_nonnegative':cmp('le',{'account/cash':-1})}
    result={}
    for key,(before,after,date) in phases.items():
        t=str(date); due='memory/due'+t
        pre={**invariant,'phase':text_eq('phase',before),
          'dated':('eq',S('date','event/event_date'),V('date','2027-06-30' if date==1 else '2027-12-31')),
          'mode':('eq',S('text','memory/mode'),S('text','parameter/mode')),
          'source':text_eq('source','synthetic-source-v1'),
          'clause':text_eq('clause','once-only-v1')}
        post={**invariant,'phase':text_eq('phase',after)}
        posts={};flows={};memory={'phase':V('text',after)}
        if key.startswith('accrue'):
            pre['coupon_range']=B('all',cmp('le',{'event/amount':-1},3),cmp('le',{'event/amount':1},-6))
            pre['selected_coupon']=cmp('eq',{'event/amount':1,'parameter/I'+t:-1})
            posts={'interest_expense':L({'event/amount':1}), 'interest_payable':L({'event/amount':-1})}
            memory['due'+t]=L({'event/amount':1})
        elif key=='receipt2':
            pre['selected_receipt']=cmp('eq',{'event/amount':1,'parameter/R':-1})
            posts={'cash':L({'event/amount':1}),'income':L({'event/amount':-1})}
            flows['operating_receipt']=('operating','operating_receipt',L({'event/amount':1}))
        elif key=='repay2':
            pre['repayment_cash']=cmp('le',{'account/facility_debt':-1,'account/cash':-1})
            posts={'cash':L({'account/facility_debt':1}),'facility_debt':L({'account/facility_debt':-1})}
            flows['facility_repayment']=('financing','facility_repayment',L({'account/facility_debt':1}))
        else:
            pre['amount_due']=cmp('eq',{due:1,'account/interest_payable':1})
            memory['paid'+t]=L({due:1});memory['action'+t]=V('text',key[:-1])
            posts['interest_payable']=L({due:1})
            flows['interest_payment']=('operating','interest_payment',L({due:-1}))
            if key.startswith('draw'):
                pre.update(right=S('boolean','memory/right'),unused=('not',S('boolean','memory/used')),
                  strict_trigger=cmp('lt',{due:-1},'11/2'),
                  cash_after_draw=cmp('le',{due:1,'account/cash':-1},'-3/4'))
                posts.update(cash=L({due:-1},'3/4'),facility_debt=L(constant=-1),fee_expense=L(constant='1/4'))
                flows.update(facility_draw=('financing','facility_draw',L(constant=1)),
                  facility_fee=('operating','facility_fee',L(constant='-1/4')))
                memory['used']=V('boolean',True)
            else:
                pre['cash_to_pay']=cmp('le',{due:1,'account/cash':-1})
                posts['cash']=L({due:-1})
        if key in ('receipt2','repay2'):
            pre['facility_matches_first_order']=B('any',
              B('all',text_eq('action1','draw'),cmp('eq',{'account/facility_debt':1},1)),
              B('all',text_eq('action1','pay'),cmp('eq',{'account/facility_debt':1})))
        else: pre['facility_zero']=cmp('eq',{'account/facility_debt':1})
        result[key]={'pre':pre,'post':post,'postings':posts,'flows':flows,'memory':memory}
    return result

# Independent required binding population, including declarations' unused inputs.
def bindings(key,part):
    t=key[-1]
    inv=['action1','action2','used','due1','due2','paid1','paid2','phase']
    out={x:{'kind':'memory','pointer':'/'+x} for x in inv}
    out.update({x:{'kind':'account','role':x} for x in ['cash','interest_payable']})
    if part=='post':return out
    numeric=({'amount':{'kind':'event','name':'amount'}} if key.startswith('accrue') or key=='receipt2'
      else {'loan':{'kind':'account','role':'facility_debt'}} if key=='repay2'
      else {'coupon':{'kind':'memory','pointer':'/due'+t}})
    if part=='monetary':return numeric
    out.update({x:{'kind':'memory','pointer':'/'+x} for x in ['mode','source','clause']})
    out.update(event_date={'kind':'event','name':'event_date'},facility_debt={'kind':'account','role':'facility_debt'})
    out.update(numeric)
    if key.startswith('draw'):out['right']={'kind':'memory','pointer':'/right'}
    return out
