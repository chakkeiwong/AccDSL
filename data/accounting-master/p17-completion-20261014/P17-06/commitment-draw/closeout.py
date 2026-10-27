"""Record bounded results and refresh direct controls without touching the index."""
from pathlib import Path
import hashlib, json, shutil, subprocess
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
ARCH=ROOT/'data/accounting-master/p17-completion-20261014/control-refresh-10'
controls=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-continuation-requirements-20261007.md','docs/plans/accounting-p17-completion-20261014.md','docs/plans/accounting-p18-completion-20261014.md','data/accounting-master/next-plan.md']
matrix='data/accounting-master/p17-completion-20261014/P17-06/operation-matrix.md'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert not ARCH.exists(), 'Do not overwrite a previous control refresh'
before={}
for name in controls+[matrix]:
 p=ROOT/name; dest=ARCH/'before'/name; dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dest); before[name]=sha(p)
oldhash='49c39ff717cb52de0d167f4fe3bcc15fcaeb30313fd1301633fcbb82202ddec9'
newhash='411072801fa21a0e360f9e0cdbc3f0c6f116663e40069c464d97930189bb54c5'
summary='P17-06’s [commitment/drawdown case](../../data/accounting-master/p17-completion-20261014/P17-06/commitment-draw/result.md)\nis delivered in 2.82: 88 exact calculation and 82 preservation/build checks\npass; seven rendered pages are inspected. Original credit history, conditional\ndraw probabilities and provision/allowance movements survive funding. P17-06/E07\nand the connected prudential case remain open.\n\n'
for name in controls:
 p=ROOT/name; s=p.read_text()
 s=s.replace(oldhash,newhash).replace('manuscript-group-fx-disposal-20261014/accounting-product-proposal.pdf','manuscript-bank-commitment-draw-20261014/accounting-product-proposal.pdf')
 s=s.replace('Version **2.81**','Version **2.82**').replace('Version **2.81,','Version **2.82,').replace('**Version 2.81,','**Version 2.82,').replace('Version 2.81, 244','Version 2.82, 246').replace('current Version 2.81 candidate','current Version 2.82 candidate').replace('progress — Version 2.81','progress — Version 2.82').replace('244 pages','246 pages').replace('2.73–2.81','2.73–2.82').replace('through 2.81','through 2.82')
 if name.endswith('accounting-master-current.md'):
  a=s.index('**P17-06:'); b=s.index('\n[P17-01]',a)
  s=s[:a]+'**P17-07: connected insurance cohort and group roll-forward.**\n'+summary+'Refresh the delivered transition, VFA, acquisition/reinsurance and Munich Re\nwork before selecting the missing connected operation. Audit grouping, service,\nfinance, loss-component and reinsurance timing; retain exact historical source\nlimits and actual-fact unknowns. Repair the stale bank-rule sentence in the\nnext successor.\n'+s[b:]
  s=s.replace('Seven pages of 2.81','Seven pages of 2.82')
 elif name.endswith('accounting-master-checkpoint.md'):
  s=s.replace('## Latest completed work\n\n','## Latest completed work\n\n'+summary,1)
  a=s.index('Execute the [P17-06'); b=s.index('\n## Preserve',a)
  s=s[:a]+'Refresh and skeptically audit P17-07’s connected insurance cohort/group case\nunder the [completion plan](accounting-p17-completion-20261014.md). Reuse delivered\nsector evidence, identify the missing interaction and then calculate, integrate\nand inspect its successor. Repair the stale bank-rule sentence there. Continue\nready cross-cutting work after local source or fact blockers.\n'+s[b:]
 elif name.endswith('accounting-continuation-requirements-20261007.md'):
  anchor='P17-05’s [connected group/FX case]'; s=s.replace(anchor,summary+anchor,1)
  s=s.replace('The immediate work is the [P17-06 commitment/drawdown case](accounting-bank-commitment-draw-20261014.md),','The immediate work is the P17-07 connected insurance cohort/group case,')
 elif name.endswith('accounting-p17-completion-20261014.md'):
  s=s.replace('Next execute the [refreshed P17-06 bank plan](accounting-bank-commitment-draw-20261014.md).',summary+'Next refresh and audit P17-07’s connected cohort/group roll-forward against\nthe delivered transition, VFA, acquisition/reinsurance and actual-report work.')
 elif name.endswith('accounting-p18-completion-20261014.md'):
  s=s.replace('139 calculation/81 preservation checks and seven inspected pages. P17-06\ncommitment/drawdown supplies the next integration.','139 calculation/81 preservation checks and seven inspected pages. Commitment/\ndrawdown is integrated in 2.82 with 88 calculation/82 preservation checks and\nseven inspected pages. The refreshed P17-07 insurance case supplies the next\nintegration, together with the narrow stale bank-rule wording repair.')
 else:
  a=s.index('1. Execute'); b=s.index('2. Give',a)
  s=s[:a]+'1. Refresh and skeptically audit **P17-07 connected insurance cohort/group\n   roll-forward** against delivered transition, VFA, acquisition/reinsurance\n   and Munich Re evidence. The [bank commitment case](p17-completion-20261014/P17-06/commitment-draw/result.md)\n   is delivered in 2.82: 88 calculation/82 preservation checks; seven inspected\n   pages. Repair the inherited stale bank-rule sentence in the successor.\n'+s[b:]
  s=s.replace('group/FX in 2.81.','group/FX in 2.81 and commitment/drawdown in 2.82.')
 p.write_text(s)
