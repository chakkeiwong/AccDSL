"""Archive and refresh current controls; preserve unrelated index and history."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent
ARCH=ROOT/'data/accounting-master/p17-completion-20261014/control-refresh-11'
controls=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
matrix='data/accounting-master/p17-completion-20261014/P17-07/operation-matrix.md'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert not ARCH.exists()
before={}
for n in controls+[matrix]:
 p=ROOT/n;q=ARCH/'before'/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q);before[n]=sha(p)
summary='P17-07’s [connected insurance groups](../../data/accounting-master/p17-completion-20261014/P17-07/connected-groups/result.md)\nare delivered in 2.83: 248 exact calculation and 83 preservation/build checks\npass; seven rendered pages are inspected. Separate issued and held groups\nreconcile through finance, service and settlement; timely/late treaty and\ninvalid pooling cases expose errors hidden by identical terminal cash.\nP17-07/E07 and actuarial/actual-fact obligations remain open.\n\n'
for n in controls:
 p=ROOT/n;s=p.read_text().replace('411072801fa21a0e360f9e0cdbc3f0c6f116663e40069c464d97930189bb54c5','2fe73c20217962911bc8454ba391f2131296dbc3d07a00f4e91e1514248b98dd').replace('manuscript-bank-commitment-draw-20261014/accounting-product-proposal.pdf','manuscript-insurance-connected-groups-20261014/accounting-product-proposal.pdf')
 s=s.replace('Version **2.82**','Version **2.83**').replace('**Version 2.82,','**Version 2.83,').replace('Version 2.82, 246','Version 2.83, 249').replace('current Version 2.82 candidate','current Version 2.83 candidate').replace('progress — Version 2.82','progress — Version 2.83').replace('246 pages','249 pages').replace('2.73–2.82','2.73–2.83').replace('through 2.82','through 2.83')
 if n.endswith('accounting-master-current.md'):
  a=s.index('**P17-07:');b=s.index('\n[P17-01]',a)
  s=s[:a]+'**P17-08: cross-cutting history and numerical contracts.**\n'+summary+'Audit existing reconstruction, query, mapping, sufficient-state and partial-\n+execution contracts against the delivered bank/group/insurance cases. Preserve\n+exact supported behavior; add connected positive/adverse exchanges only where\n+a substantive interaction remains missing. The bank-rule wording repair is\n+delivered in 2.83.\n'+s[b:]
  s=s.replace('Seven pages of 2.82','Seven pages of 2.83')
 elif n.endswith('accounting-master-checkpoint.md'):
  s=s.replace('## Latest completed work\n\n','## Latest completed work\n\n'+summary,1)
  a=s.index('Refresh and skeptically audit P17-07');b=s.index('\n## Preserve',a)
  s=s[:a]+'Refresh and skeptically audit P17-08 cross-cutting history and numerical\n+contracts under the [completion plan](accounting-p17-completion-20261014.md).\n+Use the current sector cases to test group/state preservation, query changes,\n+strict bounds, incomplete branches and result status. Continue ready literature\n+and interface work after local blockers; no runtime campaign is authorised.\n'+s[b:]
 elif n.endswith('accounting-continuation-requirements-20261007.md'):
  s=s.replace('P17-06’s [commitment/drawdown case]',summary+'P17-06’s [commitment/drawdown case]',1)
  s=s.replace('The immediate work is the P17-07 connected insurance cohort/group case,','The immediate work is the P17-08 cross-cutting history/numerical audit,')
 elif n.endswith('accounting-p17-completion-20261014.md'):
  old='Next refresh and audit P17-07’s connected cohort/group roll-forward against\nthe delivered transition, VFA, acquisition/reinsurance and actual-report work.'
  assert old in s;s=s.replace(old,summary+'Next refresh and audit P17-08’s cross-cutting history/numerical contracts\nagainst the current source, bank, group and insurance interactions.')
 elif n.endswith('accounting-p18-completion-20261014.md'):
  old='The refreshed P17-07 insurance case supplies the next\nintegration, together with the narrow stale bank-rule wording repair.'
  assert old in s;s=s.replace(old,'The connected insurance case and narrow bank-rule repair are integrated\nin 2.83 with 248 calculation/83 preservation checks and seven inspected pages.\nP17-08’s audited cross-cutting interactions supply the next integration.')
 else:
  a=s.index('1. Refresh');b=s.index('2. Give',a)
  s=s[:a]+'1. Refresh and skeptically audit **P17-08 history/numerical interactions**\n+   using the existing contracts and current bank, group and insurance cases.\n+   The [connected insurance result](p17-completion-20261014/P17-07/connected-groups/result.md)\n+   is delivered in 2.83: 248 calculation/83 preservation checks; seven inspected\n+   pages. No continuation veto fired; preserve detailed residual sector work.\n'+s[b:]
  s=s.replace('commitment/drawdown in 2.82.','commitment/drawdown in 2.82; connected insurance in 2.83.')
 p.write_text(s)
p=ROOT/matrix;s=p.read_text().replace('Baseline 2.82','Current candidate 2.83').replace('execute connected-groups plan','delivered in 2.83; broader changing-estimate/OCI cases remain').replace('Work adverse pooling with unchanged terminal cash;','Adverse pooling delivered in 2.83;').replace('Full treaty measurement/service/finance/settlement alongside gross groups; ordinary late-treaty comparator','Delivered in 2.83: full fixed-treaty measurement/service/finance/settlement and ordinary late-treaty comparator; partial/changing cover remains').replace('Execute','Delivered:').replace('Its completion supplies','The result supplies');p.write_text(s)
index=(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()==subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT);assert index
(ARCH/'refresh-manifest.json').write_text(json.dumps({'before':before,'after':{n:sha(ROOT/n) for n in controls+[matrix]},'index_preserved':index,'next':'P17-08 history/numerical audit'},indent=2)+'\n')
(ARCH/'execution-note.md').write_text('# Control refresh 11\n\nVersion 2.83 scoped supplement accepted; full readiness remains negative.\nP17-08 refresh/audit next. No continuation veto; 100 staged entries preserved.\n')
b=json.loads((OUT/'build-run.json').read_text());c=json.loads((OUT/'calculation-checks.json').read_text());v=json.loads((OUT/'manuscript-checks.json').read_text())
manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'recorded_utc':datetime.now(timezone.utc).isoformat(),'environment':'System Python Fraction arithmetic; trusted LuaLaTeX wrapper; Poppler','cpu_gpu_status':'CPU documentary tools only; no GPU/framework initialisation','random_seeds':'N/A deterministic','data_version':'insurance-connected-documentary.v1; retained AASB17 F2023C00382','plan':'docs/plans/accounting-insurance-connected-groups-20261014.md','result':str((OUT/'result.md').relative_to(ROOT)),'commands':['python3 data/accounting-master/p17-completion-20261014/P17-07/connected-groups/check_groups.py','python3 /home/chakwong/python/AccDSL/scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-insurance-connected-groups-20261014 --evidence data/accounting-master/p17-completion-20261014/P17-07/connected-groups','python3 /home/chakwong/python/AccDSL/scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-insurance-connected-groups-20261014 --evidence data/accounting-master/p17-completion-20261014/P17-07/connected-groups/final-render-v2 --pages 1,170,174-178 --dpi 100','python3 data/accounting-master/p17-completion-20261014/P17-07/connected-groups/verify_candidate.py'],'calculation_seconds':c['wall_seconds'],'final_build_seconds':b['wall_seconds'],'first_build_seconds':json.loads((OUT/'initial-wording/build-run.json').read_text())['wall_seconds'],'verification_seconds':v['wall_seconds'],'pdf_sha256':b['pdf_sha256'],'page_count':249,'control_refresh':str(ARCH.relative_to(ROOT)),'artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='run-manifest.json']}
(OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'version':'2.83','controls':6,'index_preserved':index,'next':'P17-08'}))
