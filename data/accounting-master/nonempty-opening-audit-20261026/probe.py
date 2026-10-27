"""Bounded audit of carried openings; no new admission policy is installed."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,subprocess,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'admitted-program-binding-20261026'))
import binding
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
a=binding.admission;composer=binding.composer;g=composer.guards;core=a.core
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def equal(a,b):return core.canonical(a)==core.canonical(b)

def main():
    start=time.monotonic();assertions=[];cases=[];controls=[]
    def ensure(ok,label):assertions.append(dict(check=label,passed=bool(ok)));assert ok,label
    lockpath=HERE/'source-lock.json'
    if not lockpath.exists():
        lock={}
        for folder,names in [('admitted-program-binding-20261026',['cases.json','binding.py','source-lock.json']),('declared-opening-admission-20261026',['admission.py','templates/alpha.json','templates/beta.json']),('declarative-event-program-20261026',['composer.py']),('authored-state-invariants-20261026',['guards.py']),('selected-source-integration-20261026',['verification.json','result.md'])]:
            for name in names:
                p=HERE.parent/folder/name;lock[str(p.relative_to(ROOT))]=sha(p)
        dump('source-lock.json',lock)
    lock=read(lockpath)
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    rows=read(HERE.parent/'admitted-program-binding-20261026/cases.json')[:4]
    originals={n:getattr(native,n) for n in ('validate','control','claim_type','event_types','make_request','run','protected')};builder=operating.build
    def disabled(*args,**kwargs):raise AssertionError('native callback during carried-state audit')
    try:
        for n in originals:setattr(native,n,disabled)
        operating.build=disabled
        for row in rows:
            prior=row['result']['execution'];carry=next(x for x in prior['trace'] if x['command']['kind']=='carry');offset=carry['index']+1
            book=deepcopy(carry['result']['next_opening']);program=deepcopy(row['program']);program.update(opening=book,commands=deepcopy(program['commands'][offset:]))
            body=deepcopy(row['input']);body.update(opening=deepcopy(book),commands=binding.project_commands(program))
            template=read(HERE.parent/f'declared-opening-admission-20261026/templates/{row["company"]}.json')
            check=g.assess(program['state_invariant'],book,program['memory_definition'],program['schemas'])
            ensure(equal(check,carry['invariant_after']),row['case']+':full_carried_invariant')
            ensure(check['status']=='collection_total_requirements_satisfied',row['case']+':invariant_pass')
            report=a.reports.report(a.reports.request(book,book,program['schemas'],program['mapping']))
            ensure(report['status']=='reported',row['case']+':opening_report')
            admitted=a.assess(template,body,a.make_call(template,body))
            ensure(admitted['status']=='invalid' and admitted['failed_stage']=='empty_claims',row['case']+':empty_contract_scope')
            diagnostic=deepcopy(template);diagnostic['stages']=[s for s in diagnostic['stages'] if s['id']!='empty_claims']
            second=a.assess(diagnostic,body,a.make_call(diagnostic,body))
            ensure(second['status']=='invalid' and second['failed_stage']=='claim_total',row['case']+':empty_total_scope')
            diagnostic['stages']=[s for s in diagnostic['stages'] if s['id']!='claim_total']
            structural=a.assess(diagnostic,body,a.make_call(diagnostic,body))
            ensure(structural['status']=='opening_admitted',row['case']+':other_checks')
            result=composer.run(program,composer.make_call(program))
            ensure(result['status']=='complete_provisional',row['case']+':continuation')
            for field in ('current','opening','stop','remaining_commands'):
                ensure(equal(result[field],prior[field]),row['case']+':'+field)
            expected_trace=deepcopy(prior['trace'][offset:])
            for trace in expected_trace:trace['index']-=offset
            ensure(equal(result['trace'],expected_trace),row['case']+':complete_suffix_trace_with_local_indices')
            report_ids={cmd['id'] for cmd in program['commands'] if cmd['kind'] in ('report','carry')}
            ensure(equal(result['reports'],[r for r in prior['reports'] if r['id'] in report_ids]),row['case']+':complete_suffix_reports')
            ensure(equal(result['opening_invariant'],check),row['case']+':opening_invariant')
            cases.append(dict(case=row['case'],company=row['company'],source_offset=offset,source_case_sha256=core.digest(row),
                input=body,program=program,original_opening_template=template,diagnostic_structure_template=diagnostic,
                old_admission=admitted,empty_total_diagnostic=second,structural_diagnostic=structural,
                full_invariant=check,opening_report=report,continuation=result,expected_suffix_trace=expected_trace,
                diagnostic_templates_not_promoted=True))
        # These examples retain the valid typed shape while challenging meaning.
        base=cases[0];claim=next(iter(base['input']['opening']['memory']['claims']))
        for label,mutation in [('receivable_total',lambda b:b['opening']['balances'].update(receivables='21/1',cash='99/1')),
                ('negative_claim',lambda b:b['opening']['memory']['claims'][claim].update(remaining='-1/1')),
                ('missing_sale_identity',lambda b:b['opening']['memory']['claims'][claim].update(sale_event='absent')),
                ('future_issue',lambda b:b['opening']['memory']['claims'][claim].update(issued='2029-01-02')),
                ('inconsistent_overdue',lambda b:b['opening']['memory']['claims'][claim].update(overdue='0/1'))]:
            body=deepcopy(base['input']);mutation(body)
            if label=='receivable_total':
                original=base['input']['opening']['balances'];money=a.base.monetary
                body['opening']['balances']['cash']=money.fmt(money.rational(original['cash'])-1)
            inv=g.assess(base['program']['state_invariant'],body['opening'],body['memory_definition'],body['schemas'])
            ensure(inv['status']!='collection_total_requirements_satisfied',label+':invariant_refusal')
            structural=a.assess(base['diagnostic_structure_template'],body,a.make_call(base['diagnostic_structure_template'],body))
            ensure(structural['status']=='opening_admitted',label+':structure_alone_insufficient')
            controls.append(dict(case=label,input=body,structural=structural,invariant=inv))
    finally:
        for n,v in originals.items():setattr(native,n,v)
        operating.build=builder
    dump('cases.json',cases);dump('controls.json',controls)
    for n,h in lock.items():ensure(sha(ROOT/n)==h,'protected:'+n)
    summary=dict(passed=True,carried_openings=len(cases),complete_continuation_commands=sum(len(c['continuation']['trace']) for c in cases),
        invalid_state_controls=len(controls),assertions=len(assertions),protected_files=len(lock),native_lifecycle_and_builder_disabled=True,
        successor_implemented=False,actual_company_completeness=False)
    dump('checks.json',summary);dump('assertions.json',assertions)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
        command='env CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/nonempty-opening-audit-20261026/probe.py',environment=sys.version,
        cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,data_version=sha(lockpath),
        plan_file='docs/plans/accounting-nonempty-opening-audit-20261026.md',result_file='data/accounting-master/nonempty-opening-audit-20261026/result.md',
        artifacts=['cases.json','controls.json','checks.json','assertions.json'],timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))

if __name__=='__main__':main()
