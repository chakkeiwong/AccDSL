from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];P=R/'data/accounting-master/gap-memory-refresh-20261026';O=R/'data/accounting-master/gap-runtime-refresh-20261026';O.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return json.loads((P/n).read_text())
def write(n,v):(O/n).write_text(json.dumps(v,indent=2)+'\n')
lock={str(p.relative_to(R)):sha(p) for p in P.iterdir() if p.is_file()};write('predecessor-lock.json',lock)
a=read('audit-status.json');cp=read('closure-packages.json');f=read('failure-register.json');result=R/'data/accounting-master/guarded-memory-runtime-20261026/result.md'
for title,requirements,disposition in [
 ('Common typed execution of guarded two-date histories',['MC11','MC17','MC24','MC25','MC26','MC28','MC33','MC34','W04','W11','W16'],'28 complete programs/two charts,790 checks,16 controls; unchanged common engines, full books/journals/flows/reports and reduced equity correspondence. Concrete witness scope; generic symbolic certification remains open.'),
 ('Replay-valid concrete checkpoints and unresolved region roster',['MC11','MC12','MC24','MC25','MC26','MC28','MC33','MC34','W04','W12','W16'],'16 resume cases,596 checks,26 controls. Complete replay validates concrete prefixes; finite queue partitions retained,3872 region obligations remain unresolved. No whole-region certification, source authentication or crash durability.')]:
 a['successor_deltas'].append({'id':f"D{len(a['successor_deltas'])+1}",'title':title,'requirements':requirements,'evidence':str(result.relative_to(R)),'sha256':sha(result),'current_disposition':disposition})
a['baseline']='Version5.21 plus checked common typed bridge/checkpoint evidence; protected5.22 integration selected separately by live master.'
a['predecessor']={'path':str(P.relative_to(R)),'lock':'predecessor-lock.json'}
for q in cp['packages']:
 if q['id']=='W04':
  q['existing_support']+=' Concrete two-date common-engine correspondence and replay checkpoints now checked;3872 continuous-region obligations stay explicitly unresolved.'
  q['next_action']='Construct a checked symbolic-to-common-runtime certificate for affine amounts and guards; drive region refinement/closure from those certificates, then validate approximation and capacity claims separately.'
 if q['id']=='W05':
  q['existing_support']+=' Common typed payment/draw/repayment methods preserve once-only facility memory and exact accrued-minus-paid claims in28 concrete programs.'
 if q['id']=='W11':
  q['existing_support']+=' A selected registry expresses two-date guarded accrual, settlement, repayment, income and fees using unchanged generic monetary/memory/clock/report engines across two account charts.'
  q['next_action']='Certify the selected symbolic-method mapping before generalizing expressions; preserve wider rule algorithms, migrations and independent compatible implementations as separate gaps.'
 if q['id']=='W12':
  q['existing_support']+=' Concrete JSON checkpoints replay every accepted prefix; scope changes, balanced state corruption, dropped jobs and false continuous completion are rejected in a bounded reference.'
  q['next_action']='Connect actual immutable source/actor views and certificate-aware region checkpoints; durable store/restart/migration fault behavior needs its own evidence.'
 if q['id']=='W16':
  q['existing_support']+=' Full common-engine books/journals/flows/reports match an independent concrete oracle; interrupted/resumed results match saved uninterrupted outcomes.'
  q['next_action']='Compose symbolic guard certificates with admitted measurement, financing settlement and actor information; preserve independent full-state and invalidity comparators.'
 if q['id']=='W17':q['next_action']='Integrate checked common-runtime/checkpoint findings and separate funding/authority results; continue main-chapter consistency and independent reader/domain review.'
 assert q['status']=='open'
