#!/usr/bin/env python3
"""Freeze the external exports needed by the authored debt IR example."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / 'docs/design/fixtures'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False).encode('utf-8')


def build():
    records = []

    def inline(identifier, kind, value):
        records.append(dict(id=identifier, kind=kind, value=value,
                            sha256=hashlib.sha256(canonical(value)).hexdigest(),
                            artifact=None, pointer=None))

    def bound(identifier, kind, filename, pointer):
        p = FIX / filename
        records.append(dict(id=identifier, kind=kind, artifact=str(p.relative_to(ROOT)),
                            sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                            pointer=pointer, value=None))

    inline('builtin:Core0@1', 'Library', {'version': '0.1', 'pure': True})
    inline('builtin:value@1', 'Builtin', {'arguments': ['Observation<T>'], 'result': 'T'})
    inline('builtin:constant@1', 'Builtin', {'arguments': ['T'], 'result': 'Driver<T>'})
    inline('DemoCalendar@1', 'Calendar', {'calendar': 'Gregorian',
           'one_year': ['2026-01-01', '2027-01-01'], 'instant': 'end_of_day'})
    inline('fixture:empty-view', 'EvidenceView', {'documents': [], 'observations': [], 'decisions': []})
    for value in [0, 1]:
        inline(f'fixture:alpha={value}', 'Witness', {'alpha': {'n': str(value), 'd': '1'}})
    package = 'demo-debt-package.json'
    bound('fixture:demo-debt-package.json', 'SourceRef', package, '')
    bound('fixture:synthetic-note-7/exact-reading', 'Reading', package, '/registry/synthetic-note-7')
    bound('DemoDebt@1/DebtMix', 'ContractType', package, '/DebtMix')
    for index, name in enumerate(['reset', 'accrue_and_pay', 'close']):
        bound('DemoDebt@1/' + name, 'Operation', package, f'/DebtMix/operations/{index}')
    bound('DemoDebt@1/statements', 'Operation', package, '/registry/DemoDebt.statements.v1')
    bound('DemoDebt@1/interest_operating', 'CashFlowPolicy', package,
          '/registry/DemoDebt.statements.v1/cash_flow')
    bound('DemoDebt.statements.v1', 'SourceRef', package, '/registry/DemoDebt.statements.v1')
    bound('fixture:borrowings.json#exact', 'ReferenceResult', 'borrowings.json', '/exact')
    return {'version': '1', 'profile': 'authored-debt-example', 'records': records,
            'limits': 'Frozen example exports; not a general package loader or executed third-party integration.'}


if __name__ == '__main__':
    p = FIX / 'core-demo-registry.json'
    p.write_text(json.dumps(build(), indent=2) + '\n')
    print(p.relative_to(ROOT))
