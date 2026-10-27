from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,subprocess,time,sys
import binding as b
import declared_receivable_lifecycle_v1 as native
import declared_operating_methods_v1 as operating
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(p.read_text())
def dump(name,value):
    p=HERE/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value,indent=2,ensure_ascii=False)+chr(10))
def sha(p):return sha256(p.read_bytes()).hexdigest()
def same(x,y):return b.core.canonical(x)==b.core.canonical(y)

def main():
    start=time.monotonic();prior=HERE.parent/'declarative-event-program-20261026';opening=HERE.parent/'declared-opening-admission-20261026'
    if not (HERE/'source-lock.json').exists():
        lock=read(opening/'source-lock.json')
        for folder in (prior,opening):
            for p in folder.rglob('*'):
                if p.is_file() and p.suffix in ('.py','.json','.md') and 'attempt-01' not in p.parts:lock[str(p.relative_to(ROOT))]=sha(p)
        dump('source-lock.json',lock)
    lock=read(HERE/'source-lock.json')
    for name,h in lock.items():assert sha(ROOT/name)==h,name
    assertions=[];results=[];controls=[];selections={};templates={};bodies={};inputs={}
    def ensure(ok,name):assertions.append(dict(check=name,passed=bool(ok)));assert ok,name
    for owner in ('alpha','beta'):
        program=read(prior/f'examples/{owner}.program.json');inp=read(prior/f'examples/{owner}.native-input.json');template=read(opening/f'templates/{owner}.json')
        selection=dict(profile=b.SELECTION,context=deepcopy(program['opening']['context']),native_profile=inp['profile'],program_profile=program['profile'],
                       roles=deepcopy(inp['roles']),unit_cost_pointer=inp['unit_cost_pointer'],policy=deepcopy(inp['policy']),
                       invariant_sha256=b.core.digest(program['state_invariant']),rules_sha256=b.core.digest(program['rules']),template_sha256=b.core.digest(template),
                       residuals=['Finite reviewed chart/rule selection; changed selection requires its own correspondence evidence'])
        selections[owner]=selection;templates[owner]=template;bodies[owner]=program;inputs[owner]=inp
        path=HERE/f'selections/{owner}.json'
        if path.exists():ensure(read(path)==selection,owner+':selection_stable')
        else:dump(f'selections/{owner}.json',selection)
    originals={name:getattr(native,name) for name in ('validate','control','event_types','claim_type','make_request','run','protected','observation')};build=operating.build
    def disabled(*args,**kwargs):raise AssertionError('native lifecycle/builder used')
    def run(owner,inp,program,selection=None,template=None,call=None):
        selection=selections[owner] if selection is None else selection;template=templates[owner] if template is None else template
        stable=b.admission.order_digest([selection,template,inp,program])
        try:
            for name in originals:setattr(native,name,disabled)
            operating.build=disabled
            result=b.execute(selection,template,inp,program,b.make_call(selection,template,inp,program) if call is None else call)
        finally:
            for name,value in originals.items():setattr(native,name,value)
            operating.build=build
        ensure(b.admission.order_digest([selection,template,inp,program])==stable,'inputs_preserved');return result
    def compare(label,owner,inp,program,saved):
        result=run(owner,inp,program)
        ensure(result.get('executed') and result['admission']['status']=='opening_admitted',label+':admitted:'+str(result.get('reason')))
        ensure(same(result['execution'],saved),label+':complete_execution_equal')
        results.append(dict(case=label,company=owner,input=inp,program=program,result=result));return result
    for owner in ('alpha','beta'):
        compare(owner,owner,inputs[owner],bodies[owner],read(prior/f'examples/{owner}.result.json'))
        compare(owner+':new',owner,read(prior/f'examples/{owner}.new-native-input.json'),read(prior/f'examples/{owner}.new-program.json'),read(prior/f'examples/{owner}.new-result.json'))
    for row in read(prior/'adverse.json'):
        owner=row['case'].split(':')[0];compare(row['case'],owner,row['native_program'],row['program'],row['result'])
    def refuse(label,reason,inp=None,program=None,selection=None,template=None,call=None):
        inp=inputs['alpha'] if inp is None else inp;program=bodies['alpha'] if program is None else program
        result=run('alpha',inp,program,selection,template,call)
        ensure(result['status']=='invalid' and not result['executed'] and result['execution'] is None and reason in result['reason'],label+':refused:'+str(result.get('reason')))
        controls.append(dict(case=label,result=result))
    inp=inputs['alpha'];program=bodies['alpha'];s=selections['alpha'];t=templates['alpha']
    for field in ('selection','template','input','program','input_order','program_order'):
        call=b.make_call(s,t,inp,program);call[field+'_sha256']='0'*64;refuse('stale_'+field,'stale_'+field,call=call)
    for key in ('name','opening','schemas','mapping','memory_definition'):
        changed=deepcopy(program)
        if key=='name':changed[key]+='.changed'
        elif key=='opening':changed[key]['memory']['complement']['tag']='different'
        elif key=='schemas':changed[key]['extra']={}
        elif key=='mapping':changed[key]['context']['entity']='different'
        else:changed[key]['root']['fields']['claims']['max_items']+=1
        refuse('mismatched_'+key,'shared_field:'+key,program=changed)
    changed=deepcopy(inp);changed['roles']['cost_of_sales'],changed['roles']['payroll']=changed['roles']['payroll'],changed['roles']['cost_of_sales']
    refuse('mismatched_roles','selected_roles',inp=changed)
    changed=deepcopy(inp);changed['policy']['provenance']='Different declared provenance'
    refuse('mismatched_policy','selected_policy',inp=changed)
    changed=deepcopy(s);changed['unit_cost_pointer']='/other'
    refuse('mismatched_cost_selection','selected_unit_cost_pointer',selection=changed)
    changed=deepcopy(program);changed['rules']['sale']['eligibility']['residuals'].append('Changed selected rule')
    refuse('mismatched_rules','selected_rules',program=changed)
    changed=deepcopy(program);changed['state_invariant']['residual_prerequisites'].append('Changed invariant')
    changed['invariant_sha256']=b.core.digest(changed['state_invariant']);refuse('mismatched_invariant','selected_invariant',program=changed)
    changed=deepcopy(program);changed['commands'][0]['event']['date']='2027-01-03'
    refuse('mismatched_event','complete_commands',program=changed)
    changed=deepcopy(program);changed['commands'][0]['event']['inputs']=dict(reversed(list(changed['commands'][0]['event']['inputs'].items())))
    refuse('mismatched_input_order','event_input_order',program=changed)
    changed=deepcopy(program);changed['commands'].pop();refuse('missing_command','complete_commands',program=changed)
    changed=deepcopy(program);changed['commands'].append(deepcopy(changed['commands'][-1]));refuse('extra_command','complete_commands',program=changed)
    changed=deepcopy(program);changed['carry_policy']['provenance']='different';refuse('mismatched_carry','selected_carry_policy',program=changed)
    changed=deepcopy(inp);changed['opening']['memory']['stock']['unit_cost']='0/1'
    refuse('opening_refusal_no_execution','positive_unit_cost',inp=changed)
    dump('cases.json',results);dump('controls.json',controls)
    for row in read(HERE/'cases.json'):
        ensure(same(run(row['company'],row['input'],row['program']),row['result']),row['case']+':saved_recomputed')
    for name,h in lock.items():ensure(sha(ROOT/name)==h,'protected:'+name)
    summary=dict(passed=True,full_programs=4,complete_commands=44,adverse_programs=26,complete_execution_comparisons=len(results),controls=len(controls),assertions=len(assertions),protected_files=len(lock),native_lifecycle_and_builder_disabled=True,full_native_opening_evaluator_replaced_in_selected_adapter=True,general_rule_equivalence_proved=False,accounting_admission=False,production_ready=False)
    dump('checks.json',summary);dump('assertions.json',assertions)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',command='env CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/admitted-program-binding-20261026/verify.py',environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',wall_seconds=time.monotonic()-start,data_version=sha(HERE/'source-lock.json'),plan_file='docs/plans/accounting-admitted-program-binding-20261026.md',result_file='data/accounting-master/admitted-program-binding-20261026/result.md',artifacts=['selections','cases.json','controls.json','checks.json','assertions.json'],implementation_sha256={n:sha(HERE/n) for n in ('binding.py','verify.py')},timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))
if __name__=='__main__':main()
