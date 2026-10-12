"""Bind this source inquiry once and advance the four live controls."""
import datetime
import hashlib
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v): (OUT/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (OUT/'completion.json').exists()
b=json.loads((OUT/'baseline.json').read_text())
c=json.loads((OUT/'source-checks.json').read_text())
assert c['passed']==60 and not c['failed']
old='''Read the original TableFormer technical method/evaluation and reconcile its
reported TEDS figures with the retained model card and official 4.0.2 loader.
Preserve Version 2.44 and keep local performance/runtime claims unevaluated.
Plan: `docs/plans/accounting-tableformer-paper-20261012.md`.'''
new='''Integrate the checked TableFormer structure, supplied-text and score boundaries
in a separate Version 2.45, preserving Version 2.44 and all old content. Then
inspect the exact 2023 tokenization follow-up from Docling reference 9. Plan:
`docs/plans/accounting-tableformer-integration-20261012.md`.'''
summary='''## Latest TableFormer source inquiry

The identified 2022 main paper and supplement are fully read, with twelve
selected renders and 60 passing source/preservation checks. The model-card
95.4/90.1/93.6 row belongs to Table 4's cropped-PDF-table structure-with-content
evaluation. Cell text comes from PDF/OCR inputs; matching can change structure.
The retained 4.0.2 consumer uses later OTSL tokens, so release/checkpoint score
transfer remains unsupported. Crossref pagination and the printed loss/prose
ambiguity are preserved. Thirty-nine references have dispositions; Docling
reference 9 identifies the exact 2023 tokenization follow-up, still unread.
Next integrate these material boundaries in Version 2.45. The frozen 56/136
date split, forty exhibits and E01/E05/E07/E08/E14 remain open; not_ready stays.
Result: `data/accounting-master/tableformer-paper-20261012/result.md`.

'''
rows=[]
for r in b['pointer_snapshots']:
 p=ROOT/r['live'];assert sha(p)==r['sha256']==sha(ROOT/r['snapshot'])
 s=p.read_text();start=s.index('## Current frontier after Version 2.44');end=s.index('\n## ',start+4)
 s=s[:start]+summary+s[end+1:]
 if p.name!='accounting-continuation-requirements-20261007.md':
  assert s.count(old)==1;s=s.replace(old,new,1)
 if p.name=='accounting-master-current.md':
  s=s.replace('frontier reviewed; next unit reconciles TableFormer paper and loader','TableFormer source comparison complete; next unit integrates its material boundaries',1)
  s=s.replace('Next inspect the original TableFormer method/evaluation and reconcile it with the pinned loader and model-card score; then match remaining manuscript claims to technically inspected sources.', 'The TableFormer main/supplement and paper/card/consumer comparison are complete (60 checks). Integrate the material findings, then inspect the exact 2023 tokenization follow-up and match remaining manuscript claims to technically inspected sources.',1)
  s=s.replace('1. Follow the direct next plan: reconcile the original TableFormer paper,\n   model-card score and pinned loader after the completed frontier review.', '1. Follow the direct next plan: integrate the checked TableFormer method,\n   text-source and score boundaries, then inspect the exact tokenization follow-up.',1)
 p.write_text(s);q=OUT/'pointers-after'/r['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 rows.append({'live':r['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('controls-after.json',rows)
deps=['docs/design/proposal/manuscript-score-rounding-20261012/accounting-product-proposal.pdf',
 'docs/papers/Docling Technical Report Auer (2024).pdf',
 'data/accounting-master/tableformer-loader-20261010/source-review.md',
 'data/accounting-master/tableformer-loader-20261010/run-manifest.json',
 'data/accounting-master/docling-model-metadata-20261010/sources/tableformer__README.md',
 'docs/design/research/omissions.json','docs/design/research/backward-snowball.json']
deps += [r['path'] for r in json.loads((OUT/'code-anchors.json').read_text())['sources']]
deps += [f'data/accounting-master/docling-model-metadata-20261010/sources/tableformer__model_artifacts__tableformer__{a}__tm_config.json' for a in ['accurate','fast']]
plans=[b['plan'],'docs/plans/accounting-tableformer-integration-20261012.md']
copies=[r['copy'] for r in json.loads((OUT/'paper-copies.json').read_text())]
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+[ROOT/p for p in plans+copies]
now=datetime.datetime.now(datetime.timezone.utc)
m={'git_commit':b['git_commit'],'started_utc':b['started_utc'],'closed_utc':now.isoformat(),
 'plans':plans,'result':str((OUT/'result.md').relative_to(ROOT)),
 'commands':[['python3',str((OUT/n).relative_to(ROOT))] for n in ['record_evidence.py','check_sources.py','closeout.py']],
 'source_commands':'access-receipts.json retains transfer outputs, execution limits and command-provenance limitation; no verbatim invocation invented',
 'environment':{'python':sys.executable,'version':platform.python_version(),'libraries':['PyMuPDF','BeautifulSoup']},
 'cpu_gpu':'CPU documentary processing only; no GPU framework, detection or use',
 'seeds':'N/A: deterministic documentary inquiry',
 'wall_seconds':{'elapsed_including_reading_and_recovery':(now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),'source_checks':c['wall_seconds']},
 'data_version':'Identified CVF 2022 paper/supplement, bounded Crossref/CVF metadata, pinned 4.0.2 and retained model-card sources',
 'input_hashes':{p:sha(ROOT/p) for p in deps},
 'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
 'readiness':'not_ready','runtime':'held','manuscript':'Version 2.44 unchanged','next_plan':plans[-1]}
save('run-manifest.json',m)
for p,h in (m['input_hashes']|m['artifact_hashes']).items():assert sha(ROOT/p)==h
save('completion.json',{'status':'bounded source inquiry complete','source_checks':c['passed'],'failed':0,
 'manifest_sha256':sha(OUT/'run-manifest.json'),'bound_artifacts':len(m['artifact_hashes']),
 'readiness':'not_ready','next_plan':plans[-1]})
print(json.dumps({'checks':c['passed'],'artifacts':len(m['artifact_hashes']),'controls':len(rows)}))
