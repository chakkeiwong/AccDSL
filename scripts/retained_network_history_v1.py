"""Attach the full selected retained network to histories by exact context."""
from copy import deepcopy
import retained_statement_network_v1 as network
import typed_history_measurement_attachment_v1 as attachment
core=attachment.core
PROFILE='RetainedNetworkHistoryAttachment/1'
BOUNDARY={**attachment.BOUNDARY,'scope':'selected_retained_network_history_constraints_only',
          'whole_source_compatibility':'unresolved','joint_cross_context_history':False}

def context_key(context):return core.digest(context)

def validate_request(body):
    core.need(len(core.canonical(body))<=core.MAX_BYTES,'request_size_limit')
    core.closed(body,['profile','source_request','histories'],'network_history_request')
    core.need(body['profile']==PROFILE,'profile')
    core.need(type(body['histories']) is dict and bool(body['histories']),'histories')
    for row in body['histories'].values():
        core.closed(row,['history','bindings'],'supplied_history')
        core.need(type(row['bindings']) is dict,'bindings')

def definitions(body,parent):
    measurements=parent['definition'];groups={}
    for name,item in measurements['observations'].items():
        context=item['type']['value_type']['context'];key=context_key(context)
        group=groups.setdefault(key,{'context':deepcopy(context),'observations':{},'relations':[]})
        core.need(group['context']==context,'context_hash_collision')
        group['observations'][name]=deepcopy(item)
    for row in measurements['relations']:
        ids=([t['observation'] for t in row['terms']] if row['kind']=='same_time' else
             [row['opening'],*[t['observation'] for t in row['movements']],row['closing']])
        keys={context_key(measurements['observations'][i]['type']['value_type']['context']) for i in ids}
        core.need(len(keys)==1,'cross_context_relation_requires_explicit_conversion')
        groups[next(iter(keys))]['relations'].append(deepcopy(row))
    core.need(set(body['histories'])==set(groups),'complete_exact_context_histories')
    defs={}
    for key,group in groups.items():
        supplied=body['histories'][key]
        core.need(supplied['history']['value_type']['context']==group['context'],'history_context_mismatch')
        core.need(set(supplied['bindings'])<=set(group['observations']),'unknown_observation_mapping')
        defs[key]={'profile':attachment.PROFILE,'history':deepcopy(supplied['history']),
            'measurements':{'profile':attachment.temporal.PROFILE,'observations':group['observations'],'relations':group['relations']},
            'bindings':deepcopy(supplied['bindings']),
            'obligations':[{'id':'actual_history:'+key,
                'meaning':'Source populations, actual events and legal-account mappings are not established by a supplied feasible history.',
                'affects':['actual_history','execution']},
                {'id':'whole_source:'+key,'meaning':'Only selected supported relations constrain this history; full report dispositions and unselected or uninterpreted content remain unresolved.',
                 'affects':['whole_source_compatibility','execution']}]}
    return defs

def assemble(body,budget,parent,results):
    statuses=[parent['status'],*[r['status'] for r in results.values()]]
    if 'invalid' in statuses:status='invalid_history_attachment'
    elif 'conditionally_infeasible' in statuses:status='supplied_history_incompatible'
    elif 'unresolved' in statuses:status='unresolved'
    elif any(s in ['unknown','unsupported'] for s in statuses):status='unknown'
    else:status='conditional_candidates_with_unresolved_facts'
    return {'profile':PROFILE,**BOUNDARY,'request_sha256':core.digest(body),'budget':deepcopy(budget),
        'status':status,'source_result':deepcopy(parent),'attachments':deepcopy(results),
        'selected_observations':len(parent['definition']['observations']),
        'selected_relations':len(parent['definition']['relations']),
        'context_count':len(results),
        'interpretation':'All selected source equations are retained; only explicit mappings connect them to supplied histories.'}

def invalid(exc):return {'profile':PROFILE,**BOUNDARY,'status':'invalid','reason':str(exc)[:300]}

def assess(body,budget):
    try:
        validate_request(body);parent=network.assess(body['source_request'],attachment.measurement_budget(budget))
        core.need(parent['status']!='invalid','invalid_source:'+parent.get('reason',''))
        defs=definitions(body,parent);results={k:attachment.assess(d,budget) for k,d in defs.items()}
        return assemble(body,budget,parent,results)
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError) as exc:return invalid(exc)

def verify_result(body,budget,result):
    try:
        if result.get('status')=='invalid':return result==assess(body,budget)
        validate_request(body);parent=result['source_result']
        core.need(network.verify_result(body['source_request'],attachment.measurement_budget(budget),parent),'source_replay')
        defs=definitions(body,parent);core.need(set(defs)==set(result['attachments']),'complete_attachment_results')
        for key,d in defs.items():core.need(attachment.verify_result(d,budget,result['attachments'][key]),'history_replay:'+key)
        return result==assemble(body,budget,parent,result['attachments'])
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError):return False
