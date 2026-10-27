from pathlib import Path
import json,hashlib,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not (OUT/'run-manifest.json').exists()
c=json.loads((OUT/'manuscript-checks.json').read_text());assert c['passed']
(OUT/'render-review.json').write_text(json.dumps({'pdf_sha256':c['pdf_sha256'],'physical_pages':[1,177,178,179,180,181],'review':'Scoped author visual review; no layout defect; human understanding pending'},indent=2)+'\n')
paths=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
before=OUT/'controls-before-awards-participation';before.mkdir();records=[]
section='''## Hedge components and rebalancing — 15 October 2026

R03-H1 is integrated in Version 3.05, 313 pages. Separate time-value reserves, transaction/time-period treatment, aligned terms and prospective rebalancing have source-supported conditional methods. Six groups pass 69 exact checks; 112 preservation/build checks and six final rendered pages were inspected. Result: data/accounting-master/financing-components-20261015/result.md. Complex component valuation and the other financing methods remain open; full readiness is not_ready.

Next: award conditions, settlement choice and participation under docs/plans/accounting-awards-participation-20261015.md, then remaining sector/group methods and closed extended exchanges before R07/R08. Runtime and empirical execution remain held.

'''
for rel in paths:
 p=ROOT/rel;s=p.read_text();(before/p.name).write_bytes(p.read_bytes());h=sha(p)
 s=s.replace('Version **3.04**, 310 pages','Version **3.05**, 313 pages').replace('docs/design/proposal/manuscript-impairment-tax-20261015/accounting-product-proposal.pdf','docs/design/proposal/manuscript-financing-components-20261015/accounting-product-proposal.pdf').replace('a1910d7e5a6034b37529bf2bb0f795cb52f17f385b3beaeee09b3c621f901af9',c['pdf_sha256'])
 s='\n'.join(('Next: award conditions, settlement choice and participation under docs/plans/accounting-awards-participation-20261015.md; remaining financing/sector/group methods, closed extended exchanges and R07/R08 stay open. Runtime and empirical execution remain held.' if line.startswith('Next: financing components') else line) for line in s.split('\n'))
 i=s.index('\n## ');s=s[:i+1]+section+s[i+1:];p.write_text(s);records.append({'path':rel,'before_sha256':h,'after_sha256':sha(p)})
residual=ROOT/'data/accounting-master/finite-method-decisions-20261015/residual-followup.md'
with residual.open('a') as f:f.write('\n## Progress 15 October 2026 through Version 3.05\n\nR03-H1 adds separate option-time-value accounting, aligned-term branches, forward/basis election and prospective rebalancing/layer methods; see financing-components-20261015/result.md. Complex component valuation, delayed/contingent inducement, awards/cash choice/participation and group hedges remain open. Continue awards/participation, then remaining sectors/groups and closed extended profiles before R07/R08.\n')
idx=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT);assert idx==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()
record={'date':'2026-10-15','git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'plan':'docs/plans/accounting-financing-components-20261015.md','result':str((OUT/'result.md').relative_to(ROOT)),'pdf_sha256':c['pdf_sha256'],'page_count':313,'commands':['check_cases.py','prepare_manuscript.py','accounting_document_tools.py build','accounting_document_tools.py render','verify_manuscript.py','closeout.py'],'environment':'Python stdlib rational arithmetic, pandoc, existing LuaLaTeX','cpu_gpu_status':'CPU only, no GPU detection','data_version':'Retained AASB9 compilation5; six synthetic hedge-component/rebalancing groups','random_seeds':'N/A: deterministic arithmetic','wall_seconds':{'build':json.loads((OUT/'build-run.json').read_text())['wall_seconds'],'author_total':'Not captured; no performance claim'},'checks':{'arithmetic':69,'manuscript':c['count']},'artifacts':[str(p.relative_to(ROOT)) for p in sorted(OUT.glob('*.json'))],'controls':records,'index_preserved':True,'readiness':'not_ready'}
(OUT/'run-manifest.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'version':'3.05','controls':6,'checks':record['checks'],'next':'Awards participation and remaining R03','index_preserved':True}))
