from copy import deepcopy
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from fractions import Fraction
import json
import subprocess
import sys
import time
import constructor as c
import declared_receivable_lifecycle_v1 as native
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
AUDIT=HERE.parent/'event-specialization-audit-20261026'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(n,v):(HERE/n).write_text(json.dumps(v,indent=2)+'\n')
def canon(x):return c.core.canonical(x)
def main():
    start=time.monotonic();lock=json.loads((HERE/'source-lock.json').read_text())
    for n,h in lock.items():assert sha(ROOT/n)==h,n
    templates={(o,k):json.loads((HERE/f'templates/{o}.{k}.json').read_text()) for o in ('alpha','beta') for k in ('sale','collect')}
    rows=json.loads((AUDIT/'request-comparisons.json').read_text())
    assertions=[];cases=[];controls=[]
    def ensure(ok,label):
        assertions.append({'check':label,'passed':bool(ok)});assert ok,label
    def run_case(label,owner,kind,book,event,params):
        t=templates[owner,kind];call=c.make_call(t,book,event)
        before=canon([t,book,event,params])
        constructed=c.construct(t,book,event,params['schemas'],params['memory_definition'],call)
        command={'kind':'event','method_key':kind,'event':deepcopy(event)}
        expected=native.make_request(book,params,command)
        ensure(canon(constructed['request'])==canon(expected),label+':full_request')
        left=c.frontend.v2.propose(book,constructed['request']);right=c.frontend.v2.propose(book,expected)
        ensure(left['status']==right['status']=='proposed',label+':proposed')
        ensure(canon(left)==canon(right),label+':complete_transition')
        ensure(canon([t,book,event,params])==before,label+':inputs_unchanged')
        native.control(left['after'],params['roles'])
        cases.append({'case':label,'company':owner,'method':kind,'before':deepcopy(book),'event':deepcopy(event),'parameters':deepcopy(params),
                      'template_sha256':c.core.digest(t),'construction':constructed,'native_request':expected,'complete_transition':left})
        return deepcopy(left['after'])
    for r in rows:
        if r['method'] in ('sale','collect'):
            run_case('retained_'+r['company']+'_'+str(r['index']),r['company'],r['method'],r['before'],r['full_command']['event'],r['body_parameters'])
    for owner in ('alpha','beta'):
        sale=next(r for r in rows if r['company']==owner and r['method']=='sale')
        collect=next(r for r in rows if r['company']==owner and r['method']=='collect')
        book=deepcopy(sale['before']);params=deepcopy(sale['body_parameters'])
        for i,key in enumerate(['new/a~1','債權/乙~2','(literal) ${x}']):
            event=deepcopy(sale['full_command']['event']);event.update(id='new.sale.'+str(i),date='2027-01-0'+str(2+i*2))
            for name,value in [('claim_id',key),('customer','New customer '+str(i)),('due','2027-02-0'+str(i+1)),('units','1/1'),('consideration',str(17+i)+'/1')]:event['inputs'][name]['value']=c.base.known(value)
            book=run_case(owner+'_new_sale_'+str(i),owner,'sale',book,event,params)
            event=deepcopy(collect['full_command']['event']);event.update(id='new.collect.'+str(i),date='2027-01-0'+str(3+i*2))
            for name,value in [('claim_id',key),('customer','New customer '+str(i)),('amount',str(4+i)+'/1')]:event['inputs'][name]['value']=c.base.known(value)
            book=run_case(owner+'_new_collect_'+str(i),owner,'collect',book,event,params)
    base=cases[0];t=templates[base['company'],base['method']];book=base['before'];event=base['event'];params=base['parameters']
    def attempt(template=t,state=book,ev=event,call=None):
        return c.construct(template,state,ev,params['schemas'],params['memory_definition'],call or c.make_call(template,state,ev))
    def refuse(label,fn,reason,status='invalid'):
        try:fn()
        except c.Refusal as e:
            ensure(e.status==status and reason in e.reason,label+':exact_refusal')
            controls.append({'case':label,'status':e.status,'reason':e.reason})
        else:raise AssertionError('accepted_bad_case:'+label)
    mutated=deepcopy(t);mutated['parameters'].append(deepcopy(mutated['parameters'][0]))
    refuse('duplicate_parameter',lambda:attempt(mutated),'duplicate_or_invalid_parameter')
    mutated=deepcopy(t);mutated['parameters'].append({'name':'unused','type':c.TEXT,'source':{'kind':'event_metadata','field':'id'}})
    refuse('unused_parameter',lambda:attempt(mutated),'unused_parameters')
    mutated=deepcopy(t);mutated['parameters']=[p for p in mutated['parameters'] if p['name']!='claim_id']
    refuse('missing_parameter',lambda:attempt(mutated),'unbound_parameter')
    mutated=deepcopy(t);next(p for p in mutated['parameters'] if p['name']=='claim_id')['type']=c.DATE
    refuse('wrong_parameter_type',lambda:attempt(mutated),'parameter_type')
    mutated=deepcopy(event);mutated['inputs']['claim_id']['value']={'status':'unknown','reason':'missing identity'}
    refuse('unknown_identity',lambda:attempt(ev=mutated),'unknown_event_input:claim_id','unresolved')
    mutated=deepcopy(event);mutated['inputs']['consideration']['value']={'status':'unknown','reason':'missing amount'}
    refuse('unknown_financial_input',lambda:attempt(ev=mutated),'unknown_event_input:consideration','unresolved')
    mutated=deepcopy(event);mutated['inputs']['claim_id']['type']=c.DATE;mutated['inputs']['claim_id']['value']=c.base.known('2027-01-01')
    refuse('wrong_event_input_type',lambda:attempt(ev=mutated),'parameter_type')
    mutated=deepcopy(event);del mutated['inputs']['claim_id']
    refuse('missing_event_input',lambda:attempt(ev=mutated),'missing_event_parameter')
    for field in ('template_sha256','state_sha256','event_sha256'):
        call=c.make_call(t,book,event);call[field]='0'*64
        refuse('stale_'+field,lambda call=call:attempt(call=call),'stale_'+field.split('_sha256')[0])
    mutated=deepcopy(t);mutated['context']['entity']='wrong'
    refuse('wrong_chart_context',lambda:attempt(mutated),'context_mismatch')
    mutated=deepcopy(t);mutated['method_template']={'node':'callback','name':'native.make_request'}
    refuse('callback_node',lambda:attempt(mutated),'unsupported_template_node')
    mutated=deepcopy(t);mutated['parameters'][0]['source']={'kind':'python','name':'native'}
    refuse('callback_source',lambda:attempt(mutated),'unsupported_parameter_source')
    mutated=deepcopy(t);mutated['method_template']={'node':'literal','value':{}}
    refuse('opaque_method_literal',lambda:attempt(mutated),'literal_scalar')
    mutated=deepcopy(t);mutated['parameters'][0]['extra']=True
    refuse('extra_parameter_field',lambda:attempt(mutated),'parameter_fields')
    mutated=deepcopy(t);mutated['residuals']=['x'*(c.core.MAX_BYTES+1)]
    refuse('template_size_limit',lambda:attempt(mutated),'record_size_limit')
    mutated=deepcopy(t)
    node={'node':'literal','value':'leaf'}
    for _ in range(c.core.MAX_DEPTH+1):node={'node':'array','items':[node]}
    mutated['method_template']=node
    refuse('template_depth_limit',lambda:attempt(mutated),'structure_limit')
    collection=next(x for x in cases if x['method']=='collect');ct=templates[collection['company'],'collect']
    def collect_attempt(template):
        r=collection;p=r['parameters']
        return c.construct(template,r['before'],r['event'],p['schemas'],p['memory_definition'],c.make_call(template,r['before'],r['event']))
    mutated=deepcopy(ct);pointer=mutated['parameters'].pop();mutated['parameters'].insert(0,pointer)
    refuse('forward_pointer_parameter',lambda:collect_attempt(mutated),'forward_or_missing_parameter')
    mutated=deepcopy(ct);mutated['parameters'][-1]['source']['segments'][1]={'raw_pointer':'/claims/ambiguous'}
    refuse('raw_pointer_escape_bypass',lambda:collect_attempt(mutated),'pointer_segment')
    preserved=canon([t,book,event,params]);detached=attempt();detached['request']['method']['memory']['definition']['operations'][0]['path'][1]='changed'
    ensure(canon([t,book,event,params])==preserved,'returned_values_do_not_mutate_inputs')
    alternative=deepcopy(ct)
    def encode(value):
        if type(value) is dict:return {'node':'object','fields':{k:encode(v) for k,v in value.items()}}
        if type(value) is list:return {'node':'array','items':[encode(v) for v in value]}
        return {'node':'literal','value':value}
    def replace_amount(node):
        if node.get('node')=='object':
            fields=node['fields']
            if set(fields)=={'op','id'} and fields['op']=={'node':'literal','value':'ref'} and fields['id']=={'node':'literal','value':'amount'}:
                unit={'kind':'rational','context':deepcopy(collection['native_request']['method']['monetary']['definition']['inputs']['amount']['type']['context']),'dimensions':{},'scale':'1/1'}
                return encode({'op':'mul','left':{'op':'ref','id':'amount'},'right':{'op':'const','type':unit,'value':'1/2'}})
            return {'node':'object','fields':{k:replace_amount(v) for k,v in fields.items()}}
        if node.get('node')=='array':return {'node':'array','items':[replace_amount(v) for v in node['items']]}
        return deepcopy(node)
    monetary=alternative['method_template']['fields']['monetary']['fields']['definition']
    for name in ('calculations','postings','flows'):monetary['fields'][name]=replace_amount(monetary['fields'][name])
    alt=collect_attempt(alternative)
    ar=c.frontend.v2.propose(collection['before'],alt['request'])
    ensure(ar['status']=='proposed','alternative_half_collection_proposed')
    native.control(ar['after'],collection['parameters']['roles'])
    ensure(canon(alt['request'])!=canon(collection['native_request']),'alternative_differs_from_selected_native_contract')
    cash=collection['parameters']['roles']['cash'];before_cash=Fraction(collection['before']['balances'][cash])
    amount=Fraction(collection['event']['inputs']['amount']['value']['value'])
    ensure(Fraction(ar['after']['balances'][cash])-before_cash==amount/2,'alternative_exact_half_cash')
    dump('algorithm-variant.json',{'template':alternative,'construction':alt,'transition':ar,'selected_native_request':collection['native_request'],'selected_contract_correspondence':False})
    # A visible amount change exercises the fixed algorithm, not a fixture table.
    for owner in ('alpha','beta'):
        target=[x for x in cases if x['company']==owner and x['case'].startswith(owner+'_new_collect_')]
        ensure(len({x['complete_transition']['after']['balances'][x['parameters']['roles']['cash']] for x in target})==3,owner+':consequential_changed_cash')
    original_specializer=native.make_request
    def disabled_specializer(*args,**kwargs):raise AssertionError('native_specializer_called')
    native.make_request=disabled_specializer
    try:
        isolated=attempt()
        ensure(canon(isolated['request'])==canon(base['native_request']),'constructor_works_with_native_specializer_disabled')
    finally:native.make_request=original_specializer
    badschemas=deepcopy(params['schemas']);badschemas[next(iter(badschemas))]['unexpected']=True
    refuse('corrupt_schema',lambda:c.construct(t,book,event,badschemas,params['memory_definition'],c.make_call(t,book,event)),'schema_digest')
    dump('cases.json',cases);dump('controls.json',controls);dump('check-detail.json',assertions)
    for row in json.loads((HERE/'cases.json').read_text()):
        template=templates[row['company'],row['method']];state=row['before'];ev=row['event'];pp=row['parameters']
        repeated=c.construct(template,state,ev,pp['schemas'],pp['memory_definition'],c.make_call(template,state,ev))
        ensure(canon(repeated)==canon(row['construction']),'saved_construction:'+row['case'])
        ensure(canon(c.frontend.v2.propose(state,repeated['request']))==canon(row['complete_transition']),'saved_transition:'+row['case'])
    for n,h in lock.items():ensure(sha(ROOT/n)==h,'protected:'+n)
    summary={'passed':True,'templates':len(templates),'full_request_and_transition_cases':len(cases),'retained_cases':sum(x['case'].startswith('retained_') for x in cases),'new_intent_cases':sum(not x['case'].startswith('retained_') for x in cases),'controls':len(controls),'checks':len(assertions),'protected_files':len(lock),'native_specializer_called_by_constructor':False,'native_eligibility_still_required':True,'source_admission':False,'accounting_admission':False,'production_ready':False}
    dump('check-detail.json',assertions);dump('checks.json',summary)
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True)
    dump('run-manifest.json',{'git_commit':git.stdout.strip() if git.returncode==0 else 'unavailable','command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/parameterized-method-construction-20261026/verify.py','environment':sys.version,'cpu_gpu':'CPU; GPU intentionally hidden','random_seeds':'N/A deterministic','wall_seconds':time.monotonic()-start,'data_version':sha(HERE/'source-lock.json'),'implementation_sha256':{n:sha(HERE/n) for n in ['constructor.py','prepare.py','verify.py','design.md']},'plan_file':'docs/plans/accounting-parameterized-method-construction-20261026.md','result_file':str((HERE/'result.md').relative_to(ROOT)),'artifacts':['templates','cases.json','controls.json','checks.json','check-detail.json'],'timestamp_utc':datetime.now(timezone.utc).isoformat()})
    print(json.dumps(summary))
if __name__=='__main__':main()
