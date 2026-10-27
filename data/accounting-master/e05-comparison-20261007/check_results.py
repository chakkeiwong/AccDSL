#!/usr/bin/env python3
"""Check source anchors and independent financial/tag constraints in the bounded search."""
import hashlib
import json
import time
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
start = time.monotonic()
d = json.loads((OUT/'statement-comparisons.json').read_text())
i = json.loads((OUT/'inline-comparisons.json').read_text())
checks = []


def check(label, ok):
    checks.append({'check': label, 'passed': bool(ok)})


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


for source in d['documents']:
    for field in ['original', 'input_text', 'visible']:
        check(source['document_id']+' '+field+' identity', sha(ROOT/source[field+'_path']) == source[field+'_sha256'])
    check(source['document_id']+' distinct dated columns', len(set(source['dates'])) == 2)
groups = defaultdict(dict)
ids = {}
for o in d['observations']:
    text = (ROOT/o['visible_path']).read_text()
    check(o['id']+' exact quote', text[slice(*o['span'])] == o['quote'])
    groups[o['document_id'], o['date']][o['metric']] = o['displayed_value']
    ids[o['id']] = o
for (doc, date), x in groups.items():
    check(doc+' '+date+' five scoped captions', set(x) == {'assets', 'liabilities', 'equity', 'current_assets', 'cash_caption'})
    # This identity is independently required by these consolidated statements.
    check(doc+' '+date+' displayed balance identity', x['assets'] == x['liabilities']+x['equity'])
for pair in d['pairs']:
    x, y = ids[pair['left']], ids[pair['right']]
    check(pair['left']+' / '+pair['right']+' comparison context',
          x['document_id'] != y['document_id'] and all(x[k] == y[k] for k in ['issuer','date','metric','unit','basis','perimeter']))
    check(pair['left']+' / '+pair['right']+' values', pair['values'] == [x['displayed_value'],y['displayed_value']])

# Compare statement extraction to independently parsed native tags for both dates.
names = {'assets':'Assets','current_assets':'AssetsCurrent','liabilities':'Liabilities',
         'equity':'StockholdersEquity','cash_caption':'CashAndCashEquivalentsAtCarryingValue'}
for date in ['2024-12-28','2024-09-28']:
    for metric, concept in names.items():
        matches = [f for f in i['facts'] if f['key'][0] == '{http://fasb.org/us-gaap/2024}'+concept
                   and f['key'][1][2] == [['xbrli:instant', date]] and not f['key'][1][3]]
        vals = {Decimal(f['value'])/1000000 for f in matches}
        check('native fact agrees '+date+' '+metric,
              vals == {Decimal(groups['apple-2025-q1',date][metric])})
check('all numeric occurrences accounted for', len(i['facts'])+len(i['exclusions']) == 525)
check('all 31 planned statements and 310 observations retained', len(d['documents']) == 31 and len(d['observations']) == 310 and not d['exclusions'])
check('all duplicate-group references exist', all(f in {x['id'] for x in i['facts']} for g in i['duplicate_groups'] for f in g['fact_ids']))
result = {'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),
          'wall_seconds':time.monotonic()-start,'checks':checks,
          'limits':'Scoped source/consistency checks; no semantic accuracy or conflict-absence claim.'}
(OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:result[k] for k in ['passed','failed','wall_seconds']})
assert result['failed']==0, [c for c in checks if not c['passed']]
