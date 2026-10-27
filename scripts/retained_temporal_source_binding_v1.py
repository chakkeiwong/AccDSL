"""Two exact retained cash-flow bridges; no implicit population admission."""
from copy import deepcopy
from fractions import Fraction as Q
import joint_source_relation_binding_v1 as source
import temporal_measurement_constraints_v1 as temporal

core=temporal.core
PROFILE='RetainedTemporalSourceRelations/1'
SUPPORTED=('annual.cash_closing','interim.cash_closing')
BOUNDARY={**temporal.BOUNDARY,'scope':'selected_retained_cash_flow_bridges_only'}


def identity_hypothesis(key):
    core.need(key in SUPPORTED,'unsupported_identity')
    return {'id':'underlying_bridge:'+key,'status':'proposed',
            'meaning':'The unrounded values satisfy the exact retained opening plus change equals closing relation '+key+'.'}


def mapping_hypothesis(key):
    core.need(key in SUPPORTED,'unsupported_mapping')
    return {'id':'cash_flow_population:'+key,'status':'proposed',
            'meaning':'For '+key+', opening and closing refer to the same cash-flow-statement population and the intervening change measures its net movement; this is not a legal-book cash mapping.'}


def fixture(selected=None, assume=False):
    selected=list(SUPPORTED if selected is None else selected)
    return {'profile':PROFILE,'statement_request':source.statement.fixture(),
            'selected_relations':selected,
            'rounding_hypothesis':source.rounding_hypothesis() if assume else None,
            'identity_hypotheses':{k:identity_hypothesis(k) if assume else None for k in selected},
            'mapping_hypotheses':{k:mapping_hypothesis(k) if assume else None for k in selected}}


