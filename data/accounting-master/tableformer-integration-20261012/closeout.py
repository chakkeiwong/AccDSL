"""Advance current-candidate controls and bind the final integration once."""
import datetime
import json
import platform
import sys
from build_candidate import ROOT, OUT, BASE, CAND, sha, save

assert not (OUT/'completion.json').exists()
b=json.loads((OUT/'baseline.json').read_text());c=json.loads((OUT/'integration-checks.json').read_text())
assert c['passed']==135 and not c['failed'] and c['pages']==182
pdf=CAND/'accounting-product-proposal.pdf';assert sha(pdf)==c['pdf_sha256']
old='''Integrate the checked TableFormer structure, supplied-text and score boundaries
in a separate Version 2.45, preserving Version 2.44 and all old content. Then
inspect the exact 2023 tokenization follow-up from Docling reference 9. Plan:
`docs/plans/accounting-tableformer-integration-20261012.md`.'''
new='''Inspect the exact 2023 OTSL tokenization paper identified by Docling reference
9, checking its representation, constraints and evaluation against the original
2022 paper and retained 4.0.2 consumer. Preserve Version 2.45. Plan:
`docs/plans/accounting-otsl-paper-20261012.md`.'''
summary='''Version 2.45 explains TableFormer's predicted structure, externally supplied
text and Table 4 score boundary on PDF 54–55, and adds traceable text matching
and correction requirements on PDF 150. All 135 integration checks pass;
48 displays and 89 prior references remain, with three references added.
Eleven final pages were inspected and the build is clean. The original paper
and supplement inquiry passed 60 checks. Checkpoint equivalence, downstream
performance, the exact tokenization follow-up and independent/human acceptance
remain open. Full readiness stays not_ready.
Result: `data/accounting-master/tableformer-integration-20261012/result.md`.
'''
heading='## Current Version 2.45 TableFormer explanation\n\n'
rows=[]
for r in b['pointer_snapshots']:
 p=ROOT/r['live'];assert sha(p)==r['sha256']==sha(ROOT/r['snapshot']);s=p.read_text()
 if p.name=='accounting-master-checkpoint.md':
  anchor='## Current candidate\n\n';assert s.count(anchor)==1
  insert='## Current candidate\n\n**Version 2.45, 182 pages**\nPDF: '+str(pdf.relative_to(ROOT))+'\nSHA256: '+sha(pdf)+'\n\n'+summary+'\n## Preserved Version 2.44 score-rounding explanation\n\n'
  s=s.replace(anchor,insert,1)
 elif p.name=='next-plan.md':
  s=s.replace('**181-page Version 2.44**','**182-page Version 2.45**',1)
  s=s.replace(str((BASE/'accounting-product-proposal.pdf').relative_to(ROOT)),str(pdf.relative_to(ROOT)),1)
  s=s.replace(b['pdf_sha256'],sha(pdf),1)
  s=s.replace('Result: data/accounting-master/bank-score-rounding-integration-20261012/result.md','Result: data/accounting-master/tableformer-integration-20261012/result.md',1)
  s=s.replace('## Completed boundary\n\n','## Completed boundary\n\n'+summary+'\n## Preserved Version 2.44 score-rounding explanation\n\n',1)
 elif p.name=='accounting-continuation-requirements-20261007.md':
  s=s.replace('## Current Version 2.44 score-rounding explanation',heading+'E08/C06, E14/C07, P18; MC23/25/29–35, G8/G9/G10/G18.\n'+summary+'\n## Preserved Version 2.44 score-rounding explanation',1)
 else:
  s=s.replace('Version 2.44 adds the attributed score-rounding explanation and proposal boundary.', 'Version 2.45 adds the TableFormer text/structure/score distinction and adapter evidence.\nVersion 2.44 preserves the attributed score-rounding explanation and proposal boundary.',1)
  s=s.replace('**181-page Version 2.44**','**182-page Version 2.45**',1).replace(b['pdf_sha256'],sha(pdf),1)
  s=s.replace('Current through Version 2.44 and the rule-history inquiry','Current through Version 2.45 and the TableFormer inquiry',1)
  s=s.replace('Current; Version 2.44 integrated; TableFormer source comparison complete; next unit integrates its material boundaries','Current; Version 2.45 integrated; next unit inspects the exact OTSL tokenization paper',1)
  s=s.replace('Current through Version 2.44 and the latest bounded source inquiries','Current through Version 2.45 and the latest bounded source inquiries',1)
  s=s.replace('or Version 2.44 outputs','or Version 2.45 outputs',1)
  s=s.replace('Bounded integration delivered through Version 2.44','Bounded integration delivered through Version 2.45',1)
  s=s.replace('## Latest TableFormer source inquiry',heading+summary+'\n## Latest TableFormer source inquiry',1)
  s=s.replace('Integrate the material findings, then inspect the exact 2023 tokenization follow-up', 'Version 2.45 integrates the material findings; next inspect the exact 2023 tokenization follow-up',1)
  s=s.replace('1. Follow the direct next plan: integrate the checked TableFormer method,\n   text-source and score boundaries, then inspect the exact tokenization follow-up.', '1. Follow the direct next plan: inspect the exact 2023 tokenization follow-up\n   after the checked Version 2.45 method/text/score integration.',1)
 if p.name!='accounting-continuation-requirements-20261007.md':assert s.count(old)==1;s=s.replace(old,new,1)
 s=s.replace('Next integrate these material boundaries in Version 2.45. The frozen 56/136', 'Version 2.45 now integrates these material boundaries. The frozen 56/136',1)
 p.write_text(s);q=OUT/'pointers-after'/r['live'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 rows.append({'live':r['live'],'snapshot':str(q.relative_to(ROOT)),'sha256':sha(q)})
save('controls-after.json',rows)
initial=json.loads((OUT/'initial-final-renders.json').read_text())
save('initial-final-renders.json',{'status':'Superseded diagnostic hashes; former paths were regenerated during the open-unit layout repair and do not claim retained initial images.',
 'rows':[{('former_render_path' if k=='render' else k):v for k,v in row.items()} for row in initial]})
plans=['docs/plans/accounting-tableformer-integration-20261012.md','docs/plans/accounting-otsl-paper-20261012.md']
deps=[BASE/'accounting-product-proposal.pdf',ROOT/'data/accounting-master/tableformer-paper-20261012/run-manifest.json',
      ROOT/'data/accounting-master/tableformer-paper-20261012/completion.json']
paths=[p for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
paths += [p for p in CAND.rglob('*') if p.is_file()] + [ROOT/p for p in plans]
now=datetime.datetime.now(datetime.timezone.utc)
m={'git_commit':b['git_commit'],'started_utc':b['started_utc'],'closed_utc':now.isoformat(),
 'plans':plans,'result':str((OUT/'result.md').relative_to(ROOT)),
 'commands':[['python3',str((OUT/n).relative_to(ROOT))] for n in ['build_candidate.py','refine_layout.py','render_review.py','verify_integration.py','closeout.py']],
 'build_commands':['initial-build-run.json','build-run.json'],'surface_commands':'surface-runs.json',
 'environment':{'python':sys.executable,'version':platform.python_version(),'tex':'LuaLaTeX/BibTeX through latexmk'},
 'cpu_gpu':'CPU document processing; CUDA_VISIBLE_DEVICES=-1 for builds; no framework/device use',
 'data_version':'Protected 2.44 source/PDF and exact bound TableFormer source inquiry', 'seeds':'N/A: deterministic integration',
 'wall_seconds':{'elapsed_including_review':(now-datetime.datetime.fromisoformat(b['started_utc'])).total_seconds(),'checks':c['wall_seconds']},
 'input_hashes':{str(p.relative_to(ROOT)):sha(p) for p in deps},
 'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in sorted(set(paths))},
 'pdf_sha256':sha(pdf),'pages':len(__import__('fitz').open(pdf)),'readiness':'not_ready','runtime':'held','next_plan':plans[-1]}
save('run-manifest.json',m)
for p,h in (m['input_hashes']|m['artifact_hashes']).items():assert sha(ROOT/p)==h
save('completion.json',{'status':'bounded integration complete; independent_reader_pending','integration_checks':c['passed'],'failed':0,
 'manifest_sha256':sha(OUT/'run-manifest.json'),'bound_artifacts':len(m['artifact_hashes']),'readiness':'not_ready',
 'pdf_sha256':sha(pdf),'pages':c['pages'],'next_plan':plans[-1]})
print(json.dumps({'checks':c['passed'],'artifacts':len(m['artifact_hashes']),'controls':len(rows),'pdf_sha256':sha(pdf)}))
