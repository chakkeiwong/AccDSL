"""Exact deterministic correspondence, including refusal precedence and boundaries."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
import time
import gate as g

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent/'ordered-assessment-expansion-20261026'))
import expander
sys.path.insert(0, str(HERE.parent/'authored-event-contract-20261026'))
import contract
import declared_receivable_lifecycle_v1 as native

def read(path): return json.loads(path.read_text())
def dump(name, value): (HERE/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+chr(10))
def sha(path): return sha256(path.read_bytes()).hexdigest()
def equal(a, b): return g.core.canonical(a) == g.core.canonical(b)
def known(value): return {'status': 'known', 'value': value}

def main():
    start = time.monotonic(); assertions = []; cases = []; refusals = []; controls = []
    lock = read(HERE/'source-lock.json')
    for name, digest in lock.items(): assert sha(ROOT/name) == digest, name
    templates = {(owner, kind): read(HERE/f'templates/{owner}.{kind}.json')
                 for owner in ('alpha', 'beta') for kind in ('sale', 'collect', 'assess')}
    construction_templates = {(owner, kind): read(HERE.parent/f'parameterized-method-construction-20261026/templates/{owner}.{kind}.json')
                              for owner in ('alpha', 'beta') for kind in ('sale', 'collect')}
    expansion_templates = {owner: read(HERE.parent/f'ordered-assessment-expansion-20261026/templates/{owner}.assess.json') for owner in ('alpha', 'beta')}

    def ensure(ok, label):
        assertions.append(dict(check=label, passed=bool(ok))); assert ok, label

    def assess(owner, kind, book, event, params, template=None, call=None):
        template = templates[owner, kind] if template is None else template
        return g.assess(template, book, event, params['schemas'], params['memory_definition'],
                        call if call is not None else g.make_call(template, book, event, params['schemas'], params['memory_definition']))

    def composed(row):
        owner = row['company']; kind = row.get('method', 'assess')
        book, event, params = row['before'], row['event'], row['parameters']
        gate = assess(owner, kind, book, event, params)
        ensure(gate['status'] == 'eligible', row['case']+':eligible:'+gate.get('reason', ''))
        if kind == 'assess':
            t = expansion_templates[owner]
            built = expander.construct(t, book, event, params['schemas'], params['memory_definition'],
                                       expander.make_call(t, book, event, row['order']))
            request = built['construction']['request']
        else:
            t = construction_templates[owner, kind]
            built = g.c.construct(t, book, event, params['schemas'], params['memory_definition'], g.c.make_call(t, book, event))
            request = built['request']
        result = g.c.frontend.v2.propose(book, request)
        ensure(equal(request, row['native_request']), row['case']+':complete_request')
        ensure(equal(result, row['transition'] if kind == 'assess' else row['complete_transition']), row['case']+':complete_transition')
        ensure(result['status'] == 'proposed', row['case']+':proposed')
        return dict(case=row['case'], company=owner, method=kind, before=book, event=event,
                    parameters=params, gate=gate, request=request, transition=result,
                    order=row.get('order'), native_construction_disabled=True)

    scalar = read(HERE.parent/'parameterized-method-construction-20261026/cases.json')
    expanded = read(HERE.parent/'ordered-assessment-expansion-20261026/cases.json')
    original_native = {name: getattr(native, name) for name in ('make_request', 'run', 'event_types')}
    def disabled(*args, **kwargs): raise AssertionError('native eligibility/construction called by candidate')
    for row in scalar+expanded: native.control(row['before'], row['parameters']['roles'])
    try:
        for name in original_native: setattr(native, name, disabled)
        for row in scalar+expanded:
            stable = g.core.digest(row); cases.append(composed(row))
            ensure(g.core.digest(row) == stable, row['case']+':inputs_preserved')
    finally:
        for name, value in original_native.items(): setattr(native, name, value)
    for row in cases: native.control(row['transition']['after'], row['parameters']['roles'])

    stage_for = {'unknown_event_inputs': 'full_inputs', 'applicability_not_selected': 'approval',
                 'assessment_day_sealed': 'unsealed_day', 'due_before_sale': 'sale_due',
                 'duplicate_claim': 'claim_absent', 'unknown_claim': 'claim_exists',
                 'claim_customer_mismatch': 'customer_matches', 'assessment_cursor': 'assessment_cursor',
                 'assessment_window': 'assessment_window', 'assessment_crosses_period': 'period_end',
                 'event_chronology': 'chronology'}
    def compare_refusal(label, owner, book, command, params, expected):
        kind = command['method_key']; event = command['event']; stable = g.core.digest([book, command, params])
        native.control(book, params['roles'])
        actual = assess(owner, kind, book, event, params)
        ensure(actual['status'] == expected['status'] and actual['reason'] == expected['reason'], label+':status_reason')
        ensure(actual['failed_stage'] == stage_for[expected['reason']], label+':stage')
        if 'inputs' in expected: ensure(actual['inputs'] == expected['inputs'], label+':unknown_names')
        ensure(g.core.digest([book, command, params]) == stable, label+':no_mutation')
        refusals.append(dict(case=label, company=owner, before=book, command=command, parameters=params, expected=expected, actual=actual))

    original_refusals = read(HERE.parent/'event-specialization-audit-20261026/refusal-comparisons.json')
    programs = {o: contract.native_body(read(HERE.parent/f'authored-event-contract-20261026/examples/{o}.program.json')) for o in ('alpha', 'beta')}
    mutations = [('wrong-customer',1,'customer',known('Different customer')),
                 ('missing-claim',1,'claim_id',known('absent')),
                 ('unknown-customer',1,'customer',{'status':'unknown','reason':'unobserved'}),
                 ('false-approval',1,'approved',known(False)),
                 ('assessment-start',2,'start',known('2027-01-02')),
                 ('assessment-end',2,'end_exclusive',known('2027-02-02')),
                 ('due-before-sale',0,'due',known('2027-01-01'))]
    for owner, program in programs.items():
        params = {k: program[k] for k in ('schemas', 'roles', 'unit_cost_pointer', 'memory_definition', 'policy')}
        for label, index, key, value in mutations:
            body = deepcopy(program); body['commands'][index]['event']['inputs'][key]['value'] = value
            result = native.run(body); saved = next(x for x in original_refusals if x['company']==owner and x['case']==label)
            ensure(result['current'] == saved['current'] and result['successful_commands'] == saved['successful_prefix'], owner+':'+label+':native_baseline')
            compare_refusal(owner+':original:'+label, owner, result['current'], body['commands'][index], params, result['stop'])
        for label,index,source,event_id,day in [('sealed-window',3,1,'late.same.day','2027-01-31'),('duplicate-claim',1,0,'sale.duplicate','2027-01-03')]:
            body=deepcopy(program); command=deepcopy(body['commands'][source]);command['event'].update(id=event_id,date=day)
            body['commands']=body['commands'][:index]+[command];result=native.run(body)
            saved=next(x for x in original_refusals if x['company']==owner and x['case']==label)
            ensure(result['current']==saved['current'] and result['stop']['reason']==saved['reason'],owner+':'+label+':native_baseline')
            compare_refusal(owner+':original:'+label,owner,result['current'],command,params,result['stop'])
        for label,index,mutate in [
            ('sealed_before_missing',3,lambda ev: ev['inputs']['claim_id'].update(value=known('absent'))),
            ('cursor_before_window',2,lambda ev:(ev['inputs']['start'].update(value=known('2027-01-02')),ev['inputs']['end_exclusive'].update(value=known('2027-02-02'))))]:
            body=deepcopy(program)
            if index==3:
                command=deepcopy(body['commands'][1]);command['event'].update(id='late.and.missing',date='2027-01-31');body['commands']=body['commands'][:3]+[command]
            mutate(body['commands'][index]['event']);result=native.run(body)
            compare_refusal(owner+':order:'+label,owner,result['current'],body['commands'][index],params,result['stop'])
    for row in read(HERE.parent/'event-eligibility-audit-20261026/flat-counterexamples.json'):
        p=programs[row['company']];params={k:p[k] for k in ('schemas','roles','unit_cost_pointer','memory_definition','policy')}
        compare_refusal(row['company']+':flat:'+row['case'],row['company'],row['before'],
                        {'kind':'event','method_key':'collect','event':row['event']},params,row['native_stop'])

    # Extra cases require an independent native run, preserving outer validation
    # before unknown inputs and the selected operation's semantic stages.
    for owner, program in programs.items():
        for label, changes, wanted in [
            ('chronology_before_unknown',{'date':'2026-12-31','customer':{'status':'unknown','reason':'missing'}},'event_chronology'),
            ('unknown_amount_before_false_approval',{'amount':{'status':'unknown','reason':'not observed'},'approved':known(False)},'unknown_event_inputs'),
            ('approval_before_wrong_customer',{'customer':known('Wrong owner'),'approved':known(False)},'applicability_not_selected')]:
            body=deepcopy(program);event=body['commands'][1]['event']
            for key,value in changes.items():
                if key=='date':event['date']=value
                else:event['inputs'][key]['value']=value
            result=native.run(body);ensure(result['stop']['reason']==wanted,owner+':'+label+':native_reason')
            params={k:body[k] for k in ('schemas','roles','unit_cost_pointer','memory_definition','policy')}
            compare_refusal(owner+':multi:'+label,owner,result['current'],body['commands'][1],params,result['stop'])

    # Boundary controls are appended by the second part of this verification.
    run_controls(templates, scalar, expanded, assess, ensure, controls)
    for owner, program in programs.items():
        for day,end,period_end,wanted in [
            ('0001-01-01','0001-01-02','0002-01-01','eligible'),
            ('9999-12-30','9999-12-31','9999-12-31','eligible'),
            ('2028-02-28','2028-02-29','2029-01-01','eligible'),
            ('2028-02-29','2028-03-01','2029-01-01','eligible'),
            ('2027-12-31','2028-01-01','2028-01-01','eligible'),
            ('2028-02-28','2028-03-01','2029-01-01','assessment_window'),
            ('0001-01-01','0001-01-01','0002-01-01','assessment_window')]:
            body=deepcopy(program);book=body['opening'];book['date']=day
            book['period']={'start':day,'end_exclusive':period_end};book['memory']['collection_clock']['cursor']=day
            command=deepcopy(body['commands'][2]);command['event'].update(id='calendar.boundary',date=day)
            command['event']['inputs']['start']['value']=known(day);command['event']['inputs']['end_exclusive']['value']=known(end)
            body['commands']=[command];baseline=native.run(body)
            actual=assess(owner,'assess',book,command['event'],body)
            if wanted=='eligible':
                ensure(baseline['status']=='complete_provisional' and actual['status']=='eligible',owner+':complete_calendar:'+day)
            else:
                ensure(baseline['stop']['reason']==wanted and actual['reason']==wanted and actual['failed_stage']=='assessment_window',owner+':complete_calendar_refusal:'+day)
            controls.append(dict(case='complete_calendar_boundary',company=owner,date=day,end=end,period_end=period_end,
                                 expected=wanted,native_status=baseline['status'],native_stop=baseline['stop'],gate=actual))
    dump('cases.json',cases);dump('refusals.json',refusals);dump('controls.json',controls)
    # Re-read full serialized results and recompute the gate from saved inputs.
    for row in read(HERE/'cases.json'):
        ensure(equal(assess(row['company'],row['method'],row['before'],row['event'],row['parameters']),row['gate']),row['case']+':saved_gate_recomputed')
        ensure(equal(g.c.frontend.v2.propose(row['before'],row['request']),row['transition']),row['case']+':saved_transition_recomputed')
    for row in read(HERE/'refusals.json'):
        ensure(equal(assess(row['company'],row['command']['method_key'],row['before'],row['command']['event'],row['parameters']),row['actual']),row['case']+':saved_refusal_recomputed')
    for name,digest in lock.items():ensure(sha(ROOT/name)==digest,'protected:'+name)
    summary=dict(passed=True,templates=len(templates),complete_events=len(cases),original_refusals=18,
                 all_refusal_cases=len(refusals),controls=len(controls),assertions=len(assertions),protected_files=len(lock),
                 native_eligibility_and_construction_disabled=True,source_admission=False,accounting_admission=False,
                 full_lifecycle_portable=False,production_ready=False)
    dump('checks.json',summary);dump('assertions.json',assertions)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True)
    dump('run-manifest.json',dict(git_commit=git.stdout.strip() if git.returncode==0 else 'unavailable',
        command='env CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/ordered-event-eligibility-20261026/verify.py',
        environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',
        wall_seconds=time.monotonic()-start,data_version=sha(HERE/'source-lock.json'),
        plan_file='docs/plans/accounting-ordered-event-eligibility-20261026.md',
        result_file='data/accounting-master/ordered-event-eligibility-20261026/result.md',
        artifact_paths=['templates','cases.json','refusals.json','controls.json','checks.json','assertions.json'],
        implementation_sha256={n:sha(HERE/n) for n in ('gate.py','prepare.py','verify.py')},
        timestamp_utc=datetime.now(timezone.utc).isoformat()))
    print(json.dumps(summary))


def run_controls(templates, scalar, expanded, assess, ensure, controls):
    row=next(r for r in scalar if r['company']=='alpha' and r['method']=='collect')
    book,event,params=deepcopy(row['before']),deepcopy(row['event']),deepcopy(row['parameters'])
    template=templates['alpha','collect']
    def check(label,reason,stage='compile',t=None,b=None,ev=None,p=None,call=None,status='invalid'):
        result=assess('alpha','collect',book if b is None else b,event if ev is None else ev,
                      params if p is None else p,template if t is None else t,call)
        ensure(result['status']==status and reason in result.get('reason','') and result['failed_stage']==stage,label+':exact_refusal:'+str(result.get('reason')))
        controls.append(dict(case=label,expected_status=status,expected_reason=reason,expected_stage=stage,result=result))
    for field in ('template','state','event','schemas','definition'):
        call=g.make_call(template,book,event,params['schemas'],params['memory_definition']);call[field+'_sha256']='0'*64
        check('stale_'+field,'stale_'+field,'structure',call=call)
    call=g.make_call(template,book,event,params['schemas'],params['memory_definition']);call['operation']='sale'
    check('wrong_operation','operation_mismatch','structure',call=call)
    call=g.make_call(template,book,event,params['schemas'],params['memory_definition']);call['input_order_sha256']='0'*64
    check('stale_input_order','stale_input_order','structure',call=call)
    t=deepcopy(template);t['context']['entity']='Other entity';check('wrong_context','context_mismatch',t=t)
    t=deepcopy(template);del t['stages'][0]['bindings']['approved'];check('missing_binding','exact_stage_bindings',t=t)
    t=deepcopy(template);t['stages'][0]['bindings']['extra']={'kind':'book_date'};check('extra_binding','exact_stage_bindings',t=t)
    t=deepcopy(template);t['stages'][0]['bindings']['approved']={'kind':'event_input','name':'customer'};check('wrong_binding_type','binding_type_mismatch',t=t)
    t=deepcopy(template);t['stages'][0]['manifest']['inputs']['approved']['role']='caller_finding';check('caller_finding_role','caller_finding_disallowed',t=t)
    t=deepcopy(template);t['stages'][2]['bindings']['exists']={'kind':'literal','value':True};check('invented_membership','unsupported_source_kind',t=t)
    t=deepcopy(template);t['stages'][2]['bindings']['exists']['pointer']='/claims~3';check('bad_map_escape','pointer_escape',t=t)
    t=deepcopy(template);t['stages'][2]['bindings']['exists']['pointer']='/collection_clock';check('record_not_map','declared_record_map',t=t)
    t=deepcopy(template);t['stages'][2]['bindings']['exists']['key_input']='amount';check('nontext_map_key','map_key_text_type',t=t)
    t=deepcopy(template);t['stages'][3]['bindings']['owner']['after_stage']='customer_matches';check('forward_stage','forward_or_missing_presence_stage',t=t)
    t=deepcopy(template);t['stages'][3]['bindings']['owner']['after_stage']='approval';check('unproved_presence','unproved_row_presence',t=t)
    t=deepcopy(template);t['stages'][2]['manifest']['requirements'][0]['predicate']={'op':'not','arg':{'op':'ref','id':'exists'}}
    check('absence_is_not_presence','unproved_row_presence',t=t)
    t=deepcopy(template);t['stages'][3]['bindings']['owner']['field']='absent';check('missing_row_field','row_scalar_field',t=t)
    t=deepcopy(template);t['stages'][3]['bindings']['owner']['field']='remaining';check('wrong_row_field_type','binding_type_mismatch',t=t)
    t=deepcopy(template);t['stages'].append(deepcopy(t['stages'][0]));check('duplicate_stage','duplicate_stage',t=t)
    t=deepcopy(template);t['stages'][0]['manifest']['requirements'][0]['requires']=[];check('inexact_dependencies','inexact_dependency_declaration',t=t)
    t=deepcopy(template);t['stages'][3]['manifest']['requirements'][0]['predicate']['op']='callback'
    ev=deepcopy(event);ev['inputs']['approved']['value']=known(False)
    check('malformed_skipped_stage','unsupported_operator:callback',t=t,ev=ev)
    t=deepcopy(template);t['stages'][0]['manifest']['requirements'][0]['guard']={'op':'const','type':g.TEXT,'value':'true'}
    check('bad_guard_type','predicate_boolean',t=t)
    t=deepcopy(template);t['stages'][0]['manifest']['requirements'][0]['guard']['value']=False
    check('inactive_stage_not_success','no_active_requirements','approval',t=t)
    t=deepcopy(template);t['stages'][0]['manifest']['inputs']['unused']=deepcopy(t['stages'][0]['manifest']['inputs']['approved'])
    t['stages'][0]['bindings']['unused']={'kind':'event_input','name':'approved'};check('unused_binding','unused_input_declaration',t=t)
    ev=deepcopy(event);ev['inputs']['customer']['type']=g.DATE;ev['inputs']['customer']['value']=known('2027-01-01')
    check('wrong_event_type','event_type:customer','full_inputs',ev=ev)
    ev=deepcopy(event);del ev['inputs']['amount'];check('missing_event_input','exact_event_inputs','full_inputs',ev=ev)
    ev=deepcopy(event);ev['inputs']['unexpected']=deepcopy(ev['inputs']['amount']);check('extra_event_input','exact_event_inputs','full_inputs',ev=ev)
    ev=deepcopy(event);ev['inputs']['customer']['provenance']='';check('empty_provenance','text:event_provenance','full_inputs',ev=ev)
    ev=deepcopy(event);ev['inputs']['amount']['value']=known('2/2');check('noncanonical_amount','noncanonical_rational','full_inputs',ev=ev)
    ev=deepcopy(event);ev['inputs']['customer']['value']={'status':'unknown','reason':'not supplied'};ev['inputs']['amount']['value']=known('2/2')
    check('structural_invalid_after_unknown','noncanonical_rational','full_inputs',ev=ev)
    ev=deepcopy(event);ev['id']=next(iter(book['seen']));check('duplicate_event','duplicate_command','event_structure',ev=ev)
    b=deepcopy(book);b['memory']['claims'][next(iter(b['memory']['claims']))]['customer']=False
    check('wrong_typed_book','typed_memory:','structure',b=b)
    empty=next(r for r in scalar if r['company']=='alpha' and r['method']=='sale')['before']
    t=deepcopy(template);t['stages'][3]['bindings']['owner']['field']='absent'
    check('empty_map_does_not_hide_bad_row','row_scalar_field',t=t,b=empty)
    ev=deepcopy(event);ev['inputs']['claim_id']['value']=known('not-present')
    check('membership_computed_before_lookup','unknown_claim','claim_exists',ev=ev)
    ev=deepcopy(event);ev['inputs']['customer']['value']={'status':'unknown','reason':'not supplied'};ev['inputs']['claim_id']['value']=known('not-present')
    ev['inputs']['approved']['value']=known(False)
    check('unknown_precedes_approval_and_lookup','unknown_event_inputs','full_inputs',ev=ev,status='unresolved')
    ev=deepcopy(event)
    for name in ('amount','customer'):ev['inputs'][name]['value']={'status':'unknown','reason':'not supplied'}
    reversed_event=deepcopy(ev);reversed_event['inputs']=dict(reversed(list(ev['inputs'].items())))
    call=g.make_call(template,book,ev,params['schemas'],params['memory_definition'])
    second=g.make_call(template,book,reversed_event,params['schemas'],params['memory_definition'])
    ensure(call['event_sha256']==second['event_sha256'] and call['input_order_sha256']!=second['input_order_sha256'],'input_order_identity')
    check('reordered_inputs_old_call','stale_input_order','structure',ev=reversed_event,call=call)
    one=assess('alpha','collect',book,ev,params);two=assess('alpha','collect',book,reversed_event,params)
    ensure(one['inputs']==list(reversed(two['inputs'])) and len(one['inputs'])==2,'unknown_input_order_preserved')
    controls.append(dict(case='unknown_input_order_preserved',forward=one,reverse=two))
    ev=deepcopy(event);ev['inputs']['approved']['value']=known(False)
    t=deepcopy(template);t['stages'][0]['manifest']['requirements'][0]['on_false']='invalid'
    changed=assess('alpha','collect',book,ev,params,t)
    ensure(changed['status']=='invalid' and changed['reason']=='applicability_not_selected','authored_status_variant')
    controls.append(dict(case='authored_status_variant',result=changed,native_status='unsupported',original_contract_equivalent=False))
    ev=deepcopy(event);ev['inputs']['customer']['value']=known('Wrong customer')
    t=deepcopy(template);req=t['stages'][3]['manifest']['requirements'][0];req['predicate']={'op':'not','arg':req['predicate']}
    changed=assess('alpha','collect',book,ev,params,t)
    ensure(changed['status']=='eligible','authored_predicate_truth_variant')
    controls.append(dict(case='authored_predicate_truth_variant',result=changed,native_reason='claim_customer_mismatch',original_contract_equivalent=False))

    adjacent={'kind':'calendar_adjacent','left':{'kind':'event_metadata','field':'date'},'right':{'kind':'event_input','name':'end_exclusive'}}
    for left,right,wanted in [('0001-01-01','0001-01-02',True),('0001-01-01','0001-01-01',False),
                              ('9999-12-30','9999-12-31',True),('9999-12-31','9999-12-31',False),
                              ('9999-12-31','0001-01-01',False),('2028-02-28','2028-02-29',True),
                              ('2028-02-29','2028-03-01',True),('2028-02-28','2028-03-01',False),
                              ('2027-02-28','2027-03-01',True),('2027-12-31','2028-01-01',True)]:
        ev={'date':left,'inputs':{'end_exclusive':{'value':known(right)}}}
        result=g.resolve(adjacent,{},ev);ensure(result==known(wanted),'calendar:'+left+':'+right)
        controls.append(dict(case='calendar_adjacency',left=left,right=right,expected=wanted,result=result))
    for left,right in [('2027-02-29','2027-03-01'),('2027-01-01','10000-01-01')]:
        try:g.resolve(adjacent,{},dict(date=left,inputs={'end_exclusive':{'value':known(right)}}))
        except ValueError as exc:controls.append(dict(case='invalid_calendar_date',left=left,right=right,reason=str(exc)));ensure(True,'invalid_calendar:'+left+':'+right)
        else:raise AssertionError('invalid calendar accepted')
    ev={'date':'2027-01-01','inputs':{'end_exclusive':{'value':{'status':'unknown','reason':'end unknown'}}}}
    ensure(g.resolve(adjacent,{},ev)=={'status':'unknown','reason':'end unknown'},'calendar_unknown')
    controls.append(dict(case='calendar_unknown',result=g.resolve(adjacent,{},ev)))
    assessment=next(r for r in expanded if r['company']=='alpha')
    t=deepcopy(templates['alpha','assess']);t['stages'][2]['bindings']['adjacent']['left']={'kind':'event_input','name':'approved'}
    result=assess('alpha','assess',assessment['before'],assessment['event'],assessment['parameters'],t)
    ensure(result['status']=='invalid' and result['reason']=='calendar_date_type','calendar_compile_type')
    controls.append(dict(case='calendar_compile_type',result=result))


if __name__=='__main__':main()
