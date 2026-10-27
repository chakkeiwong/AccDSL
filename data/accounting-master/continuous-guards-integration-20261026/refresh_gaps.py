"""Append evidence to a successor; never change frozen predecessor registers."""
from pathlib import Path
import json,hashlib,copy
R=Path(__file__).resolve().parents[3]
P=R/'data/accounting-master/gap-decision-refresh-20261026'
O=R/'data/accounting-master/gap-continuous-refresh-20261026';O.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((P/n).read_text())
def save(n,x):(O/n).write_text(json.dumps(x,indent=2)+'\n')
lock={str(p.relative_to(R)):sha(p) for p in P.iterdir() if p.is_file()}
save('predecessor-lock.json',lock)
a=read('audit-status.json');cp=read('closure-packages.json');f=read('failure-register.json')
new=[
 ('Selected conversion-rights bridge',['MC13','MC17','MC24','MC25','L03'],'conversion-rights-bridge-20261026','Eight complete cases,145 assertions,14 controls; supplied carrying values and rights; actual accounting measurement remains open.'),
 ('Dual-edition decision and conversion integration',['MC28','MC33','MC34'],'decision-conversion-integration-20261026','Version5.19 integrated actor decisions, two-date control and typed conversion; later funding and measurement results remain separate companions.'),
 ('Dated four-party funding with prefix liquidity',['MC13','MC14','MC17','MC20','MC24','MC25','L03'],'dated-funding-bundle-20261026','Four complete bundles,232 assertions,20 controls; each cash prefix and reciprocal transfer checked; synthetic treatments and settlement assumptions remain.'),
 ('Accounting admission mismatch for contingent financing',['MC13','MC17','MC24','MC35','L03'],'conversion-measurement-audit-20261026','Existing maturity-only accounting profile and dated admission do not cover the new2027/2028 contingent example. Seventeen source/exact checks; authority, terms, issuer/holder treatment and measurement unresolved.'),
 ('Exact mixed continuous guards and observation policies',['MC11','MC26','G16','P17-08.04','L01'],'continuous-guards-20261026','264 whole-region state comparisons,2010 assertions,24 controls;32 retained regions share14 calculations. One-rate one-date synthetic reference; broader compression and error premises remain open.')]
for title,req,unit,status in new:
 p=R/'data/accounting-master'/unit/'result.md';assert p.exists()
 a['successor_deltas'].append({'id':f"D{len(a['successor_deltas'])+1}",'title':title,'requirements':req,'evidence':str(p.relative_to(R)),'sha256':sha(p),'current_disposition':status})
a['baseline']='Version5.19 plus inspected conversion, funding, accounting-scope and continuous-guard companions; manuscript successor tracked by live master routes.'
a['predecessor']={'path':str(P.relative_to(R)),'lock':'predecessor-lock.json'}
for p in cp['packages']:
 if p['id']=='W04':
  p['existing_support']+=' Exact one-rate/one-date piecewise-affine reference compares complete states and observation-measurable policies on exhaustive intervals. Budgeted lazy transitions preserve all unresolved regions;24 controls and explicit margin derivation.'
  p['next_action']='Extend to two dates with a persistent hidden contractual mode and common typed journals; then joint multidimensional regions, validated approximation bounds, rounded money and a scoped capacity study.'
 elif p['id']=='W05':
  p['existing_support']+=' Dated four-party funding compares complete books, journals, reports and every cash prefix under six transfer orders; source finality and treatments are supplied.'
  p['next_action']='Resolve source/measurement premises before joining dated issuance to conversion; continue actual multiple-clause rights and later settlement without erasing unpaid history.'
 elif p['id']=='W06':
  p['existing_support']+=' Typed conversion-rights bridge and date0 four-party funding have complete-state comparisons. Separate measurement audit rejects unqualified reuse of maturity-only admission for2027/2028 contingent terms.'
  p['next_action']='Finish applicable dated authority and full contingent terms; derive issuer/holder classification and intervening measurement, then join issuance, conversion and terminal liquidation.'
 elif p['id']=='W07':
  p['existing_support']+=' Conversion measurement audit distinguishes pricing law, effective interest, contractual promises and dated package admission.'
  p['next_action']='Finish the active contingent-conversion authority/measurement preparation while preserving zero-weight CGU reversal and other mixed-promise/calendar/tax/costing gaps.'
 elif p['id']=='W16':
  p['existing_support']+=' Complete typed conversion, dated funding and bounded continuous-state comparisons now exist as scoped companions.'
  p['next_action']='Compose admitted measurement, financing settlement, actor information and later rights under common typed execution; preserve independent complete-state and invalidity comparators.'
 elif p['id']=='W17':
  p['existing_support']+=' Version5.19 integrates decision/control/conversion; checked continuous-guard addition is being integrated in a protected successor.'
  p['next_action']='Integrate funding and authority/measurement findings after source checking; complete main-chapter consistency and independent reader/domain review without treating local integrations as whole acceptance.'
 assert p['status']=='open'
