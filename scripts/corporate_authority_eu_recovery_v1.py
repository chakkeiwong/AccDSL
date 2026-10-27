"""Validate new EU source recovery separately from historical admission evidence."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

REGISTER = 'docs/design/research/p08-v4/source-inspection.json'


def validate_recovery(root, records=None):
    root = Path(root).resolve()
    retained = json.loads((root / REGISTER).read_text())
    d = deepcopy(retained if records is None else records)
    if d != retained or d.get('schema_version') != 'accdsl.p08.eu_recovery.v1':
        raise ValueError('EU recovery differs from retained inspection')
    if d.get('admission_allowed') is not False or not d.get('open_dependencies'):
        raise ValueError('EU recovery cannot grant admission')
    pins = d['source_pins']
    names = [p['path'] for p in pins]
    if len(names) != len(set(names)):
        raise ValueError('duplicate EU recovery pin')
    for pin in pins:
        path = Path(pin['path'])
        target = (root / path).resolve()
        if path.is_absolute() or '..' in path.parts or not target.is_relative_to(root):
            raise ValueError('unsafe EU recovery path')
        if sha256(target.read_bytes()).hexdigest() != pin['sha256']:
            raise ValueError('stale EU recovery source')
    previous = json.loads((root / d['previous_register']).read_text())
    rows = d['sources']
    if len({r['id'] for r in rows}) != len(rows) or {r['id'] for r in rows} != {r['id'] for r in previous['missing_authority']}:
        raise ValueError('incomplete EU recovery coverage')
    for row in rows:
        if row['text'] is not None and row['text'] not in names:
            raise ValueError('unpinned recovered text')
        if row['status'] == 'selected_primary_sections_inspected' and not row['anchors']:
            raise ValueError('unanchored inspection')
        if row['status'] not in {'selected_primary_sections_inspected', 'retained_uninspected', 'unavailable'}:
            raise ValueError('unknown source inspection status')
        for anchor in row['anchors']:
            if anchor['text'] != row['text'] or not anchor['section'] or not anchor['quote'].strip():
                raise ValueError('invalid EU recovery anchor')
            text = (root / anchor['text']).read_text()
            if ' '.join(anchor['quote'].split()) not in ' '.join(text.split()):
                raise ValueError('unresolved EU recovery quote')
    return d
