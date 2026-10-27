"""One-shot control refresh after verified documentary integration."""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
ARCHIVE=ROOT/'data/accounting-master/p17-completion-20261014/control-refresh-20'
CONTROLS=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
OLD_HASH='a45c9368d89a10981010a60513ad2fce2508c9b6ce0cb964815a6cef63ff077f'
NEW_HASH='6aa8565d8ce7c5bd396355206b7650f8593dfee1cad3a0f7d447a766d77f3af7'
OLD_NEXT='Next: execute the audited P17-04/08/11 error-versus-estimate bridge plan (docs/plans/accounting-error-estimate-bridge-20261014.md). Read the retained AASB108 standard, then distinguish new estimates from prior errors through comparative, opening-equity and current-book bridges with explicit availability, materiality and treatment limits. Runtime execution remains held.'
NEXT='Next: execute the refreshed P17-04/11 production-cost plan (docs/plans/accounting-production-cost-20261014.md). Reconcile delivered operations, inspect retained normal-capacity and excluded-cost authority, and connect low/high output, unsold stock and expenses to statements. Runtime execution remains held.'
SUMMARY="P17-04/08/11's error-versus-estimate bridge is integrated in Version 2.92: 198 exact calculation/semantic checks, 33 source checks and 100 preservation/build checks pass; seven rendered pages were inspected. Prior authorization, original availability, comparative and opening-equity tax effects, current-quarter correction and duplicate guards are explicit. Private-entity EPS scope is sourced; actual admission and broader EPS/restatement interactions remain. Result: data/accounting-master/p17-completion-20261014/P17-04/error-estimate/result.md. P17/E07/E14 remain open."
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,value):p.write_text(json.dumps(value,indent=2)+chr(10))
assert not ARCHIVE.exists()
for file,count in [('calculation-checks.json',198),('source-checks.json',33),('manuscript-checks.json',100)]:
    r=json.loads((OUT/file).read_text());assert r['passed'] and r['check_count']==count,file
pdf=ROOT/'docs/design/proposal/manuscript-error-estimate-20261014/accounting-product-proposal.pdf'
assert sha(pdf)==NEW_HASH
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert index==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
updates={};before={}
for name in CONTROLS:
    p=ROOT/name;s=p.read_text();original=s
    for a,b in [('manuscript-sector-revision-20261014/accounting-product-proposal.pdf','manuscript-error-estimate-20261014/accounting-product-proposal.pdf'),('Version **2.91**','Version **2.92**'),('**Version 2.91,','**Version 2.92,'),('Version 2.91, 268','Version 2.92, 271'),('current Version 2.91 candidate','current Version 2.92 candidate'),('progress — Version 2.91','progress — Version 2.92'),('268 pages','271 pages'),('2.73–2.91','2.73–2.92'),('through 2.91','through 2.92'),('Version2.91 and full2.72 assessment','Version2.92 and full2.72 assessment'),(OLD_HASH,NEW_HASH),(OLD_NEXT,NEXT)]:s=s.replace(a,b)
    if name.endswith('accounting-master-current.md'):
        s=s.replace('**P17-04/08/11: prior errors, new estimates and comparative bridges.**','**P17-04/11: production cost, normal capacity and unsold inventory.**'+chr(10)*2+SUMMARY)
        s=s.replace('Seven pages of 2.91 received','Seven pages of 2.92 received')
    elif name.endswith('accounting-master-checkpoint.md'):
        s=s.replace('## Latest completed work'+chr(10)*2,'## Latest completed work'+chr(10)*2+SUMMARY+chr(10)*2,1)
    elif name.endswith('accounting-continuation-requirements-20261007.md'):
        s=s.replace(chr(10)+"P17-08/10/11's sector-evidence",chr(10)+SUMMARY+chr(10)*2+"P17-08/10/11's sector-evidence",1)
        s=s.replace('The immediate work is the P17-04/08/11 error-versus-estimate bridge,','The immediate work is the P17-04/11 production-cost method,')
    elif name.endswith('accounting-p17-completion-20261014.md'):
        s=s.replace(chr(10)+NEXT,chr(10)+SUMMARY+chr(10)*2+NEXT,1)
        s=s.replace('the P17-04/08/11 error-versus-estimate bridge is the immediate ready action','the P17-04/11 production-cost method is the immediate ready action')
    elif name.endswith('accounting-p18-completion-20261014.md'):
        s=s.replace('integration follows the audited P17-04/08/11 error-versus-estimate bridge.','integration follows the audited P17-04/11 production-cost method.'+chr(10)*2+SUMMARY)
    else:
        s=s.replace('1. '+NEXT,'1. '+NEXT+chr(10)+'   '+SUMMARY,1)
        s=s.replace('sector revisions and EPS financing repair in 2.91.','sector revisions and EPS financing repair in 2.91; error/estimate bridge in 2.92.')
    assert s!=original and SUMMARY in s and OLD_NEXT not in s,name
    updates[name]=s;before[name]=sha(p)
