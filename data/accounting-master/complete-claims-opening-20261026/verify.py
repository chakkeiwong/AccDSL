from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,subprocess,sys,time
import complete_opening as candidate
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
AUDIT=HERE.parent/'nonempty-opening-audit-20261026'
b=candidate.binding;core=candidate.core
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def equal(a,b):return core.canonical(a)==core.canonical(b)

def main():
    start=time.monotonic();assertions=[];cases=[];controls=[]
    def ensure(ok,label):assertions.append(dict(check=label,passed=bool(ok)));assert ok,label
    lockpath=HERE/'source-lock.json'
    if not lockpath.exists():
        lock=read(HERE.parent/'admitted-program-binding-20261026/source-lock.json')
        paths=[p for p in AUDIT.iterdir() if p.is_file()]
        paths += [HERE.parent/'admitted-program-binding-20261026'/n for n in ('binding.py','cases.json','selections/alpha.json','selections/beta.json')]
        for p in paths:
            n=str(p.relative_to(ROOT));h=sha(p);assert n not in lock or lock[n]==h,n;lock[n]=h
        dump('source-lock.json',lock)
    lock=read(lockpath)
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    selections={o:read(HERE.parent/f'admitted-program-binding-20261026/selections/{o}.json') for o in ('alpha','beta')}
    originals={n:getattr(native,n) for n in ('validate','control','claim_type','event_types','make_request','run','protected')};builder=operating.build
    def disabled(*args,**kwargs):raise AssertionError('native callback during complete-claims admission')
    try:
        for n in originals:setattr(native,n,disabled)
        operating.build=disabled
        audited=read(AUDIT/'cases.json')
        for row in audited:
            selection=selections[row['company']];body=row['input'];program=row['program']
            contract=candidate.make_contract(row['original_opening_template'],program['state_invariant'])
            population=candidate.population(body['opening'],'Exact retained synthetic carry; complete supplied internal map')
            call=candidate.make_program_call(selection,contract,body,population,program)
            before=candidate.a.order_digest([selection,contract,body,population,program])
            result=candidate.execute(selection,contract,body,population,program,call)
            ensure(result['status']=='complete_provisional' and result['executed'],row['case']+':executed')
            ensure(result['admission']['status']=='opening_admitted',row['case']+':admitted')
            ensure(equal(result['admission']['invariant'],row['full_invariant']),row['case']+':full_invariant')
            ensure(equal(result['admission']['structural'],row['structural_diagnostic']),row['case']+':all_retained_checks')
            ensure(equal(result['delegated']['execution'],row['continuation']),row['case']+':complete_continuation')
            ensure(candidate.a.order_digest([selection,contract,body,population,program])==before,row['case']+':inputs_unchanged')
            cases.append(dict(case=row['case'],company=row['company'],selection=selection,contract=contract,input=body,
                              completeness=population,program=program,call=call,result=result,expected_execution=row['continuation']))
        base=cases[0]
        def run(label,reason,stage=None,status='invalid',body=None,program=None,contract=None,selection=None,population=None,call=None):
            s=base['selection'] if selection is None else selection;t=base['contract'] if contract is None else contract
            i=base['input'] if body is None else body;p=base['program'] if program is None else program
            pop=candidate.population(i['opening'],'Explicit complete supplied internal test population') if population is None else population
            actual=candidate.execute(s,t,i,pop,p,candidate.make_program_call(s,t,i,pop,p) if call is None else call)
            ensure(actual['status']==status and reason in actual.get('reason',''),label+':reason:'+str(actual.get('reason')))
            ensure(not actual['executed'] and actual.get('delegated',{}).get('execution') is None if isinstance(actual.get('delegated'),dict) else not actual['executed'],label+':no_execution')
            if stage:ensure(actual['failed_stage']==stage,label+':stage')
            controls.append(dict(case=label,result=actual));return actual
        for row in read(AUDIT/'controls.json'):
            result=run(row['case'],'complete_claim_invariant',body=row['input'])
            ensure(equal(result['admission']['invariant'],row['invariant']),row['case']+':exact_audited_invariant')
        for status in ('partial','unknown'):
            pop=deepcopy(base['completeness']);pop['status']=status
            run('population_'+status,'complete_supplied_population_required',status='unresolved',population=pop)
        for field in ('book_sha256','map_pointer','profile'):
            pop=deepcopy(base['completeness']);pop[field]='invalid'
            run('population_'+field,'stale_population_book' if field=='book_sha256' else 'population_profile_or_scope',population=pop)
        for field in ('selection_sha256','contract_sha256','input_sha256','population_sha256','input_order_sha256','program_sha256','program_order_sha256'):
            call=deepcopy(base['call']);call[field]='0'*64
            run('stale_'+field,'stale_or_incomplete_program_call',call=call,population=base['completeness'])
        changed=deepcopy(base['contract']);changed['excluded_stages'].append('roles')
        run('extra_exclusion','exact_excluded_stages',contract=changed)
        changed=deepcopy(base['contract']);changed['empty_template']['stages']=[s for s in changed['empty_template']['stages'] if s['id']!='cost_type']
        run('lost_retained_check','selected_empty_template',contract=changed)
        changed=deepcopy(base['contract']);changed['state_invariant']['residual_prerequisites'].append('edited')
        run('changed_invariant','selected_full_invariant',contract=changed)
        changed=deepcopy(base['contract']);stage=next(s for s in changed['empty_template']['stages'] if s['id']=='empty_claims');stage['value']={'x':True}
        changed['empty_template_sha256']=core.digest(changed['empty_template']);selected=deepcopy(base['selection']);selected['template_sha256']=changed['empty_template_sha256']
        run('repinned_wrong_empty_predicate','empty_population_stage',contract=changed,selection=selected)
        changed=deepcopy(base['contract']);stage=next(s for s in changed['empty_template']['stages'] if s['id']=='claim_total');stage['manifest']['requirements'][0]['predicate']['op']='le'
        changed['empty_template_sha256']=core.digest(changed['empty_template']);selected=deepcopy(base['selection']);selected['template_sha256']=changed['empty_template_sha256']
        run('repinned_wrong_zero_predicate','empty_total_predicate',contract=changed,selection=selected)
        changed=deepcopy(base['program']);changed['state_invariant']['residual_prerequisites'].append('different');changed['invariant_sha256']=core.digest(changed['state_invariant'])
        run('program_invariant_mismatch','selected_invariant',stage='bound_execution',program=changed)
        changed=deepcopy(base['program']);changed['commands'][0]['event']['date']='2028-01-04'
        run('program_command_mismatch','complete_commands',stage='bound_execution',program=changed)
        changed=deepcopy(base['program']);changed['rules']['collect']['construction']['residuals'].append('changed');changed['rules']['collect']['construction_sha256']=core.digest(changed['rules']['collect']['construction'])
        run('program_rules_mismatch','selected_rules',stage='bound_execution',program=changed)
        changed=deepcopy(base['input']);changed['policy']['past_due']='inclusive'
        run('wrong_policy','explicit_policy',body=changed)
        changed=deepcopy(base['input']);changed['roles']['cash'],changed['roles']['inventory']=changed['roles']['inventory'],changed['roles']['cash']
        run('wrong_cash_role','cash_role',body=changed)
        changed=deepcopy(base['input']);changed['unit_cost_pointer']='/absent'
        run('wrong_cost_pointer','unit_cost_leaf',body=changed)
        changed=deepcopy(base['program']);changed['mapping']['lines'][0]['label']='Edited presentation'
        run('different_program_mapping','shared_field:mapping',stage='bound_execution',program=changed)
        changed=deepcopy(base['input']);changed['mapping']['lines']=changed['mapping']['lines'][1:]
        actual=run('incomplete_statement_mapping','',body=changed)
        ensure(actual['admission']['structural']['failed_stage']=='report','mapping_report_owner')
        changed=deepcopy(base['input']);changed['schemas']={}
        actual=run('missing_schema','',body=changed)
        ensure(actual['admission']['structural']['failed_stage']=='typed_book','schema_owner')
        changed=deepcopy(base['input']);changed['policy']=dict(reversed(list(changed['policy'].items())))
        ensure(core.digest(changed)==core.digest(base['input']),'canonical_input_same_after_reorder')
        run('input_order_old_call','stale_or_incomplete_program_call',body=changed,call=base['call'],population=base['completeness'])
        changed=deepcopy(base['program']);ev=changed['commands'][0]['event'];ev['inputs']=dict(reversed(list(ev['inputs'].items())))
        run('event_input_order_mismatch','event_input_order',stage='bound_execution',program=changed)
        changed=deepcopy(base['input']);changed['opening']['date']='2028-01-02';changed['opening']['memory']['collection_clock']['cursor']='2028-01-02'
        actual=candidate.execute(base['selection'],base['contract'],changed,candidate.population(changed['opening'],'midperiod test'),base['program'],
            candidate.make_program_call(base['selection'],base['contract'],changed,candidate.population(changed['opening'],'midperiod test'),base['program']))
        ensure(actual['status']=='invalid' and not actual['executed'] and actual['admission']['structural']['failed_stage']=='report','midperiod_not_opening')
        controls.append(dict(case='midperiod_not_opening',result=actual))
        # Original empty programs are still admitted under the same full invariant.
        for row in read(HERE.parent/'admitted-program-binding-20261026/cases.json')[:4]:
            selection=selections[row['company']];template=read(HERE.parent/f'declared-opening-admission-20261026/templates/{row["company"]}.json')
            contract=candidate.make_contract(template,row['program']['state_invariant']);pop=candidate.population(row['input']['opening'],'Retained empty synthetic complete population')
            result=candidate.execute(selection,contract,row['input'],pop,row['program'],candidate.make_program_call(selection,contract,row['input'],pop,row['program']))
            ensure(result['status']=='complete_provisional',row['case']+':empty_successor_admitted')
            ensure(equal(result['delegated']['execution'],row['result']['execution']),row['case']+':empty_execution_exact')
            controls.append(dict(case=row['case']+':empty_baseline',result=result))
    finally:
        for n,v in originals.items():setattr(native,n,v)
        operating.build=builder
    dump('cases.json',cases);dump('controls.json',controls)
    for n,h in lock.items():ensure(sha(ROOT/n)==h,'protected:'+n)
    summary=dict(passed=True,complete_carried_openings=4,complete_continuation_commands=10,invalid_audited_states=5,
        controls=len(controls),assertions=len(assertions),protected_files=len(lock),native_lifecycle_and_builder_disabled=True,
        actual_source_completeness=False,accounting_admission=False,production_ready=False)
    dump('checks.json',summary);dump('assertions.json',assertions)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
        command='env CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/complete-claims-opening-20261026/verify.py',environment=sys.version,
        cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,data_version=sha(lockpath),
        plan_file='docs/plans/accounting-complete-claims-opening-20261026.md',result_file='data/accounting-master/complete-claims-opening-20261026/result.md',
        artifacts=['cases.json','controls.json','checks.json','assertions.json'],implementation_sha256={n:sha(HERE/n) for n in ('complete_opening.py','verify.py','design.md')},timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

if __name__=='__main__':main()
