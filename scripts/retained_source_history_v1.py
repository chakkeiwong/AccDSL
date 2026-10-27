"""Bind real retained measurements to supplied, explicitly conditional histories.

Each source bridge retains its own context. No transaction, account or cash
classification is inferred, and feasibility never admits an actual history.
"""
from copy import deepcopy
import retained_temporal_source_binding_v1 as source
import typed_history_measurement_attachment_v1 as attachment

core = attachment.core
PROFILE = 'RetainedSourceHistoryAttachment/1'
BOUNDARY = {**attachment.BOUNDARY, 'scope':'selected_source_bound_conditional_histories_only',
            'whole_source_compatibility':'unresolved', 'joint_cross_context_history':False}


def validate_request(body):
    core.need(len(core.canonical(body)) <= core.MAX_BYTES, 'request_size_limit')
    core.closed(body, ['profile','source_request','histories'], 'source_history_request')
    core.need(body['profile'] == PROFILE, 'profile')
    request = body['source_request']
    core.need(type(request) is dict, 'source_request')
    selected = request.get('selected_relations')
    core.identifiers(selected, 'selected_relations', nonempty=True)
    core.need(set(selected) <= set(source.SUPPORTED), 'unsupported_source_relation')
    histories = body['histories']
    core.need(type(histories) is dict and set(histories)==set(selected), 'complete_history_selection')
    for row in histories.values():
        core.closed(row, ['history','bindings'], 'supplied_history')
        core.need(type(row['bindings']) is dict, 'bindings')


def definitions(body, source_result):
    """Compose only from an internally recomputed or verified source result."""
    out = {}
    measurements = source_result['definition']
    relations = {row['id']:row for row in measurements['relations']}
    for name in body['source_request']['selected_relations']:
        row = relations[name]
        ids = [row['opening'], *[m['observation'] for m in row['movements']], row['closing']]
        supplied = body['histories'][name]
        core.need(set(supplied['bindings'])==set(ids), 'complete_bridge_bindings:'+name)
        out[name] = {'profile':attachment.PROFILE, 'history':deepcopy(supplied['history']),
            'measurements':{'profile':attachment.temporal.PROFILE,
                'observations':{k:deepcopy(measurements['observations'][k]) for k in ids},
                'relations':[deepcopy(row)]},
            'bindings':deepcopy(supplied['bindings']),
            'obligations':[
                {'id':'actual_history:'+name,
                 'meaning':'Supplied templates, dates, domains and field mappings do not identify actual company transactions or legal accounts.',
                 'affects':['actual_history','execution']},
                {'id':'unselected_disclosures:'+name,
                 'meaning':'Only the selected cash bridge constrains this history; all other retained disclosure dispositions remain unresolved for it.',
                 'affects':['whole_source_compatibility','execution']}]}
    return out


def assemble(body, budget, source_result, attachments):
    statuses = {k:r['status'] for k,r in attachments.items()}
    source_status = source_result['status']
    if any(s=='invalid' for s in statuses.values()):
        status = 'invalid_history_attachment'
    elif source_status=='conditionally_infeasible' or any(s=='conditionally_infeasible' for s in statuses.values()):
        status = 'supplied_history_incompatible'
    elif source_status=='unresolved' or any(s=='unresolved' for s in statuses.values()):
        status = 'unresolved'
    elif source_status in ['unknown','unsupported'] or any(s in ['unknown','unsupported'] for s in statuses.values()):
        status = 'unknown'
    else:
        core.need(all(s=='candidate_attachment_with_unresolved_obligations' for s in statuses.values()),
                  'unexpected_attachment_status')
        status = 'conditional_candidates_with_unresolved_facts'
    return {'profile':PROFILE, **BOUNDARY, 'request_sha256':core.digest(body),
        'budget':deepcopy(budget), 'status':status, 'source_result':deepcopy(source_result),
        'attachments':deepcopy(attachments), 'attachment_statuses':statuses, 'source_status':source_status,
        'source_observation_count':len(source_result['preserved_report']['observations']),
        'source_relation_count':len(source_result['preserved_report']['relations']),
        'selection':{k:list(v['bindings']) for k,v in body['histories'].items()},
        'interpretation':'Each supplied history is tested against its selected source bridge; no cross-context merge or whole-filing compatibility is established.'}


def invalid(exc):
    return {'profile':PROFILE, **BOUNDARY, 'status':'invalid', 'reason':str(exc)[:300]}


def assess(body, budget):
    try:
        validate_request(body)
        retained = source.assess(body['source_request'], attachment.measurement_budget(budget))
        core.need(retained['status']!='invalid', 'invalid_source:'+retained.get('reason',''))
        defs = definitions(body, retained)
        results = {k:attachment.assess(d,budget) for k,d in defs.items()}
        return assemble(body,budget,retained,results)
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError) as exc:
        return invalid(exc)


def verify_result(body, budget, result):
    try:
        if result.get('status')=='invalid': return result==assess(body,budget)
        validate_request(body)
        retained = result['source_result']
        core.need(source.verify_result(body['source_request'],attachment.measurement_budget(budget),retained), 'source_replay')
        core.need(retained['status']!='invalid', 'invalid_source_result')
        defs = definitions(body,retained)
        core.need(set(result['attachments'])==set(defs), 'attachment_result_selection')
        for key, definition in defs.items():
            core.need(attachment.verify_result(definition,budget,result['attachments'][key]),
                      'history_replay:'+key)
        expected = assemble(body,budget,retained,result['attachments'])
        return result==expected
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError):
        return False