for name in CONTROLS:
    q=ARCHIVE/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,q)
for name,s in updates.items():(ROOT/name).write_text(s)
(OUT/'before').mkdir(exist_ok=True)
matrix=ROOT/'data/accounting-master/p17-completion-20261014/P17-04/operation-matrix.md'
shutil.copy2(matrix,OUT/'before/corporate-operation-matrix.md')
s=matrix.read_text().replace('Refreshed through Version 2.80','Refreshed through Version 2.92')
s=s.replace('Execute the refreshed group-fx-disposal plan: join acquisition, goodwill, owner/NCI translation reserves and loss of control; preserve the2.52 intragroup-FX bridge','Delivered2.81: connected acquisition, goodwill, owner/NCI translation reserves and loss of control; retain group-fx-disposal/result.md and2.52 intragroup-FX bridge. Actual control/currency and wider interactions remain')
s+=chr(10)+'Version2.92 supplies the prior-error/new-estimate comparison, comparative/opening/current-book bridges, tax origins and semantic duplicate refusal; see error-estimate/result.md. It does not close actual-fact, current-authority, EPS-where-required or general-impracticability routes. Next: normal-capacity production costs and unsold inventory under the retained102 source; do not repeat delivered lot/NRV/sample cases.'+chr(10)
matrix.write_text(s)
cross=ROOT/'data/accounting-master/p17-completion-20261014/P17-08/operation-matrix.md'
shutil.copy2(cross,OUT/'before/cross-cutting-operation-matrix.md')
s=cross.read_text().replace('current2.91','current2.92').replace('Continue the prior-error versus new-estimate comparative bridge;','Prior-error/new-estimate comparative bridge delivered in2.92;')
s+=chr(10)+'Version2.92 adds an authority-supported conditional prior correction, comparative presentation versus current-book separation, original availability/authorization, tax origins and semantic idempotence. Portable encoding and whole-contract runtime conformance remain separate; actual admission is not inferred.'+chr(10)
cross.write_text(s)
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==index
assert all((ROOT/n).read_text()==s for n,s in updates.items())
save(ARCHIVE/'refresh-manifest.json',{'before':before,'after':{n:sha(ROOT/n) for n in CONTROLS},'index_preserved':True,'next':NEXT})
(ARCHIVE/'execution-note.md').write_text('# Control refresh20'+chr(10)*2+'Audit: exact2.92 candidate, checked statements and separate original/comparative/current paths; sourced historical scope, no widened readiness claim. All prior controls and staged index preserved.'+chr(10)*2+SUMMARY+chr(10)*2+NEXT+chr(10))
paths=[p for p in OUT.rglob('*') if p.is_file() and p.name!='run-manifest.json']+[ROOT/n for n in CONTROLS]+[pdf,matrix,cross,ROOT/'docs/plans/accounting-error-estimate-bridge-20261014.md',ROOT/'docs/plans/accounting-production-cost-20261014.md',ROOT/'docs/design/proposal/methods/error-estimate-bridge-20261014.md']
save(OUT/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'recorded_utc':datetime.now(timezone.utc).isoformat(),'environment':'System Python Fraction/PyMuPDF; LuaLaTeX; Poppler','cpu_gpu_status':'CPU documentary checks; no numerical framework or GPU initialized','random_seeds':'N/A; exact authored deterministic cases','data_version':'fixture.json; retained historical AASB108/116/112 and133 scope; no issuer data','plan':'docs/plans/accounting-error-estimate-bridge-20261014.md','result':str((OUT/'result.md').relative_to(ROOT)),'commands':['python3 '+str((OUT/f).relative_to(ROOT)) for f in ['verify_calculations.py','check_sources.py','prepare.py','verify_candidate.py','closeout.py']],'source_acquisition':'curl -L --fail --max-time 45 -o '+str((OUT/'aasb133-compmar20.pdf').relative_to(ROOT))+' https://www.aasb.gov.au/admin/file/content105/c9/AASB133_08-15_COMPmar20_07-21.pdf','build_record':json.loads((OUT/'build-run.json').read_text()),'render_record':'first-render/render-manifest.json','check_seconds':{f:json.loads((OUT/f).read_text())['wall_seconds'] for f in ['calculation-checks.json','source-checks.json','manuscript-checks.json']},'wall_time_note':'Build/check timings recorded; total interactive authoring time not measured','artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(set(paths))]})
print(json.dumps({'version':'2.92','controls':6,'index_preserved':True,'next':'P17-04/11 production-cost'}))
