from pathlib import Path
import hashlib,json,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'run-manifest.json').exists()
checks=json.loads((OUT/'manuscript-checks.json').read_text());assert checks['passed']
build=json.loads((OUT/'build-run.json').read_text());render=json.loads((OUT/'render-final/render-manifest.json').read_text())
review={'pdf_sha256':checks['pdf_sha256'],'physical_pages':[1,267,268,269,270,271,272],'reviewer':'Author visual inspection in active session','verdict':'Scoped typography and exposition review passed after citation/prose repair; human comprehension not assessed','prior_render':'render-v1 retained'}
(OUT/'render-review.json').write_text(json.dumps(review,indent=2)+'\n')
paths=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
before=OUT/'controls-before-r06';before.mkdir();records=[]
oldnext='Next: execute R05 future validation protocols, then R06 selected reuse/terms/exchanges, while resolving the named R03 design residuals before R07/R08. R04 scoped reconciliation is delivered; broad scholarly coverage remains open. Runtime execution remains held.'
nextline='Next: execute R06 selected reuse/terms/exchanges under docs/plans/accounting-selected-reuse-20261015.md, then the named R03 design repairs before R07/R08. R04 reconciliation and R05 future protocol design are delivered within their stated scope. Runtime execution remains held.'
section='''## Future validation design — 15 October 2026

R05 is integrated in Version 3.01 (303 pages): target-specific future protocols distinguish exact conformance, extraction, predictive, sector, numerical/causal and usability evidence. Forecast origins, partly elapsed periods, first-release outcomes, exposure, unresolved mass and uncertainty are explicit. 148 protocol/source/arithmetic checks and 110 preservation/build checks passed; seven final rendered pages were inspected. Result: data/accounting-master/future-validation-20261015/result.md. Actual eligible data, budgets, inference designs and empirical results remain separate pre-run dependencies. Full readiness remains not_ready.

Next: R06 under docs/plans/accounting-selected-reuse-20261015.md, alongside the named R03 residuals. R07/R08 follow their resolution or explicit remaining vetoes. No runtime, installation or experiment follows from this documentary completion.

'''
for rel in paths:
 p=ROOT/rel;s=p.read_text();(before/p.name).write_bytes(p.read_bytes());original=sha(p)
 s=s.replace('Version **3.00**, 298 pages','Version **3.01**, 303 pages')
 s=s.replace('docs/design/proposal/manuscript-corporate-residuals-20261015/accounting-product-proposal.pdf','docs/design/proposal/manuscript-future-validation-20261015/accounting-product-proposal.pdf')
 s=s.replace('2f827b851470e38a3242bb70a0a106a8ff8c3e9140c1cfa66a71effbc4d97f59',checks['pdf_sha256'])
 s=s.replace(oldnext,nextline)
 s=s.replace('Next: R05 under docs/plans/accounting-future-validation-20261015.md. Prepare target-specific future protocols only; no experiment, runtime, installation or review campaign is authorised by this closeout. Continue R06 and the named R03 repairs before R07/R08.',nextline)
 pos=s.index('\n## ');s=s[:pos+1]+section+s[pos+1:];p.write_text(s)
 records.append({'path':rel,'before_sha256':original,'after_sha256':sha(p)})
index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert index==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
record={'date':'2026-10-15','git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/accounting-future-validation-20261015.md','result':str((OUT/'result.md').relative_to(ROOT)),'candidate':'docs/design/proposal/manuscript-future-validation-20261015/accounting-product-proposal.pdf','pdf_sha256':checks['pdf_sha256'],'page_count':303,'commands':['prepare_evidence.py','verify_protocol.py','prepare_manuscript.py','accounting_document_tools.py build (twice)','accounting_document_tools.py render (initial and final)','repair_presentation.py','verify_manuscript.py','closeout.py'],'environment':'System python3, pandoc and existing LuaLaTeX/renderer; no candidate package imported','cpu_gpu_status':'CPU document processing; no GPU detection or use','seeds':'N/A for documentary checks; protocol future convenience seeds are not executed','data_version':'Protected Version3.00; corpus panel v2/protocol v1 retained; source DOI10.1198/016214506000001437','wall_seconds':{'build1':26.31928402557969,'build2':build['wall_seconds'],'protocol_checks':json.loads((OUT/'protocol-checks.json').read_text())['wall_seconds'],'total_author_work':'Not captured; no performance claim'},'checks':{'protocol':148,'manuscript':110},'artifacts':[str(p.relative_to(ROOT)) for p in sorted(OUT.glob('*.json'))],'controls':records,'index_preserved':True,'readiness':'not_ready','next':'R06 and named R03 repairs'}
(OUT/'run-manifest.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'version':'3.01','page_count':303,'controls_updated':len(records),'index_preserved':True,'next':'R06'}))
