"""Publish verified 2.95 routing once; retain exact prior controls and index."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,platform,re,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];ARCHIVE=OUT/'control-before-r03'
FILES=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
OLD='38c4edc2c7508e303be5c05e894768e3ab14be7c0653ae6b7cce28ded8b23a43';NEW='fc496a3d2bb1b6453e474afbfe8ca6742ced3ecbec460bf6672bbe85a665c2c8'
SUMMARY='R02 is delivered within its finite documentary scope in Version 2.95: 31 connected exchanges, 4,760 independent checks and 103 preservation/build checks pass; eight rendered pages were inspected. The Apple package preserves reported tokens, conditional histories and joint settlements, missing feasible remainder and exact-byte clocks, plus separate original/later views. JPMorgan conflict remains company-specific. Result: data/accounting-master/real-package-connection-20261015/result.md. Actual histories, full readiness and independent/human acceptance remain open.'
NEXT='Next: execute R03 finite method and sector-interaction decisions (docs/plans/accounting-finite-method-decisions-20261015.md), beginning with changed conversion/options and hedge/benchmark scope. Continue ready R04 consequential literature, R05 future validation protocols and R06 reuse locks; then R07/R08. Runtime execution remains held.'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not ARCHIVE.exists()
for name in ['independent-checks.json','manuscript-checks.json']:
 d=json.loads((OUT/name).read_text());assert d['passed'] and all(x['passed'] for x in d['checks'])
pdf=ROOT/'docs/design/proposal/manuscript-real-package-20261015/accounting-product-proposal.pdf';assert sha(pdf)==NEW
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert index==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
updates={};before={}
for name in FILES:
 p=ROOT/name;s=p.read_text();original=s
 s=s.replace('manuscript-corporate-portable-20261015/accounting-product-proposal.pdf','manuscript-real-package-20261015/accounting-product-proposal.pdf').replace(OLD,NEW)
 for a,b in [('Version **2.94**, 278','Version **2.95**, 281'),('**Version 2.94, 278','**Version 2.95, 281'),('Version 2.94, 278','Version 2.95, 281'),('current Version 2.94 candidate','current Version 2.95 candidate'),('through 2.94','through 2.95'),('2.73–2.94','2.73–2.95'),('Version2.94 and full2.72 assessment','Version2.95 and full2.72 assessment')]:s=s.replace(a,b)
 s=re.sub(r'Next: execute R02,[^\n]*',NEXT,s)
 s=s.replace('**R02: connected real-package partial and conditional results.**','**R03: finite method and sector-interaction decisions.**')
 s=s.replace('R02 real-package connection is the immediate ready action','R03 finite method decisions are the immediate ready action')
 s=s.replace('R01 is delivered within its documentary scope. The immediate plan is\ndocs/plans/accounting-real-package-connection-20261015.md.','R01 and R02 are delivered within their documentary scopes. The immediate plan is\ndocs/plans/accounting-finite-method-decisions-20261015.md.')
 s=s.replace('## Corporate completion and next work — 15 October 2026','## Real-package completion and next work — 15 October 2026\n\n'+SUMMARY+'\n\n'+NEXT+'\n\n## Corporate completion — 15 October 2026',1)
 assert s!=original and SUMMARY in s and 'Next: execute R02,' not in s
 updates[name]=s;before[name]=sha(p)
for name in FILES:
 target=ARCHIVE/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
for name,s in updates.items():(ROOT/name).write_text(s)
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==index
assert all((ROOT/n).read_text()==s for n,s in updates.items())
(OUT/'control-refresh.json').write_text(json.dumps({'recorded_utc':datetime.now(timezone.utc).isoformat(),'before':before,'after':{n:sha(ROOT/n) for n in FILES},'index_preserved':True,'next':NEXT},indent=2)+'\n')
bundle=json.loads((OUT/'portable-exchanges.json').read_text());checks=json.loads((OUT/'independent-checks.json').read_text())
commands=['python3 data/accounting-master/real-package-connection-20261015/'+n+'.py' for n in ['build_connection','verify_connection','prepare_manuscript','verify_manuscript','refresh_controls']]
commands+=['python3 scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-real-package-20261015 --evidence data/accounting-master/real-package-connection-20261015 --timeout 240 --force','python3 scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-real-package-20261015 --evidence data/accounting-master/real-package-connection-20261015/final-render --pages 1,48-51,254-256 --dpi 110']
manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'worktree':'dirty; exact inputs pinned; 100 unrelated index entries preserved','commands':commands,'environment':{'python':platform.python_version(),'execution':'system Python exact fractions/jsonschema; approved LuaLaTeX document wrapper','cpu':'CPU documentary arithmetic/build','gpu':'N/A; no numerical framework imported or GPU detected'},'data_version':bundle['source_inputs'],'random_seeds':'N/A; deterministic documentary arithmetic','wall_time':{'independent_checks_seconds':checks['wall_seconds'],'build':json.loads((OUT/'build-run.json').read_text()),'interactive_total':'not measured; do not infer from process timing'},'plan':'docs/plans/accounting-real-package-connection-20261015.md','result':str((OUT/'result.md').relative_to(ROOT)),'candidate_pdf':str(pdf.relative_to(ROOT)),'candidate_pdf_sha256':NEW,'artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(OUT.glob('*')) if p.is_file() and p.name!='run-manifest.json'],'source_blobs':[{'sha256':d,**v} for d,v in bundle['blobs'].items()],'initial_draft_failures':'Repaired syntax error before first generation; first render wording/citation repair rebuilt; prior render preserved.'}
(OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'candidate':'2.95','controls':len(updates),'index_preserved':True,'next':'R03'}))
