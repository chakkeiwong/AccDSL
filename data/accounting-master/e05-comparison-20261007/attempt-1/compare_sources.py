#!/usr/bin/env python3
"""Bounded source comparison aid. No filing or product records are modified."""
import hashlib
import itertools
import json
import platform
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
COVERAGE = ROOT / 'data/financial-report-benchmark/coverage.json'
START = time.monotonic()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, data):
    (OUT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')


def norm(text):
    return ' '.join(text.split())


MONTH = r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
NUMBER = r'\(?-?\d[\d,]*(?:\.\d+)?\)?'
METRICS = {
    'assets': r'Total assets',
    'current_assets': r'Total current assets',
    'liabilities': r'Total liabilities',
    'equity': r'Total (?:shareholders|stockholders)[’\x27]\s*equity',
    'cash_caption': r'Cash and (?:cash equivalents|short-term investments)',
}
rows = json.loads(COVERAGE.read_text())['rows']
selected = [r for r in rows if r['local_path'].endswith('.html')]
inventory = []
soups = {}
for row in selected:
    p = ROOT / row['local_path']
    assert sha(p) == row['sha256'], row['document_id']
    s = BeautifulSoup(p.read_bytes(), 'html.parser')
    soups[row['document_id']] = s
    inventory.append({
        'document_id': row['document_id'], 'issuer': row['issuer_id'],
        'path': row['local_path'], 'sha256': sha(p),
        'inline_numeric_count': len(s.find_all('ix:nonfraction')),
        'format': 'inline_numeric_html' if s.find('ix:nonfraction') else 'html_without_inline_numeric_tags',
    })
write('format-inventory.json', {
    'coverage_path': str(COVERAGE.relative_to(ROOT)), 'coverage_sha256': sha(COVERAGE),
    'scope': 'Selected HTML paths in active coverage, not all retained versions',
    'selected_html_reports': len(selected), 'by_issuer': dict(Counter(x['issuer'] for x in inventory)),
    'documents': inventory,
})

# Added annual comparators are selected corpus slots, never alternative versions.
annual_ids = {f'apple-{y}-annual' for y in [2018, 2020, 2021, 2022, 2023, 2024]}
annual_ids.add('caterpillar-2024-annual')
selected += [r for r in rows if r['document_id'] in annual_ids]
assert len(selected) == len({r['document_id'] for r in selected})
observations, documents, exclusions = [], [], []
for row in selected:
    p = ROOT / row['local_path']
    assert sha(p) == row['sha256'], row['document_id']
    if p.suffix == '.html':
        raw = soups[row['document_id']].get_text(' ', strip=True)
        raw_path = row['local_path']
    else:
        raw_path = row['extracted_text_path']
        raw = (ROOT / raw_path).read_text()
    t = norm(raw)
    output_name = row['document_id'] + '.visible.txt'
    (OUT / output_name).write_text(t)
    heading = (r'(?:CONDENSED )?CONSOLIDATED BALANCE SHEETS' if row['issuer_id'] == 'apple'
               else r'CONSOLIDATED FINANCIAL POSITION')
    # Require all five captions after the heading, before the notes footer.
    blocks = []
    for m in re.finditer(heading, t, re.I):
        tail = t[m.start():]
        end = re.search(r'See accompanying [Nn]otes', tail)
        if end is None:
            continue
        block = tail[:end.end()]
        if len(block) > 16000:
            continue
        if all(re.search(v + r'\s*\$?\s*' + NUMBER, block, re.I) for v in METRICS.values()):
            blocks.append((m.start(), m.start() + len(block), block))
    if len(blocks) != 1:
        exclusions.append({'document_id': row['document_id'], 'reason': 'statement_block_not_unique', 'count': len(blocks)})
        continue
    a, b, block = blocks[0]
    cash_at = re.search(METRICS['cash_caption'], block, re.I).start()
    header = block[:cash_at]
    if not re.search(r'(?:[Ii]n|[Dd]ollars in) millions', header):
        exclusions.append({'document_id': row['document_id'], 'reason': 'million_scale_not_confirmed', 'header': header})
        continue
    dates = re.findall(MONTH + r'\s+\d{1,2},\s*\d{4}', header)
    if len(dates) == 2:
        ds = [datetime.strptime(re.sub(r',\s*', ', ', x), '%B %d, %Y').date().isoformat() for x in dates]
    else:
        monthdays = re.findall(MONTH + r'\s+\d{1,2},?', header)
        years = re.findall(r'\b20\d{2}\b', header)
        if len(monthdays) == 1 and row['issuer_id'] == 'caterpillar':
            monthdays *= 2
        if len(monthdays) != 2 or len(years) != 2:
            exclusions.append({'document_id': row['document_id'], 'reason': 'two_date_columns_not_confirmed', 'header': header})
            continue
        ds = [datetime.strptime(md.rstrip(',') + ', ' + y, '%B %d, %Y').date().isoformat() for md, y in zip(monthdays, years)]
    source = {
        'document_id': row['document_id'], 'original_path': row['local_path'], 'original_sha256': sha(p),
        'input_text_path': raw_path, 'input_text_sha256': sha(ROOT / raw_path),
        'visible_path': str((OUT / output_name).relative_to(ROOT)), 'visible_sha256': sha(OUT / output_name),
        'statement_span': [a, b], 'header': header, 'dates': ds,
        'standard_family': row['standard_family'], 'perimeter': 'consolidated',
        'unit': 'USD million', 'unit_basis': 'Issuer US consolidated statement; in-millions heading retained',
        'precision': 'Displayed integer millions; underlying rounding rule not inferred',
        'source_url': row['source_url'],
    }
    documents.append(source)
    for metric, pattern in METRICS.items():
        hits = list(re.finditer(r'(' + pattern + r')\s*\$?\s*(' + NUMBER + r')\s*\$?\s*(' + NUMBER + r')(?![\d,])', block, re.I))
        if len(hits) != 1:
            exclusions.append({'document_id': row['document_id'], 'metric': metric, 'reason': 'row_not_unique', 'count': len(hits)})
            continue
        m = hits[0]
        for col in range(2):
            lex = m.group(col + 2)
            value = int(lex.replace(',', '').replace('(', '-').replace(')', ''))
            observations.append({
                'id': f'{row["document_id"]}:{metric}:{col}', 'document_id': row['document_id'],
                'issuer': row['issuer_id'], 'metric': metric, 'caption': m.group(1), 'date': ds[col],
                'displayed_value': value, 'unit': 'USD million', 'basis': row['standard_family'],
                'perimeter': 'consolidated', 'column_zero_based': col,
                'visible_path': source['visible_path'], 'span': [a+m.start(), a+m.end()], 'quote': m.group(),
            })

groups = defaultdict(list)
for o in observations:
    key = (o['issuer'], o['date'], o['metric'], o['caption'].lower().replace('’', "'"), o['unit'], o['basis'], o['perimeter'])
    groups[key].append(o)
pairs = []
for key, obs in sorted(groups.items()):
    for x, y in itertools.combinations(obs, 2):
        if x['document_id'] == y['document_id']:
            continue
        pairs.append({'left': x['id'], 'right': y['id'], 'context_key': key,
                      'values': [x['displayed_value'], y['displayed_value']],
                      'status': 'equal_displayed_amounts' if x['displayed_value'] == y['displayed_value'] else 'unequal_nomination_requires_review'})
write('statement-comparisons.json', {
    'scope': 'Five consolidated balance-sheet captions, 24 selected HTML reports plus seven selected annual PDF comparators',
    'documents': documents, 'observations': observations, 'exclusions': exclusions, 'pairs': pairs,
    'summary': {'documents_attempted': len(selected), 'documents_extracted': len(documents), 'observations': len(observations),
                'pairs': len(pairs), 'unequal_nominations': sum(p['status'].startswith('unequal') for p in pairs), 'exclusions': len(exclusions)},
    'limits': 'Caption/date/unit matching nominates comparisons only. Equal values do not establish accounting truth or corpus-wide consistency.',
})

# Inspect the one tagged source. All observed supported transforms are explicit.
s = soups['apple-2025-q1']
ns = {k[6:]: v for k, v in s.find('html').attrs.items() if k.startswith('xmlns:')}


def qname(v):
    prefix, local = v.split(':', 1)
    if prefix not in ns:
        raise ValueError('unknown namespace ' + prefix)
    return '{' + ns[prefix] + '}' + local


contexts = {}
for c in s.find_all('xbrli:context'):
    ident = c.find('xbrli:identifier')
    period = c.find('xbrli:period')
    if c.find('xbrldi:typedmember'):
        continue
    # Non-dimensional segment/scenario content would need another normalization.
    members = c.find_all('xbrldi:explicitmember')
    extras = [x for box in c.find_all(['xbrli:segment', 'xbrli:scenario']) for x in box.find_all(recursive=False) if x.name != 'xbrldi:explicitmember']
    if extras:
        continue
    dims = sorted((qname(x['dimension']), qname(x.get_text(strip=True))) for x in members)
    contexts[c['id']] = (ident.get('scheme'), ident.get_text(strip=True),
                         tuple((x.name, x.get_text(strip=True)) for x in period.find_all(recursive=False)), tuple(dims))
units = {}
for u in s.find_all('xbrli:unit'):
    if u.find('xbrli:divide'):
        num = u.find('xbrli:unitnumerator'); den = u.find('xbrli:unitdenominator')
        units[u['id']] = (tuple(sorted(qname(x.get_text(strip=True)) for x in num.find_all('xbrli:measure'))),
                          tuple(sorted(qname(x.get_text(strip=True)) for x in den.find_all('xbrli:measure'))))
    else:
        units[u['id']] = (tuple(sorted(qname(x.get_text(strip=True)) for x in u.find_all('xbrli:measure'))), ())
facts, rejected = [], []
for f in s.find_all('ix:nonfraction'):
    try:
        if f.get('xsi:nil') in ['true', '1']:
            raise ValueError('nil fact; not numerical agreement')
        if f.find('ix:exclude') or f.get('continuedat'):
            raise ValueError('excluded/continued content requires separate reading')
        fmt = qname(f['format']) if f.get('format') else None
        accepted = {'{http://www.xbrl.org/inlineXBRL/transformation/2020-02-12}num-dot-decimal',
                    '{http://www.xbrl.org/inlineXBRL/transformation/2020-02-12}fixed-zero', None}
        if fmt not in accepted:
            raise ValueError('unsupported transform ' + str(fmt))
        literal = f.get_text('', strip=True)
        value = Decimal(0) if fmt and fmt.endswith('}fixed-zero') else Decimal(literal.replace(',', ''))
        value *= Decimal(10) ** int(f.get('scale', '0'))
        if f.get('sign') == '-':
            value = -value
        decimals = f.get('decimals')
        if decimals is None:
            raise ValueError('decimals absent')
        radius = Decimal(0) if decimals == 'INF' else Decimal('0.5') * Decimal(10) ** -int(decimals)
        key = (qname(f['name']), contexts[f['contextref']], units[f['unitref']])
        facts.append({'id': f.get('id'), 'key': key, 'context_id': f['contextref'], 'unit_id': f['unitref'],
                      'literal': literal, 'format': fmt, 'sign': f.get('sign'), 'scale': f.get('scale'),
                      'decimals': decimals, 'value': str(value), 'interval': [str(value-radius), str(value+radius)]})
    except (ValueError, KeyError, ArithmeticError) as exc:
        rejected.append({'id': f.get('id'), 'reason': str(exc)})
fgroups = defaultdict(list)
for f in facts:
    fgroups[json.dumps(f['key'])].append(f)
duplicates = []
for key, fs in fgroups.items():
    if len(fs) < 2:
        continue
    lower = max(Decimal(f['interval'][0]) for f in fs)
    upper = min(Decimal(f['interval'][1]) for f in fs)
    duplicates.append({'key': json.loads(key), 'fact_ids': [f['id'] for f in fs],
                       'values': [f['value'] for f in fs], 'decimals': [f['decimals'] for f in fs],
                       'nominal_interval_intersection': [str(lower), str(upper)],
                       'status': 'disjoint_nomination_requires_review' if lower > upper else 'compatible_nominal_decimals_intervals'})
write('inline-comparisons.json', {
    'source': next(x for x in inventory if x['document_id'] == 'apple-2025-q1'),
    'facts': facts, 'exclusions': rejected, 'duplicate_groups': duplicates,
    'summary': {'numeric_facts': len(s.find_all('ix:nonfraction')), 'parsed': len(facts), 'excluded': len(rejected),
                'duplicate_groups': len(duplicates), 'disjoint_nominations': sum(x['status'].startswith('disjoint') for x in duplicates)},
    'limits': 'Nomination aid only, not full XBRL validation. Closed half-unit intervals screen stated decimals; endpoint-only overlap is inconclusive. Underlying economic precision and correctness are not inferred.',
})
receipt = {'command': [sys.executable, str(Path(__file__).relative_to(ROOT))],
           'finished_at': datetime.now(timezone.utc).isoformat(), 'wall_seconds': time.monotonic()-START,
           'python': platform.python_version(), 'platform': platform.platform(), 'gpu': 'No GPU/framework used',
           'git_commit': None, 'git_status': 'Unusable pre-existing .git marker; no repository changes',
           'random_seeds': 'N/A deterministic', 'plan': 'docs/plans/accounting-e05-source-comparison-20261007.md',
           'script_sha256': sha(Path(__file__)), 'data_sha256': sha(COVERAGE)}
write('run-receipt.json', receipt)
print(json.dumps({'statement': json.loads((OUT/'statement-comparisons.json').read_text())['summary'],
                  'inline': json.loads((OUT/'inline-comparisons.json').read_text())['summary'],
                  'wall_seconds': receipt['wall_seconds']}))
