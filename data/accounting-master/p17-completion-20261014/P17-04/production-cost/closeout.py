"""Publish verified2.93 documentary pointers once; preserve old evidence."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib,json,shutil,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
ARCHIVE=ROOT/'data/accounting-master/p17-completion-20261014/control-refresh-21'
CONTROLS=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
OLD_HASH='6aa8565d8ce7c5bd396355206b7650f8593dfee1cad3a0f7d447a766d77f3af7'
NEW_HASH='46d17f8440c325353f6a7e250897a1629e5f08b60107d7104ec7bf30c04bd17c'
OLD_NEXT='Next: execute the refreshed P17-04/11 production-cost plan (docs/plans/accounting-production-cost-20261014.md). Reconcile delivered operations, inspect retained normal-capacity and excluded-cost authority, and connect low/high output, unsold stock and expenses to statements. Runtime execution remains held.'
NEXT='Next: execute the P17-11/P18-03/P19-01 convergence audit (docs/plans/accounting-convergence-audit-20261015.md). Reconcile all 53 original obligations against Version 2.93 and its interactions, distinguish missing design from actual-fact/runtime/human dependencies, and execute the highest-priority ready repair. Runtime execution remains held.'
SUMMARY="P17-04/11's production-cost method is integrated in Version 2.93: 218 exact calculation/admission checks, 26 source checks and 101 preservation/build checks pass; seven rendered pages were inspected. Normal capacity, low/high/idle output, abnormal waste, unsold stock and noncash production depreciation connect through journals and pretax statements. Balanced wrong allocations are rejected. Tax remains explicitly uncomputed. Result: data/accounting-master/p17-completion-20261014/P17-04/production-cost/result.md. P17/E07/E14 remain open."
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_text(json.dumps(x,indent=2)+chr(10))
assert not ARCHIVE.exists()
for f,n in [('calculation-checks.json',218),('source-checks.json',26),('manuscript-checks.json',101)]:
    r=json.loads((OUT/f).read_text());assert r['passed'] and r['check_count']==n
pdf=ROOT/'docs/design/proposal/manuscript-production-cost-20261015/accounting-product-proposal.pdf'
assert sha(pdf)==NEW_HASH
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert index==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
updates={};before={}
for name in CONTROLS:
    p=ROOT/name;s=p.read_text();original=s
    for a,b in [('manuscript-error-estimate-20261014/accounting-product-proposal.pdf','manuscript-production-cost-20261015/accounting-product-proposal.pdf'),('Version **2.92**','Version **2.93**'),('**Version 2.92,','**Version 2.93,'),('Version 2.92, 271','Version 2.93, 274'),('current Version 2.92 candidate','current Version 2.93 candidate'),('progress — Version 2.92','progress — Version 2.93'),('271 pages','274 pages'),('2.73–2.92','2.73–2.93'),('through 2.92','through 2.93'),('Version2.92 and full2.72 assessment','Version2.93 and full2.72 assessment'),(OLD_HASH,NEW_HASH),(OLD_NEXT,NEXT)]:s=s.replace(a,b)
    if name.endswith('accounting-master-current.md'):
        s=s.replace('Refreshed 14 October 2026','Refreshed 15 October 2026',1)
        s=s.replace('**P17-04/11: production cost, normal capacity and unsold inventory.**','**P17-11/P18-03/P19-01: current evidence, interactions and finite repairs.**'+chr(10)*2+SUMMARY)
        s=s.replace('Seven pages of 2.92 received','Seven pages of 2.93 received')
    elif name.endswith('accounting-master-checkpoint.md'):
        s=s.replace('Updated 14 October 2026','Updated 15 October 2026',1)
        s=s.replace('## Latest completed work'+chr(10)*2,'## Latest completed work'+chr(10)*2+SUMMARY+chr(10)*2,1)
    elif name.endswith('accounting-continuation-requirements-20261007.md'):
        anchor=chr(10)+"P17-04/08/11's error-versus-estimate"
        assert anchor in s;s=s.replace(anchor,chr(10)+SUMMARY+chr(10)+anchor,1)
        s=s.replace('The immediate work is the P17-04/11 production-cost method,','The immediate work is the P17-11/P18-03/P19-01 convergence audit,')
    elif name.endswith('accounting-p17-completion-20261014.md'):
        s=s.replace(chr(10)+NEXT,chr(10)+SUMMARY+chr(10)*2+NEXT,1)
        s=s.replace('the P17-04/11 production-cost method is the immediate ready action','the P17-11/P18-03/P19-01 convergence audit is the immediate ready action')
    elif name.endswith('accounting-p18-completion-20261014.md'):
        s=s.replace('integration follows the audited P17-04/11 production-cost method.','integration follows the finite convergence audit and its located repairs.'+chr(10)*2+SUMMARY)
    else:
        s=s.replace('14 October 2026. Version','15 October 2026. Version',1)
        s=s.replace('1. '+NEXT,'1. '+NEXT+chr(10)+'   '+SUMMARY,1)
        s=s.replace('error/estimate bridge in 2.92.','error/estimate bridge in 2.92; production cost in 2.93.')
    assert s!=original and SUMMARY in s and OLD_NEXT not in s,name
    updates[name]=s;before[name]=sha(p)
for name in CONTROLS:
    q=ARCHIVE/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,q)
for name,s in updates.items():(ROOT/name).write_text(s)
matrix=ROOT/'data/accounting-master/p17-completion-20261014/P17-04/operation-matrix.md'
(OUT/'before').mkdir(exist_ok=True);shutil.copy2(matrix,OUT/'before/corporate-operation-matrix.md')
s=matrix.read_text().replace('Refreshed through Version 2.92','Refreshed through Version 2.93')
s=s.replace('Actual lot/NRV inputs, production conversion and payable discount terms remain operation-specific','Production conversion delivered2.93 for a homogeneous completed batch with normal-capacity low/high/idle and abnormal-cost cases; actual lot/NRV/yield/capacity inputs, WIP/joint products and payable discount terms remain operation-specific')
s=s.replace('Next: normal-capacity production costs and unsold inventory under the retained102 source; do not repeat delivered lot/NRV/sample cases.','Normal-capacity production cost and unsold inventory are now delivered2.93; retain production-cost/result.md. Next: finite convergence audit against all53 obligations; do not repeat delivered lot/NRV/sample cases.')
s+=chr(10)+'Version2.93 explicitly separates fixed cash120 from depreciation60, unsold cost and abnormal/unallocated expense. Pretax statements are not after-tax equity. The next convergence audit determines which remaining operation omissions are required for design acceptance, rather than indefinitely expanding illustrations.'+chr(10)
matrix.write_text(s)
assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==index
assert all((ROOT/n).read_text()==s for n,s in updates.items())
save(ARCHIVE/'refresh-manifest.json',{'before':before,'after':{n:sha(ROOT/n) for n in CONTROLS},'index_preserved':True,'next':NEXT})
(ARCHIVE/'execution-note.md').write_text('# Control refresh21'+chr(10)*2+'15 October2026. Audit: exact candidate/hash, independent ledger/cost allocation, explicit pretax/source scope and unchanged predecessor/index. Local counts cannot establish full readiness.'+chr(10)*2+SUMMARY+chr(10)*2+NEXT+chr(10))
paths=[p for p in OUT.rglob('*') if p.is_file() and p.name!='run-manifest.json']+[ROOT/n for n in CONTROLS]+[pdf,matrix,ROOT/'docs/plans/accounting-production-cost-20261014.md',ROOT/'docs/plans/accounting-convergence-audit-20261015.md',ROOT/'docs/design/proposal/methods/production-cost-20261015.md']
save(OUT/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'recorded_utc':datetime.now(timezone.utc).isoformat(),'environment':'System Python Fraction/PyMuPDF; LuaLaTeX; Poppler','cpu_gpu_status':'CPU documentary checks; no numerical framework or GPU initialized','random_seeds':'N/A; exact deterministic authored cases','data_version':'production-cost fixture.json; retained dated AASB102/116/15','plan':'docs/plans/accounting-production-cost-20261014.md','result':str((OUT/'result.md').relative_to(ROOT)),'commands':['python3 '+str((OUT/f).relative_to(ROOT)) for f in ['verify_calculations.py','check_sources.py','prepare.py','verify_candidate.py','closeout.py']],'source_acquisition':'None; reused retained source bytes','build_record':json.loads((OUT/'build-run.json').read_text()),'render_record':'first-render/render-manifest.json','check_seconds':{f:json.loads((OUT/f).read_text())['wall_seconds'] for f in ['calculation-checks.json','source-checks.json','manuscript-checks.json']},'wall_time_note':'Build/check timings retained; total interactive time not measured','artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(set(paths))]})
print(json.dumps({'version':'2.93','controls':6,'index_preserved':True,'next':'P17-11/P18-03/P19-01 convergence audit'}))
