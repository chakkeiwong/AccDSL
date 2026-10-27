"""Conjoin retained cash bridges and balance snapshots for supplied histories."""
from copy import deepcopy
import retained_source_history_v1 as cash
import joint_source_relation_binding_v1 as balance
attachment=cash.attachment;core=cash.core
PROFILE='RetainedStatementHistoryAttachment/1'
BOUNDARY={**cash.BOUNDARY,'scope':'selected_cash_and_balance_history_constraints_only'}

def validate_request(body):
    core.need(len(core.canonical(body))<=core.MAX_BYTES,'request_size_limit')
    core.closed(body,['profile','cash_request','balance_request','balance_bindings'],'statement_history_request')
    core.need(body['profile']==PROFILE,'profile');cash.validate_request(body['cash_request'])
    b=body['balance_request'];core.need(type(b) is dict,'balance_request')
    selected=b.get('selected_relations');core.identifiers(selected,'balance_selection',nonempty=True)
    core.need(set(selected)<=set(balance.SUPPORTED),'supported_balance_selection')
    core.need(core.canonical(b.get('statement_request'))==core.canonical(body['cash_request']['source_request']['statement_request']),
              'same_complete_source_request')
    histories=body['cash_request']['histories'];bindings=body['balance_bindings']
    core.need(type(bindings) is dict and set(bindings)==set(histories),'balance_binding_groups')
    for key,value in bindings.items():core.need(type(value) is dict,'balance_bindings')
    core.need(all(k.split('.')[0]+'.cash_closing' in histories for k in selected),'balance_group_without_history')

def convert_snapshots(result):
    observations={}
    for key,item in result['definition']['observations'].items():
        mapping=result['source_mapping'][key];original=mapping['original_context'];when=mapping['measurement_time']
        core.need(when['kind']=='instant','snapshot_required')
        old={k:v for k,v in original.items() if k!='unit'};old['instant']=when['at']
        core.need(item['type']['context']==old,'original_snapshot_context')
        core.need(original['unit']=='USD million' and item['type']['scale']=='1000000/1'
                  and item['type']['dimensions']=={'currency:USD':1},'original_snapshot_unit')
        typ=deepcopy(item['type']);typ['context']={k:v for k,v in original.items() if k not in ['unit','period','measurement_kind']}
        aliases=mapping['aliases'];core.need(len(aliases)==1,'unique_source_caption')
        observations[key]={**deepcopy(item),'type':{'value_type':typ,'time':deepcopy(when),
                                                   'quantity':'reported_balance:'+aliases[0]}}
    return observations

def definitions(body,cash_result,balance_result):
    core.need(cash_result['source_result']['preserved_report']==balance_result['preserved_report'],'source_report_mismatch')
    defs=cash.definitions(body['cash_request'],cash_result['source_result'])
    snapshots=convert_snapshots(balance_result)
    for key,definition in defs.items():
        group=key.split('.')[0];equations=[e for e in balance_result['definition']['equations'] if e['id'].startswith(group+'.')]
        ids={t['observation'] for e in equations for t in e['terms']}
        bindings=body['balance_bindings'][key]
        core.need(set(bindings)<=ids,'unknown_balance_binding')
        observations=definition['measurements']['observations']
        core.need(not set(observations)&ids,'source_identity_collision')
        for name in sorted(ids):observations[name]=deepcopy(snapshots[name])
        for row in equations:
            definition['measurements']['relations'].append({'id':row['id'],'kind':'same_time',
                'terms':deepcopy(row['terms']),'rhs':row['rhs'],'identity_premise':deepcopy(row['identity_premise'])})
        definition['bindings'].update(deepcopy(bindings))
        for obligation in definition['obligations']:
            if obligation['id']=='unselected_disclosures:'+key:
                obligation['meaning']='Only explicitly selected cash and balance relations constrain this history; all remaining disclosure dispositions are unresolved for it.'
    return defs

def assemble(body,budget,cash_result,balance_result,results):
    statuses=[balance_result['status'],cash_result['status'],*[r['status'] for r in results.values()]]
    if any(s in ['invalid','invalid_history_attachment'] for s in statuses):status='invalid_history_attachment'
    elif any(s in ['conditionally_infeasible','supplied_history_incompatible'] for s in statuses):status='supplied_history_incompatible'
    elif 'unresolved' in statuses:status='unresolved'
    elif any(s in ['unknown','unsupported'] for s in statuses):status='unknown'
    else:status='conditional_candidates_with_unresolved_facts'
    return {'profile':PROFILE,**BOUNDARY,'request_sha256':core.digest(body),'budget':deepcopy(budget),
        'status':status,'cash_parent':deepcopy(cash_result),'balance_parent':deepcopy(balance_result),
        'attachments':deepcopy(results),
        'selection':{k:{'relations':[r['id'] for r in v['definition']['measurements']['relations']],
                        'observations':list(v['definition']['measurements']['observations']),
                        'mapped_observations':list(v['definition']['bindings'])} for k,v in results.items() if 'definition' in v},
        'interpretation':'Only explicit selected source relations and supplied mappings constrain each history; actual history and whole-filing compatibility remain unresolved.'}

def invalid(exc):return {'profile':PROFILE,**BOUNDARY,'status':'invalid','reason':str(exc)[:300]}

def assess(body,budget):
    try:
        validate_request(body);c=cash.assess(body['cash_request'],budget)
        core.need(c['status']!='invalid','invalid_cash_source:'+c.get('reason',''))
        b=balance.assess(body['balance_request'],attachment.measurement_budget(budget))
        core.need(b['status']!='invalid','invalid_balance_source:'+b.get('reason',''))
        defs=definitions(body,c,b);results={k:attachment.assess(d,budget) for k,d in defs.items()}
        return assemble(body,budget,c,b,results)
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError) as exc:return invalid(exc)

def verify_result(body,budget,result):
    try:
        if result.get('status')=='invalid':return result==assess(body,budget)
        validate_request(body);c=result['cash_parent'];b=result['balance_parent']
        core.need(cash.verify_result(body['cash_request'],budget,c),'cash_parent_replay')
        core.need(balance.verify_result(body['balance_request'],attachment.measurement_budget(budget),b),'balance_parent_replay')
        defs=definitions(body,c,b);core.need(set(defs)==set(result['attachments']),'complete_attachment_results')
        for key,d in defs.items():core.need(attachment.verify_result(d,budget,result['attachments'][key]),'joined_replay:'+key)
        return result==assemble(body,budget,c,b,result['attachments'])
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError):return False
