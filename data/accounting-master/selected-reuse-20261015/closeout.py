from pathlib import Path
import json,hashlib,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'run-manifest.json').exists()
c=json.loads((OUT/'manuscript-checks.json').read_text());assert c['passed']
review={'physical_pages':[1,262,263,264],'pdf_sha256':c['pdf_sha256'],'review':'Scoped visual inspection by author; no layout defect; not human acceptance'}
(OUT/'render-review.json').write_text(json.dumps(review,indent=2)+'\n')
paths=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
before=OUT/'controls-before-method-repairs';before.mkdir();records=[]
old='Next: execute R06 selected reuse/terms/exchanges under docs/plans/accounting-selected-reuse-20261015.md, then the named R03 design repairs before R07/R08. R04 reconciliation and R05 future protocol design are delivered within their stated scope. Runtime execution remains held.'
new='Next: repair the named R03 methods under docs/plans/accounting-corporate-event-repairs-20261015.md, then reconcile remaining finance/bank/insurance/group and exchange obligations before R07/R08. R04/R05 and the finite R06 source-selection increment are delivered; exact runtime dependency admission remains open and execution held.'
section='''## Selected adapter and next method repairs — 15 October 2026

R06's finite source-selection/exchange increment is integrated in Version 3.02, 304 pages. It pins 51 retained source premises and eleven complete documentary exchanges; 1,255 source/schema/semantic checks pass. Four final rendered pages were inspected. Result: data/accounting-master/selected-reuse-20261015/result.md. The exact transitive environment, runtime translation and component-specific terms remain explicitly unresolved; no converter ran. Full readiness stays not_ready.

Next: the named R03 corporate event repairs under docs/plans/accounting-corporate-event-repairs-20261015.md; remaining finance/bank/insurance/group and extended exchanges follow. R07 whole-candidate and R08 all53 assessment retain each unresolved required method and acceptance dependency.

'''
for rel in paths:
 p=ROOT/rel;s=p.read_text();(before/p.name).write_bytes(p.read_bytes());h=sha(p)
 s=s.replace('Version **3.01**, 303 pages','Version **3.02**, 304 pages')
 s=s.replace('docs/design/proposal/manuscript-future-validation-20261015/accounting-product-proposal.pdf','docs/design/proposal/manuscript-selected-reuse-20261015/accounting-product-proposal.pdf')
 s=s.replace('2b942a59c8adfbd5319d96c7ea7948c9fa182ad62cc000e16f9fbe6dd64fd849',c['pdf_sha256']).replace(old,new)
 s=s.replace('Next: R06 under docs/plans/accounting-selected-reuse-20261015.md, alongside the named R03 residuals. R07/R08 follow their resolution or explicit remaining vetoes. No runtime, installation or experiment follows from this documentary completion.',new)
 i=s.index('\n## ');s=s[:i+1]+section+s[i+1:];p.write_text(s);records.append({'path':rel,'before_sha256':h,'after_sha256':sha(p)})
idx=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT);assert idx==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
manifest={'date':'2026-10-15','git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/accounting-selected-reuse-20261015.md','result':str((OUT/'result.md').relative_to(ROOT)),'pdf_sha256':c['pdf_sha256'],'page_count':304,'commands':['inspect_retained.py','build_documentary.py','repair_exchange_closure.py','verify_documentary.py (failed type-check, then repaired pass)','prepare_manuscript.py','accounting_document_tools.py build','accounting_document_tools.py render','verify_manuscript.py','closeout.py'],'environment':'System Python stdlib, pandoc and existing LuaLaTeX; no selected dependency imported','cpu_gpu_status':'CPU document/JSON processing only; no GPU detection','data_version':'51 pinned retained source bodies/dossiers; synthetic fixture bodies supplied in exchanges.json','seeds':'N/A: deterministic documentary checks','wall_seconds':{'build':json.loads((OUT/'build-run.json').read_text())['wall_seconds'],'total':'Not captured; no performance claim'},'checks':{'documentary':1255,'manuscript':c['count']},'controls':records,'index_preserved':True,'readiness':'not_ready','artifacts':[str(p.relative_to(ROOT)) for p in sorted(OUT.glob('*.json'))]}
(OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'version':'3.02','controls':6,'next':'R03 named methods','index_preserved':True}))
