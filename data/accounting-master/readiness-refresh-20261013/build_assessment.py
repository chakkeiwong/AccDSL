"""Assemble an author supplement from explicit, individually written dispositions."""
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UNIT = Path(__file__).resolve().parent
if (UNIT / 'completion.json').exists():
    raise SystemExit('Completed unit; preserve its evidence.')

def read(path):
    return json.loads((ROOT / path).read_text())

def digest(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()

def write(name, data):
    (UNIT / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')

old = read('data/accounting-master/deliverables/P19/readiness.json')
updates = json.loads((UNIT / 'row-updates.json').read_text())
gupdates = json.loads((UNIT / 'gap-updates.json').read_text())
requirements_path = 'docs/plans/accounting-mission-requirements.md'
original = {}
for line in (ROOT / requirements_path).read_text().splitlines():
    if re.match(r'\| MC\d\d \|', line):
        cols = [c.strip() for c in line.split('|')[1:-1]]
        original[cols[0]] = cols
aliases = {
    'crosswalk': 'chapter2-source-crosswalk-20261010',
    'jpmorgan': 'accounting-package-semantic-annotation-20261011',
    'package': 'accounting-package-ledger-20261011',
    'munich': 'munich-transition-disclosures-20261012',
    'dates': 'publication-frontier-20261013',
    'munich_dates': 'munich-publication-imprints-20261012',
    'lease': 'pingan-lease-transition-20261013',
    'fx': 'intragroup-fx-20261013',
    'tamer': 'tamer-source-recovery-20261013',
    'caiani': 'caiani-source-recovery-20261013',
    'counterpart': 'pingan-2019-counterparts-20261013',
}
evidence = {key: {'path': f'data/accounting-master/{name}/result.md',
                  'role': 'Scoped result; no new independent acceptance'}
            for key, name in aliases.items()}
for item in evidence.values():
    item['sha256'] = digest(item['path'])
comparison = json.loads((UNIT / 'prior-source-comparison.json').read_text())
by_old = {x['old_path']: x for x in comparison}
rows = []
for row in old['requirements']:
    identity = row['id']
    change, remaining, dependency, refs = updates[identity]
    assert original[identity][2] == row['acceptance_obligation'], identity
    current_sources = []
    for ref in row['evidence']:
        if ref['path'] in by_old:
            comp = by_old[ref['path']]
            current_sources.append({'path': comp['new_path'],
                                   'sha256': digest(comp['new_path']),
                                   'review_basis': 'Historical judgment carried forward; exact source unchanged' if comp['equal'] else 'Current changed passage/delta inspected; scoped author reassessment'})
    rows.append({'id': identity, 'requirement': original[identity][1],
                 'acceptance_obligation': original[identity][2],
                 'status': row['status'], 'historical_status': row['status'],
                 'status_scope': 'Specified means the bounded contract only; not full acceptance',
                 'retained_contract': row['contract'], 'current_assessment': change,
                 'remaining_work': remaining, 'dependency': dependency,
                 'current_sources': current_sources, 'supplemental_evidence': refs})

gaps = []
for row in old['gaps']:
    identity = row['id']
    path = 'docs/design/review/' + ('gap-audit-2026-10-02.md' if int(identity[1:]) <= 10 else 'mission-gap-audit-2026-10-02.md')
    source = (ROOT / path).read_text()
    section = re.search(r'### ' + identity + r'\. (.*?)(?=\n### |\n## |\Z)', source, re.S).group(1)
    obligation = re.search(r'Required (?:repair|evidence): (.*?)(?=\n\n|\Z)', section, re.S).group(1)
    change, remaining, dependency = gupdates[identity]
    gaps.append({'id': identity, 'title': section.splitlines()[0],
                 'original_obligation': obligation,
                 'original_source': {'path': path, 'sha256': digest(path), 'locator': identity},
                 'requirements': row['requirements'], 'status': row['status'],
                 'historical_status': row['status'],
                 'current_assessment': change, 'remaining_work': remaining,
                 'dependency': dependency})

assessment = {'schema_version': 1, 'date': '2026-10-13',
              'review_class': 'Author supplement, with explicit carried-forward historical judgments',
              'candidate_version': '2.52', 'ready': False, 'status': 'not_ready',
              'independent_review': 'not performed by this unit', 'human_acceptance': 'pending',
              'implementation_enabled': False,
              'original_requirements': {'path': requirements_path, 'sha256': digest(requirements_path)},
              'requirements': rows, 'gaps': gaps, 'evidence': evidence,
              'remaining_blockers': ['E01', 'E05', 'E07', 'E08', 'E14'],
              'next_repair': 'JPMorgan 2023 source-reference conflict and layered review/invalidation walkthrough'}
write('assessment.json', assessment)

lines = ['# Current MC01–MC35 and G1–G18 dispositions', '',
         '13 October 2026. Version 2.52. Author supplement; full readiness **not_ready**.',
         'The original acceptance wording is reproduced exactly in `assessment.json`.',
         'Historical statuses are retained: `specified` applies to a bounded contract, not full acceptance.',
         'Eleven of the 23 directly cited manuscript files are unchanged; their prior judgments are carried forward.',
         'Changed passages and scoped results inform the updates below. This is not a fresh independent review of all 195 pages.', '',
         '| Requirement | Status | Current evidence/change | Residual acceptance and dependency |',
         '| --- | --- | --- | --- |']
for row in rows:
    lines.append(f"| {row['id']} | {row['status']} | {row['current_assessment']} | {row['remaining_work']} **Dependency:** {row['dependency']}. |")
lines += ['', '| Gap | Status | Current evidence/change | Residual acceptance and dependency |', '| --- | --- | --- | --- |']
for row in gaps:
    lines.append(f"| {row['id']} — {row['title']} | {row['status']} | {row['current_assessment']} | {row['remaining_work']} **Dependency:** {row['dependency']}. |")
(UNIT / 'dispositions.md').write_text('\n'.join(lines) + '\n')
index = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
if not (UNIT / 'unrelated-index-before.txt').exists():
    (UNIT / 'unrelated-index-before.txt').write_bytes(index)
print(json.dumps({'requirements': len(rows), 'gaps': len(gaps),
                  'requirement_statuses': dict(Counter(x['status'] for x in rows)),
                  'gap_statuses': dict(Counter(x['status'] for x in gaps))}))
