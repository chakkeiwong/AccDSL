"""Bounded synthetic one-date rational-affine reference; no probability model."""
from dataclasses import dataclass, asdict
from fractions import Fraction as F
import hashlib, json

@dataclass(frozen=True)
class Aff:
    a: F = F(0)
    b: F = F(0)
    def __call__(self, r): return self.a*r+self.b
    def __add__(self, other):
        other=other if isinstance(other,Aff) else Aff(b=F(other))
        return Aff(self.a+other.a,self.b+other.b)
    __radd__=__add__
    def __neg__(self): return Aff(-self.a,-self.b)
    def __sub__(self,other): return self+-as_aff(other)
    def __rsub__(self,other): return as_aff(other)+-self

def as_aff(x): return x if isinstance(x,Aff) else Aff(b=F(x))

@dataclass(frozen=True)
class Cell:
    lo: F
    hi: F
    point: bool=False
    def __post_init__(self):
        if (self.point and self.lo != self.hi) or (not self.point and self.lo >= self.hi):
            raise ValueError('invalid cell')
    def contains(self,x): return x==self.lo if self.point else self.lo<x<self.hi
    def sample(self): return (self.lo+self.hi)/2
    def key(self): return (str(self.lo),str(self.hi),self.point)

@dataclass(frozen=True)
class Scope:
    domain: tuple=(F(1,50),F(2,25))
    modes: tuple=(('fixed',False),('fixed',True),('floating',False),('floating',True))
    floor: F=F(3,100)
    cap: F=F(3,50)
    trigger: F=F(11,2)
    signal_cut: F=F(1,25)
    observation: str='coarse'
    horizon: str='one-date-after-accrual'
    query: str='full-state-feasible-policies-cash-bounds'
    actions: tuple=('pay','draw')
    clause_version: str='synthetic-facility-1'
    precision: str='rational-unrounded'
    def validate(self):
        if not (self.domain[0]<self.domain[1] and self.floor<self.cap): raise ValueError('domain')
        if self.observation not in ('coarse','refined','full'): raise ValueError('observation')
        if self.horizon!='one-date-after-accrual' or self.actions!=('pay','draw'): raise ValueError('unsupported policy/horizon')
        if self.precision!='rational-unrounded': raise ValueError('unsupported precision')
        if any(m not in ('fixed','floating') or type(c)!=bool for m,c in self.modes): raise ValueError('mode')
    def fingerprint(self): return hashlib.sha256(json.dumps(encode(asdict(self)),sort_keys=True).encode()).hexdigest()

def partition(lo,hi,roots):
    points=sorted({lo,hi,*[r for r in roots if lo<=r<=hi]})
    cells=[]
    for k,p in enumerate(points):
        cells.append(Cell(p,p,True))
        if k+1<len(points): cells.append(Cell(p,points[k+1]))
    return cells

def image(f,c):
    x,y=f(c.lo),f(c.hi)
    return dict(inf=min(x,y),sup=max(x,y),inf_attained=c.point or f.a==0,sup_attained=c.point or f.a==0)

def truth(f,c,op):
    """Tri-valued universal truth on a point/open interval."""
    q=image(f,c);lo,hi=q['inf'],q['sup']
    if op=='>':
        if lo>0 or (lo==0 and not q['inf_attained']): return True
        if hi<=0: return False
    elif op=='>=':
        if lo>=0:return True
        if hi<0 or (hi==0 and not q['sup_attained']):return False
    elif op=='<=': return truth(-f,c,'>=')
    else: raise ValueError(op)
    return None

def coupon(mode,c,s):
    if mode=='fixed':return Aff(b=F(5))
    x=c.sample()
    if x<=s.floor:return Aff(b=100*s.floor)
    if x>=s.cap:return Aff(b=100*s.cap)
    return Aff(a=F(100))

def observation(mode,right,c,s,I):
    z=truth(Aff(a=F(1),b=-s.signal_cut),c,'<=')
    if z is None: raise ValueError('unsplit observation')
    ans=('low' if z else 'high',)
    if s.observation in ('refined','full'):
        t=truth(I-s.trigger,c,'>')
        if t is None:raise ValueError('unsplit trigger')
        ans+=(t,)
    if s.observation=='full':ans+=(mode,right)
    return ans