new_failures=[
 ('A root is extrapolated outside the affine regime that produced it',['W04','W13'],'Interior coupon root0.0625 lies beyond cap0.06; whole-region comparator rejected attempt01. Add roots only inside their formula domains.','continuous-guards-20261026'),
 ('A failed payment removes the accrued payable',['W04','W05','W16'],'Refused pay/draw must retain the full accrual journal, unpaid claim and complete balance sheet.','continuous-guards-20261026'),
 ('Equal coupon values erase a facility right or reveal a hidden trigger',['W03','W04','W06'],'Compare committed/unavailable modes and coarse/refined observation policies; keep no-feasible-policy answers.','continuous-guards-20261026'),
 ('Open-interval bounds are treated as attained or unfinished regions are dropped',['W04','W13'],'Cash on(0.055,0.06) has unattained limits; retain separate boundary cells and every budget-unresolved region.','continuous-guards-20261026'),
 ('A date0 aggregate cash balance hides an insolvent intermediate payer',['W05','W06','W16'],'Four-party funding checks all six transfer orders and every payer cash prefix, plus joint reciprocal transfers.','dated-funding-bundle-20261026'),
 ('A pricing discount or old accounting admission is silently reused for changed promises and dates',['W06','W07','W15'],'Compare2027/2028 contingent terms with maturity-only admitted profile; retain unknown liability valuation and effective interest.','conversion-measurement-audit-20261026')]
for desc,packs,case,unit in new_failures:
 f['cross_interface'].append({'id':f"X{len(f['cross_interface'])+1}",'failure':desc,'closure_packages':packs,'discriminating_case':case,'status':'Checked bounded failure/control; broad package remains open','evidence':f'data/accounting-master/{unit}/result.md'})
save('audit-status.json',a);save('closure-packages.json',cp);save('failure-register.json',f)
lines=['# Full closure program after continuous guards and dated funding','',
'26 October2026. All18 packages remain open. Inherited53 obligations,6 interactions,46 operations,9 literature gaps,67 original failures and48 literature extensions remain verbatim. This refresh credits checked companions; it is not a new independent audit of every operation.','']
for p in cp['packages']:
 lines += [f"## {p['id']} — {p['title']}",'','Requirements: '+', '.join(p['requirements'])+'.','',
           'Dependencies: '+(', '.join(p['depends_on']) or 'none')+'.','',
           'Known failure: '+p['failure'],'','Existing support: '+p['existing_support'],'',
           'Closure evidence: '+p['closure_evidence'],'','Next action: '+p['next_action'],'','Limits: '+p['limits'],'','Status: open.','']
(O/'closure-program.md').write_text('\n'.join(lines))
(O/'remaining-work.md').write_text('# Complete remaining-work queue\n\n26 October2026. No whole requirement closes. The active financing-authority plan is preserved by the live master; W04 now needs a two-date persistent-mode extension. Funding and measurement companions require source-aware manuscript integration.\n\n'+'\n'.join(f"- **{p['id']} {p['title']}:** {p['next_action']}" for p in cp['packages'])+'\n\nS1–S5 partial; S6 held; E3 deferred. Independent reader/domain and whole-document acceptance remain pending. Complete feasible internal research before any paid referral; no fees or outreach authorized.\n')
old=read('audit-status.json');oldf=read('failure-register.json')
assert a['groups']==old['groups'] and a['literature']==old['literature'] and a['successor_deltas'][:len(old['successor_deltas'])]==old['successor_deltas']
assert all(f[k]==oldf[k] for k in ['original','literature_extensions']) and f['cross_interface'][:18]==oldf['cross_interface']
assert all(sha(R/n)==h for n,h in lock.items())
counts={'obligations':53,'interactions':6,'operations':46,'literature_gaps':9,'original_failures':67,'literature_extensions':48,'cross_interface_challenges':len(f['cross_interface']),'successor_deltas':len(a['successor_deltas']),'closure_packages':18}
save('verification.json',{'status':'PASS','counts':counts,'original_rows_preserved':True,'all_packages_open':True,'whole_requirements_closed':0,'scope':'Trace reconciliation; no independent full audit'})
(O/'plan-review.md').write_text('# Skeptical refresh review\n\nThe prior register contains stale conversion next actions, but completed bounded companions cannot close broad requirements. Preserve every original row and append source-hashed deltas. Keep accounting scope rejection separate from rejection of economic mechanics; preserve all failure attempts. Current master fields may change concurrently, so re-read before updating and preserve unrelated live work. Counts are descriptive, not coverage or acceptance measures. Review passes under the integration plan and these restrictions.\n')
(O/'result.md').write_text('# Full program reconciled after continuous and funding work\n\nThe successor retains every inherited obligation, interaction, operation, literature row and failure. Five new evidence deltas and six explicit interface failures update the queue to32 deltas and24 cross-interface challenges. All18 packages remain open. W04 has an exact one-date continuous reference; W05/W06 have selected conversion and dated funding; W07 retains an identified accounting-admission mismatch. Each has a concrete next task and source limits. No legacy controller binding or predecessor source was changed. Verification is in verification.json. Manuscript and active concurrent plan are selected separately by the live master.\n')
print(json.dumps({'status':'PASS','counts':counts,'successor':str(O.relative_to(R))}))
