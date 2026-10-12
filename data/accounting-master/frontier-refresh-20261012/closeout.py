"""Bind the frontier review and advance live next-action text."""
import datetime
import hashlib
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n, o): (OUT / n).write_text(json.dumps(o, indent=2) + '\n')
assert not (OUT / 'completion.json').exists()
b = json.loads((OUT / 'baseline.json').read_text())
old = '''Audit the latest evidence and dependencies for E01/E05/E07/E08/E14, correct
stale live instructions and execute an independent ready source/specification
unit. Preserve Version 2.44 and all held implementation boundaries. Plan:
`docs/plans/accounting-frontier-refresh-20261012.md`.'''
new = '''Read the original TableFormer technical method/evaluation and reconcile its
reported TEDS figures with the retained model card and official 4.0.2 loader.
Preserve Version 2.44 and keep local performance/runtime claims unevaluated.
Plan: `docs/plans/accounting-tableformer-paper-20261012.md`.'''
summary = '''## Current frontier after Version 2.44

The five-workstream review is complete. The next substantive unit is E08/E14:
the original TableFormer paper remains deferred in the historical literature
ledger despite later loader/model preparation. Read its method/evaluation and
compare the reported score, text source and decoder with the pinned consumer.
This is source preparation, not installation or a parser ranking. E01's latest
Chapter 2 crosswalk has 130 assertion, 164 query and 208 source/provenance
records; the older 32-assertion selection is a narrower historical population.
Forty exhibit targets, the frozen 56/136 date split, genuine conflict, wider
accounting and four blocked papers remain open. Readiness is not_ready.
Result: `data/accounting-master/frontier-refresh-20261012/result.md`.

'''
rows = []
for r in b['pointer_snapshots']:
    p = ROOT / r['live']; assert sha(p) == r['sha256'] == sha(ROOT / r['snapshot'])
    s = p.read_text()
    anchor = {'accounting-master-current.md': '## Exact next action', 'accounting-master-checkpoint.md': '## Next bounded unit',
              'next-plan.md': '## Next bounded unit', 'accounting-continuation-requirements-20261007.md': '## Current Version 2.44 score-rounding explanation'}[p.name]
    assert s.count(anchor) == 1; s = s.replace(anchor, summary + anchor, 1)
    if p.name != 'accounting-continuation-requirements-20261007.md':
        assert s.count(old) == 1; s = s.replace(old, new, 1)
    if p.name == 'accounting-master-current.md':
        s = s.replace('next unit reviews the five-workstream frontier', 'frontier reviewed; next unit reconciles TableFormer paper and loader', 1)
        s = s.replace('Expand the note-by-note assertion and query map beyond the 32 selected assertions;',
                      'Extend the current 130-assertion/164-query Chapter 2 crosswalk (the earlier 32 selected assertions were a narrower population);', 1)
        s = s.replace('Match the remaining manuscript claims to technically inspected sources.',
                      'Next inspect the original TableFormer method/evaluation and reconcile it with the pinned loader and model-card score; then match remaining manuscript claims to technically inspected sources.', 1)
        s = s.replace('1. Follow the direct next plan: review all five remaining workstreams after\n   Version 2.44 and execute an independent ready source/specification unit.',
                      '1. Follow the direct next plan: reconcile the original TableFormer paper,\n   model-card score and pinned loader after the completed frontier review.', 1)
        s = s.replace('refresh the wider frontier before selecting another source unit.',
                      'the frontier review selects independent TableFormer literature/consumer work next.', 1)
    p.write_text(s); q = OUT / 'pointers-after' / r['live']; q.parent.mkdir(parents=True, exist_ok=True); q.write_bytes(p.read_bytes())
    rows.append({'live': r['live'], 'snapshot': str(q.relative_to(ROOT)), 'sha256': sha(q)})
save('controls-after.json', rows)
deps = ['data/accounting-master/e05-comparison-20261007/result.md',
        'data/accounting-master/chapter2-source-crosswalk-20261010/result.md',
        'data/accounting-master/apple-constitutional-sources-20261011/next-source-frontier.md',
        'data/accounting-master/authority-literature-20261008/result.md',
        'data/accounting-master/bidi-remaining-rust-terms-20261011/result.md',
        'data/accounting-master/tableformer-loader-20261010/result.md',
        'data/accounting-master/docling-model-metadata-20261010/sources/tableformer__README.md',
        'data/accounting-master/bank-score-rounding-integration-20261012/completion.json',
        'docs/design/research/omissions.json', 'docs/design/research/backward-snowball.json',
        'docs/plans/accounting-mission-requirements.md', 'scripts/accounting_master_catalog.json']
plans = ['docs/plans/accounting-frontier-refresh-20261012.md', 'docs/plans/accounting-tableformer-paper-20261012.md']
now = datetime.datetime.now(datetime.timezone.utc)
paths = [p for p in OUT.rglob('*') if p.is_file()] + [ROOT / p for p in plans]
manifest = {'git_commit': b['git_commit'], 'started_utc': b['started_utc'], 'closed_utc': now.isoformat(),
    'plans': plans, 'result': str((OUT / 'result.md').relative_to(ROOT)),
    'command': ['python3', str(Path(__file__).relative_to(ROOT))],
    'environment': {'python': sys.executable, 'version': platform.python_version()},
    'cpu_gpu': 'CPU documentary review; no framework or device use', 'seeds': 'N/A: deterministic review',
    'wall_seconds': (now - datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),
    'data_version': 'Exact retained results and source ledgers; original records preserved',
    'input_hashes': {rel: sha(ROOT / rel) for rel in deps},
    'artifact_hashes': {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))},
    'workstreams_reviewed': ['E01', 'E05', 'E07', 'E08', 'E14'], 'readiness': 'not_ready', 'next_plan': plans[-1]}
save('run-manifest.json', manifest)
for rel, digest in (manifest['input_hashes'] | manifest['artifact_hashes']).items(): assert sha(ROOT / rel) == digest
save('completion.json', {'status': 'bounded frontier review complete', 'manifest_sha256': sha(OUT / 'run-manifest.json'),
     'bound_artifacts': len(manifest['artifact_hashes']), 'readiness': 'not_ready', 'next_plan': plans[-1]})
print(json.dumps({'workstreams': 5, 'artifacts': len(manifest['artifact_hashes']), 'controls': len(rows)}))
