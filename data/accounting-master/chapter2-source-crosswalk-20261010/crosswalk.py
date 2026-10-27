"""Enumerate source records without inferring manuscript support.

Author dispositions are an explicit, separately maintained input. JSON pointers
identify records; source spans and nested claims have different record kinds.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def enumerate_records():
    supplements = sorted((ROOT / 'data/accounting-master').glob('apple-*/source-claim-supplement.json'))
    ledgers = sorted((ROOT / 'data/accounting-master').glob('apple-*/claim-query-ledger.json'))
    assert len(supplements) == 19 and len(ledgers) == 5
    paths = sorted(supplements + ledgers + [ROOT / 'data/accounting-master/apple-revenue-20261008/revenue-history.json'])
    inventory, rows = [], []
    for path in paths:
        name = str(path.relative_to(ROOT))
        digest = sha(path)
        data = json.loads(path.read_text())
        inventory.append(dict(path=name, sha256=digest))

        def add(pointer, kind, record):
            rid = record.get('id', record.get('query', pointer)) if isinstance(record, dict) else pointer
            rows.append(dict(identity=name + '#' + pointer, input_path=name,
                             input_sha256=digest, json_pointer=pointer,
                             record_kind=kind, record_id=rid, content=record))

        for key in ('units', 'material_units'):
            for i, record in enumerate(data.get(key, [])):
                add(f'/{key}/{i}', 'retained_source_unit', record)
        for key in ('claims', 'narrative_claims'):
            for i, record in enumerate(data.get(key, [])):
                add(f'/{key}/{i}', 'explicit_assertion', record)
        for i, matter in enumerate(data.get('matters', [])):
            add(f'/matters/{i}', 'legal_source_body', {k: v for k, v in matter.items() if k != 'assertions'})
            for j, record in enumerate(matter['assertions']):
                add(f'/matters/{i}/assertions/{j}', 'legal_assertion', record)
        for i, record in enumerate(data.get('body', {}).get('paragraphs', [])):
            add(f'/body/paragraphs/{i}', 'retained_source_paragraph', record)
        for i, record in enumerate(data.get('queries', [])):
            add(f'/queries/{i}', 'query', record)
    assert len(rows) == len({r['identity'] for r in rows})
    assert sum(r['record_kind'] == 'query' for r in rows) == 164
    assert sum(r['record_kind'] == 'legal_assertion' for r in rows) == 39
    return inventory, rows


def main():
    inventory, rows = enumerate_records()
    review_path = OUT / 'author-dispositions.json'
    groups = json.loads(review_path.read_text()) if review_path.exists() else []
    assigned = {}
    for group in groups:
        assert group['disposition'] in {'exact_support', 'mechanism_reuse', 'source_only', 'structural_provenance', 'missing_bridge'}
        assert group['reason'].strip()
        for anchor in group.get('anchors', []):
            p = ROOT / anchor['path']
            text = p.read_text()
            assert anchor['quote'] in text, (group['id'], anchor['quote'])
            anchor['sha256'] = sha(p)
            anchor['line'] = text[:text.index(anchor['quote'])].count('\n') + 1
        if group['disposition'] in {'exact_support', 'mechanism_reuse'}:
            assert group.get('anchors'), group['id']
        for identity in group['records']:
            assert identity not in assigned, identity
            assigned[identity] = group['id']
    ids = {r['identity'] for r in rows}
    assert set(assigned) <= ids
    for row in rows:
        row['author_disposition_group'] = assigned.get(row['identity'])
    save('ledger-inventory.json', dict(inputs=inventory, input_count=len(inventory),
        scope='19 completed Apple units; 19 supplements, five claim ledgers, revenue-history queries',
        excluded='Insurance/literature supplements; numeric tables and external facts are not new claim rows'))
    save('claim-query-crosswalk.json', dict(rows=rows, author_groups=groups,
        counts_by_kind=dict(Counter(r['record_kind'] for r in rows)),
        pending=sum(r['author_disposition_group'] is None for r in rows),
        semantic_completeness=False, independent_reader='pending', readiness='not_ready'))
    print(json.dumps(dict(inputs=len(inventory), counts=dict(Counter(r['record_kind'] for r in rows)),
                         assigned=len(assigned), pending=len(rows)-len(assigned))))


if __name__ == '__main__':
    main()
