"""Exact dependency inspection of an authored affine history; no state reduction."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
import typed_affine_history_v1 as native


def add(target, source, coefficient=Q(1)):
    for key, value in source.items():
        target[key] = target.get(key, Q(0)) + coefficient * value
        if target[key] == 0:
            del target[key]
    return target


def encode(expression):
    return {k: native.rat(v) for k, v in sorted(expression.items())}


def evaluate(expression, witness):
    return native.rat(sum((Q(a) * Q(witness[k]) for k, a in expression.items()), Q(0)))


def inspect(history, budget, queries, expected_sha256):
    native.core.need(native.core.digest(history) == expected_sha256, 'history_identity')
    _, _, domains, premises, missing, _, fields = native.validate_and_lower(history, budget)
    native.core.need(type(queries) is list, 'queries')
    native.core.need(len(queries) <= native.MAX_TERMS, 'query_limit')
    state = {kind: {name: {native.identifier('opening_' + kind, name): Q(1)}
                    for name in names} for kind, names in fields.items()}
    prefixes = [deepcopy(state)]
    events = []
    constraints = []

    def linear(terms, at):
        expression = {}
        for term in terms:
            add(expression, at[term['kind']][term['field']], Q(term['coefficient']['value']))
        return expression

    def check_prefix(index):
        balance = {}
        for expression in state['account'].values():
            add(balance, expression)
        constraints.append(dict(kind='balance', id='balance.' + str(index), prefix=index,
                                expression=encode(balance), expected='0/1'))
        for row in history['state_constraints']:
            constraints.append(dict(kind='state_constraint', id=row['id'], prefix=index,
                                    expression=encode(linear(row['terms'], state)),
                                    domain=deepcopy(row['domain'])))

    check_prefix(0)
    for index, event in enumerate(history['events'], 1):
        template = history['templates'][event['template']]
        variable = native.identifier('event_amount', event['id'])
        writes = []
        for group, kind in [('postings', 'account'), ('memory', 'memory')]:
            for name, coefficient in template[group].items():
                add(state[kind][name], {variable: Q(1)}, Q(coefficient['value']))
                writes.append(dict(kind=kind, field=name, coefficient=coefficient['value']))
        events.append(dict(id=event['id'], date=event['date'], prefix=index,
                           event_amount=variable, writes=writes,
                           template=event['template'], template_sha256=native.core.digest(template)))
        prefixes.append(deepcopy(state))
        check_prefix(index)
    date_prefix = {history['opening_date']: 0}
    for day in history['dates']:
        date_prefix[day] = max([0] + [i for i, e in enumerate(history['events'], 1) if e['date'] <= day])
    for row in history['measurements']:
        index = date_prefix[row['date']]
        constraints.append(dict(kind='reported_measurement', id=row['id'], prefix=index,
                                expression=encode(linear(row['terms'], prefixes[index])),
                                domain=deepcopy(row['domain'])))
    results, ids = [], set()
    for query in queries:
        native.core.closed(query, ['id', 'date', 'terms'], 'query')
        native.core.text(query['id'], 'query_id')
        native.core.need(query['id'] not in ids, 'duplicate_query')
        ids.add(query['id'])
        native.core.need(query['date'] in date_prefix, 'unsupported_query_date')
        native.core.need(type(query['terms']) is list and 0 < len(query['terms']) <= native.MAX_TERMS, 'query_terms')
        expression, target_type = {}, None
        syntactic = set()
        for term in query['terms']:
            native.core.closed(term, ['kind', 'field', 'coefficient'], 'query_term')
            kind, name = term['kind'], term['field']
            native.core.need(kind in fields and name in fields[kind], 'unsupported_query_field')
            typ = fields[kind][name]
            if target_type is None:
                target_type = typ
            native.core.need(typ == target_type, 'query_type_mismatch')
            coefficient = native.joint.rational(term['coefficient'])
            native.core.need(coefficient != 0, 'zero_query_term')
            form = prefixes[date_prefix[query['date']]][kind][name]
            syntactic.update(form)
            add(expression, form, coefficient)
        results.append(dict(query=deepcopy(query), prefix=date_prefix[query['date']],
                            type=deepcopy(target_type), expression=encode(expression),
                            output_dependencies=sorted(expression),
                            syntactic_dependencies=sorted(syntactic),
                            cancelled_dependencies=sorted(syntactic-set(expression))))
    constraint_dependencies = sorted({v for c in constraints for v in c['expression']})
    return dict(profile='TypedAffineDependencyInspection/1',
        status='conditional_dependency_inspection', history_sha256=expected_sha256,
        history=deepcopy(history), domains=deepcopy(domains), premises=deepcopy(premises),
        missing_premises=deepcopy(missing), field_types=deepcopy(fields),
        obligations=deepcopy(history['obligations']), exclusions=deepcopy(history['scope']['exclusions']),
        events=events, date_prefix=date_prefix, queries=results,
        constraints=constraints, constraint_dependencies=constraint_dependencies,
        domain_dependencies=sorted(domains), retained_variables=sorted(domains),
        removed_variables=[], executable_reduction=None, source_admission=False,
        accounting_admission=False, operational_preconditions_checked=False,
        scope='Exact symbolic dependency inspection within the supplied affine profile; no general operation constructor or permitted state reduction')
