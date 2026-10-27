"""Ordered identity diagnostics, with no financial or durable state execution."""
from copy import deepcopy
import method_requirements_v1 as core
import method_collections_v1 as snapshot

PROFILE='MethodIdentityLifecycle/1'
MAX_POOLS=32
MAX_ACTIONS=32
MAX_OPERATIONS=32
BOUNDARY={**snapshot.BOUNDARY,'scope':'selected_identity_lifecycle_only',
          'identity_trace_meaning':'diagnostic simulation; no financial posting or durable commit'}


def field(definition,collection,key):
    core.text(collection,'collection_name');core.text(key,'field_name')
    collections=definition['snapshot']['collections']
    core.need(collection in collections,'undeclared_collection')
    core.need(key in collections[collection]['fields'],'undeclared_field')
    return collections[collection]['fields'][key]


def validate(definition):
    core.need(len(core.canonical(definition))<=core.MAX_BYTES,'definition_size_limit')
    core.closed(definition,['profile','method_id','version','snapshot','events','action_field',
                           'pools','actions','residual_prerequisites'],'identity_definition')
    core.need(definition['profile']==PROFILE,'identity_profile')
    for name in ['method_id','version']:
        core.text(definition[name],name)
    snapshot.validate(definition['snapshot'])
    tag=field(definition,definition['events'],definition['action_field'])
    core.need(tag['type']['kind']=='text','action_text_required')
    pools=definition['pools']
    core.need(type(pools) is dict and 0<len(pools)<=MAX_POOLS,'pool_limit')
    pool_types={}
    for name,pool in pools.items():
        core.text(name,'pool_name')
        core.closed(pool,['live','retired'],'pool')
        types=[]
        for state in ['live','retired']:
            core.closed(pool[state],['collection','field'],'pool_initial_binding')
            types.append(field(definition,pool[state]['collection'],pool[state]['field'])['type'])
        core.need(types[0]==types[1] and types[0]['kind']=='text','pool_key_type_mismatch')
        pool_types[name]=types[0]
    actions=definition['actions']
    core.need(type(actions) is list and 0<len(actions)<=MAX_ACTIONS,'action_limit')
    seen=set()
    for action in actions:
        core.closed(action,['tag','operations'],'action')
        core.text(action['tag'],'action_tag')
        core.need(action['tag'] not in seen,'duplicate_action_tag');seen.add(action['tag'])
        operations=action['operations']
        core.need(type(operations) is list and 0<len(operations)<=MAX_OPERATIONS,'operation_limit')
        for operation in operations:
            core.closed(operation,['op','pool','key'],'identity_operation')
            core.need(operation['op'] in ['create','require','consume'],'identity_operator')
            core.need(type(operation['pool']) is str and operation['pool'] in pools,'undeclared_pool')
            binding=operation['key']
            core.closed(binding,['scope','field'],'identity_key_binding')
            core.text(binding['field'],'key_field')
            if binding['scope']=='row':
                declaration=field(definition,definition['events'],binding['field'])
            else:
                core.need(binding['scope']=='global','key_scope')
                core.need(binding['field'] in definition['snapshot']['inputs'],'undeclared_global')
                declaration=definition['snapshot']['inputs'][binding['field']]
            core.need(declaration['type']==pool_types[operation['pool']],'operation_key_type_mismatch')
    core.identifiers(definition['residual_prerequisites'],'residual_prerequisites',True)
    return definition


