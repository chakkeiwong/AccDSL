"""Bind this source inquiry and advance the master to the justified repair."""
import datetime
import hashlib
import json
import platform
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(OUT/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (OUT/'completion.json').exists()
b=json.loads((OUT/'baseline.json').read_text());c=json.loads((OUT/'source-checks.json').read_text())
assert c['passed']==50 and not c['failed']
old='''Inspect the exact 2023 OTSL tokenization paper identified by Docling reference
9, checking its representation, constraints and evaluation against the original
2022 paper and retained 4.0.2 consumer. Preserve Version 2.45. Plan:
`docs/plans/accounting-otsl-paper-20261012.md`.'''
new='''Integrate the checked OTSL syntax/geometry distinction and specific later-code
verification boundary in a separate Version 2.46. Preserve Version 2.45 and
all old content, then rotate to another concrete workstream. Plan:
`docs/plans/accounting-otsl-integration-20261012.md`.'''
summary='''## Latest OTSL source inquiry

The identified arXiv v1 copy is fully read (14 PDF pages, ten renders); seven
resources and relevant official 4.0.2 helpers pass 50 source/diagnostic checks.
The six printed rules accept a 2×2 sequence whose merge meanings create an
L-shaped cell, so they do not ensure rectangular merged-cell geometry. The
later source's first-line counter remains zero; runtime occurrence is untested.
These are specific claim/code limits, not rejection of the token language or
reported experiments. Add explicit geometry validation in Version 2.46.
Published full-text equivalence, checkpoint transfer and wider source/runtime
acceptance remain open. E01/E05/E07/E08/E14 and not_ready remain.
Result: `data/accounting-master/otsl-paper-20261012/result.md`.

'''
rows=[]
for r in b['pointer_snapshots']:
 p=ROOT/r['live'];assert sha(p)==r['sha256']==sha(ROOT/r['snapshot']);s=p.read_text()
 marker='## Latest TableFormer source inquiry';assert s.count(marker)==1;s=s.replace(marker,summary+marker,1)
 if p.name!='accounting-continuation-requirements-20261007.md':assert s.count(old)==1;s=s.replace(old,new,1)
 if p.name=='accounting-master-current.md':
  s=s.replace('next unit inspects the exact OTSL tokenization paper','OTSL inquiry complete; next unit integrates geometry validation',1)
  s=s.replace('next inspect the exact 2023 tokenization follow-up and match remaining manuscript claims','the exact tokenization follow-up is now inspected (50 checks); integrate the syntax/geometry distinction and match remaining manuscript claims',1)
  s=s.replace('1. Follow the direct next plan: inspect the exact 2023 tokenization follow-up\n   after the checked Version 2.45 method/text/score integration.', '1. Follow the direct next plan: integrate the checked OTSL syntax/geometry\n   distinction in Version 2.46, then rotate to another concrete workstream.',1)
 p.write_text(s);q=OUT/'pointers-after'/r['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 rows.append({'live':r['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('controls-after.json',rows)
deps=['docs/design/proposal/manuscript-tableformer-20261012/accounting-product-proposal.pdf',
 'docs/papers/Docling Technical Report Auer (2024).pdf','data/accounting-master/tableformer-paper-20261012/run-manifest.json',
 'data/accounting-master/tableformer-loader-20261010/sources/tree.json',
 'data/accounting-master/tableformer-loader-20261010/sources/docling_ibm_models__tableformer__models__table04_rs__tablemodel04_rs.py',
 'data/accounting-master/tableformer-loader-20261010/sources/docling_ibm_models__tableformer__data_management__tf_predictor.py',
 'docs/design/research/omissions.json','docs/design/research/backward-snowball.json']
plans=[b['plan'],'docs/plans/accounting-otsl-integration-20261012.md']
copy=json.loads((OUT/'paper-copy.json').read_text())['copy']
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[ROOT/p for p in plans+[copy]]
now=datetime.datetime.now(datetime.timezone.utc)
m={'git_commit':b['git_commit'],'started_utc':b['started_utc'],'closed_utc':now.isoformat(),'plans':plans,
 'result':str((OUT/'result.md').relative_to(ROOT)),
 'commands':[['python3',str((OUT/n).relative_to(ROOT))] for n in ['finite_diagnostic.py','record_evidence.py','check_sources.py','closeout.py']],
 'source_commands':'access-receipts.json, exact argv and stdout/stderr paths',
 'environment':{'python':sys.executable,'version':platform.python_version(),'libraries':['PyMuPDF','BeautifulSoup','standard library']},
 'cpu_gpu':'CPU documentary/mathematical/AST checks; no upstream module/framework/device execution',
 'seeds':'N/A: deterministic source inquiry and finite example',
 'wall_seconds':{'elapsed_including_reading':(now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),'checks':c['wall_seconds']},
 'data_version':'arXiv:2305.03393v1 and Git-blob-verified helper at exact 4.0.2 commit',
 'input_hashes':{p:sha(ROOT/p) for p in deps},'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
 'readiness':'not_ready','runtime':'held','manuscript':'Version 2.45 unchanged','next_plan':plans[-1]}
save('run-manifest.json',m)
for p,h in (m['input_hashes']|m['artifact_hashes']).items():assert sha(ROOT/p)==h
save('completion.json',{'status':'bounded source inquiry complete','source_checks':c['passed'],'failed':0,
 'manifest_sha256':sha(OUT/'run-manifest.json'),'bound_artifacts':len(m['artifact_hashes']),'readiness':'not_ready','next_plan':plans[-1]})
print({'checks':c['passed'],'artifacts':len(m['artifact_hashes']),'controls':len(rows)})
