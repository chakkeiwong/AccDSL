"""Preserve 201 distinct failure targets; separate observed and proposed evidence."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, subprocess, sys, time
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
assert len(sys.argv)==2
O=H/sys.argv[1];O.mkdir(exist_ok=False);start=time.monotonic()
register=B/'gap-insurance-stage-refresh-20261027/failure-register.json'
old=read(register);packages=read(B/'acceptance-priority-20261027/closure-packages.json')['packages'];owners={p['id']:p for p in packages}
checks=[];locks={str(register.relative_to(R)):sha(register)}
def check(ok,name):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
def pin(p):
    p=Path(p);name=str(p.relative_to(R));locks[name]=sha(p);return dict(path=name,sha256=locks[name])

# The exact X09 financial target is authored here before reading saved states.
expected_initial=dict(term_id='initial',as_of='2027-02-28',remaining='20/1',overdue='20/1',origin='imported_snapshot',event_id='unknown')
expected_mar=dict(term_id='extension1',as_of='2027-03-31',remaining='20/1',overdue='0/1',origin='recorded_event',event_id='assess.mar')
expected_apr=dict(term_id='extension2',as_of='2027-04-30',remaining='15/1',overdue='0/1',origin='recorded_event',event_id='assess.apr')
expected_jun=dict(term_id='extension2',as_of='2027-06-30',remaining='15/1',overdue='15/1',origin='recorded_event',event_id='assess.jun')
x09=[]
for chart in ['alpha','beta']:
    path=B/'selected-term-program-20261027/attempt-01'/f'{chart}-result.json';identity=pin(path);result=read(path)
    states={s['id']:s['result']['execution']['after'] for s in result['steps']}
    claim=lambda key:states[key]['book']['memory']['claims']['invoice/a~1']
    check(result['status']=='complete_provisional' and len(states)==10,chart+':complete_program')
    for key in states:check(claim(key)['assessments']['imported']==expected_initial,chart+':prior_assessment_immutable:'+key)
    check(claim('event-0')['due']=='2027-04-30' and claim('event-0')['overdue']=='20/1',chart+':extension_does_not_reassess')
    check(claim('event-1')['assessments']['assess.mar']==expected_mar,chart+':march_current_term')
    check(claim('event-2')['due']=='2027-05-31' and claim('event-2')['assessments']['assess.mar']==expected_mar,chart+':second_extension_preserves_march')
    check(claim('event-3')['remaining']=='15/1' and claim('event-3')['assessments']['assess.mar']==expected_mar,chart+':receipt_does_not_rewrite_assessment')
    check(claim('event-4')['assessments']['assess.apr']==expected_apr,chart+':april_current_basis')
    check(claim('event-5')['assessments']['assess.jun']==expected_jun,chart+':june_overdue_basis')
    check(claim('carry')['terms']==claim('event-6')['terms'] and claim('carry')['assessments']==claim('event-6')['assessments'],chart+':carry_exact_history')
    check(claim('event-7')['remaining']=='0/1' and claim('event-7')['overdue']=='15/1',chart+':receipt_keeps_prior_assessment')
    check(claim('event-8')['remaining']=='0/1' and claim('event-8')['overdue']=='0/1',chart+':explicit_new_zero_assessment')
    x09.append(dict(chart=chart,evidence=identity,checked_states=list(states),scope='Supplied prospective date-only amendments; no monetary modification or actual historical admission'))
dump(O/'X09-assessment-continuity.json',dict(passed=True,cases=x09,expected=dict(initial=expected_initial,march=expected_mar,april=expected_apr,june=expected_jun)))

rows=[];linked=0
for group in ['original','literature_extensions','cross_interface']:
    for previous in old[group]:
        item=dict(group=group,id=previous['id'],failure=previous['failure'],original_record=previous,
                  owners=previous['closure_packages'],full_failure_closed=False,new_runtime_execution=False)
        evidence=[]
        if previous.get('evidence'):
            evidence.append(pin(R/previous['evidence']));linked+=1
        item['retained_evidence']=evidence
        item['evidence_class']='inherited_explicit_result_link_identity_checked' if evidence else 'inherited_documentary_target'
        item['evidence_limit']='A hash-bound result link preserves prior evidence; this mapping does not newly reproduce or independently review its financial claims.'
        if group=='original':
            trigger=previous['discriminating_case'];expectation=previous['proposed_remedy']
            residual='The exact original discriminating case still needs a claim-specific fixture or derivation mapping; a similarly named control in another domain cannot close it.'
        elif group=='literature_extensions':
            trigger=previous['failure']+'; reproduce the stated discriminator: '+previous['inherited_discriminating_evidence']
            expectation=previous['required_treatment'];residual=previous['residual']
        else:
            trigger=previous['discriminating_case'];expectation=previous['discriminating_case']
            residual='Verify the exact full-state/query predicate in the linked result, then identify any broader company/source conditions not exercised.' if evidence else 'Bind this exact cross-interface discriminator to a complete retained case or an independently specified new test.'
        item['remaining_test']=dict(input_or_perturbation=trigger,required_outcome=expectation,
            assertion_target=previous['failure'],remaining_scope=residual,
            prerequisite_actions=[dict(package=k,action=owners[k]['next_action']) for k in previous['closure_packages']],
            evidence_to_record='Exact selected input/source identities, independent expected full state or derivation, actual outcome/refusal, limits and run/source manifest.',
            execution_status='not_run_by_this_reconciliation')
        item['decision']='retain_inherited_scoped_evidence_and_complete_remaining_test' if evidence else 'precise_original_test_target_retained_not_claimed_executed'
        if item['id']=='X09':
            item.update(evidence_class='new_exact_saved_result_audit_plus_prior_runtime',decision='selected_date_only_program_discriminator_checked_broader_scope_open',
              new_result_audit=str((O/'X09-assessment-continuity.json').relative_to(R)))
            item['retained_evidence'] += [x['evidence'] for x in x09]
            item['remaining_test']['remaining_scope']='Actual modification accounting, incomplete imported prehistory and other term-rule families remain outside this two-chart result.'
            item['remaining_test']['execution_status']='saved complete runtime results checked against independently specified historical-assessment predicates; no rerun'
        if item['id'] in ['SIM-F004','SIM-F065','SIM-F066','LIT-F027','LIT-F028','LIT-F031']:
            item['nonmatching_new_evidence']='The recent selected-term controls and relocation do not close this different original guarantee, probability, refinancing-cache or external-software target.'
        rows.append(item)
counts={k:sum(r['group']==k for r in rows) for k in ['original','literature_extensions','cross_interface']}
check(counts==dict(original=67,literature_extensions=48,cross_interface=86),'exact_original_population')
check(len({(r['group'],r['id']) for r in rows})==201,'unique_complete_identifiers')
check(all(r['remaining_test']['input_or_perturbation'] and r['remaining_test']['required_outcome'] and r['owners'] for r in rows),'all_specific_tests_and_owners')
check(all(not r['full_failure_closed'] for r in rows),'no_broad_closure')
for path in [H/'reconcile.py',R/'docs/plans/accounting-integrated-failure-dispositions-20261027.md',B/'selected-term-program-20261027/attempt-01/checks.json',B/'selected-term-bundle-20261027/attempt-02/verification.json']:pin(path)
check(all(sha(R/p)==h for p,h in locks.items()),'all_original_evidence_unchanged')
dump(O/'failure-dispositions.json',dict(date='2026-10-27',candidate='5.51 unchanged',counts=counts,scope='Original discriminators preserved. Linked evidence has identity checks; only X09 receives a new financial predicate audit here.',rows=rows))
dump(O/'source-lock.json',locks)
lines=['# Current failure dispositions','',
 'All 201 original mechanisms are retained. This is an evidence/task index, not a claim that all tests have run. Seventy-five existing cross-interface result links are preserved and hash-bound; other rows retain their exact discriminating case, treatment and residual rather than an invented passing status. X09 is newly checked against the complete selected-term results.','']
for r in rows:
    t=r['remaining_test'];lines+=['## '+r['id']+' — '+r['failure'],'','Decision: '+r['decision'],
      '','Input/perturbation: '+t['input_or_perturbation'],'','Required outcome: '+t['required_outcome'],'',
      'Remaining: '+t['remaining_scope'],'','Owners: '+', '.join(r['owners'])+'.','']
(H/'failure-dispositions.md').write_text('\n'.join(lines)+'\n')
summary=dict(passed=True,counts=counts,checks=len(checks),inherited_explicit_evidence_links=linked,new_financial_predicate_audits=1,protected_files=len(locks),full_failure_closures=0)
dump(O/'checks.json',dict(summary,assertions=checks))
git=subprocess.run(['git','rev-parse','HEAD'],cwd=R,capture_output=True,text=True)
dump(O/'run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/integrated-failure-dispositions-20261027/reconcile.py '+sys.argv[1],environment=sys.version,git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,data_version=sha(register),timestamp_utc=datetime.now(timezone.utc).isoformat(),plan_file='docs/plans/accounting-integrated-failure-dispositions-20261027.md',result_file=str((H/'result.md').relative_to(R))))
print(json.dumps(summary))
