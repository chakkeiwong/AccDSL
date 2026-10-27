"""Create traceability records for this audit; does not close upstream requirements."""
from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
b=json.loads((H/'baseline.json').read_text());ae=b['active_execution']
def read(p):return json.loads((R/p).read_text())
def dump(n,x):(H/n).write_text(json.dumps(x,indent=2)+chr(10))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
a=read('data/accounting-master/release-readiness-audit-20261027/cutoff-v550/'+ae['current_audit']);packages=read('data/accounting-master/release-readiness-audit-20261027/cutoff-v550/'+ae['closure_packages'])['packages']
# A package maps to precise release work; neither broad closure nor product readiness follows.
maprows=[
('W01',['R01','R06'],['C0','C4'],'Design requires complete declared source-frontier dispositions and selected critical contexts; actual historical availability is required when an as-of claim uses it. General extraction and forecast validation remain separate.'),
('W02',['R04','R06','R08'],['C2','C4'],'Design requires an explicit admitted-history domain and complete/partial answer semantics, with independent feasible/contradictory/out-of-domain cases. General arbitrary-company identification is not established.'),
('W03',['R04','R07','R08'],['C2','C3','C4'],'Preserve actor information, persistent unknowns and revision dependencies in each supported model. Probability laws require actual support; general company inference is a separate unresolved research claim.'),
('W04',['R08'],['C2','C4'],'Specify exact query/horizon/policy/observation premises for every supported reduction; test changed-scope invalidation. General mixed/continuous guarantees and measured scale cannot be inferred from finite checks.'),
('W05',['R04','R05','R06'],['C2','C3','C4'],'Use the checked coupon, missed-payment and nominal-credit evidence in a complete profile; finish required settlement/accounting joins without equating face, cash and carrying amount.'),
('W06',['R05','R08'],['C2','C3','C4'],'Separate solved finite quote/policy examples from measured conversion/control and broader equilibrium. Allocation support and complete paired/consolidated consequences are still required for that promoted operation.'),
('W07',['R05','R06','R07'],['C3','C4'],'Each promoted corporate operation needs edition/applicability, fact pattern, formulas and full statements. Same-fact alternatives or unsupported treatments require explicit decisions; historical examples do not establish general compliance.'),
('W08',['R04','R05','R06'],['C2','C3','C4'],'Control, legal entity, transfer, FX/tax origin and nonadditive report identities must survive the selected integrated case. Source-qualified conversion/acquisition remains unresolved where measurement is required.'),
('W09',['R05','R06','R08'],['C3','C4'],'Current closed-credit intake preserves missing evidence and has no positive recovery effects. Define supported credit/reset/settlement and regulatory scopes; do not promote unresolved receipt or legal rights.'),
('W10',['R05','R06'],['C3','C4'],'Audit existing insurance report composition before new code; distinguish estimates, changing treaties and termination. Bind origins and actuarial/measure assumptions, then specify remaining transitions and valuation evidence.'),
('W11',['R03','R04'],['C1','C2','C6'],'Release the normative grammar/IR/profile/error/version map and exact source-to-result goldens. Existing native-off cases help, but compatible independent implementation and migration require separate assessment.'),
('W12',['R03','R04'],['C1','C2','C6'],'Design requires state/effect ownership, identity, revision and recovery semantics; real-store fault/concurrency implementation is a retained product obligation. Pure replay cannot close the latter.'),
('W13',['R04','R08'],['C2','C4'],'Declare each numerical domain and witness/bound/unknown result; verify actual financial guards. Root, rounding and nonlinear/general optimization claims require their own premises and tests.'),
('W14',['R03','R07'],['C1','C3','C6'],'Inspected software capabilities and exact adapter contracts can support a design; a claimed executable adapter requires a matched environment/runtime. Missing optional software is not a universal release veto.'),
('W15',['R07'],['C3','C5'],'Reconcile current claims across all literature supplements; inspect consequential technical and source-version dependencies. Resolve direct-competitor and unavailable-source dispositions without treating metadata or citation count as support.'),
('W16',['R04','R05','R06','R08'],['C2','C3','C4','C6'],'Map documented failure mechanisms to exact scoped evidence/refusal or a remaining test. Complete original/revised/failed-prefix joined company cases; never turn a finite catalogue into universal coverage.'),
('W17',['R01','R02','R03','R09'],['C0','C1','C5','C6','C7'],'Consolidate one current specification, repair confirmed prose/notation/interface defects, preserve math/citations and complete full rendered/technical review. Independent reader/domain/implementer acceptance is still separate.'),
('W18',['R01','R09'],['C0','C7'],'Record the design release decision while preserving S6 held and E3 deferred. Production and empirical promotion need their stated separate workloads, baselines, validity and uncertainty evidence.')]
mp={w:{'release_gaps':rs,'closure_steps':cs,'release_disposition':txt} for w,rs,cs,txt in maprows}
pr=[]
for p in packages:
 pr.append({**{k:p[k] for k in ['id','title','requirements','depends_on','status','closure_evidence','next_action','limits']},**mp[p['id']],'full_package_closed':False,'source':ae['closure_packages']})
