"""Close the transition reading once; keep all earlier units immutable."""
import datetime
import hashlib
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
assert not (OUT/'completion.json').exists()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value): (OUT/name).write_text(json.dumps(value, indent=2)+'\n')
b = json.loads((OUT/'baseline.json').read_text())
c = json.loads((OUT/'source-checks.json').read_text())
assert c['passed'] == 43 and not c['failed']
for p,h in b['inputs'].items(): assert sha(ROOT/p) == h
old = '''Inspect the retained insurance transition provisions to distinguish full
retrospection, modified retrospection and fair-value transition, including
method-selection and information limits. Preserve the issuer/AASB authority
distinction and Version 2.47. Plan:
`docs/plans/accounting-insurance-transition-source-20261012.md`.'''
new = '''Integrate the checked transition-method and information-limit explanation
in a separate Version 2.48. Preserve Version 2.47, the ASBE/AASB distinction,
C5A/C25 exceptions and the unresolved AASB 108/13 dependencies. Plan:
`docs/plans/accounting-insurance-transition-integration-20261012.md`.'''
note = '''## Latest insurance transition source inquiry

Ten selected AASB 17 pages, including complete Appendix C, support a map of
transition routes and information limits. All 43 preservation/source checks
pass; 25 exact excerpts and six inspected renders are retained. C5A permits
a conditional fair-value election despite feasible retrospection; C25 changes
the transition date for earlier adjusted comparatives. The two AASB 108/13
PDF probes returned 404; the official paginated portal is a new follow-up lead.
No actual group, valuation or impracticability judgment is supplied. Version
2.47 stays current pending 2.48 integration; full readiness remains not_ready.
Result: `data/accounting-master/insurance-transition-source-20261012/result.md`.

'''
prepared = []
for r in b['pointer_snapshots']:
    p=ROOT/r['live']; assert sha(p)==sha(ROOT/r['snapshot'])==r['sha256']
    s=p.read_text(); anchor='## Latest direct-participation and guarantee source inquiry\n\n'
    assert s.count(anchor)==1; s=s.replace(anchor,note+anchor,1)
    if p.name != 'accounting-continuation-requirements-20261007.md':
        assert s.count(old)==1;s=s.replace(old,new,1)
    if p.name=='accounting-master-current.md':
        s=s.replace('next unit inspects insurance transition methods and information limits',
                    'transition source inquiry complete; next integrate Version 2.48')
        s=s.replace('next inspect transition-method information limits.',
                    'transition-method source preparation is complete; next integrate its information limits in Version 2.48.')
        s=s.replace('1. Follow the direct next plan: inspect retained insurance transition methods\n   and their historical-information limits.',
                    '1. Follow the direct next plan: integrate the checked transition explanation\n   in a separate Version 2.48.')
    prepared.append((p,r,s))
rows=[]
for p,r,s in prepared:
    p.write_text(s); q=OUT/'pointers-after'/r['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    rows.append({'live':r['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('controls-after.json',rows)
plans=['docs/plans/accounting-insurance-transition-source-20261012.md',
       'docs/plans/accounting-insurance-transition-integration-20261012.md']
now=datetime.datetime.now(datetime.timezone.utc)
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[ROOT/p for p in plans]
manifest={'git_commit':b['git_commit'],'started_utc':b['started_utc'],'closed_utc':now.isoformat(),
    'plans':plans,'result':str((OUT/'result.md').relative_to(ROOT)),
    'commands':[['python3',str((OUT/n).relative_to(ROOT))] for n in ['prepare_evidence.py','check_source.py','closeout.py']],
    'acquisition_commands':'acquisition.json; four trusted curl requests; 40-second and 12 MB limits',
    'document_processing':'PyMuPDF page.get_text and get_pixmap at 1.3x; at most two pages per inspection/extraction call',
    'environment':{'python':sys.executable,'version':platform.python_version()},
    'cpu_gpu':'CPU document/file processing; no ML import or GPU probe',
    'data_version':'AASB 17 compilation 4, December 2022; stated period-start boundary preserved',
    'random_seeds':'N/A: deterministic source review; no numerical experiment',
    'wall_seconds':{'elapsed_including_review':(now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),
                    'checks':c['wall_seconds']},
    'input_hashes':b['inputs'],
    'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
    'readiness':'not_ready','next_plan':plans[-1]}
save('run-manifest.json',manifest)
for p,h in (manifest['input_hashes']|manifest['artifact_hashes']).items(): assert sha(ROOT/p)==h
save('completion.json',{'status':'bounded transition-source inquiry complete; independent interpretation pending',
    'source_checks':c['passed'],'failed':0,'source_pages':10,'source_anchors':25,'inspected_renders':6,
    'manifest_sha256':sha(OUT/'run-manifest.json'),'bound_artifacts':len(manifest['artifact_hashes']),
    'readiness':'not_ready','next_plan':plans[-1]})
print(json.dumps({'checks':c['passed'],'artifacts':len(manifest['artifact_hashes']),'readiness':'not_ready'}))
