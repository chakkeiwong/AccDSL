"""Closed audit-only request bound to one reviewed native owner."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
from jsonschema import Draft202012Validator,FormatChecker
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'data/accounting-master/company-state-population-admission-20261028'))
import admission
rel=admission.rel
OWNER='CompanyOperationPathDraft/1'

def schema():
    def closed(fields):return dict(type='object',properties=fields,required=list(fields),additionalProperties=False)
    text=dict(type='string',minLength=1)
    digest=dict(type='string',pattern='^[0-9a-f]{64}$')
    query=[]
    for kind,fields in [
        ('annual_report',dict(period_start=dict(type='string',format='date',pattern='^[0-9]{4}-[0-9]{2}-[0-9]{2}$'))),
        ('event_prefix',dict(year_index=dict(type='integer',minimum=0),operation_id=text)),
        ('claim_history',dict(claim_id=text)),
        ('asset_history',dict(asset_id=text))]:
        query.append(closed(dict(id=text,kind=dict(const=kind),**fields)))
    result=closed(dict(profile=dict(const='CompanyStateInspectionRequest/1'),
        owner=text,path_sha256=digest,source_sha256=digest,
        context=closed(dict(entity=text,book=text,currency=text)),
        information=closed(dict(use=text,view=text)),
        joins=dict(type='array',items=text),
        queries=dict(type='array',minItems=1,items=dict(oneOf=query))))
    result['$schema']='https://json-schema.org/draft/2020-12/schema'
    return result

def answer(status,**kwargs):
    return dict(status=status,source_admission=False,actor_information_admission=False,
                population_complete=False,full_company_constructor=False,**kwargs)

def inspect(request,path,source):
    errors=list(Draft202012Validator(schema(),format_checker=FormatChecker()).iter_errors(request))
    if errors:return answer('invalid',reason='request_schema',path=list(errors[0].path))
    ids=[q['id'] for q in request['queries']]
    if len(set(ids))!=len(ids):return answer('invalid',reason='duplicate_query_id')
    if request['owner']!=OWNER:return answer('unsupported',reason='native_owner',requested_owner=request['owner'])
    if request['joins']:return answer('unsupported',reason='cross_profile_join',requested_joins=deepcopy(request['joins']))
    if request['information']!=dict(use='audit_only',view='archival_exogenous_stress'):
        return answer('unsupported',reason='actor_information_request')
    if request['path_sha256']!=rel.native.digest(path):return answer('invalid',reason='path_digest')
    if request['source_sha256']!=sha256(source).hexdigest():return answer('invalid',reason='source_digest')
    if not isinstance(path,dict) or path.get('profile')!=OWNER:
        return answer('invalid',reason='path_profile')
    if path.get('initial_year',{}).get('context')!=request['context']:
        return answer('invalid',reason='context_mismatch')
    admitted=admission.inspect(path,source,request['path_sha256'])
    native=admitted['native_result']
    result=answer('inspected',profile='CompanyStateInspectionResult/1',request=deepcopy(request),
        request_sha256=rel.native.digest(request),native_owner=OWNER,admission=admitted,queries=[])
    if admitted['status']=='native_refusal':
        result['status']='native_refusal'
        result['queries']=[dict(id=q['id'],kind=q['kind'],status='unresolved',reason='native_refusal') for q in request['queries']]
        return result
    population=admitted['population_inspection']
    relation=population['relationship_result'] if population is not None else None
    events={} if relation is None else {e['id']:e for e in relation['event_nodes']}
    claim_prefixes={} if relation is None else {r['event']:r['claims'] for r in relation['prefixes']}
    asset_prefixes={} if population is None else {r['event']:r['assets'] for r in population['prefixes']}
    for q in request['queries']:
        row=dict(id=q['id'],kind=q['kind'])
        if q['kind']=='annual_report':
            view=rel.native.report_view(path,native,q['period_start'])
            row.update(status=view['report']['status'] if 'report' in view else view['status'],native_view=view)
        elif population is None:
            row.update(status='unresolved',reason='opening_not_executable',
                       obligations=deepcopy(admitted.get('obligations',[])))
        elif q['kind']=='event_prefix':
            key=rel.event_key(q['year_index'],q['operation_id']);event=events.get(key)
            if event is None:row.update(status='invalid',reason='event_not_in_supplied_path')
            elif event['status']!='executed':
                row.update(status='not_executed',event=deepcopy(event),reason=event['status'])
            else:row.update(status='known_conditional',event=deepcopy(event),
                            claims=deepcopy(claim_prefixes[key]),assets=deepcopy(asset_prefixes[key]))
        else:
            claim=q['kind']=='claim_history';identity=q['claim_id' if claim else 'asset_id']
            prefixes=relation['prefixes'] if claim else population['prefixes']
            selected=[]
            for prefix in prefixes:
                state=prefix['claims'].get(identity) if claim else next((a for a in prefix['assets'] if a['id']==identity),None)
                if state is not None:selected.append(dict(event=prefix['event'],state=deepcopy(state)))
            nodes=relation['claim_nodes'] if claim else population['cohorts']
            node=next((c for c in nodes if c['id']==identity),None)
            # Unknown or never-executed origins cannot be replaced by empty real populations.
            row.update(status='known_conditional' if selected or node is not None else 'not_present_in_executed_prefix',
                identity=identity,origin=deepcopy(node['origin']) if node is not None else None,
                history=selected,coverage='supplied executed history only',actual_existence='unknown')
        result['queries'].append(row)
    return result
