"""Joined documentary semantics; no portable admission or durable writes."""
from copy import deepcopy
from pathlib import Path
import hashlib
import importlib.util
import sys
from jsonschema import Draft202012Validator, FormatChecker

HERE=Path(__file__).resolve().parent
OPS=HERE.parent/'company-operations-20261023'
PATH=HERE.parent/'company-path-20261023'
sys.path.insert(0,str(OPS))
from operations import execute as execute_operations, schema as operations_schema
from operations import wire, canonical, digest, closed, result


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


reports=load('joined_operation_reports',OPS/'reporting.py')
annual_path=load('joined_annual_path_helpers',PATH/'path_semantics.py')


def schema():
    first=operations_schema();p=first['properties']
    keys=['name','assumption','period','inventory','depreciation_method','debt','loan','tax','operations']
    continuation={k:deepcopy(p[k]) for k in keys}
    facility=deepcopy(p['facility']['properties']);facility.pop('drawn')
    continuation['facility']=closed(facility)
    out=closed({'profile':{'const':'CompanyOperationPathDraft/1'},
        'name':{'type':'string','minLength':1},'assumption':{'type':'string','minLength':1},
        'initial_year':first,'continuations':{'type':'array','minItems':1,'items':closed(continuation)}})
    out['$schema']='https://json-schema.org/draft/2020-12/schema'
    return out


def execute(path,source):
    errors=list(Draft202012Validator(schema(),format_checker=FormatChecker()).iter_errors(path))
    if errors:return result('invalid',reason='path_schema',path=list(errors[0].path))
    definitions=[path['initial_year']]+path['continuations']
    if len({d['name'] for d in definitions})!=len(definitions):return result('invalid',reason='duplicate_year_name')
    if any(a['period']['end_exclusive']!=b['period']['start'] for a,b in zip(definitions,definitions[1:])):
        return result('invalid',reason='nonconsecutive_periods')
    identity={'branch_sha256':digest(path),'source_sha256':hashlib.sha256(source).hexdigest()}
    years=[];memory=None;predecessor=None
    for i,definition in enumerate(definitions):
        body=deepcopy(definition)
        if i==0:
            raw=source
            origin={'kind':'pinned_historical_opening','source_sha256':identity['source_sha256'],
                    'opening_digest':body['opening_digest']}
        else:
            if body['facility']['id']!=memory['facility_id']:
                return result('invalid',reason='facility_identity_changed',years=years,stopped_index=i,**identity)
            raw,od=annual_path.opening_adapter(memory,predecessor)
            body.update(profile='CompanyOperationsDraft/1',
                source={'path':'internal-conditional-state:'+predecessor,'sha256':hashlib.sha256(raw).hexdigest()},
                opening_digest=od,context=deepcopy(memory['context']),information=memory['information'],
                assets=deepcopy(memory['assets']),opening_claims=[{'id':k,'ledger':c['ledger'],
                    'amount':wire(c['outstanding'])} for k,c in memory['claims'].items()])
            body['facility']['drawn']=wire(memory['facility_drawn'])
            origin={'kind':'conditional_predecessor','result_sha256':predecessor,
                    'closing_memory_sha256':digest(memory),'historical_admission':False}
        run=execute_operations(body,raw);report=reports.build_report(body,run,raw)
        if report['status']=='invalid' and run['status']!='invalid':
            return result('invalid',reason='annual_report',detail=report,years=years,**identity)
        record={'index':i,'name':definition['name'],'period':body['period'],
            'definition_sha256':digest(definition),'effective_input_sha256':digest(body),
            'origin':origin,'run':run,'report':report}
        if run['status']=='complete_conditional':
            new_memory=annual_path.closing_memory(body,run)
            if memory is not None:
                new_memory['claims']=annual_path.carry_lifetime_claims(memory['claims'],run['claims'])
            record['closing_memory']=new_memory
        record['result_sha256']=digest(record);years.append(record)
        if run['status']!='complete_conditional':
            return result('partial',years=years,stopped_index=i,stopped_status=run['status'],
                unexecuted=[{'index':j,'period':d['period'],'status':'unresolved','reason':'predecessor_incomplete'}
                    for j,d in enumerate(definitions) if j>i],**identity)
        memory,predecessor=new_memory,record['result_sha256']
    return result('complete_conditional',years=years,unexecuted=[],**identity)


