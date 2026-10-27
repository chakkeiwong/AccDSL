"""Original evaluator plus explicit execution-policy mismatch finding."""
from copy import deepcopy
from composition import validate,canonical,path_value,requested_heads,Invalid,PROFILE
from hashlib import sha256

def assess(plan,library):
    validate(plan);stages={};findings=[];publications=set()
    for stage in plan['stages']:
        reader,exchange,d=library.select(stage);request=reader.body(exchange['request_ref'])
        stage_info={'descriptor':d,'view_ref':deepcopy(request['view_ref']),
            'context_ref':deepcopy(request.get('context_ref')),'signature_ref':deepcopy(request.get('signature_ref'))}
        stages[stage['id']]={'reader':reader,'exchange':exchange,'description':d,'info':stage_info}
        if d['publication_knowledge']=='unknown':
            findings.append({'stage':stage['id'],'status':'unresolved','reason':'acknowledgement_unknown'})
        elif d['disposition']=='rejected':
            findings.append({'stage':stage['id'],'status':'invalid','reason':'refused_stage_unavailable'})
        elif d['disposition']=='partial':
            findings.append({'stage':stage['id'],'status':'unresolved','reason':'native_partial_result'})
        if d['effects'] and d['effects']['record_publication']:
            identity=canonical([d['profile_ref'],d['identity']])
            if identity in publications:findings.append({'stage':stage['id'],'status':'invalid','reason':'duplicate_publication_decision'})
            publications.add(identity)
    for edge in plan['dependencies']:
        a,b=stages[edge['from']],stages[edge['to']];da,db=a['description'],b['description']
        status,reason='compatible','exact_native_dependency'
        evidence={}
        if da['publication_knowledge']=='unknown' or db['publication_knowledge']=='unknown':
            status,reason='unresolved','acknowledgement_unknown'
        elif da['disposition']=='rejected' or db['disposition']=='rejected':
            status,reason='invalid','refused_stage_unavailable'
        elif edge['relation'] in {'sequence','state'}:
            if da['profile_ref']!=db['profile_ref']:
                status,reason='unsupported','cross_profile_adapter_missing'
                if edge['relation']=='state':
                    try:evidence={'produced_ref':path_value(a['exchange']['world_after'],edge['produced_path']),
                        'consumed_ref':path_value(b['exchange']['world_before'],edge['consumed_path'])}
                    except Invalid as exc:evidence={'path_error':str(exc)}
            elif da.get('execution_binding',{}).get('identity_policy_ref')!=db.get('execution_binding',{}).get('identity_policy_ref'):
                status,reason='unsupported','execution_policy_adapter_missing'
            elif edge['relation']=='state' and da['disposition']=='partial':
                status,reason='unresolved','partial_result_not_financial_successor'
            else:
                before=b['exchange']['world_before'];after=a['exchange']['world_after']
                if after!=before:status,reason='invalid','intervening_world_not_declared'
                if edge['relation']=='state':
                    try:
                        produced=path_value(after,edge['produced_path']);consumed=path_value(before,edge['consumed_path'])
                        evidence={'produced_ref':produced,'consumed_ref':consumed}
                        if produced!=consumed:status,reason='invalid','state_reference_mismatch'
                        elif consumed not in requested_heads(b['reader'],b['reader'].body(b['exchange']['request_ref'])):
                            status,reason='invalid','state_not_requested'
                    except Invalid as exc:status,reason='invalid',str(exc)
        else:
            receipt=da.get('receipt_ref')
            receiver=b['reader'];closure=receiver.closure([b['exchange']['request_ref']])
            if receipt is None:status,reason='unresolved','source_receipt_unavailable'
            elif receipt['digest'] not in closure:status,reason='invalid','receipt_not_consumed'
            else:evidence={'receipt_ref':deepcopy(receipt)}
        findings.append({'dependency':deepcopy(edge),'status':status,'reason':reason,'evidence':evidence})
    severity={'compatible':0,'unresolved':1,'unsupported':2,'invalid':3}
    availability={}
    for stage in plan['stages']:
        identity=stage['id'];reasons=[]
        for finding in findings:
            if finding.get('stage')==identity:
                reasons.append((finding['status'],finding['reason']))
            dep=finding.get('dependency')
            if dep and dep['to']==identity:
                reasons.append((finding['status'],finding['reason']))
                inherited=availability[dep['from']]
                if inherited['status']!='compatible':
                    reasons.append((inherited['status'],'predecessor_unavailable:'+dep['from']))
        status=max((s for s,r in reasons),key=lambda s:severity[s],default='compatible')
        availability[identity]={'status':status,'reasons':[r for s,r in reasons if s!='compatible']}
    status=max((f['status'] for f in findings),key=lambda s:severity[s],default='compatible')
    return {'profile':PROFILE,'plan_sha256':sha256(canonical(plan)).hexdigest(),
        'status':'documentary_consistent' if status=='compatible' else status,
        'stages':{k:v['info'] for k,v in stages.items()},'findings':findings,'dependency_availability':availability,
        'scope':'selected_retained_dependencies_only','execution_admission':False,
        'source_admission':False,'accounting_admission':False,'concurrent_execution_admission':False}