for desc,packages,case in [
 ('Reduced equity is incorrectly posted as capital, erasing income and expenses',['W05','W11','W16'],'Check complete income/fee/interest accounts and statements; only the explicit capital-plus-profit map corresponds to reduced economic equity.'),
 ('A completed witness is promoted to a whole continuous region certificate',['W04','W12','W16'],'Concrete checkpoint completion cannot remove any of3872 unresolved region obligations; altered completed_regions refuses.'),
 ('A balanced altered checkpoint passes a checksum but no longer follows from its opening',['W12','W16'],'Replay full accepted requests/results; mutate balanced cash, paid memory, used flag, cursor and stop record independently.'),
 ('A queue drops or reassigns unresolved work during interruption',['W04','W12','W16'],'Pending/completed/refused concrete ids must partition the expected roster and bind their program digests; missing/duplicate/foreign ids and erased regions refuse.')]:
 f['cross_interface'].append({'id':f"X{len(f['cross_interface'])+1}",'failure':desc,'closure_packages':packages,'discriminating_case':case,'status':'Checked bounded failure/control; broad package open','evidence':str(result.relative_to(R))})
write('audit-status.json',a);write('closure-packages.json',cp);write('failure-register.json',f)
lines=['# Full closure program after common guarded execution','',
'26 October2026. All18 broad packages remain open. Every inherited obligation, interaction, operation, literature row and failure remains preserved. This is trace reconciliation, not a new independent audit of every native operation.','']
for q in cp['packages']:
 lines += [f"## {q['id']} — {q['title']}",'','Requirements: '+', '.join(q['requirements'])+'.','','Dependencies: '+(', '.join(q['depends_on']) or 'none')+'.','','Known failure: '+q['failure'],'','Existing support: '+q['existing_support'],'','Closure evidence: '+q['closure_evidence'],'','Next action: '+q['next_action'],'','Limits: '+q['limits'],'','Status: open.','']
(O/'closure-program.md').write_text('\n'.join(lines))
(O/'remaining-work.md').write_text('# Complete remaining-work queue\n\nThe common typed bridge and concrete replay checkpoint are checked. Whole-region symbolic certification, source admission, durable persistence and scalability remain separate. Preserve the financing-authority plan in the live master. All18 packages remain open.\n\n'+'\n'.join(f"- **{q['id']} {q['title']}:** {q['next_action']}" for q in cp['packages'])+'\n\nS1–S5 partial; S6 held; E3 deferred. Independent reader/domain and whole-document acceptance remain pending. Feasible internal work continues; no fees, outreach or background campaign authorized.\n')
old=read('audit-status.json');oldf=read('failure-register.json');assert a['groups']==old['groups'] and a['literature']==old['literature'] and a['successor_deltas'][:35]==old['successor_deltas']
assert all(f[k]==oldf[k] for k in ['original','literature_extensions']) and f['cross_interface'][:27]==oldf['cross_interface']
assert all(sha(R/n)==h for n,h in lock.items())
counts={'obligations':53,'interactions':6,'operations':46,'literature_gaps':9,'original_failures':67,'literature_extensions':48,'cross_interface_challenges':31,'successor_deltas':37,'closure_packages':18}
write('verification.json',{'status':'PASS','counts':counts,'original_rows_preserved':True,'all_packages_open':True,'whole_requirements_closed':0,'scope':'Trace reconciliation only; concrete and continuous acceptance distinguished'})
(O/'plan-review.md').write_text('# Skeptical program refresh\n\nConcrete full-state correspondence and JSON replay are new evidence but cannot close symbolic-region, durable persistence or source-admission gaps. Preserve all original rows and add source-hashed deltas, explicit failure cases and the next evidence obligation. Check live routes before promotion; do not overwrite concurrent financing or legacy controller bindings. No page, check or job count is an acceptance metric. Audit passes under accounting-guarded-memory-integration-20261026.md.\n')
(O/'result.md').write_text('# Master program after guarded common execution\n\nD36–37 add concrete common-engine conformance and replay/queue evidence. The successor retains53 obligations,6 interactions,46 operations,9 literature gaps,67 original failures and48 literature extensions. There are37 deltas and31 cross-interface challenges. All18 packages remain open. The next computational task is checked symbolic-to-common-runtime certification; concrete witness completion cannot close a region. Actual financing authority and measurement stay active separately. Verification preserves all predecessor rows and source hashes.\n')
print(json.dumps({'status':'PASS','counts':counts}))
