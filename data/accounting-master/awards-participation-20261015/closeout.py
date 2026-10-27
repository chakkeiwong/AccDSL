from pathlib import Path
import json,hashlib,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'run-manifest.json').exists()
c=json.loads((OUT/'manuscript-checks.json').read_text());assert c['passed']
(OUT/'render-review.json').write_text(json.dumps({'pdf_sha256':c['pdf_sha256'],'physical_pages':[1,180,181,182,183,184],'review':'Scoped author visual review; no layout defect; human understanding pending'},indent=2)+'\n')
paths=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
before=OUT/'controls-before-bank-transfer-fees';before.mkdir();records=[]
section='''## Award conditions and participation — 15 October 2026

R03-H2 is integrated in Version 3.06, 316 pages: service/market/non-market conditions, cancellation, cash remeasurement, settlement choice and participation/EPS have conditional methods. Eleven groups pass 79 exact checks; 113 preservation/build checks and six final rendered pages were inspected. Result: data/accounting-master/awards-participation-20261015/result.md. Valuation, further financing methods and complete exchanges remain open. Full readiness stays not_ready.

Next: bank revolving drawings, fee classification and partial transfer/continuing involvement under docs/plans/accounting-bank-transfer-fees-20261015.md, then remaining methods and closed extended exchanges before R07/R08. Runtime and empirical execution remain held.

'''
for rel in paths:
 p=ROOT/rel;s=p.read_text();(before/p.name).write_bytes(p.read_bytes());h=sha(p)
 s=s.replace('Version **3.05**, 313 pages','Version **3.06**, 316 pages').replace('docs/design/proposal/manuscript-financing-components-20261015/accounting-product-proposal.pdf','docs/design/proposal/manuscript-awards-participation-20261015/accounting-product-proposal.pdf').replace('4fe5f9c2d878aad0f848d63e31cdba799fcea111717dac6e21dad0d0c062153e',c['pdf_sha256'])
 s='\n'.join(('Next: bank revolving drawings, fees and partial transfers under docs/plans/accounting-bank-transfer-fees-20261015.md; remaining financing/sector/group methods, closed extended exchanges and R07/R08 stay open. Runtime and empirical execution remain held.' if line.startswith('Next: award conditions') else line) for line in s.split('\n'))
 i=s.index('\n## ');s=s[:i+1]+section+s[i+1:];p.write_text(s);records.append({'path':rel,'before_sha256':h,'after_sha256':sha(p)})
residual=ROOT/'data/accounting-master/finite-method-decisions-20261015/residual-followup.md'
with residual.open('a') as f:f.write('\n## Progress 15 October 2026 through Version 3.06\n\nR03-H2 adds service/market/non-market/cancellation and cash-choice award methods, participating earnings and option/cash-share EPS distinctions; see awards-participation-20261015/result.md. Complex valuation, beneficial modifications, delayed inducement and group hedges remain separate financing work. Next: bank revolving drawings, fee classification and partial transfer/continuing involvement; then remaining sector/group methods and complete exchanges before R07/R08.\n')
idx=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT);assert idx==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
record={'date':'2026-10-15','git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/accounting-awards-participation-20261015.md','result':str((OUT/'result.md').relative_to(ROOT)),'pdf_sha256':c['pdf_sha256'],'page_count':316,'commands':['check_cases.py','prepare_manuscript.py','accounting_document_tools.py build','accounting_document_tools.py render','verify_manuscript.py','closeout.py'],'environment':'Python stdlib rational arithmetic, pandoc, existing LuaLaTeX','cpu_gpu_status':'CPU only, no GPU detection','data_version':'Retained EU2023/1803 IFRS2/IAS33; eleven synthetic award/EPS groups','random_seeds':'N/A: deterministic arithmetic','wall_seconds':{'build':json.loads((OUT/'build-run.json').read_text())['wall_seconds'],'author_total':'Not captured; no performance claim'},'checks':{'arithmetic':79,'manuscript':c['count']},'artifacts':[str(p.relative_to(ROOT)) for p in sorted(OUT.glob('*.json'))],'controls':records,'index_preserved':True,'readiness':'not_ready'}
(OUT/'run-manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'version':'3.06','controls':6,'checks':record['checks'],'next':'Bank transfer fees and remaining R03','index_preserved':True}))