def state(I,action,right,c,s):
    a=as_aff; zero=a(0)
    loan=zero;cash=a(F(11,2));equity=-I;due=I;fee=zero
    journals=[('interest-accrual','interest-expense','interest-payable',I)]
    allowed=truth(cash-I,c,'>=') if action=='pay' else (right and truth(I-s.trigger,c,'>') and truth(cash+1-F(1,4)-I,c,'>='))
    if allowed is None: raise ValueError('unsplit action guard')
    if allowed:
        if action=='draw':
            loan=a(1);fee=a(F(1,4));cash=cash+loan-fee;equity=equity-fee
            journals.extend([('facility-draw','cash','facility-debt',loan),('facility-fee','fee-expense','cash',fee)])
        cash=cash-I;due=zero
        journals.append(('interest-payment','interest-payable','cash',I))
    balances={'cash':cash,'other_assets':a(F(189,2)),'old_debt':a(100),'facility_debt':loan,'interest_payable':due,'equity':equity}
    return {'status':'accepted' if allowed else 'refused','balances':balances,'journal':tuple(journals),
            'cash_flow':{'borrowing':loan,'interest_paid':I if allowed else zero,'fees_paid':fee},
            'claim':{'due':I,'paid':I if allowed else zero,'unpaid':due,'facility_available':right},
            'report':{'assets':cash+F(189,2),'liabilities':a(100)+loan+due,'equity':equity}}

def nodes_for(mode,right,s):
    roots=[s.signal_cut]
    if mode=='floating':roots += [s.floor,s.cap]
    base=partition(*s.domain,roots)
    for c in base:
        I=coupon(mode,c,s)
        for f in (I-s.trigger,Aff(b=F(11,2))-I,Aff(b=F(25,4))-I):
            if f.a:
                root=-f.b/f.a
                if c.lo<=root<=c.hi:roots.append(root)
    return partition(*s.domain,roots)

class Shared:
    def __init__(self,s):
        s.validate();self.scope=s;self.stamp=s.fingerprint();self.nodes={};self.records=[]
        for mode,right in s.modes:
            for c in nodes_for(mode,right,s):
                self.records.append({'mode':mode,'right':right,'cell':c,'node':None})
    def resolve(self,record):
        if record['node'] is None:
            mode,right,c=record['mode'],record['right'],record['cell'];s=self.scope
            I=coupon(mode,c,s);obs=observation(mode,right,c,s,I)
            node={'interest':I,'observation':obs,'actions':{a:state(I,a,right,c,s) for a in s.actions}}
            nid=hashlib.sha256(json.dumps(encode(node),sort_keys=True).encode()).hexdigest()
            self.nodes.setdefault(nid,node);record['node']=nid
        return self.nodes[record['node']]
    def check_scope(self,s):
        if s.fingerprint()!=self.stamp:raise ValueError('stale scope')
    def evaluate(self,mode,right,r,s):
        self.check_scope(s)
        xs=[q for q in self.records if q['mode']==mode and q['right']==right and q['cell'].contains(r)]
        if len(xs)!=1:raise ValueError('not exactly one retained region')
        return specialize(self.resolve(xs[0]),r)
    def materialize(self,budget):
        if type(budget)!=int or budget<0:raise ValueError('budget')
        resolved=self.records[:budget];pending=self.records[budget:]
        for record in resolved:self.resolve(record)
        # Partition metadata is constructed eagerly; transitions are evaluated on
        # demand. No general complexity or runtime improvement is inferred.
        lo=min(F(5),100*self.scope.floor);hi=max(F(5),100*self.scope.cap)
        return {'resolved':resolved,'unresolved':pending,'complete':not pending,
                'interest_outer':{'inf':lo,'sup':hi},'guarantee':'outer bounds; unresolved states retained'}

def specialize(x,r):
    if isinstance(x,Aff):return x(r)
    if isinstance(x,dict):return {k:specialize(v,r) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return tuple(specialize(v,r) for v in x)
    return x

def encode(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,Aff):return {'a':str(x.a),'b':str(x.b)}
    if isinstance(x,Cell):return {'lo':str(x.lo),'hi':str(x.hi),'point':x.point}
    if isinstance(x,dict):return {str(k):encode(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [encode(v) for v in x]
    return x

def guard_margin(center,error,threshold,op):
    if error<0:raise ValueError('negative bound')
    lo,hi=center-error,center+error
    if op=='>':return True if lo>threshold else False if hi<=threshold else None
    if op=='<=':return True if hi<=threshold else False if lo>threshold else None
    raise ValueError(op)
