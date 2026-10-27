"""Structural and synthetic temporal admission; does not execute supplied code."""
from copy import deepcopy
from datetime import datetime,timedelta,timezone
from fractions import Fraction as Q
import hashlib
import json
from jsonschema import Draft202012Validator,FormatChecker


def canonical(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def digest(x):return hashlib.sha256(canonical(x)).hexdigest()


def record_digest(x):
    return hashlib.sha256(('accdsl.portable.v1/'+x['schema']).encode()+b'\0'+canonical(x)).hexdigest()


def refs(x):
    if isinstance(x,dict):
        if set(x)=={'kind','schema','digest'}:yield x
        else:
            for v in x.values():yield from refs(v)
    elif isinstance(x,list):
        for v in x:yield from refs(v)


def blobs(x):
    if isinstance(x,dict):
        if x.get('kind')=='blob':yield x
        else:
            for v in x.values():yield from blobs(v)
    elif isinstance(x,list):
        for v in x:yield from blobs(v)


def dependencies(body):
    found={canonical(r):r for r in refs(body)}
    return [found[k] for k in sorted(found)]


def exact(x):
    if isinstance(x,float):raise ValueError('floating value in portable record')
    if isinstance(x,dict):
        if set(x)=={'n','d'}:
            if type(x['n']) is not str or type(x['d']) is not str:raise ValueError('integer-string rational required')
            q=Q(int(x['n']),int(x['d']))
            if x!={'n':str(q.numerator),'d':str(q.denominator)}:raise ValueError('noncanonical rational')
        for value in x.values():exact(value)
    elif isinstance(x,list):
        for value in x:exact(value)


def validate_registry(registry,roots,schemas,blob_bytes):
    """Validate only the declared reachable closure, rejecting dangling records."""
    done=set();active=set();blob_ids=set();errors=[]
    def visit(ref):
        d=ref['digest']
        if d in active:raise ValueError('reference cycle')
        entry=registry[d]
        if (entry['kind'],entry['schema'])!=(ref['kind'],ref['schema']):raise ValueError('reference type mismatch')
        if d in done:return
        active.add(d)
        if set(entry)!={'kind','schema','key','revision','body','dependencies'}:raise ValueError('record fields')
        if not isinstance(entry['key'],str) or not entry['key']:raise ValueError('record key')
        if type(entry['revision']) is not int or entry['revision']<0:raise ValueError('record revision')
        if entry['schema']!=schemas['schema_ids'][entry['kind']]:raise ValueError('record schema identity')
        Draft202012Validator(schemas['$defs'][entry['kind']],format_checker=FormatChecker()).validate(entry['body'])
        exact(entry)
        if record_digest(entry)!=d:raise ValueError('record digest mismatch')
        if entry['dependencies']!=dependencies(entry['body']):raise ValueError('dependency list mismatch')
        for b in blobs(entry):
            raw=blob_bytes[b['digest']]
            if type(raw) is not bytes or len(raw)!=b['byte_length'] or hashlib.sha256(raw).hexdigest()!=b['digest']:
                raise ValueError('blob identity mismatch')
            blob_ids.add(b['digest'])
        for dep in entry['dependencies']:visit(dep)
        active.remove(d);done.add(d)
    try:
        for root in roots:visit(root)
    except (ValueError,KeyError,TypeError,ZeroDivisionError,RecursionError) as exc:
        errors.append(type(exc).__name__+':'+str(exc)[:500])
    except Exception as exc:
        # jsonschema ValidationError remains an invalid record, never admission.
        errors.append(type(exc).__name__+':'+str(exc).splitlines()[0][:500])
    return {'status':'invalid' if errors else 'validated','errors':errors,
            'record_digests':sorted(done),'blob_digests':sorted(blob_ids)}


def information_view(registry,closure,mode,cutoff=None):
    """Timing eligibility only; all fixture sources remain authored synthetic."""
    if mode not in ['archival_exploration','investor_information','system_as_of']:
        return {'status':'invalid','reason':'information_mode'}
    if mode=='archival_exploration':
        if cutoff is not None:return {'status':'invalid','reason':'archival_cutoff_not_used'}
        return {'status':'eligible_synthetic','mode':mode,'cutoff':None,
                'real_world_admission':False,'reason':'archival_exploration_uses_retained_sources'}
    try:
        if not isinstance(cutoff,str) or not cutoff.endswith('Z'):raise ValueError('UTC cutoff required')
        at=datetime.fromisoformat(cutoff[:-1]+'+00:00')
        if at.tzinfo!=timezone.utc:raise ValueError('UTC cutoff required')
    except (ValueError,TypeError):return {'status':'invalid','reason':'cutoff'}
    unavailable=[];unknown=[];eligible=[]
    for d in closure:
        r=registry[d];b=r['body'];reason=None
        if r['kind']=='SourceUnit':
            if b['fact_status']!='authored_synthetic':return {'status':'invalid','reason':'non_synthetic_source_outside_profile'}
            if mode=='investor_information':
                if not b['public_date'] or not b['public_bytes_verified']:
                    unknown.append({'digest':d,'reason':'PUBLICATION_UNVERIFIED'});continue
                start=datetime.fromisoformat(b['public_date']).replace(tzinfo=timezone.utc)
                if at<start:reason='AFTER_INFORMATION_CUTOFF'
                elif at<start+timedelta(days=1):
                    unknown.append({'digest':d,'reason':'PUBLICATION_PRECISION_UNRESOLVED'});continue
            else:
                if not b['ingestion_verified'] or not b['ingested_at']:
                    unknown.append({'digest':d,'reason':'INGESTION_UNVERIFIED'});continue
                if datetime.fromisoformat(b['ingested_at'].replace('Z','+00:00'))>at:reason='AFTER_SYSTEM_CUTOFF'
            if reason:unavailable.append({'digest':d,'reason':reason})
            else:eligible.append(d)
        elif r['kind']=='LiteralAdmission' and mode=='system_as_of':
            if not b['accepted_at']:unknown.append({'digest':d,'reason':'ACCEPTANCE_UNVERIFIED'})
            elif datetime.fromisoformat(b['accepted_at'].replace('Z','+00:00'))>at:
                unavailable.append({'digest':d,'reason':'AFTER_ACCEPTANCE_CUTOFF'})
    status='ineligible' if unavailable else 'unresolved' if unknown else 'eligible_synthetic'
    return {'status':status,'mode':mode,'cutoff':cutoff,'eligible_source_digests':eligible,
            'unavailable':unavailable,'unresolved':unknown,'real_world_admission':False}


def closed(fields):
    return {'type':'object','properties':fields,'required':list(fields),'additionalProperties':False}


def extension_schemas():
    text={'type':'string','minLength':1};sha={'type':'string','pattern':'^[0-9a-f]{64}$'}
    blob=closed({'kind':{'const':'blob'},'algorithm':{'const':'sha256'},'digest':sha,'byte_length':{'type':'integer','minimum':0}})
    ref=lambda kind,uri:closed({'kind':{'const':kind},'schema':{'const':uri},'digest':sha})
    ids={k:'accdsl.companypath.'+k.lower()+'.draft1' for k in ['PathMethod','ConditionalClose','PathReport','PathExport']}
    methodref=ref('PathMethod',ids['PathMethod']);closeref=ref('ConditionalClose',ids['ConditionalClose'])
    oldstate=ref('CompanyState','accdsl.corporate.companystate.v1')
    oldadmit=ref('Admission','accdsl.corporate.admission.v1')
    rat={'type':'string','pattern':r'^(?:0|-?[1-9][0-9]*)/[1-9][0-9]*$'}
    array=lambda value:{'type':'array','minItems':1,'items':value}
    method=closed({'method_id':text,'operation_kind':text,'payload_schema_sha256':sha,
        'contract_blob':blob,'implementation_blob':blob,'conformance_blob':blob,
        'evidence_scope':{'const':'checked_synthetic_reference_only'}})
    close=closed({'year_index':{'type':'integer','minimum':0},'year_result_sha256':sha,
        'path_input_sha256':sha,'memory_blob':blob,'source_opening_ref':oldstate,
        'predecessor_ref':{'oneOf':[{'type':'null'},closeref]},
        'state_kind':{'const':'conditional_projection'},'historical_admission':{'const':False}})
    report=closed({'year_result_sha256':sha,'report_blob':blob,'closing_ref':closeref,
        'annual_complete':{'const':True}})
    export=closed({'profile':{'const':'CompanyPathEvidenceDraft/1'},'path_blob':blob,
        'result_blob':blob,'source_bundle_blob':blob,'schema_lock_blob':blob,
        'path_schema_blob':blob,'engine_files':array(closed({'role':text,'blob':blob})),
        'opening_ref':oldstate,'synthetic_admission_ref':oldadmit,
        'method_refs':array(methodref),'closing_refs':array(closeref),
        'report_refs':array(ref('PathReport',ids['PathReport'])),
        'evidence_scope':{'const':'archival_synthetic_conditional_only'},
        'product_implemented':{'const':False}})
    return {'schema_ids':ids,'$defs':{'PathMethod':method,'ConditionalClose':close,'PathReport':report,'PathExport':export}}


def admit_packet(packet,blob_bytes,trusted_schema_bytes,trusted_path_schema_bytes,
                 engine_lock,method_lock,chain_verifier,mode='archival_exploration',cutoff=None):
    """Trusted callbacks are supplied locally; never import code named by a packet."""
    try:
        if set(packet)!={'profile','root_ref','record_registry','blobs'} or packet['profile']!='CompanyPathEvidenceDraft/1':
            raise ValueError('packet fields/profile')
        registry=packet['record_registry'];root=packet['root_ref']
        if root['kind']!='PathExport':raise ValueError('export root kind')
        original_schemas=json.loads(trusted_schema_bytes);schemas=deepcopy(original_schemas)
        ext=extension_schemas();schemas['schema_ids'].update(ext['schema_ids']);schemas['$defs'].update(ext['$defs'])
        structural=validate_registry(registry,[root],schemas,blob_bytes)
        if structural['status']!='validated':return {'status':'invalid','reason':'record_closure','details':structural}
        if set(structural['record_digests'])!=set(registry):raise ValueError('unreachable exported record')
        if set(structural['blob_digests'])!=set(packet['blobs']):raise ValueError('blob manifest closure')
        for h,meta in packet['blobs'].items():
            if meta['byte_length']!=len(blob_bytes[h]):raise ValueError('blob manifest length')
        export=registry[root['digest']]['body']
        def raw(b):return blob_bytes[b['digest']]
        def read(b):return json.loads(raw(b))
        if raw(export['schema_lock_blob'])!=trusted_schema_bytes:raise ValueError('schema lock mismatch')
        if raw(export['path_schema_blob'])!=trusted_path_schema_bytes:raise ValueError('path schema lock mismatch')
        path=read(export['path_blob']);run=read(export['result_blob']);source=raw(export['source_bundle_blob'])
        original=json.loads(source)
        if hashlib.sha256(source).hexdigest()!=path['initial_year']['source']['sha256']:raise ValueError('source bundle mismatch')
        Draft202012Validator(json.loads(trusted_path_schema_bytes),format_checker=FormatChecker()).validate(path)
        if not chain_verifier(path,run):raise ValueError('conditional result chain')
        if run['status']!='complete_conditional':raise ValueError('incomplete export unsupported')
        opening=registry[export['opening_ref']['digest']]
        if export['opening_ref']['digest']!=path['initial_year']['opening_digest']:raise ValueError('opening binding')
        for h,entry in registry.items():
            if entry['kind'] in original_schemas['schema_ids'] and original['record_registry'].get(h)!=entry:
                raise ValueError('changed original record')
        admission=registry[export['synthetic_admission_ref']['digest']]['body']
        if admission['status']!='synthetic_only' or admission['facts_ref']!=opening['body']['source_ref'] or admission['view_ref']!=opening['body']['view_ref']:
            raise ValueError('synthetic admission/opening mismatch')
        engines=export['engine_files'];roles=[x['role'] for x in engines]
        if len(set(roles))!=len(roles) or set(roles)!=set(engine_lock):raise ValueError('engine role coverage')
        if any(x['blob']['digest']!=engine_lock[x['role']] for x in engines):raise ValueError('engine lock mismatch')
        method_refs=export['method_refs'];methods=[registry[r['digest']]['body'] for r in method_refs]
        ids=[m['method_id'] for m in methods]
        if len(set(ids))!=len(ids) or set(ids)!=set(method_lock):raise ValueError('method coverage')
        method_map={m['method_id']:m for m in methods}
        for m in methods:
            if digest(m)!=method_lock[m['method_id']]:raise ValueError('method lock mismatch')
            contract=read(m['contract_blob'])
            if contract['method_id']!=m['method_id'] or contract['operation_kind']!=m['operation_kind']:
                raise ValueError('method contract identity')
            if digest(contract['payload_schema'])!=m['payload_schema_sha256']:raise ValueError('method payload schema')
            if m['implementation_blob']['digest']!=engine_lock['operations']:raise ValueError('method implementation mismatch')
            evidence=read(m['conformance_blob'])
            if evidence.get('passed') is not True or not evidence.get('checks') or not all(c['passed'] is True for c in evidence['checks']):
                raise ValueError('method conformance not passed')
        definitions=[path['initial_year']]+path['continuations']
        for definition,year in zip(definitions,run['years']):
            operations={o['id']:o for o in definition['operations']}
            if [j['event'] for j in year['run']['journals']]!=[o['id'] for o in definition['operations']]:raise ValueError('journal coverage')
            for j in year['run']['journals']:
                if j['method'] not in method_map:raise ValueError('unresolved method')
                m=method_map[j['method']]
                if m['operation_kind']!=j['kind'] or operations[j['event']]['kind']!=m['operation_kind']:
                    raise ValueError('method operation mismatch')
        closes,reports=export['closing_refs'],export['report_refs']
        if len(closes)!=len(run['years']) or len(reports)!=len(closes):raise ValueError('closing/report coverage')
        for i,(c,r,y) in enumerate(zip(closes,reports,run['years'])):
            cb=registry[c['digest']]['body'];rb=registry[r['digest']]['body']
            if cb['year_index']!=i or cb['year_result_sha256']!=y['result_sha256'] or cb['path_input_sha256']!=run['branch_sha256']:raise ValueError('closing identity')
            if cb['predecessor_ref']!=(None if i==0 else closes[i-1]) or cb['source_opening_ref']!=export['opening_ref']:raise ValueError('closing origin')
            if read(cb['memory_blob'])!=y['closing_memory']:raise ValueError('closing memory mismatch')
            if rb['closing_ref']!=c or rb['year_result_sha256']!=y['result_sha256'] or read(rb['report_blob'])!=y['report']:raise ValueError('report binding')
        # Temporal selection applies to the actual historical root closure, not
        # to future conditional closings or author-supplied simulation dates.
        old_check=validate_registry(registry,[export['opening_ref'],export['synthetic_admission_ref']],original_schemas,blob_bytes)
        if old_check['status']!='validated':raise ValueError('original opening closure')
        timing=information_view(registry,old_check['record_digests'],mode,cutoff)
        if timing['status']!='eligible_synthetic':return {'status':timing['status'],'reason':'information_view','timing':timing,'structural':structural}
        # A dated source view does not establish when the path assumptions were
        # authored, admitted or available to an actual decision-maker.
        if mode!='archival_exploration':
            return {'status':'unresolved','reason':'path_assumption_information_not_admitted',
                    'source_timing':timing,'structural':structural,'real_world_admission':False}
        return {'status':'admitted_synthetic_archival','scope':'source_closure_method_identity_and_conditional_bindings',
            'record_count':len(registry),'method_count':len(methods),'year_count':len(closes),
            'operation_count':sum(len(y['run']['journals']) for y in run['years']),
            'source_timing':timing,'real_world_admission':False,'product_implemented':False,
            'semantic_replay_required':True,'trusted_code_executed_by_validator':False}
    except Exception as exc:
        return {'status':'invalid','reason':'packet_semantics','detail':type(exc).__name__+':'+str(exc).splitlines()[0][:500]}
