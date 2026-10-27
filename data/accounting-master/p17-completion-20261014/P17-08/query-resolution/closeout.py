"""Refresh six live controls while preserving prior exact evidence."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent
ARCH=ROOT/'data/accounting-master/p17-completion-20261014/control-refresh-12'
controls=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
matrix='data/accounting-master/p17-completion-20261014/P17-08/operation-matrix.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not ARCH.exists()
before={}
for n in controls+[matrix]:
 p=ROOT/n;q=ARCH/'before'/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);before[n]=sha(p)
summary="""P17-08’s [query-resolution cases](../../data/accounting-master/p17-completion-20261014/P17-08/query-resolution/result.md)
are delivered in 2.84: 671 exact numerical/dependency checks, 13 semantic
comparisons of 17 specified exchanges, and 84 preservation/build checks pass;
five pages are inspected. Exact-real bounds, output rounding and cent-grid
inputs stay distinct; sector memory and unresolved mass survive query changes.
P17-08 and broader mapping/continuous/interaction obligations remain open.

"""
for n in controls:
 p=ROOT/n;s=p.read_text()
 # Remove accidental literal patch markers from the previous refresh only.
 s='\n'.join(line[1:] if line.startswith('+') else line for line in s.split('\n'))
 s=s.replace('2fe73c20217962911bc8454ba391f2131296dbc3d07a00f4e91e1514248b98dd','12979f23fbac7ea69d3b2fe55917e8fd6a1a4e3d15243c4e455effc3c9a87943').replace('manuscript-insurance-connected-groups-20261014/accounting-product-proposal.pdf','manuscript-query-resolution-20261014/accounting-product-proposal.pdf')
 s=s.replace('Version **2.83**','Version **2.84**').replace('**Version 2.83,','**Version 2.84,').replace('Version 2.83, 249','Version 2.84, 251').replace('current Version 2.83 candidate','current Version 2.84 candidate').replace('progress — Version 2.83','progress — Version 2.84').replace('249 pages','251 pages').replace('2.73–2.83','2.73–2.84').replace('through 2.83','through 2.84')
 if n.endswith('accounting-master-current.md'):
  a=s.index('**P17-08:');b=s.index('\n[P17-01]',a)
  s=s[:a]+'**P17-09: consequential literature and claim support.**\n'+summary+'Audit cumulative source inquiries and the six ledgers against current claims.\nChoose a specific consequential missing method or competitor, inspect retained\ntechnical evidence first, then use a distinct supported retrieval lead where\nneeded. Preserve blocked originals and exact source/version boundaries.\n'+s[b:]
  s=s.replace('Seven pages of 2.83 received','Five pages of 2.84 received')
 elif n.endswith('accounting-master-checkpoint.md'):
  s=s.replace('## Latest completed work\n\n','## Latest completed work\n\n'+summary,1)
  a=s.index('Refresh and skeptically audit P17-08');b=s.index('\n## Preserve',a)
  s=s[:a]+'Refresh and skeptically audit P17-09 consequential literature/claim support\nunder the [completion plan](accounting-p17-completion-20261014.md). Reuse the\ncumulative inquiries and six ledgers, choose a specific missing decision and\nrecord source, derivation and omission boundaries. Continue independent ready\ninterface work after any local source block.\n'+s[b:]
 elif n.endswith('accounting-continuation-requirements-20261007.md'):
  s=s.replace('P17-07’s [connected insurance groups]',summary+'P17-07’s [connected insurance groups]',1)
  s=s.replace('The immediate work is the P17-08 cross-cutting history/numerical audit,','The immediate work is the P17-09 consequential literature/claim audit,')
 elif n.endswith('accounting-p17-completion-20261014.md'):
  old='Next refresh and audit P17-08’s cross-cutting history/numerical contracts\nagainst the current source, bank, group and insurance interactions.'
  assert old in s;s=s.replace(old,summary+'Next refresh and audit P17-09 consequential source claims and competing\nmethods against cumulative research before selecting a bounded inquiry.')
 elif n.endswith('accounting-p18-completion-20261014.md'):
  old='P17-08’s audited cross-cutting interactions supply the next integration.'
  assert old in s;s=s.replace(old,'Query-resolution interactions are integrated in 2.84 with 671 numerical,\n13 exchange and 84 preservation checks plus five inspected pages. The next\nintegration follows the refreshed P17-09 consequential-source audit.')
 else:
  a=s.index('1. Refresh');b=s.index('2. Give',a)
  s=s[:a]+'1. Refresh and skeptically audit **P17-09 consequential literature/claims**\n   against cumulative inquiries and all six ledgers before choosing the next\n   supported source route. The [query-resolution result](p17-completion-20261014/P17-08/query-resolution/result.md)\n   is delivered in 2.84: 671 numerical, 13 exchange and 84 preservation checks;\n   five inspected pages. No continuation veto fired.\n'+s[b:]
  s=s.replace('connected insurance in 2.83.','connected insurance in 2.83; query resolution in 2.84.')
 p.write_text(s)
p=ROOT/matrix;s=p.read_text().replace('current2.83','current2.84').replace('Ready exact images/tie/endpoints and operation-order exchange','Delivered2.84: exact images/tie/endpoints and operation-order exchanges').replace('New sector history counterexamples and changed-query refusal','Delivered2.84: sector history counterexamples and changed-query refusal').replace('Execute accounting-query-resolution-boundaries-20261014.md after its skeptical\naudit.','Query-resolution plan delivered; see query-resolution/result.md.');p.write_text(s)
index=(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()==subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT);assert index
(ARCH/'refresh-manifest.json').write_text(json.dumps({'before':before,'after':{n:sha(ROOT/n) for n in controls+[matrix]},'index_preserved':index,'next':'P17-09 literature audit','repair':'Removed literal leading plus signs inadvertently introduced in refresh11 controls; substantive content preserved.'},indent=2)+'\n')
(ARCH/'execution-note.md').write_text('# Control refresh12\n\nVersion2.84 scoped supplement current; full readiness negative. P17-09 audit\nnext. Literal patch markers repaired. All100 staged entries preserved.\n')
b=json.loads((OUT/'build-run.json').read_text());c=json.loads((OUT/'calculation-checks.json').read_text());v=json.loads((OUT/'manuscript-checks.json').read_text())
manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'recorded_utc':datetime.now(timezone.utc).isoformat(),'environment':'System Python Fraction/integer arithmetic; trusted LuaLaTeX wrapper; Poppler','cpu_gpu_status':'CPU documentary calculations only; no GPU/framework initialisation','random_seeds':'N/A deterministic','data_version':'query-resolution-documentary.v1 and retained2.82/2.83 cases','plan':'docs/plans/accounting-query-resolution-boundaries-20261014.md','result':str((OUT/'result.md').relative_to(ROOT)),'commands':['python3 data/accounting-master/p17-completion-20261014/P17-08/query-resolution/check_queries.py','python3 data/accounting-master/p17-completion-20261014/P17-08/query-resolution/exchanges.py','python3 /home/chakwong/python/AccDSL/scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-query-resolution-20261014 --evidence data/accounting-master/p17-completion-20261014/P17-08/query-resolution','python3 /home/chakwong/python/AccDSL/scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-query-resolution-20261014 --evidence data/accounting-master/p17-completion-20261014/P17-08/query-resolution/final-render --pages 1,74-77 --dpi 100','python3 data/accounting-master/p17-completion-20261014/P17-08/query-resolution/verify_candidate.py'],'calculation_seconds':c['wall_seconds'],'build_seconds':b['wall_seconds'],'verification_seconds':v['wall_seconds'],'pdf_sha256':b['pdf_sha256'],'page_count':251,'control_refresh':str(ARCH.relative_to(ROOT)),'artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='run-manifest.json']}
(OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'version':'2.84','controls':6,'index_preserved':index,'next':'P17-09'}))
