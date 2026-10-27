"""Finite, read-only dependency analysis of exactly imported native exchanges."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
sys.path.insert(0,str(ROOT/'data/accounting-master/profile-publication-effects-20261026'))
import method_requirement_text_v1 as syntax
from descriptor import Descriptor, Refusal, canonical, refs

PROFILE='RetainedProfileComposition/1'
class Invalid(ValueError):pass
def need(value,reason):
    if not value:raise Invalid(reason)
def closed(value,keys,reason):need(type(value) is dict and set(value)==set(keys),reason)
def word(value):need(type(value) is str and 0<len(value)<=200 and not any(ord(c)<32 for c in value),'invalid_name')
def digest(value):need(type(value) is str and re.fullmatch('[a-f0-9]{64}',value) is not None,'invalid_digest')
def validate(plan):
    closed(plan,['profile','name','stages','dependencies'],'plan_fields');need(plan['profile']==PROFILE,'plan_profile');word(plan['name'])
    need(type(plan['stages']) is list and 1<=len(plan['stages'])<=100,'stage_limit')
    need(type(plan['dependencies']) is list and len(plan['dependencies'])<=400,'dependency_limit')
    ids=[]
    for stage in plan['stages']:
        closed(stage,['id','packet_sha256','exchange_id'],'stage_fields')
        word(stage['id']);word(stage['exchange_id']);digest(stage['packet_sha256']);ids.append(stage['id'])
    need(len(ids)==len(set(ids)),'duplicate_stage')
    edges=set()
    for edge in plan['dependencies']:
        closed(edge,['from','to','relation','produced_path','consumed_path'],'dependency_fields')
        need(edge['from'] in ids and edge['to'] in ids,'missing_dependency_stage')
        need(edge['relation'] in {'sequence','state','receipt'},'unsupported_relation')
        # Declared stages form the topological execution order.
        need(ids.index(edge['from'])<ids.index(edge['to']),'dependency_cycle_or_order')
        for key in ('produced_path','consumed_path'):
            path=edge[key];need(type(path) is list and len(path)<=4,'invalid_path')
            for item in path:word(item)
        if edge['relation']!='state':need(not edge['produced_path'] and not edge['consumed_path'],'unexpected_path')
        else:need(len(edge['produced_path'])>=2 and len(edge['consumed_path'])>=2,'state_path_required')
        encoded=canonical(edge);need(encoded not in edges,'duplicate_dependency');edges.add(encoded)
    need(len(canonical(plan))<=100000,'plan_size_limit')

class Library:
    def __init__(self):
        self.lock=json.loads((HERE/'source-lock.json').read_text())
        for path,h in self.lock['files'].items():need(sha256((ROOT/path).read_bytes()).hexdigest()==h,'source_lock_changed:'+path)
        self.entries={};self.packets={};self.readers={};self.exchanges={}
        for entry in self.lock['native_profiles']:
            h=entry['files'][entry['packet']];packet=json.loads((ROOT/entry['packet']).read_text())
            self.entries[h]=entry;self.packets[h]=packet;self.readers[h]=Descriptor(packet,entry)
            self.exchanges[h]={x['id']:x for x in packet['exchanges']}
    def select(self,stage):
        key=stage['packet_sha256'];need(key in self.entries,'unresolved_packet_import')
        need(stage['exchange_id'] in self.exchanges[key],'unresolved_exchange_import')
        reader=self.readers[key];exchange=self.exchanges[key][stage['exchange_id']]
        return reader,exchange,reader.describe(exchange)

def path_value(world,path):
    need(path[0] in {'heads','group_heads','accounting_heads','legal_heads'},'unsupported_head_path')
    value=world
    for key in path:
        need(type(value) is dict and key in value,'missing_head_path');value=value[key]
    need(type(value) is dict and set(value)=={'kind','schema','digest'},'path_not_state_reference')
    return value

def requested_heads(reader,request):
    if reader.name=='insurance':return list(request['expected_heads'].values())
    head=request['expected_head']
    return [head['state_ref'] if 'state_ref' in head else head]

def assess(plan,library):
    validate(plan);stages={};findings=[];publications=set()
    for stage in plan['stages']:
        reader,exchange,d=library.select(stage);request=reader.body(exchange['request_ref'])
        stage_info={'descriptor':d,'view_ref':deepcopy(request['view_ref']),
            'context_ref':deepcopy(request.get('context_ref')),'signature_ref':deepcopy(request.get('signature_ref'))}
        stages[stage['id']]={'reader':reader,'exchange':exchange,'description':d,'info':stage_info}
        if d['publication_knowledge']=='unknown':
            findings.append({'stage':stage['id'],'status':'unresolved','reason':'acknowledgement_unknown'})
        elif d['disposition']=='rejected':
            findings.append({'stage':stage['id'],'status':'invalid','reason':'refused_stage_unavailable'})
        elif d['disposition']=='partial':
            findings.append({'stage':stage['id'],'status':'unresolved','reason':'native_partial_result'})
        if d['effects'] and d['effects']['record_publication']:
            identity=canonical([d['profile_ref'],d['identity']])
            if identity in publications:findings.append({'stage':stage['id'],'status':'invalid','reason':'duplicate_publication_decision'})
            publications.add(identity)
    for edge in plan['dependencies']:
        a,b=stages[edge['from']],stages[edge['to']];da,db=a['description'],b['description']
        status,reason='compatible','exact_native_dependency'
        evidence={}
        if da['publication_knowledge']=='unknown' or db['publication_knowledge']=='unknown':
            status,reason='unresolved','acknowledgement_unknown'
        elif da['disposition']=='rejected' or db['disposition']=='rejected':
            status,reason='invalid','refused_stage_unavailable'
        elif edge['relation'] in {'sequence','state'}:
            if da['profile_ref']!=db['profile_ref']:
                status,reason='unsupported','cross_profile_adapter_missing'
                if edge['relation']=='state':
                    try:evidence={'produced_ref':path_value(a['exchange']['world_after'],edge['produced_path']),
                        'consumed_ref':path_value(b['exchange']['world_before'],edge['consumed_path'])}
                    except Invalid as exc:evidence={'path_error':str(exc)}
            elif edge['relation']=='state' and da['disposition']=='partial':
                status,reason='unresolved','partial_result_not_financial_successor'
            else:
                before=b['exchange']['world_before'];after=a['exchange']['world_after']
                if after!=before:status,reason='invalid','intervening_world_not_declared'
                if edge['relation']=='state':
                    try:
                        produced=path_value(after,edge['produced_path']);consumed=path_value(before,edge['consumed_path'])
                        evidence={'produced_ref':produced,'consumed_ref':consumed}
                        if produced!=consumed:status,reason='invalid','state_reference_mismatch'
                        elif consumed not in requested_heads(b['reader'],b['reader'].body(b['exchange']['request_ref'])):
                            status,reason='invalid','state_not_requested'
                    except Invalid as exc:status,reason='invalid',str(exc)
        else:
            receipt=da.get('receipt_ref')
            receiver=b['reader'];closure=receiver.closure([b['exchange']['request_ref']])
            if receipt is None:status,reason='unresolved','source_receipt_unavailable'
            elif receipt['digest'] not in closure:status,reason='invalid','receipt_not_consumed'
            else:evidence={'receipt_ref':deepcopy(receipt)}
        findings.append({'dependency':deepcopy(edge),'status':status,'reason':reason,'evidence':evidence})
    severity={'compatible':0,'unresolved':1,'unsupported':2,'invalid':3}
    availability={}
    for stage in plan['stages']:
        identity=stage['id'];reasons=[]
        for finding in findings:
            if finding.get('stage')==identity:
                reasons.append((finding['status'],finding['reason']))
            dep=finding.get('dependency')
            if dep and dep['to']==identity:
                reasons.append((finding['status'],finding['reason']))
                inherited=availability[dep['from']]
                if inherited['status']!='compatible':
                    reasons.append((inherited['status'],'predecessor_unavailable:'+dep['from']))
        status=max((s for s,r in reasons),key=lambda s:severity[s],default='compatible')
        availability[identity]={'status':status,'reasons':[r for s,r in reasons if s!='compatible']}
    status=max((f['status'] for f in findings),key=lambda s:severity[s],default='compatible')
    return {'profile':PROFILE,'plan_sha256':sha256(canonical(plan)).hexdigest(),
        'status':'documentary_consistent' if status=='compatible' else status,
        'stages':{k:v['info'] for k,v in stages.items()},'findings':findings,'dependency_availability':availability,
        'scope':'selected_retained_dependencies_only','execution_admission':False,
        'source_admission':False,'accounting_admission':False,'concurrent_execution_admission':False}

def parse(source):
    need(type(source) in {str,bytes},'source_type')
    try:source=source.decode('utf-8','strict') if isinstance(source,bytes) else source;raw=source.encode('utf-8','strict')
    except UnicodeError as exc:raise Invalid('invalid_utf8') from exc
    need(len(raw)<=100000 and not source.startswith('\ufeff'),'source_size_or_bom')
    need(not any(c in source for c in '\x85\u2028\u2029') and re.search(r'\r(?!\n)',source) is None,'line_ending')
    plan=None;done=False;spans={'stages':{},'dependencies':[]}
    for number,line in enumerate(source.splitlines(),1):
        if not line.strip():continue
        try:
            need(not done,'declaration_after_end');reader=syntax.Reader(syntax.tokens(line));command=reader.take('word')
            if plan is None:
                need(command=='composition','header_required');plan={'profile':reader.string(),'name':reader.string(),'stages':[],'dependencies':[]};spans['header']=number
            elif command=='stage':
                stage={'id':reader.string(),'packet_sha256':reader.string(),'exchange_id':reader.string()};plan['stages'].append(stage);spans['stages'][stage['id']]=number
            elif command=='depend':
                plan['dependencies'].append({'from':reader.string(),'to':reader.string(),'relation':reader.string(),
                    'produced_path':reader.take('value'),'consumed_path':reader.take('value')});spans['dependencies'].append(number)
            elif command=='end_composition':done=True;spans['end']=number
            else:raise Invalid('unknown_declaration')
            reader.finish()
        except (ValueError,TypeError,KeyError,RecursionError) as exc:raise Invalid('line '+str(number)+': '+str(exc)) from exc
    need(done and plan is not None,'incomplete_program');validate(plan);return plan,spans

def render(plan):
    validate(plan);token=lambda x:json.dumps(x,ensure_ascii=False,separators=(',',':'))
    lines=['composition '+token(plan['profile'])+' '+token(plan['name'])+';']
    for s in plan['stages']:lines.append('stage '+' '.join(token(s[k]) for k in ['id','packet_sha256','exchange_id'])+';')
    for e in plan['dependencies']:lines.append('depend '+' '.join(token(e[k]) for k in ['from','to','relation','produced_path','consumed_path'])+';')
    return '\n'.join(lines+['end_composition;',''])

def compile_text(source,library):
    plan,spans=parse(source)
    return {'plan':plan,'assessment':assess(plan,library),'source_map':spans}
