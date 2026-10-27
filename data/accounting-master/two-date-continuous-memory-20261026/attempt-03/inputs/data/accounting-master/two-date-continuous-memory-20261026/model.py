"""Exact bounded two-rate fixture. Region arithmetic is two-dimensional only."""
from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations,product

@dataclass(frozen=True)
class A:
    x:F=F(0);y:F=F(0);c:F=F(0)
    def __call__(self,p):return self.x*p[0]+self.y*p[1]+self.c
    def __add__(self,b):
        b=aff(b);return A(self.x+b.x,self.y+b.y,self.c+b.c)
    __radd__=__add__
    def __neg__(self):return A(-self.x,-self.y,-self.c)
    def __sub__(self,b):return self+-aff(b)
    def __rsub__(self,b):return aff(b)+-self

def aff(b):return b if isinstance(b,A) else A(c=F(b))
@dataclass(frozen=True)
class H:
    f:A
    strict:bool=False  # f <= 0 or f < 0
    def opposite(self):return H(-self.f,not self.strict)

class Region:
    def __init__(self,hs):self.hs=tuple(hs);self._vertices=None
    def add(self,*hs):return Region(self.hs+tuple(hs))
    def vertices(self):
        if self._vertices is None:
            vs=set()
            for a,b in combinations(self.hs,2):
                f,g=a.f,b.f;det=f.x*g.y-g.x*f.y
                if not det:continue
                p=((f.y*g.c-g.y*f.c)/det,(f.c*g.x-g.c*f.x)/det)
                if all(h.f(p)<=0 for h in self.hs):vs.add(p)
            self._vertices=tuple(sorted(vs))
        return self._vertices
    def witness(self):
        v=self.vertices()
        if not v:return None
        p=(sum(q[0] for q in v)/len(v),sum(q[1] for q in v)/len(v))
        return p if all(h.f(p)<0 if h.strict else h.f(p)<=0 for h in self.hs) else None
    def feasible(self):return self.witness() is not None
    def split(self,h):
        return [(flag,q) for flag,q in [(True,self.add(h)),(False,self.add(h.opposite()))] if q.feasible()]
    def bounds(self,f):
        if not self.feasible():raise ValueError('empty')
        vals=[f(p) for p in self.vertices()];lo,hi=min(vals),max(vals)
        return {'inf':lo,'sup':hi,'inf_attained':self.add(H(f-lo),H(lo-f)).feasible(),'sup_attained':self.add(H(f-hi),H(hi-f)).feasible()}
    def subset(self,other):return all(not self.add(h.opposite()).feasible() for h in other.hs)
    def equal(self,other):return self.subset(other) and other.subset(self)

def interval(axis,lo,hi):
    x=A(x=1) if axis==0 else A(y=1)
    return [H(lo-x,lo!=hi),H(x-hi,lo!=hi)]
def rect(xlo,xhi,ylo,yhi):return Region(interval(0,xlo,xhi)+interval(1,ylo,yhi))
ROOTS=tuple(map(F,('1/50','3/100','1/25','11/200','3/50','2/25')))
def atoms():
    for i,p in enumerate(ROOTS):
        yield p,p
        if i+1<len(ROOTS):yield p,ROOTS[i+1]
def coupon(mode,axis,lo,hi):
    if mode=='fixed':return aff(5)
    mid=(lo+hi)/2
    if mid<=F(3,100):return aff(3)
    if mid>=F(3,50):return aff(6)
    return A(x=100) if axis==0 else A(y=100)

def opening():
    return {'cash':aff(F(11,2)),'other_assets':aff(F(189,2)),'old_debt':aff(100),'facility_debt':aff(0),'interest_payable':aff(0),'equity':aff(0)}
def post(b,dr,cr,amt):
    b=dict(b);asset={'cash','other_assets'}
    b[dr]=b[dr]+amt if dr in asset else b[dr]-amt
    b[cr]=b[cr]-amt if cr in asset else b[cr]+amt
    return b

def accrued(b,j,I,t):
    b=post(b,'equity','interest_payable',I)
    return b,j+[(t,'interest-accrual','equity','interest-payable',I)]
