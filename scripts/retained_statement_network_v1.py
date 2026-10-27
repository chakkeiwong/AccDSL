"""Conditional retained statement network; explicit scope and unresolved sources."""
from copy import deepcopy
from fractions import Fraction as Q
import joint_source_relation_binding_v1 as source
import temporal_measurement_constraints_v1 as temporal

core=temporal.core
PROFILE='RetainedStatementNetwork/1'
KINDS={'snapshot_sum','period_sum','same_period_measurement','same_date_endpoint','stock_flow_bridge'}
BRIDGE_PAIRS={
    'capital':('equity.capital_opening','equity.capital_closing','reported_equity_capital'),
    'retained':('equity.retained_opening','equity.retained_closing','reported_retained_earnings'),
    'aoci':('equity.aoci_opening','equity.aoci_closing','reported_accumulated_oci'),
    'cash_closing':('cash_flow.opening','cash_flow.closing','cash_flow_statement_cash_population'),
    'whole_equity_bridge':('equity.opening','equity.closing','reported_total_equity')}
BOUNDARY={**temporal.BOUNDARY,'scope':'explicit_selected_retained_statement_network_only'}


def classification(row):
    if row['kind'] not in KINDS:
        return 'outside_relation_forms'
    if row['omitted_source_rows']:
        return 'omitted_source_rows_require_separate_interpretation'
    return 'supported'


def identity_hypothesis(key):
    core.text(key,'relation_id')
    return {'id':'underlying_statement_identity:'+key,'status':'proposed',
            'meaning':'The unrounded measurements satisfy all exact retained signed terms of '+key+'.'}


def mapping_hypothesis(key):
    core.text(key,'relation_id')
    return {'id':'statement_population_mapping:'+key,'status':'proposed',
            'meaning':'For '+key+', the retained operands describe the quantities and populations needed for this relation at their exact source times; this supplies no legal-book mapping or source admission.'}


def supported_selection(request):
    return [r['id'] for r in request['relations'] if classification(r)=='supported']


def numeric_selection(request,report):
    """Explicit authoring diagnostic, never an automatic fallback in assess."""
    return [r['id'] for r in request['relations'] if classification(r)=='supported'
            and all(report['observations'][t['alias']]['observation']['record']['body']['value']['tag']=='known_displayed'
                    for t in r['lhs']+r['rhs'])]


def fixture(selected=None,assume=False):
    request=source.statement.fixture()
    selected=supported_selection(request) if selected is None else list(selected)
    return {'profile':PROFILE,'statement_request':request,'selected_relations':selected,
            'rounding_hypothesis':source.rounding_hypothesis() if assume else None,
            'identity_hypotheses':{k:identity_hypothesis(k) if assume else None for k in selected},
            'mapping_hypotheses':{k:mapping_hypothesis(k) if assume else None for k in selected}}


def _quantity(alias,row_id):
    group=alias.split('.',1)[0]
    for opening,closing,quantity in BRIDGE_PAIRS.values():
        if alias in [group+'.'+opening,group+'.'+closing]:return quantity
    return 'retained_measurement:'+row_id


