"""Independent explicit full enumeration for the fixed plan's one-rate model.
No import of candidate coupon/partition/guard/state methods.
"""
from fractions import Fraction as F
from itertools import product
ROOTS=tuple(map(F,('1/50','3/100','1/25','11/200','3/50','2/25')))

def cells():
    for i,x in enumerate(ROOTS):
        yield (x,x)
        if i+1<len(ROOTS):yield (x,ROOTS[i+1])

def affine(a=0,b=0):return {'a':str(F(a)),'b':str(F(b))}

def expected(mode,right,lo,hi,view):
    # Each open interval lies inside one known coupon, signal and eligibility
    # regime. At singleton cells constants are the canonical normal form.
    r=(lo+hi)/2
    if mode=='fixed':aa,bb=F(0),F(5)
    elif hi<=F(3,100):aa,bb=F(0),F(3)
    elif lo>=F(3,50):aa,bb=F(0),F(6)
    else:aa,bb=F(100),F(0)
    if lo==hi:bb=aa*lo+bb;aa=F(0)
    I=aa*r+bb
    obs=['low' if hi<=F(1,25) else 'high']
    if view in ('refined','full'):obs.append(I>F(11,2))
    if view=='full':obs += [mode,right]
    interest=affine(aa,bb);zero=affine()
    ans={'interest':interest,'observation':obs,'actions':{}}
    for action in ('pay','draw'):
        ok=(I<=F(11,2)) if action=='pay' else (right and I>F(11,2) and I<=F(25,4))
        if not ok:
            ca,cb=F(0),F(11,2);ea,eb=-aa,-bb;loan=F(0);fee=F(0);due=interest;paid=zero
        else:
            loan=F(action=='draw');fee=loan/4;ca,cb=-aa,F(11,2)+loan-fee-bb
            ea,eb=-aa,-bb-fee;due=zero;paid=interest
        journal=[['interest-accrual','interest-expense','interest-payable',interest]]
        if ok and action=='draw':journal += [['facility-draw','cash','facility-debt',affine(b=1)],['facility-fee','fee-expense','cash',affine(b=F(1,4))]]
        if ok:journal += [['interest-payment','interest-payable','cash',interest]]
        liabilities=affine(b=100+loan) if ok else affine(aa,100+bb)
        ans['actions'][action]={
          'status':'accepted' if ok else 'refused',
          'balances':{'cash':affine(ca,cb),'other_assets':affine(b=F(189,2)), 'old_debt':affine(b=100),'facility_debt':affine(b=loan),'interest_payable':due,'equity':affine(ea,eb)},
          'journal':journal,'cash_flow':{'borrowing':affine(b=loan),'interest_paid':paid,'fees_paid':affine(b=fee)},
          'claim':{'due':interest,'paid':paid,'unpaid':due,'facility_available':right},
          'report':{'assets':affine(ca,cb+F(189,2)),'liabilities':liabilities,'equity':affine(ea,eb)}}
    return ans

def policies(rows):
    observations=sorted({tuple(x['observation']) for x in rows},key=repr)
    allowed=[]
    for assignments in product(('pay','draw'),repeat=len(observations)):
        p=dict(zip(observations,assignments))
        if all(x['actions'][p[tuple(x['observation'])]]['status']=='accepted' for x in rows):
            allowed.append(tuple(zip(observations,assignments)))
    return allowed