def transition(b,j,I,action,used,t):
    b=dict(b);j=list(j)
    if action=='draw':
        b=post(b,'cash','facility_debt',aff(1));j.append((t,'facility-draw','cash','facility-debt',aff(1)))
        b=post(b,'equity','cash',aff(F(1,4)));j.append((t,'facility-fee','equity','cash',aff(F(1,4))));used=True
    b=post(b,'interest_payable','cash',I);j.append((t,'coupon-payment','interest-payable','cash',I))
    return b,j,used

def action_split(region,b,I,action,right,used):
    if action=='draw' and (not right or used):return [(False,region)]
    predicates=[H(I-b['cash'])] if action=='pay' else [H(F(11,2)-I,True),H(I-b['cash']-F(3,4))]
    pending=[region];rejected=[]
    for h in predicates:
        new=[]
        for r in pending:
            for yes,s in r.split(h):(new if yes else rejected).append(s)
        pending=new
    return [(True,r) for r in pending]+[(False,r) for r in rejected]

def obs1(I,lo,hi,view):
    o=('low' if hi<=F(1,25) else 'high',)
    # Coupon sign is constant on each atom.
    if view=='refined':o+=(I(((lo+hi)/2,F(1,20)))>F(11,2),)
    return o

def output(b,j,used,right,status,t,I1,I2):
    return {'status':status,'date':t,'balances':b,'journal':tuple(j),'facility_used':used,'facility_right':right,
            'due_history':(I1,) if t==1 else (I1,I2),'unpaid':b['interest_payable'],
            'report':{'assets':b['cash']+b['other_assets'],'liabilities':b['old_debt']+b['facility_debt']+b['interest_payable'],'equity':b['equity']}}

def traces(mode,right,xatom,yatom,receipt,view):
    region=rect(*xatom,*yatom);I1=coupon(mode,0,*xatom);I2=coupon(mode,1,*yatom)
    o1=obs1(I1,*xatom,view);b,j=accrued(opening(),[],I1,1)
    for a1 in ('pay','draw'):
      for yes,r1 in action_split(region,b,I1,a1,right,False):
        if not yes:
          yield {'region':r1,'obs1':o1,'a1':a1,'obs2':None,'a2':None,'state':output(b,j,False,right,'refused1',1,I1,I2)};continue
        b1,j1,used=transition(b,j,I1,a1,False,1)
        # Receipt, then repayment, then accrual. Receipt covers the facility
        # repayment in this explicitly bounded receipt/interest profile.
        b2=post(b1,'cash','equity',aff(receipt));j2=j1+[(2,'operating-receipt','cash','equity',aff(receipt))]
        if used:
          b2=post(b2,'facility_debt','cash',aff(1));j2.append((2,'facility-repayment','facility_debt','cash',aff(1)))
        b2,j2=accrued(b2,j2,I2,2)
        # The actor observes the amount-coverage predicate, not the hidden right.
        trigger=I2((F(1,20),(yatom[0]+yatom[1])/2))>F(11,2)
        for covers,r2 in r1.split(H(I2-b2['cash'])):
          o2=o1+(a1,trigger,covers)
          for a2 in ('pay','draw'):
            for accepts,r3 in action_split(r2,b2,I2,a2,right,used):
              if accepts:bb,jj,uu=transition(b2,j2,I2,a2,used,2)
              else:bb,jj,uu=b2,j2,used
              yield {'region':r3,'obs1':o1,'a1':a1,'obs2':o2,'a2':a2,'state':output(bb,jj,uu,right,'accepted' if accepts else 'refused2',2,I1,I2)}

def enc(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,A):return {'x':str(x.x),'y':str(x.y),'c':str(x.c)}
    if isinstance(x,H):return {'f':enc(x.f),'strict':x.strict}
    if isinstance(x,Region):return {'constraints':enc(x.hs),'vertices':enc(x.vertices()),'witness':enc(x.witness())}
    if isinstance(x,dict):return {str(k):enc(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [enc(v) for v in x]
    return x
