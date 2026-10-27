"""One-time publication of verified 2.94 and R02 routing."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
ARCHIVE=OUT/'control-before-r02'
FILES=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
OLD='46d17f8440c325353f6a7e250897a1629e5f08b60107d7104ec7bf30c04bd17c'
NEW='38c4edc2c7508e303be5c05e894768e3ab14be7c0653ae6b7cce28ded8b23a43'
SUMMARY='R01 is delivered as a finite documentary specification in Version 2.94: 70 connected exchanges, 724 independent checks and 101 preservation/build checks pass; eight rendered pages were inspected. Historical journals feed the scenario opening; typed unknowns, time admission, conditional interpretations, separate transaction owners and complete recovery worlds are explicit. Result: data/accounting-master/corporate-portable-20261015/result.md. Runtime, full readiness and independent/human acceptance remain open.'
NEXT='Next: execute R02, the connected real-package partial/conditional specification (docs/plans/accounting-real-package-connection-20261015.md). Preserve the Apple inventory, annual/interim and later-comparative source views, conditional history transformation and missing feasible remainder. Keep JPMorgan source conflict in its own company namespace. Then refresh and continue R03–R06 before R07/R08; runtime execution remains held.'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not ARCHIVE.exists()
for name in ['independent-checks.json','manuscript-checks.json']:
    d=json.loads((OUT/name).read_text());assert d['passed'] and all(x['passed'] for x in d['checks'])
assert sha(ROOT/'docs/design/proposal/manuscript-corporate-portable-20261015/accounting-product-proposal.pdf')==NEW
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert index==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
updates={};before={}
for name in FILES:
    p=ROOT/name;s=p.read_text();original=s
    s=s.replace('manuscript-production-cost-20261015/accounting-product-proposal.pdf','manuscript-corporate-portable-20261015/accounting-product-proposal.pdf').replace(OLD,NEW)
    for a,b in [('Version **2.93**, 274','Version **2.94**, 278'),('**Version 2.93, 274','**Version 2.94, 278'),('Version 2.93, 274','Version 2.94, 278'),('current Version 2.93 candidate','current Version 2.94 candidate'),('through 2.93','through 2.94'),('2.73–2.93','2.73–2.94'),('Version2.93 and full2.72 assessment','Version2.94 and full2.72 assessment')]:s=s.replace(a,b)
    s=s.replace('inspected. Northstar has complete financial statements, but IX01–IX06 and the\noperation registry do not supply its complete portable request/result closure.','inspected. The audit found a corporate request/result closure gap. R01 now\nsupplies its finite exact documentary exchanges in Version 2.94.')
    s=s.replace('The immediate plan is docs/plans/accounting-corporate-portable-20261015.md.','R01 is delivered within its documentary scope. The immediate plan is\ndocs/plans/accounting-real-package-connection-20261015.md.')
    s=re.sub(r'Next: execute R01,[^\n]*',NEXT,s)
    s=s.replace('the P17-11/P18-03/P19-01 convergence audit is the immediate ready action','R02 real-package connection is the immediate ready action')
    s=s.replace('**P17-11/P18-03/P19-01: current evidence, interactions and finite repairs.**','**R02: connected real-package partial and conditional results.**')
    s=s.replace('## Convergence audit and finite continuation — 15 October 2026','## Corporate completion and next work — 15 October 2026\n\n'+SUMMARY+'\n\n'+NEXT+'\n\n## Convergence audit and finite continuation — 15 October 2026',1)
    assert s!=original and SUMMARY in s and 'Next: execute R01,' not in s
    updates[name]=s;before[name]=sha(p)
for name in FILES:
    target=ARCHIVE/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
for name,s in updates.items():(ROOT/name).write_text(s)
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==index
assert all((ROOT/n).read_text()==s for n,s in updates.items())
(OUT/'control-refresh.json').write_text(json.dumps({'recorded_utc':datetime.now(timezone.utc).isoformat(),'before':before,'after':{n:sha(ROOT/n) for n in FILES},'index_preserved':True,'next':NEXT},indent=2)+'\n')
manifest=json.loads((OUT/'run-manifest.json').read_text())
manifest.update(build_record=json.loads((OUT/'build-run.json').read_text()),render_record='first-render/render-manifest.json',candidate_pdf_sha256=NEW,manuscript_check_seconds=json.loads((OUT/'manuscript-checks.json').read_text())['wall_seconds'],interactive_wall_time='not measured; build/check times retained separately')
manifest['commands']+=['python3 data/accounting-master/corporate-portable-20261015/prepare_manuscript.py','python3 scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-corporate-portable-20261015 --evidence data/accounting-master/corporate-portable-20261015 --timeout 240 --force','python3 scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-corporate-portable-20261015 --evidence data/accounting-master/corporate-portable-20261015/first-render --pages 1,15-18,251-253 --dpi 110','python3 data/accounting-master/corporate-portable-20261015/verify_manuscript.py','python3 data/accounting-master/corporate-portable-20261015/refresh_controls.py']
for p in [OUT/'result.md',OUT/'manuscript-checks.json',OUT/'control-refresh.json',OUT/'render-review.json',ROOT/'docs/design/proposal/architecture/corporate-portable-20261015.md']:
    manifest['artifacts'].append({'path':str(p.relative_to(ROOT)),'sha256':sha(p)})
(OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'candidate':'2.94','controls':len(updates),'index_preserved':True,'next':'R02'}))