p=ROOT/matrix; s=p.read_text().replace('protected baseline2.81','current candidate2.82').replace('Preserve; join actual commitment history in next unit','Delivered authored commitment/drawdown connection in 2.82; actual calibration stays open').replace('**Ready:** historical AASB9/7 full draw/lapse, conditional ECL, original risk baseline and provision-to-allowance transfer','**Delivered in 2.82:** historical AASB9/7 full draw/lapse, conditional ECL, original risk baseline and provision-to-allowance transfer; partial/revolving facilities remain broader cases').replace('Next execute `docs/plans/accounting-bank-commitment-draw-20261014.md`.\nAfterward refresh','Commitment/drawdown delivered; see `commitment-draw/result.md`.\nNow refresh');p.write_text(s)
index_ok=(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes()==subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
assert index_ok
refresh={'before':before,'after':{n:sha(ROOT/n) for n in controls+[matrix]},'index_preserved':index_ok,'next':'P17-07 connected insurance cohort/group roll-forward','scope':'Scoped 2.82 supplement; original requirements and full 2.72 assessment unchanged'}
(ARCH/'refresh-manifest.json').write_text(json.dumps(refresh,indent=2)+'\n')
(ARCH/'execution-note.md').write_text('# Direct control refresh 10\n\nVersion 2.82 is current after scoped source, arithmetic, build and page review.\nP17-07 refresh/audit is next. No continuation veto fired. All 100 staged entries\nremain unchanged. Full readiness stays negative; runtime/controller held.\n')
b=json.loads((OUT/'build-run.json').read_text()); c=json.loads((OUT/'calculation-checks.json').read_text()); v=json.loads((OUT/'manuscript-checks.json').read_text())
manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'recorded_utc':datetime.now(timezone.utc).isoformat(),'environment':'System Python exact fractions; trusted LuaLaTeX approved wrapper; Poppler','cpu_gpu_status':'CPU documentary calculations and document tools only; no framework/GPU initialised','random_seeds':'N/A; deterministic','data_version':'commitment documentary case v1; retained AASB9 compilation5 and AASB7 compilation7','plan':'docs/plans/accounting-bank-commitment-draw-20261014.md','result':str((OUT/'result.md').relative_to(ROOT)),'commands':['python3 data/accounting-master/p17-completion-20261014/P17-06/commitment-draw/check_commitment.py','python3 /home/chakwong/python/AccDSL/scripts/accounting_document_tools.py build --candidate docs/design/proposal/manuscript-bank-commitment-draw-20261014 --evidence data/accounting-master/p17-completion-20261014/P17-06/commitment-draw','python3 /home/chakwong/python/AccDSL/scripts/accounting_document_tools.py render --candidate docs/design/proposal/manuscript-bank-commitment-draw-20261014 --evidence data/accounting-master/p17-completion-20261014/P17-06/commitment-draw/final-render --pages 1,165-169,237 --dpi 100','python3 data/accounting-master/p17-completion-20261014/P17-06/commitment-draw/verify_candidate.py'],'calculation_seconds':c['wall_seconds'],'build_seconds':b['wall_seconds'],'verification_seconds':v['wall_seconds'],'page_count':246,'pdf_sha256':newhash,'control_refresh':str(ARCH.relative_to(ROOT)),'artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='run-manifest.json']}
(OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'controls_refreshed':len(controls),'index_preserved':index_ok,'version':'2.82','next':refresh['next']}))
