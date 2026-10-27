"""Exact time-aware measurement relations with explicit scalar lowering."""
from copy import deepcopy
from datetime import date, timedelta

import joint_measurement_constraints_v1 as joint

core = joint.core
PROFILE = 'TemporalMeasurementConstraints/1'
BOUNDARY = {**joint.BOUNDARY, 'scope': 'conditional_temporal_measurement_relations_only'}
TEMPORAL_KEYS = {'date', 'at', 'instant', 'period', 'start', 'end', 'end_exclusive',
                 'time', 'measurement_time', 'measurement_kind'}


def day(value):
    core.text(value, 'civil_date')
    result = date.fromisoformat(value)
    core.need(result.isoformat() == value, 'canonical_civil_date')
    return result


def time_type(value):
    core.need(type(value) is dict, 'measurement_time')
    if value.get('kind') == 'instant':
        core.closed(value, ['kind', 'at'], 'instant_time')
        day(value['at'])
    else:
        core.closed(value, ['kind', 'start', 'end_exclusive'], 'period_time')
        core.need(value['kind'] == 'period', 'time_kind')
        core.need(day(value['start']) < day(value['end_exclusive']), 'nonempty_period')
    return value


def measurement_type(value):
    core.closed(value, ['value_type', 'time', 'quantity'], 'measurement_type')
    joint.types.typed(value['value_type'])
    core.need(value['value_type']['kind'] == 'rational', 'numeric_measurement')
    core.need(not set(value['value_type']['context']) & TEMPORAL_KEYS,
              'time_and_kind_require_explicit_measurement_type')
    time_type(value['time']); core.text(value['quantity'], 'measured_quantity')
    return value


def lower(definition, budget):
    core.need(len(core.canonical(definition)) <= core.MAX_BYTES, 'definition_size_limit')
    core.closed(definition, ['profile', 'observations', 'relations'], 'temporal_definition')
    core.need(definition['profile'] == PROFILE, 'profile')
    observations, relations = definition['observations'], definition['relations']
    core.need(type(observations) is dict and len(observations) <= joint.MAX_ENTRIES, 'observation_limit')
    core.need(type(relations) is list and 0 < len(relations) <= joint.MAX_ENTRIES, 'relation_limit')
    numeric_observations = {}
    for key, item in observations.items():
        core.text(key, 'observation_id')
        core.closed(item, ['type', 'interval', 'interval_premise', 'source_ref'], 'temporal_observation')
        measurement_type(item['type'])
        numeric_observations[key] = {**deepcopy(item), 'type': deepcopy(item['type']['value_type'])}
    equations, certificates, ids = [], [], set()
    term_count = 0
    for relation in relations:
        core.need(type(relation) is dict, 'relation')
        kind = relation.get('kind')
        if kind == 'same_time':
            core.closed(relation, ['id','kind','terms','rhs','identity_premise'], 'same_time_relation')
        elif kind == 'stock_flow':
            core.closed(relation, ['id','kind','period','opening','movements','closing','identity_premise'], 'stock_flow_relation')
        else:
            raise core.Invalid('unsupported_temporal_relation')
        core.text(relation['id'], 'relation_id')
        core.need(relation['id'] not in ids, 'duplicate_relation'); ids.add(relation['id'])
        joint.premise(relation['identity_premise'])
        terms = relation['terms'] if kind == 'same_time' else relation['movements']
        core.need(type(terms) is list and bool(terms), 'nonempty_relation_terms')
        term_count += len(terms) + (2 if kind == 'stock_flow' else 0)
        core.need(term_count <= joint.MAX_TERMS, 'term_limit')
        keys = []
        for term in terms:
            core.closed(term, ['observation','coefficient'], 'relation_term')
            key = term['observation']; core.text(key, 'term_observation')
            core.need(key in observations, 'undeclared_observation')
            joint.rational(term['coefficient']); keys.append(key)
        if kind == 'same_time':
            joint.rational(relation['rhs'])
            anchor = observations[keys[0]]['type']
            for key in keys:
                typ = observations[key]['type']
                core.need(typ['value_type'] == anchor['value_type'], 'economic_context_mismatch')
                core.need(typ['time'] == anchor['time'], 'same_time_mismatch')
            numeric_terms, rhs = deepcopy(terms), relation['rhs']
            roles = [{'observation':key, 'role':'same_time_operand'} for key in keys]
        else:
            period = time_type(relation['period'])
            core.need(period['kind'] == 'period', 'bridge_period_required')
            opening, closing = relation['opening'], relation['closing']
            core.text(opening, 'opening_observation'); core.text(closing, 'closing_observation')
            core.need(opening in observations and closing in observations, 'undeclared_endpoint')
            core.need(opening != closing and opening not in keys and closing not in keys, 'distinct_endpoint_roles')
            start = (day(period['start'])-timedelta(days=1)).isoformat()
            end = (day(period['end_exclusive'])-timedelta(days=1)).isoformat()
            anchor = observations[opening]['type']; terminal = observations[closing]['type']
            core.need(anchor['time'] == {'kind':'instant','at':start}, 'opening_time_mismatch')
            core.need(terminal['time'] == {'kind':'instant','at':end}, 'closing_time_mismatch')
            core.need(anchor['quantity'] == terminal['quantity'], 'endpoint_quantity_mismatch')
            for key in keys+[closing]:
                core.need(observations[key]['type']['value_type'] == anchor['value_type'], 'economic_context_mismatch')
            for key in keys:
                core.need(observations[key]['type']['time'] == period, 'movement_period_mismatch')
            numeric_terms = [{'observation':opening,'coefficient':'1/1'}, *deepcopy(terms),
                             {'observation':closing,'coefficient':'-1/1'}]
            rhs = '0/1'
            roles = [{'observation':opening,'role':'opening'},
                     *[{'observation':key,'role':'period_movement'} for key in keys],
                     {'observation':closing,'role':'closing'}]
        equations.append({'id':relation['id'],'type':deepcopy(anchor['value_type']),
                          'terms':numeric_terms,'rhs':rhs,'identity_premise':deepcopy(relation['identity_premise'])})
        certificates.append({'relation_id':relation['id'],'kind':kind,'roles':roles,
                             'original_relation_sha256':core.digest(relation),
                             'numeric_equation_sha256':core.digest(equations[-1])})
    numeric = {'profile':joint.PROFILE,'observations':numeric_observations,'equations':equations}
    joint.validate(numeric, budget)
    return numeric, certificates


def check_witness(definition, budget, witness):
    numeric, _ = lower(definition, budget)
    return joint.check_witness(numeric, witness)


def assess(definition, budget):
    try:
        numeric, certificates = lower(definition, budget)
        result = joint.assess(numeric, budget)
        if 'witness' in result: check_witness(definition, budget, result['witness'])
        return {'profile':PROFILE, **BOUNDARY, 'definition_sha256':core.digest(definition),
                'definition':deepcopy(definition), 'numeric_definition':numeric,
                'numeric_definition_sha256':core.digest(numeric), 'lowering':certificates,
                'status':result['status'], 'joint_assessment':result}
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError) as exc:
        return {'profile':PROFILE, **BOUNDARY, 'status':'invalid','reason':str(exc)[:300]}
