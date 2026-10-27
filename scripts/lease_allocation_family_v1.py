"""Exact conditional two-right lease allocations; no actual-history admission."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/lease-allocation-family-20261024'
SOURCE_LOCK_SHA256='a9dd1dc3cb7e3d3a75d2aa7f7727f66492c3db7eec9b473236cbd9231dc0bb25'
PROFILE='LeaseAllocationFamily/1'
QUERY='LeaseAllocationQuery/1'
FLAGS={'source_admission':False,'accounting_admission':False,'method_eligible':False,
       'actual_history_identified':False,'production_committed':False}

class Refused(ValueError):
    def __init__(self,status,reason):
        self.status=status;self.reason=reason;super().__init__(reason)

def need(condition,reason,status='invalid'):
    if not condition:raise Refused(status,reason)

def canonical(value):
    try:return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
    except (TypeError,ValueError):raise Refused('invalid','finite JSON required')

def digest(value):return sha256(canonical(value)).hexdigest()
def fmt(value):
    value=Q(value);return f'{value.numerator}/{value.denominator}'

def amount(value):
    need(type(value) is str,'canonical rational string required')
    need(len(value)<=256,'rational length limit')
    try:result=Q(value)
    except (ValueError,ZeroDivisionError):raise Refused('invalid','malformed rational')
    need(fmt(result)==value,'canonical rational required');return result

def closed(value,fields,name):need(type(value) is dict and set(value)==set(fields),'closed '+name+' fields')
def text(value,name):need(type(value) is str and bool(value.strip()) and len(value)<=4096,name+' required')

def protected():
    p=HERE/'source-lock.json'
    need(sha256(p.read_bytes()).hexdigest()==SOURCE_LOCK_SHA256,'source lock changed','unsupported')
    for name,h in json.loads(p.read_text()).items():
        p=ROOT/name
        need(p.is_file() and sha256(p.read_bytes()).hexdigest()==h,'protected source changed: '+name,'unsupported')

protected()
import lease_shared_book_v1 as native

def interval(value):
    closed(value,['lower','upper','lower_inclusive','upper_inclusive'],'interval')
    a,b=amount(value['lower']),amount(value['upper'])
    lc,uc=value['lower_inclusive'],value['upper_inclusive']
    need(type(lc) is bool and type(uc) is bool,'Boolean endpoint inclusion required')
    need(a<b or a==b and lc and uc,'nonempty ordered interval required')
    return a,b,lc,uc

def wire_interval(value):
    a,b,lc,uc=value
    return {'lower':fmt(a),'upper':fmt(b),'lower_inclusive':lc,'upper_inclusive':uc}

def intersect(a,b):
    lo=max(a[0],b[0]);hi=min(a[1],b[1])
    lc=(a[2] if lo==a[0] else True) and (b[2] if lo==b[0] else True)
    uc=(a[3] if hi==a[1] else True) and (b[3] if hi==b[1] else True)
    return (lo,hi,lc,uc) if lo<hi or lo==hi and lc and uc else None

def contains(domain,x):
    return (x>domain[0] or x==domain[0] and domain[2]) and (x<domain[1] or x==domain[1] and domain[3])

def affine_range(domain,constant,coefficient):
    a,b,lc,uc=domain
    if coefficient==0:return wire_interval((Q(constant),Q(constant),True,True))
    lo=constant+coefficient*a;hi=constant+coefficient*b
    if coefficient<0:lo,hi,lc,uc=hi,lo,uc,lc
    return wire_interval((lo,hi,lc,uc))

CELLS=[
 {'id':'complete','domain':(Q(0),Q(30),True,True),'native_status':'hypothetical_sequence_complete',
  'prefix_length':4,'failed_event_index':None,'reason':None,
  'outcomes':{'final_rou':(30,-1),'profit':(-39,-1),'cash':(101,0),'lease_liability':(0,0)}},
 {'id':'rejected_depreciation','domain':(Q(30),Q(111),False,True),'native_status':'rejected',
  'prefix_length':3,'failed_event_index':3,'reason':'lease_depreciation_invalid',
  'outcomes':{'prefix_rou':(111,-1),'prefix_profit':(42,-1),'cash':(101,0),'lease_liability':(0,0)}},
 {'id':'unsupported_reduction','domain':(Q(111),Q(120),False,True),'native_status':'unsupported',
  'prefix_length':1,'failed_event_index':1,'reason':'negative_remaining_rou_unspecified',
  'outcomes':{'prefix_rou':(130,-1),'prefix_profit':(50,-1),'cash':(200,0),'lease_liability':(-110,0)}}]

def validate(request):
    protected();need(len(canonical(request))<=32768,'request byte limit')
    closed(request,['profile','source_lock_sha256','allocation_domain','allocation_premise',
                    'source_ref','collection_complete','max_cells'],'family request')
    need(request['profile']==PROFILE,'unsupported family profile','unsupported')
    need(request['source_lock_sha256']==SOURCE_LOCK_SHA256,'source scope mismatch','unsupported')
    domain=interval(request['allocation_domain'])
    need(0<=domain[0]<=domain[1]<=120,'allocation outside declared original total')
    text(request['source_ref'],'source reference')
    count=request['max_cells'];need(type(count) is int and 0<=count<=3,'max_cells must be integer0..3')
    completeness=request['collection_complete']
    if completeness is not True:
        need(completeness is False or completeness is None or
             type(completeness) is str and completeness=='unknown','collection-completeness type')
        raise Refused('unresolved','complete right membership not supplied')
    if request['allocation_premise'] is None:raise Refused('unresolved','allocation premise missing')
    text(request['allocation_premise'],'allocation premise')
    return domain

def instantiate(x):
    protected();x=Q(x);need(0<=x<=120,'allocation outside original opening')
    cases=json.loads((ROOT/'data/accounting-master/lease-shared-book-20261024/cases.json').read_text())
    case=next(row for row in cases if row['case']=='original_lifecycle')
    opening,events=deepcopy(case['opening']),deepcopy(case['events'])
    opening['leases'][0]['component']['rights'][0]['rou']=fmt(120-x)
    opening['leases'][0]['component']['rights'][1]['rou']=fmt(x)
    events[0]['parameters']['rights'][1]['removed_rou']=fmt(x)
    return opening,events

def native_replay(x):
    opening,events=instantiate(x);result=native.run_prefix(opening,events)
    return {'x':fmt(x),'opening':opening,'events':events,'result':result}

def _assess(request):
    domain=validate(request);cells=[];checked=0
    for spec in CELLS:
        part=intersect(domain,spec['domain'])
        if part is None:continue
        row={k:deepcopy(spec[k]) for k in ['id','native_status','prefix_length','failed_event_index','reason']}
        row.update(allocation_domain=wire_interval(part),checked=False,native_replay=None,
                   outcome_formulas={k:{'constant':fmt(a),'x_coefficient':fmt(b)} for k,(a,b) in spec['outcomes'].items()},
                   conditional_prefix_ranges=None)
        if checked<request['max_cells']:
            x=part[0] if part[2] else (part[0]+part[1])/2
            replay=native_replay(x);r=replay['result'];b=r['state']['balances']
            need(r['status']==spec['native_status'] and len(r['proposals'])==spec['prefix_length'] and
                 r.get('failed_event_index')==spec['failed_event_index'] and r.get('reason')==spec['reason'],
                 'original native status mismatch','unsupported')
            need(Q(b['rou'])==next(a+c*x for k,(a,c) in spec['outcomes'].items() if k.endswith('rou')) and
                 -sum(Q(b[k]) for k in native.types.PROFIT)==next(a+c*x for k,(a,c) in spec['outcomes'].items() if k.endswith('profit')),
                 'original native amount mismatch','unsupported')
            need(all(Q(b[k])==a+c*x for k,(a,c) in spec['outcomes'].items()
                     if k in ['cash','lease_liability']),
                 'original native cash/liability mismatch','unsupported')
            row.update(checked=True,native_replay=replay,
                       conditional_prefix_ranges={k:affine_range(part,a,c) for k,(a,c) in spec['outcomes'].items()})
            checked+=1
        cells.append(row)
    complete=checked==len(cells)
    successful=next((r for r in cells if r['id']=='complete'),None)
    return {'profile':PROFILE,'status':'exact_conditional_partition' if complete else 'partial_search',
            'request_sha256':digest(request),'source_lock_sha256':SOURCE_LOCK_SHA256,
            'allocation_domain':wire_interval(domain),'allocation_premise':request['allocation_premise'],
            'source_ref':request['source_ref'],'cells':cells,
            'coverage':{'total_cells':len(cells),'checked_cells':checked,'complete':complete,
                        'unvisited_cell_ids':[r['id'] for r in cells if not r['checked']]},
            'all_allocations_complete':all(r['id']=='complete' for r in cells) if complete else None,
            'complete_execution_bounds':deepcopy(successful['conditional_prefix_ranges']) if complete and successful else None,
            'bounds_condition':'complete_execution_only',
            'proof_basis':'Protected affine derivation plus original representative replay; no actual-company coverage',
            **FLAGS}

def assess(request):
    try:return _assess(request)
    except Refused as exc:return {'profile':PROFILE,'status':exc.status,'reason':exc.reason,
                                 'cells':[],'complete_execution_bounds':None,**FLAGS}

def verify_result(request,result):
    expected=assess(request)
    need(canonical(expected)==canonical(result),'saved family differs from full recomputation')
    return True

def query(request,condition):
    family=assess(request)
    try:
        need(len(canonical(condition))<=32768,'query byte limit')
        closed(condition,['profile','conditional_on','constraints','premise','source_ref','max_replays'],'query')
        need(type(condition['max_replays']) is int and 0<=condition['max_replays']<=1,
             'max_replays must be integer0..1')
        need(condition['profile']==QUERY and condition['conditional_on']=='complete_execution',
             'query requires explicit complete-execution condition','unsupported')
        text(condition['source_ref'],'query source reference')
        if condition['premise'] is None:raise Refused('unresolved','query premise missing')
        text(condition['premise'],'query premise')
        constraints=condition['constraints']
        need(type(constraints) is list and len(constraints)<=32,'query constraint limit')
        parsed=[]
        for row in constraints:
            closed(row,['target','domain'],'outcome constraint')
            need(type(row['target']) is str and row['target'] in CELLS[0]['outcomes'],'unknown complete outcome','unsupported')
            parsed.append((row['target'],interval(row['domain'])))
        if family['status']!='exact_conditional_partition':
            return {'profile':QUERY,'status':family['status'],'family':family,
                    'condition':deepcopy(condition),'selection':None,'outcome_bounds':None,**FLAGS}
        complete=next((r for r in family['cells'] if r['id']=='complete'),None)
        selected=interval(complete['allocation_domain']) if complete else None
        for target,domain in parsed:
            if selected is None:break
            a,b=CELLS[0]['outcomes'][target]
            if b==0:
                if not contains(domain,Q(a)):selected=None
            else:
                # All varying outcomes have coefficient -1 in this profile.
                inverse=(a-domain[1],a-domain[0],domain[3],domain[2])
                selected=intersect(selected,inverse)
        if selected and condition['max_replays']==0:
            return {'profile':QUERY,'status':'partial_search','reason':'query native replay budget exhausted',
                    'family':family,'condition':deepcopy(condition),'selection':None,
                    'unverified_candidate_selection':wire_interval(selected),'outcome_bounds':None,
                    'native_replay':None,'unconditional_family_preserved':True,**FLAGS}
        bounds={k:affine_range(selected,a,b) for k,(a,b) in CELLS[0]['outcomes'].items()} if selected else None
        replay=native_replay(selected[0] if selected[2] else (selected[0]+selected[1])/2) if selected else None
        return {'profile':QUERY,'status':'feasible_conditional_selection' if selected else 'infeasible_conditional_selection',
                'family':family,'condition':deepcopy(condition),'selection':wire_interval(selected) if selected else None,
                'outcome_bounds':bounds,'native_replay':replay,'unconditional_family_preserved':True,**FLAGS}
    except Refused as exc:return {'profile':QUERY,'status':exc.status,'reason':exc.reason,
                                 'family':family,'selection':None,'outcome_bounds':None,**FLAGS}
