"""Close selected transition dependencies and schedule their material prose."""
import datetime
import hashlib
import json
import platform
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
assert not (OUT/'completion.json').exists()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
b=json.loads((OUT/'baseline.json').read_text());c=json.loads((OUT/'source-checks.json').read_text())
assert c['passed']==55 and not c['failed']
for p,h in b['inputs'].items():assert sha(ROOT/p)==h
old='''Follow the newly acquired official AASB portal/search lead for historically
applicable AASB 108 and AASB 13 primary text. Resolve impracticability/hindsight
and group-fair-value dependencies without repeating the two failed PDF URLs.
Preserve Version 2.48 and the ASBE distinction. Plan:
`docs/plans/accounting-transition-dependencies-20261012.md`.'''
new='''Integrate the newly supported hindsight, market-participant valuation and
own-non-performance-risk distinctions in a separate Version 2.49. Preserve
Version 2.48, historical editions, insurance-specific exceptions and actual
group/valuation limitations. Plan:
`docs/plans/accounting-transition-dependencies-integration-20261012.md`.'''
note='''## Latest transition dependency source inquiry

Eight official requests acquired historical AASB 108 and AASB 13 primary PDFs;
the first 2024-applicable AASB 13 result was excluded from the 2023 comparison.
All 55 source/edition checks pass, with 45 selected pages read, 29 exact anchors
and ten inspected renders. Hindsight differs from an estimate prepared later;
fair value's market-participant and own-credit assumptions differ from issued-
insurance FCF. Actual group judgments, valuation and current applicability
remain open. Version 2.48 stays current pending 2.49 integration; not_ready.
Result: `data/accounting-master/transition-dependencies-20261012/result.md`.

'''
prepared=[]
for r in b['pointer_snapshots']:
    p=ROOT/r['live'];assert sha(p)==r['sha256']==sha(ROOT/r['snapshot']);s=p.read_text()
    anchor='## Latest insurance transition source inquiry\n\n';assert s.count(anchor)==1;s=s.replace(anchor,note+anchor,1)
    if p.name!='accounting-continuation-requirements-20261007.md':assert s.count(old)==1;s=s.replace(old,new,1)
    else:s=s.replace('Next internal unit: `docs/plans/accounting-transition-dependencies-20261012.md`.',
                        'Next internal unit: `docs/plans/accounting-transition-dependencies-integration-20261012.md`.')
    if p.name=='accounting-master-current.md':
        s=s.replace('Version 2.48 integrated; next resolve the AASB 108/13 source dependencies',
                    'AASB 108/13 dependency source review complete; next integrate Version 2.49')
        s=s.replace('next resolve AASB 108/13 primary-source dependencies.',
                    'selected AASB 108/13 dependencies are now inspected; next integrate the supported distinctions in Version 2.49.')
        s=s.replace('1. Follow the direct next plan: resolve the historically applicable AASB\n   108/13 dependencies through the new official index/search lead.',
                    '1. Follow the direct next plan: integrate the checked hindsight and\n   fair-value/FCF distinctions in a separate Version 2.49.')
    prepared.append((p,r,s))
rows=[]
for p,r,s in prepared:
    p.write_text(s);q=OUT/'pointers-after'/r['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
    rows.append({'live':r['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('controls-after.json',rows)
plans=['docs/plans/accounting-transition-dependencies-20261012.md','docs/plans/accounting-transition-dependencies-integration-20261012.md']
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[ROOT/p for p in plans]
now=datetime.datetime.now(datetime.timezone.utc);e=json.loads((OUT/'source-evidence.json').read_text())
m={'git_commit':b['git_commit'],'started_utc':b['started_utc'],'closed_utc':now.isoformat(),'plans':plans,
 'result':str((OUT/'result.md').relative_to(ROOT)),
 'commands':[['python3',str((OUT/n).relative_to(ROOT))] for n in ['prepare_evidence.py','check_source.py','closeout.py']],
 'source_commands':'acquisition.json: eight trusted curl requests; inspect_source.py source page [page] [--render] in two-page batches; selected page inventory in source-evidence.json',
 'source_processing':'PyMuPDF; AASB 17 page 10 extracted directly to text/aasb17-10.txt; ten normal-resolution source images inspected',
 'environment':{'python':sys.executable,'version':platform.python_version(),'html':'BeautifulSoup'},
 'cpu_gpu':'CPU document/file processing; no ML import or GPU probe',
 'data_version':e['selected_editions'],'random_seeds':'N/A: deterministic source review',
 'wall_seconds':{'elapsed_including_review':(now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),
                 'requests':sum(r['wall_seconds'] for r in json.loads((OUT/'acquisition.json').read_text())),
                 'checks':c['wall_seconds']},
 'input_hashes':b['inputs'],'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
 'readiness':'not_ready','next_plan':plans[-1]}
save('run-manifest.json',m)
for p,h in (m['input_hashes']|m['artifact_hashes']).items():assert sha(ROOT/p)==h
save('completion.json',{'status':'selected dependency-source review complete; independent interpretation pending',
 'source_checks':c['passed'],'failed':0,'source_pages':45,'source_anchors':29,'inspected_renders':10,
 'manifest_sha256':sha(OUT/'run-manifest.json'),'bound_artifacts':len(m['artifact_hashes']),
 'readiness':'not_ready','next_plan':plans[-1]})
print(json.dumps({'checks':c['passed'],'artifacts':len(m['artifact_hashes']),'readiness':'not_ready'}))