def build(body,budget):
    core.need(len(core.canonical(body))<=core.MAX_BYTES,'request_size_limit')
    core.closed(body,['profile','statement_request','selected_relations','rounding_hypothesis',
                      'identity_hypotheses','mapping_hypotheses'],'temporal_source_request')
    core.need(body['profile']==PROFILE,'profile')
    selected=body['selected_relations'];core.identifiers(selected,'selected_relations')
    core.need(bool(selected) and set(selected)<=set(SUPPORTED),'supported_nonempty_selection')
    rounding=body['rounding_hypothesis']
    core.need(rounding is None or rounding==source.rounding_hypothesis(),'rounding_hypothesis_mismatch')
    for field,builder in [('identity_hypotheses',identity_hypothesis),('mapping_hypotheses',mapping_hypothesis)]:
        values=body[field]
        core.need(type(values) is dict and set(values)==set(selected),'hypothesis_selection_mismatch')
        for key,value in values.items():
            core.need(value is None or value==builder(key),'hypothesis_semantics_mismatch:'+key)
    base=source.build({'profile':source.PROFILE,'statement_request':body['statement_request'],
        'selected_relations':[],'rounding_hypothesis':None,'identity_hypotheses':{}},budget)
    report=base['preserved_report'];rows={r['id']:r for r in body['statement_request']['relations']}
    dispositions={r['id']:r for r in report['relations']}
    observations,relations,mappings,missing={},[],{},[]
    for key in selected:
        row=rows[key];group=row['group']
        aliases=[group+'.cash_flow.'+part for part in ['opening','change','closing']]
        core.need(row['kind']=='stock_flow_bridge' and row['comparison']=='terms' and not row['omitted_source_rows'],
                  'unsupported_bridge_shape')
        core.need(row['lhs']==[{'alias':aliases[0],'coefficient':'1/1'},{'alias':aliases[1],'coefficient':'1/1'}]
                  and row['rhs']==[{'alias':aliases[2],'coefficient':'1/1'}],'bridge_terms_mismatch')
        core.need(dispositions[key]['context_check']['status']=='compatible_for_declared_displayed_relation',
                  'source_context_mismatch')
        ids=[]
        for alias in aliases:
            item=report['observations'][alias];original=item['observation'];decl=item['declaration']
            context=original['context'];when=decl['measurement_time'];ref=decl['observation_ref'];digest=ref['digest']
            core.need(context['unit']==decl['unit']=='USD million','source_unit_mismatch')
            value_context={k:v for k,v in context.items() if k not in ['unit','period','measurement_kind']}
            quantity='cash_flow_statement_cash_population' if when['kind']=='instant' else 'cash_flow_statement_net_change'
            value=original['record']['body']['value'];interval=None
            if rounding is not None and value['tag']=='known_displayed':
                amount=value['amount'];displayed=Q(int(amount['n']),int(amount['d']))
                interval=source.statement.state.rounding_interval(displayed,Q(rounding['quantum']))
            observations[digest]={'type':{'value_type':{'kind':'rational','context':value_context,
                'dimensions':{'currency:USD':1},'scale':'1000000/1'},'time':deepcopy(when),'quantity':quantity},
                'interval':interval,'interval_premise':None if rounding is None else
                    {k:rounding[k] for k in ['id','status','meaning']},'source_ref':ref['schema']+':'+digest}
            mappings[digest]={'alias':alias,'observation_ref':deepcopy(ref),'original_context':deepcopy(context),
                'measurement_time':deepcopy(when),'reading_pointer':item['reading_pointer'],
                'reading_file_ref':deepcopy(item['reading_file_ref']),
                'population_interpretation':deepcopy(body['mapping_hypotheses'][key])}
            ids.append(digest)
        identity=body['identity_hypotheses'][key];mapping=body['mapping_hypotheses'][key]
        for name,value in [('identity',identity),('population_mapping',mapping)]:
            if value is None:missing.append(name+':'+key)
        if rounding is None:missing.append('rounding:'+key)
        combined=None if identity is None or mapping is None else {
            'id':'source_temporal_premises:'+key,'status':'proposed',
            'meaning':identity['meaning']+' '+mapping['meaning']}
        relations.append({'id':key,'kind':'stock_flow','period':deepcopy(observations[ids[1]]['type']['time']),
            'opening':ids[0],'movements':[{'observation':ids[1],'coefficient':row['lhs'][1]['coefficient']}],
            'closing':ids[2],'identity_premise':combined})
    definition={'profile':temporal.PROFILE,'observations':observations,'relations':relations}
    temporal.lower(definition,budget)
    return {'profile':PROFILE,**BOUNDARY,'request_sha256':core.digest(body),'budget':deepcopy(budget),
        'selected_relations':deepcopy(selected),'definition':definition,'source_mapping':mappings,
        'missing_hypotheses':missing,'preserved_report':report,'preserved_report_sha256':core.digest(report),
        'relation_dispositions':[{'id':r['id'],'selected':r['id'] in selected,
            'original_disposition_sha256':core.digest(r),
            'reason':'Explicit conditional temporal relation' if r['id'] in selected else
                     'Unselected; complete original disposition retained without a new identity assumption'}
            for r in report['relations']]}


def assess(body,budget):
    try:
        result=build(body,budget);assessment=temporal.assess(result['definition'],budget)
        return {**result,'status':assessment['status'],'temporal_assessment':assessment}
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError,source.ValidationError) as exc:
        return {'profile':PROFILE,**BOUNDARY,'status':'invalid','reason':str(exc)[:300]}


def verify_result(body,budget,result):
    try:
        replay=assess(body,budget)
        if replay['status']=='invalid':return result==replay
        core.need(type(result) is dict and set(result)==set(replay),'result_fields')
        for key in replay:
            if key!='temporal_assessment':core.need(result[key]==replay[key],'changed_result:'+key)
        saved,current=result['temporal_assessment'],replay['temporal_assessment']
        core.need(set(saved)==set(current),'temporal_result_fields')
        for key in current:
            if key!='joint_assessment':core.need(saved[key]==current[key],'changed_temporal_result:'+key)
        a,b=saved['joint_assessment'],current['joint_assessment']
        core.need(set(a)==set(b),'joint_result_fields')
        for key in b:
            if key not in ['witness','conflicts','solver_wall_seconds']:core.need(a[key]==b[key],'changed_joint_result:'+key)
        if 'witness' in a:temporal.check_witness(result['definition'],budget,a['witness'])
        if 'conflicts' in a:source._check_conflicts(saved['numeric_definition'],budget,a['conflicts'])
        if 'solver_wall_seconds' in a:
            wall=a['solver_wall_seconds'];core.need(type(wall) in [int,float] and 0<=wall<float('inf'),'invalid_timing')
        return True
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError):return False