def assess(definition,values,available_capabilities):
    try:
        validate(definition)
        snapshot.validate_values(definition['snapshot'],values)
        base=snapshot.assess(definition['snapshot'],values,available_capabilities)
        core.need('findings' in base,'snapshot_structure_invalid:'+base.get('reason',''))
        actions={a['tag']:a['operations'] for a in definition['actions']}
        def collection(name):
            return values['collections'].get(name,{'status':'partial','rows':[],'reason':'missing_collection'})
        events=collection(definition['events'])
        for row in events['rows']:
            tag=row.get(definition['action_field'],{'status':'unknown','reason':'missing_action'})
            if tag['status']=='known':
                core.need(tag['value'] in actions,'unmapped_action_tag:'+tag['value'])
        state={};initial_unknown={};initial_violations=[];trace=[]
        for name,pool in definition['pools'].items():
            state[name]={'live':[],'retired':[]}
            for status in ['live','retired']:
                source=pool[status];c=collection(source['collection']);seen=set()
                for i,row in enumerate(c['rows']):
                    value=row.get(source['field'],{'status':'unknown','reason':'missing_initial_key'})
                    if value['status']=='unknown':
                        initial_unknown[name+'/'+status+'/'+str(i)]=value['reason']
                    elif value['value'] in seen:
                        initial_violations.append({'pool':name,'state':status,'key':value['value'],
                                                   'reason':'duplicate_initial_identity'})
                    else:
                        seen.add(value['value'])
                state[name][status]=sorted(seen)
                if c['status']=='partial':initial_unknown[name+'/'+status]=c['reason']
            for key in set(state[name]['live'])&set(state[name]['retired']):
                initial_violations.append({'pool':name,'key':key,'reason':'initial_live_retired_overlap'})
        initial_state=deepcopy(state)
        def result(identity_status,reason=None,position=None,details=None):
            statuses=[base['status'],identity_status]
            status=next((s for s in ['invalid','unsupported','unresolved'] if s in statuses),
                        'identity_requirements_satisfied')
            return {**BOUNDARY,'profile':PROFILE,'status':status,'identity_status':identity_status,
                    'reason':reason,'stopped_index':position,'details':details or {},
                    'definition_sha256':core.digest(definition),'values_sha256':core.digest(values),
                    'snapshot_assessment':base,'initial_state':initial_state,'state':deepcopy(state),
                    'trace':deepcopy(trace),'unprocessed_indices':list(range(position,len(events['rows'])))
                    if position is not None else [],'residual_prerequisites':deepcopy(definition['residual_prerequisites'])}
        if initial_violations:
            return result('invalid','invalid_initial_identity',0,{'violations':initial_violations,'unknown':initial_unknown})
        if base['status'] in ['invalid','unsupported']:
            return result(base['status'],'snapshot_precondition_failed',0)
        if initial_unknown:
            return result('unresolved','initial_identity_incomplete',0,{'unknown':initial_unknown})
        if events['status']=='partial':
            return result('unresolved','event_sequence_incomplete',0,{'reason':events['reason']})
        for i,row in enumerate(events['rows']):
            tag=row.get(definition['action_field'],{'status':'unknown','reason':'missing_action'})
            if tag['status']=='unknown':
                return result('unresolved','event_action_unknown',i,{'reason':tag['reason']})
            staged=deepcopy(state);operations=[]
            for j,operation in enumerate(actions[tag['value']]):
                binding=operation['key']
                source=values['globals'] if binding['scope']=='global' else row
                value=source.get(binding['field'],{'status':'unknown','reason':'missing_identity_key'})
                if value['status']=='unknown':
                    return result('unresolved','event_key_unknown',i,{'operation':j,'reason':value['reason']})
                key=value['value'];pool=staged[operation['pool']];op=operation['op']
                if op=='create':
                    if key in pool['live'] or key in pool['retired']:
                        return result('invalid','identity_already_used',i,{'operation':j,'pool':operation['pool'],'key':key})
                    pool['live'].append(key);pool['live'].sort()
                else:
                    if key not in pool['live']:
                        return result('invalid','identity_not_live',i,{'operation':j,'pool':operation['pool'],'key':key})
                    if op=='consume':
                        pool['live'].remove(key);pool['retired'].append(key);pool['retired'].sort()
                operations.append({'operation':j,'op':op,'pool':operation['pool'],'key':key})
            state=staged
            trace.append({'index':i,'action':tag['value'],'operations':operations,'state':deepcopy(state)})
        return result('complete')
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError) as exc:
        return {**BOUNDARY,'status':'invalid','reason':str(exc)[:250]}
