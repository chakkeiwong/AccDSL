"""Rational enclosures; no floating point or unlabelled rounding."""
from dataclasses import dataclass
from datetime import date
from fractions import Fraction as Q
from functools import lru_cache
from math import gcd

@dataclass(frozen=True)
class I:
    lo: Q
    hi: Q
    def __post_init__(self):
        object.__setattr__(self,'lo',Q(self.lo));object.__setattr__(self,'hi',Q(self.hi))
        if self.lo>self.hi:raise ValueError('interval_order')
    @classmethod
    def point(cls,x):return cls(Q(x),Q(x))
    def __add__(self,o):
        o=as_i(o);return I(self.lo+o.lo,self.hi+o.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,o):return self+-as_i(o)
    def __rsub__(self,o):return as_i(o)+-self
    def __mul__(self,o):
        o=as_i(o);v=[a*b for a in (self.lo,self.hi) for b in (o.lo,o.hi)]
        return I(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,o):
        o=as_i(o)
        if o.lo<=0<=o.hi:raise ValueError('division_interval_contains_zero')
        return self*I(1/o.hi,1/o.lo)
    @property
    def width(self):return self.hi-self.lo
    def contains(self,x):return self.lo<=x<=self.hi
    def overlaps(self,o):return max(self.lo,o.lo)<=min(self.hi,o.hi)
    def wire(self):return dict(lower=str(self.lo),upper=str(self.hi),width=str(self.width),exact=self.lo==self.hi)

def as_i(x):return x if isinstance(x,I) else I.point(x)

def day(s):
    if not isinstance(s,str):raise ValueError('date_encoding')
    d=date.fromisoformat(s)
    if d.isoformat()!=s:raise ValueError('date_encoding')
    return d

@lru_cache(maxsize=8192)
def factor(rate,days,scale):
    """Certify lo**q <= (1+r)**p <= hi**q after reducing days/365."""
    r=Q(rate)
    if r<=-1 or type(days)!=int or not 0<=days<=7305 or type(scale)!=int or not 12<=scale<=24:
        raise ValueError('factor_domain')
    if days==0 or r==0:return I.point(1)
    g=gcd(days,365);p=days//g;q=365//g;target=(1+r)**p
    if q==1:return I.point(target)
    grid=10**scale
    num=target.numerator*grid**q;den=target.denominator
    lo=0;hi=grid
    while hi**q*den<num:hi*=2
    while hi-lo>1:
        mid=(lo+hi)//2
        if mid**q*den<=num:lo=mid
        else:hi=mid
    if lo**q*den==num:hi=lo
    result=I(Q(lo,grid),Q(hi,grid))
    assert result.lo**q<=target<=result.hi**q
    return result

def between(r,s,t,scale):return factor(Q(r),(day(t)-day(s)).days,scale)

def pv(flows,t,r,scale):
    return sum((I.point(v)/between(r,t,d,scale) for d,v in flows.items()),I.point(0))

def solve_rate(flows,start,carrying,low,high,width,scale):
    """Bound a unique root for strictly future nonnegative, nonzero receipts."""
    carrying=Q(carrying);low=Q(low);high=Q(high);width=Q(width)
    if carrying<=0 or low<=-1 or low>=high or width<=0 or len(flows)>64:
        raise ValueError('root_domain')
    if not flows or any(day(d)<=day(start) or Q(v)<0 for d,v in flows.items()) or not any(Q(v)>0 for v in flows.values()):
        raise ValueError('positive_future_flows_required')
    def residual(r):return pv(flows,start,r,scale)-carrying
    a,b=residual(low),residual(high)
    if a.lo<0 or b.hi>0:raise ValueError('uncertified_root_bracket')
    steps=0
    while high-low>width:
        steps+=1
        if steps>160:raise ValueError('root_budget')
        mid=(low+high)/2;c=residual(mid)
        if c.lo==c.hi==0:low=high=mid;break
        if c.lo>0:low=mid
        elif c.hi<0:high=mid
        else:
            aa=max(low,mid-width/2);bb=min(high,mid+width/2)
            if residual(aa).lo>=0 and residual(bb).hi<=0:low,high=aa,bb;break
            raise ValueError('root_precision_insufficient')
    a,b=residual(low),residual(high)
    assert a.lo>=0 and b.hi<=0 and high-low<=width
    return dict(rate=I(low,high).wire(),low_pv_residual=a.wire(),high_pv_residual=b.wire(),
                iterations=steps,scale=scale,criterion='monotone_positive_future_receipts')
