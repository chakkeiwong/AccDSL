from pathlib import Path
import json,hashlib,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'run-manifest.json').exists()
c=json.loads((OUT/'manuscript-checks.json').read_text());assert c['passed']
(OUT/'render-review.json').write_text(json.dumps({'pdf_sha256':c['pdf_sha256'],'physical_pages':[1,124,125,126,127],'review':'Scoped author visual review; no layout defect; human understanding pending'},indent=2)+'\n')
paths=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
before=OUT/'controls-before-financing-components';before.mkdir();records=[]
section='''## Impairment and tax-origin methods — 15 October 2026

R03-G is integrated in Version 3.04, 310 pages. Corporate-asset ordering, partial/NCI goodwill, revalued tax origins, acquisition/investment tax and the historical Pillar Two accounting exception have conditional methods. Six case groups pass 39 exact checks and 113 preservation/build checks; final pages 1 and 124–127 were inspected. Result: data/accounting-master/impairment-tax-repairs-20261015/result.md. Full readiness remains not_ready.

Next: financing components and conditions under docs/plans/accounting-financing-components-20261015.md, then remaining bank/insurance/group methods and closed extended exchanges before R07/R08. Runtime and empirical execution remain held.

'''
for rel in paths:
 p=ROOT/rel;s=p.read_text();(before/p.name).write_bytes(p.read_bytes());h=sha(p)
 s=s.replace('Version **3.03**, 307 pages','Version **3.04**, 310 pages').replace('docs/design/proposal/manuscript-corporate-events-20261015/accounting-product-proposal.pdf','docs/design/proposal/manuscript-impairment-tax-20261015/accounting-product-proposal.pdf').replace('898396c21a3fd019304ba6c204de0a341b17eb6d629586e2d549fab5a810bbc2',c['pdf_sha256'])
 s='\n'.join(('Next: financing components and conditions under docs/plans/accounting-financing-components-20261015.md; remaining sector/group methods, closed extended exchanges and R07/R08 stay open. Runtime and empirical execution remain held.' if line.startswith('Next: corporate/group impairment') else line) for line in s.split('\n'))
 i=s.index('\n## ');s=s[:i+1]+section+s[i+1:];p.write_text(s);records.append({'path':rel,'before_sha256':h,'after_sha256':sha(p)})
residual=ROOT/'data/accounting-master/finite-method-decisions-20261015/residual-followup.md'
with residual.open('a') as f:f.write('\n## Progress 15 October 2026 through Version 3.04\n\nR03-G conditionally resolves corporate asset/NCI impairment interaction, profit/OCI tax origins, acquisition and investment exceptions, and the historical Pillar Two accounting boundary. See impairment-tax-repairs-20261015/result.md. Actual values and current authority remain application dependencies. Next: financing components/conditions, remaining bank/insurance/group operations and closed extended profiles. R07/R08 remain open.\n')
idx=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT);assert idx==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
record={'date':'2026-10-15','git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/accounting-impairment-tax-repairs-20261015.md','result':str((OUT/'result.md').relative_to(ROOT)),'pdf_sha256':c['pdf_sha256'],'page_count':310,'commands':['check_cases.py','prepare_manuscript.py','repair_presentation.py','accounting_document_tools.py build','accounting_document_tools.py render','verify_manuscript.py','closeout.py'],'environment':'Python stdlib rational arithmetic, pandoc, existing LuaLaTeX','cpu_gpu_status':'CPU only, no GPU detection','data_version':'Retained EU2023/1803 and EU2023/2468; six synthetic case groups','random_seeds':'N/A: deterministic arithmetic','wall_seconds':{'build':json.loads((OUT/'build-run.json').read_text())['wall_seconds'],'author_total':'Not captured; no performance claim'},'checks':{'arithmetic':39,'manuscript':c['count']},'artifacts':[str(p.relative_to(ROOT)) for p in sorted(OUT.glob('*.json'))],'controls':records,'index_preserved':True,'readiness':'not_ready'}
(OUT/'run-manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'version':'3.04','controls':6,'checks':record['checks'],'next':'Financing components and remaining R03','index_preserved':True}))
