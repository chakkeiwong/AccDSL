from pathlib import Path
import json,hashlib,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'run-manifest.json').exists()
c=json.loads((OUT/'manuscript-checks.json').read_text());assert c['passed']
(OUT/'render-review.json').write_text(json.dumps({'pdf_sha256':c['pdf_sha256'],'physical_pages':[1,212,213,214,215,216],'review':'Scoped author visual review; no layout defect; human understanding pending'},indent=2)+'\n')
paths=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
before=OUT/'controls-before-insurance-treaty';before.mkdir();records=[]
section='''## Revolving facilities, fees and transfers — 15 October 2026

R03-I is integrated in Version 3.07, 319 pages: partial/revolving funding and ECL, fee purpose and effective interest, eligible partial transfers, retained-risk funding and guarantee continuing involvement. Eight groups pass 74 exact checks; 116 preservation/build checks and six final pages were inspected. Result: data/accounting-master/bank-transfer-fees-20261015/result.md. Actual facts, complex branches and closed exchanges remain open; readiness stays not_ready.

Next: partial/changing insurance treaties and changed estimates/finance presentation under docs/plans/accounting-insurance-treaty-changes-20261015.md, then remaining methods and closed extended exchanges before R07/R08. Runtime and empirical execution remain held.

'''
for rel in paths:
 p=ROOT/rel;s=p.read_text();(before/p.name).write_bytes(p.read_bytes());h=sha(p)
 s=s.replace('Version **3.06**, 316 pages','Version **3.07**, 319 pages').replace('docs/design/proposal/manuscript-awards-participation-20261015/accounting-product-proposal.pdf','docs/design/proposal/manuscript-bank-transfer-fees-20261015/accounting-product-proposal.pdf').replace('2fec624bc40c3ffcdeb41e62d451a5c171fd5e9715aa585b19b73141cc28294e',c['pdf_sha256'])
 s='\n'.join(('Next: partial/changing insurance treaties and estimate/finance methods under docs/plans/accounting-insurance-treaty-changes-20261015.md; remaining methods, closed extended exchanges and R07/R08 stay open. Runtime and empirical execution remain held.' if line.startswith('Next: bank revolving') else line) for line in s.split('\n'))
 i=s.index('\n## ');s=s[:i+1]+section+s[i+1:];p.write_text(s);records.append({'path':rel,'before_sha256':h,'after_sha256':sha(p)})
residual=ROOT/'data/accounting-master/finite-method-decisions-20261015/residual-followup.md'
with residual.open('a') as f:f.write('\n## Progress 15 October 2026 through Version 3.07\n\nR03-I adds partial/revolving capacity and funded/undrawn loss methods, fee classification, eligible partial transfer and guarantee continuing involvement. See bank-transfer-fees-20261015/result.md. Complex transfer options, actual classifications and credit/valuation inputs retain dependencies. Next: partial/changing insurance treaties and estimate/finance methods, remaining groups/financing, and complete exchanges before R07/R08.\n')
idx=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT);assert idx==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
record={'date':'2026-10-15','git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/accounting-bank-transfer-fees-20261015.md','result':str((OUT/'result.md').relative_to(ROOT)),'pdf_sha256':c['pdf_sha256'],'page_count':319,'commands':['check_cases.py','prepare_manuscript.py','accounting_document_tools.py build','accounting_document_tools.py render','verify_manuscript.py','closeout.py'],'environment':'Python stdlib rational arithmetic, pandoc, existing LuaLaTeX','cpu_gpu_status':'CPU only, no GPU detection','data_version':'Retained AASB9/AASB7; eight synthetic bank groups','random_seeds':'N/A: deterministic arithmetic','wall_seconds':{'build':json.loads((OUT/'build-run.json').read_text())['wall_seconds'],'author_total':'Not captured; no performance claim'},'checks':{'arithmetic':74,'manuscript':c['count']},'artifacts':[str(p.relative_to(ROOT)) for p in sorted(OUT.glob('*.json'))],'controls':records,'index_preserved':True,'readiness':'not_ready'}
(OUT/'run-manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'version':'3.07','controls':6,'checks':record['checks'],'next':'Insurance treaty changes and remaining R03','index_preserved':True}))
