"""Conditional aggregate intersections lowered to the existing linear engine.

Regions are monetary aggregates of Boolean membership predicates. They are
never financial accounts, enumerated members, events or proven source facts.
"""
from copy import deepcopy
import itertools
import z3
import joint_measurement_constraints_v1 as joint

core = joint.core
PROFILE = 'ConditionalPopulationOverlap/1'
BOUNDARY = {**joint.BOUNDARY, 'scope': 'conditional_aggregate_population_overlap_only',
    'membership_identity': 'unresolved', 'member_enumeration': 'unresolved',
    'posting_authorized': False}


def region_keys(count):
    core.need(type(count) is int and 2 <= count <= 4, 'population_count_2_to_4')
    return [''.join(bits) for bits in itertools.product('01', repeat=count)
            if '1' in bits]


def lower(body):
    core.need(len(core.canonical(body)) <= core.MAX_BYTES, 'request_size_limit')
    core.closed(body, ['profile','value_type','populations','regions','valuation_premise'], 'overlap')
    core.need(body['profile'] == PROFILE, 'profile')
    joint.types.typed(body['value_type'])
    core.need(body['value_type']['kind'] == 'rational', 'numeric_value_type')
    core.need(type(body['populations']) is dict, 'populations')
    names = sorted(body['populations'])
    keys = region_keys(len(names))
    core.need(type(body['regions']) is dict and set(body['regions']) == set(keys),
              'complete_boolean_regions_required')
    premises, missing, observations, equations = {}, [], {}, []

    def remember(p, location):
        joint.premise(p)
        if p is None:
            missing.append(location)
        else:
            core.need(p['id'] not in premises or premises[p['id']] == p,
                      'conflicting_premise_identity')
            premises[p['id']] = deepcopy(p)

    remember(body['valuation_premise'], 'valuation_premise')
    for name in names:
        core.text(name, 'population_id')
        row = body['populations'][name]
        core.closed(row, ['measurement','predicate','source_dimensions','projection_premise'], 'population')
        core.text(row['predicate'], 'population_predicate')
        core.need(type(row['source_dimensions']) is dict, 'source_dimensions')
        for axis, member in row['source_dimensions'].items():
            core.text(axis, 'source_axis'); core.text(member, 'source_member')
        measure = row['measurement']
        core.closed(measure, ['type','interval','interval_premise','source_ref'], 'measurement')
        core.need(measure['type'] == body['value_type'], 'population_context_type_mismatch')
        remember(row['projection_premise'], 'projection_premise:' + name)
        remember(measure['interval_premise'], 'interval_premise:' + name)
        observations['population:' + name] = deepcopy(measure)
    for key, row in body['regions'].items():
        core.closed(row, ['interval','bound_premise'], 'region')
        remember(row['bound_premise'], 'region_bound:' + key)
        interval = row['interval']
        if interval is not None:
            core.need(joint.rational(interval['lower']) >= 0, 'negative_region_value')
        observations['region:' + key] = {'type':deepcopy(body['value_type']),
            'interval':deepcopy(interval), 'interval_premise':deepcopy(row['bound_premise']),
            'source_ref':'constructed_boolean_region:' + key}
    for index, name in enumerate(names):
        # Every nonempty Boolean atom occurs once in each applicable aggregate.
        equations.append({'id':'membership:' + name, 'type':deepcopy(body['value_type']),
            'terms':[{'observation':'population:' + name,'coefficient':'1/1'}] +
                    [{'observation':'region:' + k,'coefficient':'-1/1'}
                     for k in keys if k[index] == '1'],
            'rhs':'0/1', 'identity_premise':deepcopy(body['valuation_premise'])})
    return {'profile':joint.PROFILE, 'observations':observations, 'equations':equations}, {
        'population_order':names, 'region_order':keys, 'premises':premises,
        'missing':missing,
        'source_dimensions':{n:deepcopy(body['populations'][n]['source_dimensions']) for n in names},
        'predicates':{n:body['populations'][n]['predicate'] for n in names}}