def build(body,budget):
    core.need(len(core.canonical(body))<=core.MAX_BYTES,'request_size_limit')
    core.closed(body,['profile','statement_request','selected_relations','rounding_hypothesis',
                      'identity_hypotheses','mapping_hypotheses'],'statement_network_request')
    core.need(body['profile']==PROFILE,'profile')
    selected=body['selected_relations'];core.identifiers(selected,'selected_relations',nonempty=True)
    core.need(len(selected)<=143,'selection_limit')
    rounding=body['rounding_hypothesis']
    core.need(rounding is None or rounding==source.rounding_hypothesis(),'rounding_hypothesis_mismatch')
    for field,builder in [('identity_hypotheses',identity_hypothesis),('mapping_hypotheses',mapping_hypothesis)]:
        items=body[field];core.need(type(items) is dict and set(items)==set(selected),'premise_selection_mismatch')
        for key,value in items.items():core.need(value is None or value==builder(key),'premise_semantics_mismatch:'+key)
    base=source.build({'profile':source.PROFILE,'statement_request':body['statement_request'],
        'selected_relations':[],'rounding_hypothesis':None,'identity_hypotheses':{}},budget)
    report=base['preserved_report'];rows={r['id']:r for r in body['statement_request']['relations']}
    supported=supported_selection(body['statement_request'])
    core.need(set(selected)<=set(supported),'unsupported_selection_or_uninterpreted_omission')
    dispositions={r['id']:r for r in report['relations']}
    observations,relations,mappings,unresolved,missing={},[],{},[],[]
    for key in selected:
        row=rows[key]
        core.need(row['comparison']=='terms','independent_target_required')
        core.need(dispositions[key]['context_check']['status']=='compatible_for_declared_displayed_relation',
                  'source_context_mismatch')
        terms=[];alias_ids={}
        for side,sign in [('lhs',Q(1)),('rhs',Q(-1))]:
            for term in row[side]:
                alias=term['alias'];item=report['observations'][alias]
                original=item['observation'];declaration=item['declaration'];ref=declaration['observation_ref']
                digest=ref['digest'];context=original['context'];when=declaration['measurement_time']
                core.need(context['unit']==declaration['unit']=='USD million','unsupported_unit')
                core.need(ref==original['ref'],'observation_reference_mismatch')
                value_context={k:v for k,v in context.items() if k not in ['unit','period','measurement_kind']}
                value=original['record']['body']['value'];interval=None
                if value['tag']=='known_displayed' and rounding is not None:
                    amount=value['amount'];displayed=Q(int(amount['n']),int(amount['d']))
                    interval=source.statement.state.rounding_interval(displayed,Q(rounding['quantum']))
                definition={'type':{'value_type':{'kind':'rational','context':value_context,
                    'dimensions':{'currency:USD':1},'scale':'1000000/1'},'time':deepcopy(when),
                    'quantity':_quantity(alias,original['record']['body']['row_id'])},'interval':interval,
                    'interval_premise':None if rounding is None else {k:rounding[k] for k in ['id','status','meaning']},
                    'source_ref':ref['schema']+':'+digest}
                core.need(digest not in observations or observations[digest]==definition,'shared_observation_conflict')
                observations[digest]=definition
                if digest not in mappings:
                    mappings[digest]={'observation_ref':deepcopy(ref),'aliases':[],
                        'original_context':deepcopy(context),'measurement_time':deepcopy(when),
                        'reading_pointer':item['reading_pointer'],'reading_file_ref':deepcopy(item['reading_file_ref']),
                        'literal':original['record']['body']['literal'],'relation_ids':[]}
                mapping=mappings[digest]
                if alias not in mapping['aliases']:mapping['aliases'].append(alias)
                if key not in mapping['relation_ids']:mapping['relation_ids'].append(key)
                if value['tag']!='known_displayed':
                    finding={'observation':digest,'alias':alias,'relation_id':key,'reason':'nonnumeric_source_measurement',
                             'literal':original['record']['body']['literal'],'source_value':deepcopy(value)}
                    if finding not in unresolved:unresolved.append(finding)
                coefficient=sign*temporal.joint.rational(term['coefficient'])
                terms.append({'observation':digest,'coefficient':f'{coefficient.numerator}/{coefficient.denominator}'})
                alias_ids[alias]=digest
        identity=body['identity_hypotheses'][key];mapping=body['mapping_hypotheses'][key]
        for name,value in [('identity',identity),('population_mapping',mapping)]:
            if value is None:missing.append(name+':'+key)
        combined=None if identity is None or mapping is None else {
            'id':'statement_network_premises:'+key,'status':'proposed','meaning':identity['meaning']+' '+mapping['meaning']}
        if row['kind']=='stock_flow_bridge':
            group,bridge=key.split('.',1)
            core.need(bridge in BRIDGE_PAIRS,'unsupported_bridge_identity')
            open_id,close_id,_=BRIDGE_PAIRS[bridge]
            opening,closing=group+'.'+open_id,group+'.'+close_id
            core.need(row['lhs'][0]=={'alias':opening,'coefficient':'1/1'}
                      and row['rhs']==[{'alias':closing,'coefficient':'1/1'}],'bridge_endpoint_terms')
            moves=[{'observation':alias_ids[t['alias']],'coefficient':t['coefficient']} for t in row['lhs'][1:]]
            period=observations[moves[0]['observation']]['type']['time']
            relation={'id':key,'kind':'stock_flow','period':deepcopy(period),'opening':alias_ids[opening],
                      'movements':moves,'closing':alias_ids[closing],'identity_premise':combined}
        else:
            relation={'id':key,'kind':'same_time','terms':terms,'rhs':'0/1','identity_premise':combined}
        relations.append(relation)
    if rounding is None:missing.append('rounding_hypothesis')
    definition={'profile':temporal.PROFILE,'observations':observations,'relations':relations}
    temporal.lower(definition,budget)
    exclusions=[]
    for row in body['statement_request']['relations']:
        category=classification(row)
        exclusions.append({'id':row['id'],'classification':category,'selected':row['id'] in selected,
            'status':'selected' if row['id'] in selected else 'supported_unselected' if category=='supported' else category,
            'original_disposition_sha256':core.digest(dispositions[row['id']]),
            'omitted_source_rows':deepcopy(row['omitted_source_rows'])})
    return {'profile':PROFILE,**BOUNDARY,'request_sha256':core.digest(body),'budget':deepcopy(budget),
        'selected_relations':deepcopy(selected),'definition':definition,'source_mapping':mappings,
        'preserved_report':report,'preserved_report_sha256':core.digest(report),
        'missing_hypotheses':missing,'unresolved_measurements':unresolved,'relation_dispositions':exclusions,
        'selection_coverage':{'total_source_relations':len(rows),'supported_relations':len(supported),
            'selected_relations':len(selected),'selected_observations':len(observations),
            'all_supported_selected':set(selected)==set(supported),
            'excluded_supported_relations':[k for k in supported if k not in selected],
            'whole_statement_history_complete':False}}


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
        a,b=result['temporal_assessment'],replay['temporal_assessment']
        core.need(set(a)==set(b),'temporal_result_fields')
        for key in b:
            if key!='joint_assessment':core.need(a[key]==b[key],'changed_temporal_result:'+key)
        saved,current=a['joint_assessment'],b['joint_assessment']
        core.need(set(saved)==set(current),'joint_fields')
        for key in current:
            if key not in ['witness','conflicts','solver_wall_seconds']:core.need(saved[key]==current[key],'changed_joint_result:'+key)
        if 'witness' in saved:temporal.check_witness(result['definition'],budget,saved['witness'])
        if 'conflicts' in saved:source._check_conflicts(a['numeric_definition'],budget,saved['conflicts'])
        if 'solver_wall_seconds' in saved:
            elapsed=saved['solver_wall_seconds'];core.need(type(elapsed) in [int,float] and 0<=elapsed<float('inf'),'invalid_timing')
        return True
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError):return False
