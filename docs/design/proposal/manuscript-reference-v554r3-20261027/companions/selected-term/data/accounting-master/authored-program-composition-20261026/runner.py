"""Finite authored programs with explicit registries and native statement owners."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'authored-method-registry-20261026'))
import registry as methods
import company_book_reports_v1 as reports
import company_book_carry_v1 as carry
core=methods.core;base=methods.base;typed=methods.frontend.v2;digest=core.digest
PROFILE='AuthoredCompanyProgram/1';FLAGS=reports.FLAGS;MAX_COMMANDS=64;MAX_TRACE_BYTES=8*1024*1024

def identity(command):return command['event']['id'] if command['kind']=='event' else command['id']
def validate(body):
    core.need(len(core.canonical(body))<=core.MAX_BYTES,'program_size_limit')
    base.closed(body,['profile','name','opening','schemas','mapping','memory_definition','registries','commands'])
    core.need(body['profile']==PROFILE,'program_profile');base.text(body['name'],'program_name')
    typed.typed_book(body['opening'],body['memory_definition'],body['schemas'])
    core.need(type(body['registries']) is dict and 0<len(body['registries'])<=MAX_COMMANDS,'registry_population')
    for key,registry in body['registries'].items():
        core.need(key==digest(registry),'registry_digest');base.closed(registry,['profile','context','entries'])
        core.need(registry['profile']==methods.REGISTRY,'registry_profile')
        core.need(registry['context']==body['opening']['context'],'registry_context')
        entries=registry['entries'];core.need(type(entries) is dict and 0<len(entries)<=methods.MAX_ENTRIES,'registry_entry_limit')
        for name,entry in entries.items():
            base.text(name,'method_key');profile=entry.get('transition_profile')
            core.need(profile in methods.frontend.ENGINES,'transition_profile')
            base.closed(entry,methods.FIELDS+(['memory_definition'] if profile==typed.PROFILE else []))
            core.need(entry['method_sha256']==digest(entry['method']),'method_digest')
            core.need(type(entry['source']) is str and sha256(entry['source'].encode()).hexdigest()==entry['source_sha256'],'source_digest')
            lowered=methods.frontend.lower(entry['source'])
            core.need(lowered['method']==entry['method'] and lowered['transition_profile']==profile,'source_correspondence')
            if profile==typed.PROFILE:core.need(entry['memory_definition']==body['memory_definition'],'program_memory_definition')
            for h,shape in entry['schemas'].items():
                core.need(h==digest(shape),'schema_digest')
                if h in body['schemas']:core.need(core.canonical(shape)==core.canonical(body['schemas'][h]),'program_schema_correspondence')
    commands=body['commands'];core.need(type(commands) is list and 0<len(commands)<=MAX_COMMANDS,'command_limit')
    for command in commands:
        base.memory.bounded(command);core.need(type(command) is dict,'command_record');kind=command.get('kind')
        if kind=='event':
            base.closed(command,['kind','registry_sha256','method_key','event'])
            core.need(command['registry_sha256'] in body['registries'],'missing_registry')
            base.text(command['method_key'],'method_key');base.closed(command['event'],['id','date','inputs'])
            core.scalar(command['event']['date'],'date');core.need(type(command['event']['inputs']) is dict,'event_inputs')
        else:
            core.need(kind in ['report','carry'],'command_kind');fields=['kind','id','cutoff','equity_movements','notes']
            if kind=='carry':fields+=['retained_account','next_end_exclusive','memory_policies']
            base.closed(command,fields);core.scalar(command['cutoff'],'date')
            core.need(type(command['equity_movements']) is list and type(command['notes']) is list,'report_lists')
        base.text(identity(command),'command_id')

def invalid(exc):return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:300] or type(exc).__name__}
def run(body):
    try:validate(body)
    except Exception as exc:return invalid(exc)
    current=deepcopy(body['opening']);opening=deepcopy(current)
    trace=[];output_reports=[];archives=[];used=set(current['seen']);stop=None;trace_bytes=2
    for index,command in enumerate(body['commands']):
        request=None;result=None
        try:
            key=identity(command);core.need(key not in used,'duplicate_command_identity')
            next_opening=opening;kind=command['kind']
            typed.typed_book(current,body['memory_definition'],body['schemas'])
            if kind=='event':
                registry=body['registries'][command['registry_sha256']]
                request={'profile':methods.PROFILE,'expected_state_sha256':digest(current),
                    'expected_registry_sha256':command['registry_sha256'],'registry':deepcopy(registry),
                    'method_key':command['method_key'],'event':deepcopy(command['event'])}
                result=methods.propose(current,request);success=result['status']=='proposed'
                after=result['transition']['after'] if success else current
            else:
                cutoff=command['cutoff'];core.need(current['date']<=cutoff<current['period']['end_exclusive'],'cutoff_chronology')
                observed=deepcopy(current);observed['date']=cutoff
                request=reports.request(opening,observed,body['schemas'],body['mapping'],command['equity_movements'],command['notes'])
                if kind=='report':result=reports.report(request);success=result['status']=='reported';after=observed
                else:
                    request=carry.request(request,key,command['retained_account'],command['next_end_exclusive'],command['memory_policies'])
                    result=carry.propose(request);success=result['status']=='proposed'
                    after=result['next_opening'] if success else current;next_opening=after if success else opening
            if success:typed.typed_book(after,body['memory_definition'],body['schemas'])
            item={'index':index,'command':deepcopy(command),'request':request,'result':result,
                'before_sha256':digest(current),'after_sha256':digest(after if success else current),
                'opening_before_sha256':digest(opening),'opening_after_sha256':digest(next_opening)}
            size=len(core.canonical(item))
            if trace_bytes+size>MAX_TRACE_BYTES:
                stop={'index':index,'status':'invalid','reason':'trace_size_limit','before_sha256':digest(current)};break
            if not success:
                stop={**item,'status':result['status'],'reason':result.get('reason',result.get('transition',{}).get('reason','engine_refusal'))};break
            trace.append(item);trace_bytes+=size;used.add(key);current=deepcopy(after);opening=deepcopy(next_opening)
            if kind in ['report','carry']:
                output_reports.append({'id':key,'result':deepcopy(result if kind=='report' else result['report'])})
            if kind=='carry':archives.append({'id':key,'archive':deepcopy(result['archive'])})
        except Exception as exc:
            stop={'index':index,'status':'invalid','reason':str(exc)[:300],'before_sha256':digest(current),'request':request,'result':result};break
    return {'profile':PROFILE,**FLAGS,'status':'stopped_provisional' if stop else 'complete_provisional',
        'program_sha256':digest(body),'current':current,'opening':opening,'trace':trace,'stop':stop,
        'remaining_commands':deepcopy(body['commands'][len(trace):]),'reports':output_reports,'archives':archives,
        'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope':'Finite explicitly authored methods and native reports/carry; no admission or durability'}

def verify(body,result):
    try:
        core.need(len(core.canonical(result))<=MAX_TRACE_BYTES+2*core.MAX_BYTES,'result_size_limit')
        return core.canonical(run(body))==core.canonical(result)
    except Exception:return False