def invalid(exc):
    return {'profile':PROFILE, **BOUNDARY, 'status':'invalid', 'reason':str(exc)[:300]}


def shell(body, budget, definition, metadata):
    return {'profile':PROFILE, **BOUNDARY, 'request_sha256':core.digest(body),
        'budget':deepcopy(budget), 'definition':definition, **metadata,
        'interpretation':'Region values constrain conditional additive measurements; zero value does not prove an empty set.'}


def assess(body, budget):
    try:
        definition, metadata = lower(body)
        # Validate all syntax before an unresolved premise can hide an error.
        joint.validate(definition, budget)
        result = shell(body,budget,definition,metadata)
        if metadata['missing']:
            return {**result, 'status':'unresolved', 'joint_result':None}
        parent = joint.assess(definition,budget)
        return {**result, 'status':parent['status'], 'joint_result':parent}
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError, z3.Z3Exception) as exc:
        return invalid(exc)


def verify_result(body, budget, result):
    """Accept any exact feasible witness; do not pin solver-selected bytes."""
    try:
        if result.get('status') == 'invalid': return result == assess(body,budget)
        definition, metadata = lower(body)
        joint.validate(definition,budget)
        expected = shell(body,budget,definition,metadata)
        if metadata['missing']:
            return result == {**expected,'status':'unresolved','joint_result':None}
        fresh = joint.assess(definition,budget)
        parent = deepcopy(result['joint_result'])
        if parent.get('status') == 'conditionally_feasible':
            core.need(fresh['status'] == parent['status'], 'feasibility_replay')
            joint.check_witness(definition,parent['witness'])
            fresh['witness'] = deepcopy(parent['witness'])
        if 'conflicts' in parent:
            core.need(fresh['status'] == 'conditionally_infeasible', 'infeasibility_replay')
            coeffs, _, _, _ = joint.validate(definition,budget)
            variables = {k:z3.Real('overlap.recheck.'+str(i))
                         for i,k in enumerate(definition['observations'])}
            formulas = {}
            for key,item in definition['observations'].items():
                bounds=item['interval']
                formulas['domain:'+key]=joint.solver.domain_formula(variables[key],{
                    'lower':bounds['lower'],'upper':bounds['upper'],
                    'lower_closed':bounds['lower_inclusive'],'upper_closed':bounds['upper_inclusive']})
            for row,terms in zip(definition['equations'],coeffs):
                formulas['equation:'+row['id']]=sum((joint.solver.q(a)*variables[k]
                    for k,a in terms.items()),joint.solver.q(0))==joint.solver.q(row['rhs'])
            core.need(type(parent['conflicts']) is list and len(parent['conflicts'])==1,'conflict_scope')
            for conflict in parent['conflicts']:
                core.closed(conflict,['labels','rechecked','minimal'],'conflict')
                core.identifiers(conflict['labels'],'conflict_labels',nonempty=True)
                core.need(set(conflict['labels'])<=set(formulas),'unknown_conflict_label')
                core.need(conflict['rechecked']=='unsat' and conflict['minimal'] is False,'conflict_claim')
                engine=z3.Solver();engine.set(timeout=budget['solver_timeout_ms'],rlimit=budget['solver_rlimit'])
                engine.add(*(formulas[k] for k in conflict['labels']))
                core.need(engine.check()==z3.unsat,'conflict_not_unsat')
            fresh['conflicts']=deepcopy(parent['conflicts'])
        # Runtime duration is descriptive, not a semantic acceptance field.
        if 'solver_wall_seconds' in fresh:
            value = parent.get('solver_wall_seconds')
            core.need(type(value) in [int,float] and 0 <= value < float('inf'), 'invalid_timing')
            fresh['solver_wall_seconds'] = value
        core.need(parent == fresh, 'joint_result_replay')
        return result == {**expected,'status':parent['status'],'joint_result':parent}
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError, z3.Z3Exception):
        return False
