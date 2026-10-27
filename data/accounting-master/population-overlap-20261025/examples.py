"""Source-bound cash illustrations; all population projections are proposed."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import population_overlap_v1 as overlap

LEDGER = ROOT/'data/accounting-master/cash-population-reconciliation-20261025/source-ledger.json'
BUDGET = {'max_slots':0,'max_formula_nodes':10000,'max_integer_assignments':1,
          'max_cells':1,'elapsed_ms':5000,'solver_timeout_ms':1000,'solver_rlimit':1000000}

def fraction(x):
    x=Q(x); return f'{x.numerator}/{x.denominator}'

def interval(lo, hi=None, li=True, ui=True):
    return {'lower':fraction(lo),'upper':fraction(lo if hi is None else hi),
            'lower_inclusive':li,'upper_inclusive':ui}

def premise(name,meaning):return {'id':name,'status':'proposed','meaning':meaning}

def fixture(year='2023', rounded=False, restricted=False):
    data=json.loads(LEDGER.read_text())
    for name,h in data['source_sha256'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest()==h, name
    facts={r['id']:r for r in data['cash_facts']}
    ids={'B':'f-148','F':'f-262'} if year=='2023' else {'B':'f-147','F':'f-343'}
    if restricted:
        assert year=='2024';ids['R']='f-610'
    t={'kind':'rational','context':{'entity':'0000320193','perimeter':'consolidated',
       'basis':'US GAAP','at':'2023-09-30' if year=='2023' else '2024-09-28',
       'valuation':'proposed_common_nonnegative_additive_cash_value'},
       'dimensions':{'currency:USD':1},'scale':'1000000/1'}
    populations={}
    for name,fid in ids.items():
        fact=facts[fid];value=Q(fact['literal'])/1000000
        assert fact['context']['entity']==t['context']['entity']
        assert fact['context']['period']=={'instant':t['context']['at']}
        quantum=Q(10)**(-int(fact['decimals']))/1000000
        bound=interval(value-quantum/2,value+quantum/2,True,False) if rounded else interval(value)
        populations[name]={'predicate':fact['concept'],
            'source_dimensions':{d['dimension']:d['member'] for d in fact['context']['dimensions']},
            'projection_premise':premise('projection.'+name,
                'Conditional interpretation of this retained concept and dimensions as one population under the common valuation; no source admission.'),
            'measurement':{'type':deepcopy(t),'interval':bound,
                'interval_premise':premise('precision.'+name,
                    'Assume nearest rounding with lower-closed upper-open endpoints.' if rounded else
                    'Treat displayed number as exact for this algebraic comparator only; no exact-unrounded source claim.'),
                'source_ref':str(LEDGER.relative_to(ROOT))+'#'+fid}}
    ceiling=40000
    body={'profile':overlap.PROFILE,'value_type':t,'populations':populations,
          'valuation_premise':premise('common.valuation',
              'Assume a common nonnegative additive valuation, comparable dates and monetary basis; regions are aggregate values, not accounts.'),
          'regions':{k:{'interval':interval(0,ceiling),'bound_premise':premise('bound.'+k,
              'Authored finite bound on aggregate region value; no membership enumeration or account identity.')}
              for k in overlap.region_keys(len(ids))}}
    if restricted:
        # Source notes support inclusion, but its formal projection remains proposed.
        constrain(body,['001','011'],'R subset B supported by Notes4 and7; formal mapping remains conditional.')
    return body

def constrain(body,keys,meaning):
    for k in keys:
        body['regions'][k]={'interval':interval(0),'bound_premise':premise('bound.'+k,meaning)}
    return body

def cases():
    b23=fixture();b24=fixture('2024');r24=fixture('2024',True,True)
    disjoint=deepcopy(r24);constrain(disjoint,['101','111'],'Test disjoint restricted and balance-sheet cash; expected rejection.')
    missing=deepcopy(b23);missing['populations']['B']['projection_premise']=None
    wrong=deepcopy(b23);wrong['populations']['F']['measurement']['type']['context']['at']='2024-09-28'
    return {
        '2023_unknown_overlap':(b23,BUDGET,'conditionally_feasible'),
        '2023_assumed_B_subset_F':(constrain(deepcopy(b23),['10'],'Assumed B subset F; zero mass only.'),BUDGET,'conditionally_feasible'),
        '2023_assumed_equal_populations':(constrain(deepcopy(b23),['10','01'],'Assumed equal populations; unequal measured totals reject.'),BUDGET,'conditionally_infeasible'),
        '2023_rounded_unknown_overlap':(fixture(rounded=True),BUDGET,'conditionally_feasible'),
        '2024_equal_display_totals':(b24,BUDGET,'conditionally_feasible'),
        '2024_restricted_overlap':(r24,BUDGET,'conditionally_feasible'),
        '2024_false_disjoint_restricted':(disjoint,BUDGET,'conditionally_infeasible'),
        'missing_projection':(missing,BUDGET,'unresolved'),
        'wrong_date':(wrong,BUDGET,'invalid'),
        'zero_budget':(b23,{**BUDGET,'max_cells':0},'unknown'),
    }

def explicit_witnesses():
    return {
        '2023_unknown_overlap':[
            {'population:B':'29965/1','population:F':'30737/1','region:10':'0/1','region:01':'772/1','region:11':'29965/1'},
            {'population:B':'29965/1','population:F':'30737/1','region:10':'100/1','region:01':'872/1','region:11':'29865/1'}],
        '2024_equal_display_totals':[
            {'population:B':'29943/1','population:F':'29943/1','region:10':'0/1','region:01':'0/1','region:11':'29943/1'},
            {'population:B':'29943/1','population:F':'29943/1','region:10':'100/1','region:01':'100/1','region:11':'29843/1'}]}
