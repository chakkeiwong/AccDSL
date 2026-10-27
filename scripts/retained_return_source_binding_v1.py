"""Finite synthetic source correspondence; no real filing or authority admission."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util, json, math, sys
import typed_return_transition_v1 as typed
core=typed.core
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/return-source-binding-20261024'
PACKET='data/accounting-master/company-composition-20261016/attempt-03/portable-exchanges.json'
PACKET_SHA256='690265c8b88b620ebb5de0e9aa3544428f6895e41343b6098f13ae1a72b76612'
MAX_PACKET_BYTES=8*1024*1024
PROFILE='RetainedReturnSourceBinding/1'
BOUNDARY={**typed.BOUNDARY,'scope':'exact_retained_synthetic_source_and_prefix_only'}


def strict_packet(raw):
    core.need(type(raw) is bytes and len(raw)<=MAX_PACKET_BYTES,'packet_size_limit')
    def pairs(items):
        out={}
        for key,value in items:
            core.need(key not in out,'duplicate_packet_key');out[key]=value
        return out
    def invalid_constant(value):raise core.Invalid('nonfinite_packet_number')
    packet=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=invalid_constant)
    core.need(type(packet) is dict,'packet_object')
    stack=[(packet,(),0)];count=0
    while stack:
        value,path,depth=stack.pop();count+=1
        core.need(count<=300000 and depth<=48,'packet_structure_limit')
        if type(value) is float:
            core.need(path==('build_wall_seconds',) and math.isfinite(value) and value>=0,'financial_float_forbidden')
        elif type(value) is dict:
            stack.extend((child,path+(key,),depth+1) for key,child in value.items())
        elif type(value) is list:
            stack.extend((child,path+(str(i),),depth+1) for i,child in enumerate(value))
    return packet


def helpers():
    locks=json.loads((HERE/'dependency-lock.json').read_text())
    for name,h in locks.items():
        core.need(sha256((ROOT/name).read_bytes()).hexdigest()==h,'retained_dependency_changed:'+name)
    paths=[ROOT/'data/accounting-master/company-return-schema-20261023',
           ROOT/'data/accounting-master/company-return-execution-20261024']
    prior=list(sys.path)
    try:
        sys.path[:0]=[str(p) for p in paths]
        spec=importlib.util.spec_from_file_location('bound_retained_execution_context',paths[1]/'retained_execution_context.py')
        context=importlib.util.module_from_spec(spec);spec.loader.exec_module(context)
        spec=importlib.util.spec_from_file_location('bound_retained_fixture',paths[0]/'retained_fixture.py')
        fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)
    finally:sys.path[:]=prior
    return context,fixture


def bind_and_propose(packet_raw,state_raw,state_sha256,event_raw,event_sha256):
    try:
        core.need(type(packet_raw) is bytes and len(packet_raw)<=MAX_PACKET_BYTES,'packet_size_limit')
        core.need(sha256(packet_raw).hexdigest()==PACKET_SHA256,'retained_packet_digest_mismatch')
        packet=strict_packet(packet_raw);context,fixture=helpers()
        registry=packet['record_registry'];aliases=packet['aliases']
        core.need(type(registry) is dict,'record_registry')
        for h,record in registry.items():
            core.need(typed.binding.portable.record_digest(record)==h,'source_record_digest_mismatch')
        def item(key):
            alias=aliases[key];record=registry[alias['digest']]
            core.need(alias['kind']==record['kind'] and alias['schema']==record['schema'] and record['key']==key,'source_alias_mismatch')
            return deepcopy(record['body'])
        author=fixture.from_source(packet_raw)
        core.need(context.bound_to_retained(author,packet_raw),'retained_projection_mismatch')
        path=ROOT/packet['input_snapshots']['financial_checks.py']['path']
        core.need(sha256(path.read_bytes()).hexdigest()==packet['input_snapshots']['financial_checks.py']['sha256'],'financial_method_digest')
        spec=importlib.util.spec_from_file_location('bound_retained_financial',path)
        financial=importlib.util.module_from_spec(spec);spec.loader.exec_module(financial)
        supplied_state=typed.decode(state_raw,state_sha256);supplied_event=typed.decode(event_raw,event_sha256)
        initial=item('opening')
        current=typed.structure.native.initialize(author,initial['books']['P'],initial['compound']['prior_interest_expensed'])
        retained=deepcopy(initial);prefix=[]
        def need(ok,reason,*status):
            if not ok:raise core.Invalid('retained_prefix:'+reason)
        for entry in packet['transitions']:
            key=entry['id'].removesuffix('.commit');original=item('event.'+key)
            event=context.event_for(key,original,author)
            if event['kind'] in ['settle','sell'] and event['id']==supplied_event.get('id'):
                core.need(core.canonical(supplied_event)==core.canonical(event),'source_event_correspondence')
                core.need(core.canonical(supplied_state)==core.canonical(current),'source_prefix_state_correspondence')
                result=typed.propose(state_raw,state_sha256,event_raw,event_sha256)
                if result['status']!='proposed':return result
                return {**BOUNDARY,'profile':PROFILE,'status':'source_bound_proposal',
                        'packet_sha256':PACKET_SHA256,'opening_record':deepcopy(aliases['opening']),
                        'event_record':deepcopy(aliases['event.'+key]),'prefix':prefix,
                        'recomputed_before_sha256':core.digest(current),
                        'result':result,'meaning':'exact finite synthetic source projection and recomputed prefix; no external authority'}
            adapter=context.adapter_for(retained,financial) if event['kind']=='surrounding' else None
            p=typed.structure.native.propose(current,event,adapter)
            after=typed.structure.native.apply(current,event,p,adapter)
            computed,_,_=financial.derive(retained,original,need)
            core.need({k:typed.structure.native.fmt(v) for k,v in computed['books']['P'].items()}==after['balances'],'prefix_recomputed_book_mismatch')
            prefix.append({'source_event':deepcopy(aliases['event.'+key]),'event_sha256':core.digest(event),
                           'before_sha256':core.digest(current),'after_sha256':core.digest(after)})
            current=after;retained=computed
        return {**BOUNDARY,'status':'unsupported','reason':'selected_event_not_in_retained_packet'}
    except typed.structure.native.Rejected as exc:
        return {**BOUNDARY,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,RecursionError,OverflowError,AttributeError) as exc:
        return {**BOUNDARY,'status':'invalid','reason':str(exc)[:300]}
