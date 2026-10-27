"""Write six explicit retained-chart rule sets; never run native eligibility."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import json
import gate as g

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + chr(10))

def ref(name): return {'op': 'ref', 'id': name}
def binary(op, left, right): return {'op': op, 'left': ref(left), 'right': ref(right)}
def event(name): return {'kind': 'event_input', 'name': name}
def metadata(field): return {'kind': 'event_metadata', 'field': field}
def memory(pointer): return {'kind': 'memory_leaf', 'pointer': pointer}
def membership(): return {'kind': 'map_contains', 'pointer': '/claims', 'key_input': 'claim_id'}

def stage(name, reason, inputs, predicate, consequence='invalid'):
    return {'id': name, 'reason': reason,
            'bindings': {key: source for key, (typ, source) in inputs.items()},
            'manifest': {'profile': g.guarded.PROFILE, 'method_id': 'eligibility.'+name, 'version': '1',
                         'inputs': {key: {'type': g.base.dimensions.encoded(typ), 'role': 'state',
                                          'source_ref': 'Explicit binding evaluated against the current full intent and typed book'}
                                    for key, (typ, source) in inputs.items()},
                         'requirements': [{'id': name, 'guard': {'op': 'const', 'type': g.BOOL, 'value': True},
                                           'guard_requires': [], 'predicate': predicate, 'requires': list(inputs),
                                           'admission_refs': [], 'on_false': consequence, 'on_unknown': 'unresolved'}],
                         'required_known': [], 'capabilities': [],
                         'residual_prerequisites': ['Selected synthetic contract; lifecycle invariants and accounting admission remain separate']}}

def build(book, kind, input_types):
    rows = [stage('approval', 'applicability_not_selected', {'approved': (g.BOOL, event('approved'))}, ref('approved'), 'unsupported')]
    if kind in ('sale', 'collect'):
        rows.append(stage('unsealed_day', 'assessment_day_sealed',
                          {'cursor': (g.DATE, memory('/collection_clock/cursor')), 'day': (g.DATE, metadata('date'))},
                          binary('le', 'cursor', 'day')))
    if kind == 'sale':
        rows.extend([
            stage('sale_due', 'due_before_sale', {'day': (g.DATE, metadata('date')), 'due': (g.DATE, event('due'))}, binary('le', 'day', 'due')),
            stage('claim_absent', 'duplicate_claim', {'exists': (g.BOOL, membership())}, {'op': 'not', 'arg': ref('exists')})])
    elif kind == 'collect':
        rows.extend([
            stage('claim_exists', 'unknown_claim', {'exists': (g.BOOL, membership())}, ref('exists')),
            stage('customer_matches', 'claim_customer_mismatch',
                  {'customer': (g.TEXT, event('customer')),
                   'owner': (g.TEXT, {'kind': 'map_field', 'pointer': '/claims', 'key_input': 'claim_id',
                                      'field': 'customer', 'after_stage': 'claim_exists'})}, binary('eq', 'customer', 'owner'))])
    elif kind == 'assess':
        rows.extend([
            stage('assessment_cursor', 'assessment_cursor',
                  {'start': (g.DATE, event('start')), 'cursor': (g.DATE, memory('/collection_clock/cursor'))}, binary('eq', 'start', 'cursor')),
            stage('assessment_window', 'assessment_window',
                  {'start': (g.DATE, event('start')), 'end': (g.DATE, event('end_exclusive')),
                   'adjacent': (g.BOOL, {'kind': 'calendar_adjacent', 'left': metadata('date'), 'right': event('end_exclusive')})},
                  {'op': 'all', 'args': [binary('lt', 'start', 'end'), ref('adjacent')]}),
            stage('period_end', 'assessment_crosses_period',
                  {'end': (g.DATE, event('end_exclusive')), 'period': (g.DATE, {'kind': 'period_end'})}, binary('le', 'end', 'period'))])
    else: raise ValueError(kind)
    return dict(profile=g.PROFILE, context=deepcopy(book['context']), operation=kind,
                input_types=deepcopy(input_types), stages=rows,
                residuals=['Finite declared lifecycle; full state invariants are separate prerequisites',
                           'No accounting, source or general language admission'])

def main():
    assert not (HERE/'templates').exists(), 'Do not rerun completed preparation'
    audit = HERE.parent/'event-specialization-audit-20261026'
    rows = json.loads((audit/'request-comparisons.json').read_text())
    provenance = []
    for company in ('alpha', 'beta'):
        for kind in ('sale', 'collect', 'assess'):
            row = next(r for r in rows if r['company'] == company and r['method'] == kind)
            inputs = {name: value['type'] for name, value in row['full_command']['event']['inputs'].items()}
            template = build(row['before'], kind, inputs)
            g.compile_template(template, row['before'], row['body_parameters']['memory_definition'])
            path = HERE/f'templates/{company}.{kind}.json'; dump(path, template)
            provenance.append(dict(template=str(path.relative_to(ROOT)), template_sha256=g.core.digest(template),
                                   event_types_from=str((audit/'request-comparisons.json').relative_to(ROOT)),
                                   company=company, command_index=row['index'],
                                   rule_source='scripts/declared_receivable_lifecycle_v1.py:run,make_request',
                                   construction='Explicit declarations, no native specializer execution'))
    lock = {}
    for directory in ('event-eligibility-audit-20261026', 'parameterized-method-construction-20261026', 'ordered-assessment-expansion-20261026'):
        p = HERE.parent/directory; lock.update(json.loads((p/'source-lock.json').read_text()))
        for source in p.iterdir():
            if source.is_file() and source.suffix in ('.py', '.json', '.md'):
                lock[str(source.relative_to(ROOT))] = sha256(source.read_bytes()).hexdigest()
        for source in (p/'templates').glob('*.json'):
            lock[str(source.relative_to(ROOT))] = sha256(source.read_bytes()).hexdigest()
    for name, expected in lock.items(): assert sha256((ROOT/name).read_bytes()).hexdigest() == expected, name
    dump(HERE/'source-lock.json', lock); dump(HERE/'template-provenance.json', provenance)
    print(json.dumps(dict(templates=len(provenance), protected_files=len(lock))))

if __name__ == '__main__': main()