dump('package-release-map.json',pr)
original={}
for line in (R/'docs/plans/accounting-mission-requirements.md').read_text().splitlines():
 if line.startswith('| MC'):
  cells=[x.strip() for x in line.split('|')[1:-1]]
  if len(cells)>=4:original[cells[0]]={'requirement':cells[1],'acceptance':cells[2],'historical_assessment':cells[3]}
rows=[]
for group,items in list(a['groups'].items())+[('literature',a['literature'])]:
 for x in items:
  ws=x.get('closure_packages',[]);rs=sorted({y for w in ws for y in mp[w]['release_gaps']});cs=sorted({y for w in ws for y in mp[w]['closure_steps']})
  rows.append({'id':x['id'],'group':group,'original_requirement':original.get(x['id']),'current_supported_scope':x.get('supported_scope'),'inherited_next_action':x.get('remaining_work_and_next_action'),'original_source':x.get('source',x.get('review_note',ae['current_audit'])),'original_source_line':x.get('line'),'closure_packages':ws,'release_gaps':rs,'closure_steps':cs,'release_interpretations':{w:mp[w]['release_disposition'] for w in ws},'release_acceptance_decision':'pending_C0_original_condition_reconciliation','full_requirement_closed':False,'scope':'Traceability and triage only; the audit does not independently accept every original condition.'})
dump('requirement-crosswalk.json',{'candidate':b['candidate'],'source':ae['current_audit'],'counts':{g:len(v) for g,v in a['groups'].items()}|{'literature':len(a['literature'])},'rows':rows})
f=read(ae['failure_register']);out=[]
for group in ['original','literature_extensions','cross_interface']:
 for x in f[group]:
  ws=x['closure_packages'];out.append({'group':group,'id':x['id'],'failure':x.get('failure'),'existing_evidence_status':x.get('evidence_status',x.get('status')),'closure_packages':ws,'release_gaps':sorted({y for w in ws for y in mp[w]['release_gaps']}),'release_test_disposition':'C4 must bind an actual fixture/derivation, justified unsupported profile, or precise remaining task; runtime execution is not inferred.'})
dump('failure-release-crosswalk.json',{'source':ae['failure_register'],'counts':{g:len(f[g]) for g in ['original','literature_extensions','cross_interface']},'rows':out})
cs=read('data/accounting-master/release-readiness-audit-20261027/chapters.json');nav=read('data/accounting-master/release-readiness-audit-20261027/pdf-navigation.json');render=read('data/accounting-master/release-readiness-audit-20261027/rendered-selection.json')
deeper={'chapters/01-purpose.tex':'Purpose, alpha convention and first-release workflow; source and rendered excerpt.','chapters/04-architecture.tex':'Typed IR, authoring and component boundaries.','chapters/10-validation.tex':'Release classes, reference-vs-engine distinction, corpus/annotation and workload/acceptance passages.','chapters/12-research.tex':'Source collection, version/access qualifications and companion acceptance limits.','simulation/20-implementation.tex':'Selected implementation/acceptance scope passages.','simulation/24-evaluation.tex':'Selected real-company and empirical-validation boundaries.','simulation/17-continuous-methods.tex':'Selected included family-policy, observation-binding and temporal-frontier passages; not full 23k-word chapter.','chapters/09-implementation.tex':'Normative paths and recovery/adapter boundaries; not full chapter.','simulation/01-observations.tex':'Fixed/floating family definition and selected rendered equation.','simulation/25-interactions.tex':'New recovery-source scope and unresolved-intake section in full; other included content not fully reviewed.'}
coverage=[]
for i,c in enumerate(cs,1):coverage.append({'ordinal':i,'source':c['source'],'title':c['title'],'inventory':'located_in_source_and_count_crosschecked_to_PDF','entry_exit_review':'opening_and_ending_excerpts_inspected','scope_review':'selected_flags_and_release_connections_only','deeper_read':deeper.get(c['source'],'none beyond entry/exit and structural inspection'),'continuous_read':'not_checked','all_math_and_source_claims_verified':'not_checked','independent_human_acceptance':'pending'})
dump('review-coverage.json',{'candidate':b['candidate'],'source_chapters':len(cs),'compiled_chapter_bookmarks':sum(x[0]==2 for x in nav[0]['toc']),'chapters':coverage,'rendered_pages':[x|{'review':'inspected at rendered scale; no clipping seen in selected page','semantic_notes':'Local scope/notation/acceptance observations recorded in result.md; no whole-volume visual acceptance.'} for x in render],'limitations':['Entry/exit excerpts are not continuous chapter reading.','446 lexical display nodes remain unverified; TeX macros are not expanded.','All PDF pages inventoried by text identity; only five pages visually reviewed this turn.','No external technical/accounting source verification or runtime benchmark conducted.']})
# Explicitly preserve v5.49 control provenance and separately identify the v5.50 cutoff controls.
b['original_control_snapshot_candidate']='5.49;826 pages;not_ready';b['cutoff_control_snapshots']={str(p.relative_to(H/'cutoff-v550')):sha(p) for p in (H/'cutoff-v550').rglob('*') if p.is_file()};dump('baseline.json',b)
print(json.dumps({'packages':len(pr),'requirements':len(rows),'failure_rows':len(out),'chapters':len(coverage),'compiled_chapters':sum(x[0]==2 for x in nav[0]['toc']),'rendered_pages':len(render)}))
