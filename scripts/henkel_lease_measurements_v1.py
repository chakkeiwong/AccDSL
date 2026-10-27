"""Named retained Henkel measurements; conditional consistency, no lease execution."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import math

import temporal_measurement_constraints_v1 as temporal

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'data/accounting-master/henkel-lease-measurements-20261024'
SOURCE=ROOT/'data/accounting-master/henkel-lease-source-audit-20261024'
LOCK_SHA256='6101a539f60654b63ea09dd54088c9ccb6688c1c15be7f400f32b3b8be6cef35'
INVENTORY_SHA256='78e63e62939fc64d8d7b9b378e1bcdce64e2388e56d09c76a5dd3b0f7de2a801'
PROFILE='HenkelLeaseMeasurements/1'
core=temporal.core
BOUNDARY={**temporal.BOUNDARY,'scope':'named_henkel_lease_measurements_only',
          'native_state_admission':False,'complete_right_membership':'unknown'}
BUDGET={'max_slots':0,'max_formula_nodes':10000,'max_integer_assignments':1,
        'max_cells':1,'elapsed_ms':5000,'solver_timeout_ms':1000,'solver_rlimit':1000000}


def rational(x):
    x=Q(x)
    return f'{x.numerator}/{x.denominator}'


def verify_dependencies():
    raw=(PACKAGE/'dependency-lock.json').read_bytes()
    core.need(sha256(raw).hexdigest()==LOCK_SHA256,'dependency_lock_changed')
    locks=json.loads(raw)
    for name,digest in locks.items():
        core.need(sha256((ROOT/name).read_bytes()).hexdigest()==digest,'dependency_changed:'+name)
    # The source manifest protects the declaration of its PDF hash. Check those
    # original bytes as well, rather than treating its manifest as source proof.
    for name,digest in json.loads((SOURCE/'source-lock.json').read_text()).items():
        core.need(sha256((ROOT/name).read_bytes()).hexdigest()==digest,'source_changed:'+name)
    return locks


def rounding_hypothesis():
    return {'id':'henkel_nearest_million_ties_away_proposed','status':'proposed',
            'meaning':'Selected underlying measurements round to displayed EUR millions by nearest rounding, with exact half ties away from zero; this is not an evidenced issuer rule.',
            'mode':'nearest_ties_away_from_zero','quantum':'1/1','unit':'million EUR'}


def interval(displayed):
    d=Q(displayed)
    return {'lower':rational(d-Q(1,2)),'upper':rational(d+Q(1,2)),
            'lower_inclusive':d>0,'upper_inclusive':d<0}


def registry():
    result={}
    def same(key,terms):
        result[key]={'id':key,'kind':'same_time','terms':[{'observation':name,'coefficient':rational(a)} for name,a in terms],'rhs':'0/1'}
    for year in [2024,2025]:
        def same_year(name,terms): same(f'{year}.{name}',[(f'{year}.{key}',a) for key,a in terms])
        same_year('liability_categories',[('liability.total',1),('liability.current',-1),('liability.noncurrent',-1)])
        same_year('rou_gross_net',[('rou_net.total',1),('rou_gross.total',-1),('rou_accumulated.total',1)])
        same_year('depreciation_categories',[('rou_depreciation',1),('rou_dep_land',-1),('rou_dep_plant',-1),('rou_dep_office',-1)])
        same_year('maturity_categories',[('maturity.total',1),('maturity.due_le_1y',-1),('maturity.due_1_to_5y',-1),('maturity.due_gt_5y',-1)])
        same_year('cash_components',[('reconciliation.cash',1),('reconciliation.interest_paid',-1),('reconciliation.redemption',-1)])
        key=f'{year}.signed_liability_bridge'
        result[key]={'id':key,'kind':'stock_flow','period':{'kind':'period','start':f'{year}-01-01','end_exclusive':f'{year+1}-01-01'},
                     'opening':f'{year}.reconciliation.opening','closing':f'{year}.reconciliation.closing',
                     'movements':[{'observation':f'{year}.reconciliation.{name}','coefficient':'1/1'} for name in ['cash','expense','additions','acquisitions','fx','fair_value','sundry']]}
        same_year('closing_sign',[('reconciliation.closing',1),('liability.total',1)])
        same_year('redemption_sign',[('reconciliation.redemption',1),('cashflow_redemption',1)])
        same_year('maturity_carrying',[('maturity.carrying',1),('liability.total',-1)])
    same('2025.opening_continuity',[('2025.reconciliation.opening',1),('2024.reconciliation.closing',-1)])
    return result


SUPPORTED=tuple(registry())


def identity_hypothesis(key):
    core.need(key in SUPPORTED,'unknown_relation')
    return {'id':'henkel_underlying_relation:'+key,'status':'proposed',
            'meaning':'Underlying measurements satisfy exactly the named relation '+key+'; this premise is proposed, not source admitted.'}


def fixture(selected=None, assume=False):
    keys=list(SUPPORTED if selected is None else selected)
    return {'profile':PROFILE,'inventory_sha256':INVENTORY_SHA256,'selected_relations':keys,
            'rounding_hypothesis':rounding_hypothesis() if assume else None,
            'identity_hypotheses':{k:identity_hypothesis(k) if assume else None for k in keys}}


def _budget(value):
    core.closed(value,temporal.joint.BUDGET_FIELDS,'budget')
    b=temporal.joint.solver.Budget(**value)
    core.need(b.max_slots==0 and b.max_cells<=1 and b.max_integer_assignments<=1,'single_conjunction_budget')
    core.need(b.elapsed_ms<=60000 and b.solver_timeout_ms<=10000 and b.solver_rlimit<=10000000,'reference_runtime_limit')


def build(body,budget):
    verify_dependencies()
    core.need(len(core.canonical(body))<=core.MAX_BYTES,'request_size_limit')
    core.closed(body,['profile','inventory_sha256','selected_relations','rounding_hypothesis','identity_hypotheses'],'request')
    core.need(body['profile']==PROFILE,'profile')
    core.need(body['inventory_sha256']==INVENTORY_SHA256,'inventory_hash')
    keys=body['selected_relations'];core.identifiers(keys,'selected_relations')
    core.need(set(keys)<=set(SUPPORTED),'unknown_relation');_budget(budget)
    rnd=body['rounding_hypothesis'];core.need(rnd is None or rnd==rounding_hypothesis(),'rounding_hypothesis_mismatch')
    ids=body['identity_hypotheses'];core.need(type(ids) is dict and set(ids)==set(keys),'identity_selection_mismatch')
    for key in keys: core.need(ids[key] is None or ids[key]==identity_hypothesis(key),'identity_hypothesis_mismatch')
    inventory=json.loads((SOURCE/'observations.json').read_text())
    dependencies=json.loads((SOURCE/'state-dependencies.json').read_text())
    source={o['id']:o for o in inventory['observations']}
    definitions=registry();relations=[];used=set()
    for key in keys:
        r=deepcopy(definitions[key]);r['identity_premise']=deepcopy(ids[key]);relations.append(r)
        if r['kind']=='same_time': used.update(t['observation'] for t in r['terms'])
        else: used.update([r['opening'],r['closing'],*[t['observation'] for t in r['movements']]])
    c=inventory['context']
    value_type={'kind':'rational','context':{'issuer':c['issuer'],'perimeter':c['perimeter'],'basis':c['basis'],'document_id':c['document_id']},
                'dimensions':{'currency:EUR':1},'scale':'1000000/1'}
    observations={}
    for key in sorted(used):
        o=source[key];core.need(o['displayed_rational'] is not None,'dash_has_no_numeric_domain')
        when={'kind':'period',**o['period']} if o['period'] is not None else {'kind':'instant','at':o['measurement_date']}
        quantity='signed_lease_liability' if key.endswith(('reconciliation.opening','reconciliation.closing')) else o['concept']
        observations[key]={'type':{'value_type':deepcopy(value_type),'time':when,'quantity':quantity},
                           'interval':interval(o['displayed_rational']) if rnd is not None else None,
                           'interval_premise':None if rnd is None else {k:rnd[k] for k in ['id','status','meaning']},
                           'source_ref':INVENTORY_SHA256+':'+key}
    definition={'profile':temporal.PROFILE,'observations':observations,'relations':relations}
    if relations: temporal.lower(definition,budget)
    return {'profile':PROFILE,**BOUNDARY,'request_sha256':core.digest(body),'dependency_lock_sha256':LOCK_SHA256,
            'inventory_sha256':INVENTORY_SHA256,'budget':deepcopy(budget),'selected_relations':deepcopy(keys),
            'preserved_inventory':inventory,'preserved_state_dependencies':dependencies,'definition':definition,
            'source_mapping':{k:deepcopy(source[k]) for k in sorted(used)},
            'relation_dispositions':[{'id':k,'status':'selected_conditional_system' if k in keys else 'supported_unselected'} for k in SUPPORTED],
            'excluded_relations':['dash_dependent_rou_category_sums','incomplete_rou_bridge','cash_expense_attribution','discounted_equals_undiscounted']}


def assess(body,budget):
    try:
        result=build(body,budget)
        assessment=temporal.assess(result['definition'],budget) if result['selected_relations'] else {**temporal.BOUNDARY,'status':'no_asserted_system'}
        return {**result,'status':assessment['status'],'temporal_assessment':assessment}
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError) as exc:
        return {'profile':PROFILE,**BOUNDARY,'status':'invalid','reason':str(exc)[:300]}


def _stable(result):
    d=deepcopy(result)
    if 'temporal_assessment' in d:
        joint=d['temporal_assessment'].get('joint_assessment',{})
        joint.pop('solver_wall_seconds',None);joint.pop('witness',None)
    return d


def verify_result(body,budget,result):
    """Recompute all fixed fields and validate a saved witness independently."""
    try:
        replay=assess(body,budget)
        core.need(_stable(result)==_stable(replay),'result_changed')
        saved=result.get('temporal_assessment',{}).get('joint_assessment',{})
        current=replay.get('temporal_assessment',{}).get('joint_assessment',{})
        core.need(set(saved)==set(current),'joint_result_fields')
        if 'witness' in saved: temporal.check_witness(result['definition'],budget,saved['witness'])
        if 'solver_wall_seconds' in saved:
            t=saved['solver_wall_seconds'];core.need(type(t) in [int,float] and t>=0 and math.isfinite(t),'invalid_solver_time')
        return True
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError):
        return False
