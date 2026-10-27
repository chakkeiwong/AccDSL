"""Inspect supplied claim relationships; the retained executor owns execution."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
PATH_DIR = ROOT / 'data/accounting-master/company-operation-path-20261023'
spec = importlib.util.spec_from_file_location('claim_relation_native_path', PATH_DIR / 'composition.py')
native = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native)
wire = native.wire
TRADE = {'purchase', 'delivery', 'collection', 'supplier_payment'}


def event_key(year, operation):
    return json.dumps(['year', year, 'operation', operation], separators=(',', ':'))


def totals(claims):
    return {ledger: sum((c['outstanding'] for c in claims.values()
                        if c['ledger'] == ledger), Q(0))
            for ledger in ['receivable', 'payable']}


def inspect(path, source, expected_digest):
    if native.digest(path) != expected_digest:
        raise ValueError('path identity mismatch')
    answer = native.execute(path, source)
    # Invalid schemas/source bindings supply no reliable operation population.
    if (answer['status'] not in {'complete_conditional', 'partial'}
            or hashlib.sha256(source).hexdigest() != path['initial_year']['source']['sha256']):
        return dict(status='native_refusal', native_result=wire(answer),
                    input_sha256=expected_digest, relation_graph=None)
    if not native.verify_chain(path, answer):
        raise ValueError('native chain binding')
    definitions = [path['initial_year'], *path['continuations']]
    claims = {c['id']: dict(ledger=c['ledger'], recognised=Q(c['amount']),
                           settled=Q(0), outstanding=Q(c['amount']))
              for c in path['initial_year']['opening_claims']}
    origins = {c['id']: dict(kind='supplied_opening', source=path['initial_year']['source'],
                             opening_digest=path['initial_year']['opening_digest'],
                             input_path='/initial_year/opening_claims/'+str(i))
               for i, c in enumerate(path['initial_year']['opening_claims'])}
    nodes, edges, prefixes, guards, year_ends = [], [], [], [], []
    uninspected = set()
    for yi, definition in enumerate(definitions):
        year = answer['years'][yi] if yi < len(answer['years']) else None
        run = year['run'] if year is not None else None
        applied = [] if run is None else run.get('journals', run.get('applied', []))
        applied_by_id = {j['event']: j for j in applied}
        if len(applied_by_id) != len(applied):
            raise ValueError('duplicate native event')
        annual_opening = deepcopy(claims)
        base = '/initial_year' if yi == 0 else '/continuations/'+str(yi-1)
        for oi, op in enumerate(definition['operations']):
            key = event_key(yi, op['id'])
            where = base+'/operations/'+str(oi)
            journal = applied_by_id.get(op['id'])
            state = ('executed' if journal is not None else 'refused'
                     if run is not None and run.get('event') == op['id'] else 'unexecuted')
            nodes.append(dict(id=key, year=yi, operation_id=op['id'], kind=op['kind'],
                              at=op['at'], status=state, input_path=where))
            if journal is None:
                continue
            if journal['kind'] != op['kind'] or journal['at'] != op['at']:
                raise ValueError('native event mismatch')
            before = totals(claims)
            kind, payload = op['kind'], op['payload']
            if kind in {'purchase', 'delivery'}:
                cid = payload['claim_id']
                if cid in claims:
                    raise ValueError('executed duplicate claim')
                amount = Q(payload['units']) * Q(definition['inventory']['unit_cost']
                    if kind == 'purchase' else payload['unit_price'])
                ledger = 'payable' if kind == 'purchase' else 'receivable'
                claims[cid] = dict(ledger=ledger, recognised=amount, settled=Q(0), outstanding=amount)
                origins[cid] = dict(kind='executed_creation', event=key, input_path=where+'/payload/claim_id')
                edges.append(dict(kind='creates_claim', event=key, claim_id=cid,
                                  amount=wire(amount), ledger=ledger, input_path=where+'/payload'))
                guards.append(dict(event=key, claim_id=cid, reads=['claim_population'],
                    writes=['claim_population', 'claims/'+cid], requirements=['fresh_claim_id'],
                    other_native_guards=['inventory_shortfall', 'control_not_transferred_method']
                    if kind == 'delivery' else []))
            elif kind in {'collection', 'supplier_payment'}:
                ledger = 'receivable' if kind == 'collection' else 'payable'
                for ai, allocation in enumerate(payload['allocations']):
                    cid, amount = allocation['claim_id'], Q(allocation['amount'])
                    if cid not in claims or claims[cid]['ledger'] != ledger:
                        raise ValueError('executed invalid endpoint')
                    if amount < 0 or amount > claims[cid]['outstanding']:
                        raise ValueError('executed invalid allocation')
                    claims[cid]['settled'] += amount
                    claims[cid]['outstanding'] -= amount
                    edges.append(dict(kind='settles_claim', event=key, claim_id=cid,
                        amount=wire(amount), ledger=ledger, is_zero=amount == 0,
                        input_path=where+'/payload/allocations/'+str(ai)))
                    guards.append(dict(event=key, claim_id=cid,
                        reads=['claims/'+cid+'/ledger', 'claims/'+cid+'/outstanding'],
                        writes=['claims/'+cid+'/settled', 'claims/'+cid+'/outstanding'],
                        requirements=['recognised_claim', 'correct_ledger', 'nonnegative_allocation',
                                      'no_duplicate_allocation', 'no_over_settlement'],
                        other_native_guards=['cash_shortfall'] if kind == 'supplier_payment' else []))
            else:
                uninspected.add(kind)
            after = totals(claims)
            if after['receivable'] - before['receivable'] != journal['journal'].get('receivables', Q(0)):
                raise ValueError('receivable journal mismatch')
            if after['payable'] - before['payable'] != -journal['journal'].get('payables', Q(0)):
                raise ValueError('payable journal mismatch')
            prefixes.append(dict(event=key, claims=wire(deepcopy(claims))))
        if run is not None and 'claims' in run:
            # The annual executor starts retained claims with their outstanding
            # amount. Check its annual counters, then its separate lifetime carry.
            annual = deepcopy(claims)
            for cid, opening in annual_opening.items():
                annual[cid]['recognised'] = opening['outstanding']
                annual[cid]['settled'] -= opening['settled']
            if wire(annual) != wire(run['claims']):
                raise ValueError('native annual claim mismatch')
            if 'closing_memory' in year and wire(claims) != wire(year['closing_memory']['claims']):
                raise ValueError('native lifetime carry mismatch')
            year_ends.append(dict(year=yi, native_status=run['status'], claims=wire(deepcopy(claims))))
    claim_nodes = [dict(id=cid, **wire(c), origin=origins[cid],
        counterparty=None, legal_instrument=None, authority=None,
        unresolved=['counterparty', 'legal_instrument', 'authority', 'population_completeness'])
        for cid, c in claims.items()]
    return dict(profile='CompanyClaimRelationshipInspection/1', status='inspected',
        input_sha256=expected_digest, source_sha256=hashlib.sha256(source).hexdigest(),
        input=deepcopy(path), native_result=wire(answer), event_nodes=nodes,
        claim_nodes=claim_nodes, relation_edges=edges, claim_guard_dependencies=guards,
        prefixes=prefixes, year_ends=year_ends,
        uninspected_executed_kinds=sorted(uninspected),
        scope='Executed trade-claim relationships and amounts; native executor retains all guards and refusals',
        generic_preconditions_complete=False, executable_reduction=None,
        real_behavior_evidence=False, historical_admission=False, actor_information_admission=False,
        legal_identity_admission=False, population_coverage='supplied synthetic path only')
