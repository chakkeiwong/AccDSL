"""Scoped two-year loan fixture and exact dated reset arithmetic."""
from copy import deepcopy
from datetime import date, timedelta
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
SOURCE=ROOT/'data/accounting-master/literature-closure-20261026/runtime-integration.py'
spec=importlib.util.spec_from_file_location('retained_persistent_factory',SOURCE)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
program,h,native=base.program,base.h,base.native


def make(kind,owner='alpha'):
    if kind not in ['fixed','floating']:raise ValueError('explicit original type required')
    b,m=base.make(kind,owner);book=b['opening']
    book['balances']={account:'0/1' for account in book['balances']}
    book['balances'].update({m['cash']:'20/1',m['inventory']:'100/1',m['debt']:'-100/1',m['capital']:'-20/1'})
    unit=book['memory_types']['/terms/stage'];money=program.engine.money_type(book)
    old_schema=book['memory_schema'];shape=deepcopy(b['schemas'][old_schema])
    shape['properties']['terms']['properties']['rate_type']=h.scalar('rational')
    shape['properties']['terms']['required'].append('rate_type')
    book['memory']['terms']['rate_type']=h.fmt(0 if kind=='fixed' else 1)
    book['memory_types']['/terms/rate_type']=deepcopy(unit)
    new_schema=program.digest(shape);book['memory_schema']=new_schema;b['schemas'][new_schema]=shape
    entry=deepcopy(b['registry']['entries']['coupon']);entry['schemas'][new_schema]=shape
    method=entry['method'];method['memory']['definition']['state_schema']=new_schema
    pre=method['preconditions'];pre['manifest']['inputs']['rate_type']=h.declaration(unit,'rate_type')
    pre['bindings']['rate_type']=h.memory('/terms/rate_type')
    pre['manifest']['inputs']['coupon']=h.declaration(money,'coupon')
    pre['bindings']['coupon']=h.memory('/terms/coupon')
    guards=[('same_contract_type',h.binary('eq',h.ref('rate_type'),h.constant(unit,h.fmt(0 if kind=='fixed' else 1))),['rate_type']),
        ('supplied_coupon_matches_type',h.binary('eq',h.ref('coupon'),h.binary('add',h.constant(money,'5/1'),h.binary('mul',h.constant(money,'2/1'),h.ref('rate_type')))),['coupon','rate_type'])]
    for name,predicate,deps in guards:
        pre['manifest']['requirements'].append(dict(id=name,guard=h.constant(program.core.BOOL,True),guard_requires=[],predicate=predicate,requires=deps,admission_refs=[],on_false='invalid',on_unknown='unresolved'))
    method['residual_prerequisites']=['Original two-year synthetic100 loan with supplied annual coupon5 or7.',
        'No amendment, principal change, source admission, floating reset construction or actual contract claim.']
    entry['method_sha256']=program.digest(method);b['registry']['entries']={'coupon':entry}
    policies={key:dict(kind='preserve',provenance='Same original contract and exact complementary memory') for key in book['memory_types']}
    policies['/terms/stage']=dict(kind='reset',type=deepcopy(unit),value='0/1',provenance='Reset annual execution stage only; contract type/coupon persist')
    notes=[dict(id='loan',label='Supplied original loan',status='unresolved',reason='Constant annual cash amounts supplied; source, reset schedule and treatment admission remain open')]
    def payment(year):return dict(kind='event',method_key='coupon',event=dict(id='coupon.'+str(year),date=str(year)+'-12-30',inputs={}))
    def report(year):return dict(kind='report',id='report.'+str(year),cutoff=str(year)+'-12-31',equity_movements=[],notes=deepcopy(notes))
    close={**report(2027), 'kind':'carry','id':'close.2027','retained_account':m['retained'],'next_end_exclusive':'2029-01-01','memory_policies':policies}
    b['commands']=[payment(2027),report(2027),close,payment(2028),report(2028)]
    b['name']='original-persistent-'+kind+'-'+owner
    return b,m


def exact(value):
    if isinstance(value,(bool,float)):raise ValueError('exact rational required')
    return Q(value)


def schedule(contract,shocks):
    """Declared ACT/365 simple synthetic contract; no general calendar admission."""
    keys={'kind','principal','fixed_rate','reference_rate','spread','start','maturity','resets','convention'}
    if not isinstance(contract,dict) or set(contract)!=keys:raise ValueError('contract fields')
    if contract['kind'] not in ['fixed','floating']:raise ValueError('unsupported loan type')
    if contract['convention']!='actual_days/365_simple':raise ValueError('unsupported day count')
    start,end=date.fromisoformat(contract['start']),date.fromisoformat(contract['maturity'])
    if not start<end:raise ValueError('positive horizon required')
    reset=[date.fromisoformat(v) for v in contract['resets']]
    if reset!=sorted(set(reset)) or not reset or reset[0]!=start:raise ValueError('ordered unique resets from start required')
    if any(v>end for v in reset):raise ValueError('reset after maturity unsupported')
    principal=exact(contract['principal']);fixed=exact(contract['fixed_rate'])
    reference=exact(contract['reference_rate']);spread=exact(contract['spread'])
    if min(principal,fixed,reference,spread)<0:raise ValueError('nonnegative supplied terms required')
    seen=set();normalized=[]
    for shock in shocks:
        if not isinstance(shock,dict) or set(shock)!={'id','target','effective','delta'}:raise ValueError('shock fields')
        if not isinstance(shock['id'],str) or not shock['id'] or shock['id'] in seen:raise ValueError('duplicate or absent shock identity')
        seen.add(shock['id'])
        if shock['target']!='reference_rate':raise ValueError('only reference-rate shock admitted')
        normalized.append((shock['id'],date.fromisoformat(shock['effective']),exact(shock['delta'])))
    boundaries=sorted({start,end,*[r for r in reset if r<end]}) if contract['kind']=='floating' else [start,end]
    rows=[]
    for left,right in zip(boundaries,boundaries[1:]):
        applied=[(ident,delta) for ident,effective,delta in normalized if effective<=left] if contract['kind']=='floating' else []
        rate=fixed if contract['kind']=='fixed' else reference+spread+sum((delta for _,delta in applied),Q())
        if rate<0:raise ValueError('negative all-in rate outside synthetic scope')
        days=(right-left).days;amount=principal*rate*Q(days,365)
        rows.append(dict(start=left.isoformat(),end_exclusive=right.isoformat(),days=days,rate=str(rate),interest=str(amount),shock_ids=[x[0] for x in applied]))
    return dict(status='conditional_schedule',segments=rows,interest=str(sum((Q(x['interest']) for x in rows),Q())),native_schedule_admission=False)


def daily_oracle(contract,shocks):
    """Independent day enumeration rather than interval integration."""
    day=date.fromisoformat(contract['start']);end=date.fromisoformat(contract['maturity'])
    resets=[date.fromisoformat(x) for x in contract['resets']];value=Q()
    while day<end:
        reset=max(x for x in resets if x<=day)
        if contract['kind']=='fixed':rate=Q(contract['fixed_rate'])
        else:rate=Q(contract['reference_rate'])+Q(contract['spread'])+sum((Q(s['delta']) for s in shocks if date.fromisoformat(s['effective'])<=reset),Q())
        value+=Q(contract['principal'])*rate/365;day+=timedelta(days=1)
    return str(value)