def verify_chain(path,run):
    if list(Draft202012Validator(schema(),format_checker=FormatChecker()).iter_errors(path)):return False
    if run.get('branch_sha256')!=digest(path) or run.get('source_sha256')!=path['initial_year']['source']['sha256']:return False
    definitions=[path['initial_year']]+path['continuations'];years=run.get('years',[])
    if not years or len(years)>len(definitions):return False
    if run['status']=='complete_conditional':
        if len(years)!=len(definitions) or run.get('unexecuted')!=[]:return False
    elif run['status']=='partial':
        expected=[{'index':j,'period':d['period'],'status':'unresolved','reason':'predecessor_incomplete'}
                  for j,d in enumerate(definitions) if j>=len(years)]
        if run.get('stopped_index')!=len(years)-1 or run.get('unexecuted')!=expected:return False
    else:return False
    for i,y in enumerate(years):
        if y.get('result_sha256')!=digest({k:v for k,v in y.items() if k!='result_sha256'}):return False
        if y['index']!=i or y['period']!=definitions[i]['period'] or y['definition_sha256']!=digest(definitions[i]):return False
        if y['effective_input_sha256']!=y['run'].get('input_sha256'):return False
        if y['run']['status']!='invalid':
            if y['report'].get('run_sha256')!=digest(y['run']) or y['report'].get('input_sha256')!=y['effective_input_sha256']:return False
            if y['report'].get('source_sha256')!=y['run'].get('source_sha256'):return False
        complete=y['run']['status']=='complete_conditional'
        if complete!=('closing_memory' in y):return False
        if (i<len(years)-1 or run['status']=='complete_conditional') and not complete:return False
        if i==len(years)-1 and run['status']=='partial' and (complete or run['stopped_status']!=y['run']['status']):return False
        if i==0:
            if y['origin']!={'kind':'pinned_historical_opening','source_sha256':run['source_sha256'],'opening_digest':path['initial_year']['opening_digest']}:return False
        elif y['origin']!={'kind':'conditional_predecessor','result_sha256':years[i-1]['result_sha256'],
            'closing_memory_sha256':digest(years[i-1]['closing_memory']),'historical_admission':False}:return False
    return True


def report_view(path,run,period_start):
    if not verify_chain(path,run):return result('invalid',reason='path_result_binding')
    matches=[y for y in run['years'] if y['period']['start']==period_start]
    if matches:
        y=matches[0]
        return {'branch_sha256':run['branch_sha256'],'year_result_sha256':y['result_sha256'],
                'origin':deepcopy(y['origin']),'report':deepcopy(y['report'])}
    requested=[path['initial_year']]+path['continuations']
    return result('unresolved' if any(d['period']['start']==period_start for d in requested) else 'invalid',reason='period_not_executed')


def revise(path,source,index,replacement,reason):
    if list(Draft202012Validator(schema(),format_checker=FormatChecker()).iter_errors(path)) or not isinstance(replacement,dict):return result('invalid',reason='revision_schema')
    definitions=[path['initial_year']]+path['continuations']
    if type(index) is not int or not 0<=index<len(definitions) or not isinstance(reason,str) or not reason.strip():return result('invalid',reason='revision_request')
    keys=['source','opening_digest','context','period','information','opening_claims','assets'] if index==0 else ['period']
    if any(replacement.get(k)!=definitions[index][k] for k in keys):return result('invalid',reason='revision_changes_opening_or_period')
    child=deepcopy(path)
    if index==0:child['initial_year']=deepcopy(replacement)
    else:child['continuations'][index-1]=deepcopy(replacement)
    if digest(child)==digest(path):return result('invalid',reason='unchanged_revision')
    return {'kind':'conditional_assumption_revision','parent_input_sha256':digest(path),
        'child_input_sha256':digest(child),'changed_year_index':index,'reason':reason,
        'historical_restatement':False,'path':child,'result':execute(child,source)}
