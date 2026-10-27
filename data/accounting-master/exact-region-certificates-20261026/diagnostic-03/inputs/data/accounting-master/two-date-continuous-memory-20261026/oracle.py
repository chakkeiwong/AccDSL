"""Closed forms authored independently of posting and transition functions."""
from fractions import Fraction as F
from model import A,H,Region,aff
# Shared affine/region value types only; no candidate financial method imported.
def oracle_interest(mode,axis,lo,hi):
    if mode=='fixed':return aff(5)
    if hi<=F(3,100):return aff(3)
    if lo>=F(3,50):return aff(6)
    if lo==hi:return aff(100*lo)
    return A(x=100) if axis==0 else A(y=100)
def guards(I1,I2,a1,a2,right,R):
    if a1=='draw' and not right:return None
    first=[H(I1-F(11,2))] if a1=='pay' else [H(F(11,2)-I1,True),H(I1-F(25,4))]
    cash=aff(F(11,2)+R)-I1-(F(1,4) if a1=='draw' else 0)
    if a2=='pay':return first+[H(I2-cash)]
    if not right or a1=='draw':return None
    return first+[H(F(11,2)-I2,True),H(I2-cash-F(3,4))]

def expected(mode,right,xatom,yatom,R,a1,a2,status):
    I1=oracle_interest(mode,0,*xatom);I2=oracle_interest(mode,1,*yatom);z=aff(0)
    journal=[(1,'interest-accrual','equity','interest_payable',I1)]
    used=False
    if status=='refused1':cash=aff(F(11,2));debt=z;due=I1;eq=-I1;t=1
    else:
        first_draw=a1=='draw';used=first_draw
        if first_draw:journal += [(1,'facility-draw','cash','facility_debt',aff(1)),(1,'facility-fee','equity','cash',aff(F(1,4)))]
        journal += [(1,'coupon-payment','interest_payable','cash',I1),(2,'operating-receipt','cash','equity',aff(R))]
        if first_draw:journal += [(2,'facility-repayment','facility_debt','cash',aff(1))]
        journal += [(2,'interest-accrual','equity','interest_payable',I2)]
        cash=aff(F(11,2)+R)-I1-(F(1,4) if first_draw else 0)
        eq=aff(R)-I1-I2-(F(1,4) if first_draw else 0);debt=z;due=I2;t=2
        if status=='accepted':
            if a2=='draw':
                used=True;cash=cash+F(3,4);eq=eq-F(1,4);debt=aff(1)
                journal += [(2,'facility-draw','cash','facility_debt',aff(1)),(2,'facility-fee','equity','cash',aff(F(1,4)))]
            cash=cash-I2;due=z;journal += [(2,'coupon-payment','interest_payable','cash',I2)]
    b={'cash':cash,'other_assets':aff(F(189,2)),'old_debt':aff(100),'facility_debt':debt,'interest_payable':due,'equity':eq}
    return {'status':status,'date':t,'balances':b,'journal':tuple(journal),'facility_used':used,'facility_right':right,
            'due_history':(I1,) if t==1 else (I1,I2),'unpaid':due,
            'report':{'assets':cash+F(189,2),'liabilities':aff(100)+debt+due,'equity':eq}}
