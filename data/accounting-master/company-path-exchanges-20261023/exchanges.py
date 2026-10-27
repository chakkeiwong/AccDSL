"""Portable conditional outcomes; no transaction or historic restatement claim."""
from copy import deepcopy
from pathlib import Path
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ADMIT=HERE.parent/'company-path-admission-20261023'
sys.path.insert(0,str(ADMIT))
from admission import (canonical,digest,record_digest,dependencies,closed,
                       extension_schemas as admission_schemas,validate_registry)


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def schemas():
    sha={'type':'string','pattern':'^[0-9a-f]{64}$'};text={'type':'string','minLength':1}
    blob=closed({'kind':{'const':'blob'},'algorithm':{'const':'sha256'},'digest':sha,'byte_length':{'type':'integer','minimum':0}})
    ids={k:'accdsl.companyexchange.'+k.lower()+'.draft1' for k in ['YearOutcome','PathOutcome','PathRevision','PathExchange']}
    ref=lambda k,s:closed({'kind':{'const':k},'schema':{'const':s},'digest':sha})
    yr=ref('YearOutcome',ids['YearOutcome']);pr=ref('PathOutcome',ids['PathOutcome'])
    nullable=lambda s:{'oneOf':[{'type':'null'},s]}
    array=lambda s,minimum=1:{'type':'array','minItems':minimum,'items':s}
    period=closed({'start':{'type':'string','format':'date'},'end_exclusive':{'type':'string','format':'date'}})
    state=closed({'index':{'type':'integer','minimum':0},'period':period,
        'status':{'const':'unresolved'},'reason':{'const':'predecessor_incomplete'}})
    year=closed({'index':{'type':'integer','minimum':0},'period':period,
        'year_result_sha256':sha,'path_input_sha256':sha,'year_blob':blob,
        'predecessor_ref':nullable(yr),'outcome':{'enum':['complete_conditional','partial']},
        'closing_memory_blob':nullable(blob),'historical_admission':{'const':False}})
    path=closed({'name':text,'path_blob':blob,'result_blob':blob,'branch_sha256':sha,
        'baseline_export_ref':ref('PathExport','accdsl.companypath.pathexport.draft1'),
        'year_refs':array(yr),'status':{'enum':['complete_conditional','partial']},
        'unexecuted':array(state,0),'historical_restatement':{'const':False}})
    revision=closed({'parent_ref':pr,'child_ref':pr,'changed_year_index':{'type':'integer','minimum':0},
        'reason':text,'replacement_blob':blob,'parent_input_sha256':sha,'child_input_sha256':sha,
        'historical_restatement':{'const':False},'committed':{'const':False}})
    root=closed({'profile':{'const':'CompanyPathExchangeDraft/1'},'baseline_packet_blob':blob,
        'baseline_export_ref':ref('PathExport','accdsl.companypath.pathexport.draft1'),
        'path_refs':array(pr),'revision_refs':array(ref('PathRevision',ids['PathRevision']),0),
        'scope':{'const':'archival_synthetic_outcomes_and_assumption_revisions'},
        'transactional_storage':{'const':False}})
    return {'schema_ids':ids,'$defs':{'YearOutcome':year,'PathOutcome':path,'PathRevision':revision,'PathExchange':root}}


def validate(packet,blob_bytes,original_schemas,baseline_packet_sha256,
             baseline_admitter,engine,replay=False):
    """Caller supplies trusted baseline admission and local semantic executor."""
    try:
        if set(packet)!={'profile','root_ref','record_registry','blobs'} or packet['profile']!='CompanyPathExchangeDraft/1':raise ValueError('exchange profile/fields')
        if packet['root_ref']['kind']!='PathExchange':raise ValueError('exchange root type')
        all_schemas=deepcopy(original_schemas)
        for addition in [admission_schemas(),schemas()]:
            all_schemas['schema_ids'].update(addition['schema_ids']);all_schemas['$defs'].update(addition['$defs'])
        registry=packet['record_registry'];structural=validate_registry(registry,[packet['root_ref']],all_schemas,blob_bytes)
        if structural['status']!='validated':return {'status':'invalid','reason':'record_closure','details':structural}
        if set(structural['record_digests'])!=set(registry):raise ValueError('orphan record')
        if set(structural['blob_digests'])!=set(packet['blobs']):raise ValueError('blob manifest closure')
        if any(meta['byte_length']!=len(blob_bytes[h]) for h,meta in packet['blobs'].items()):raise ValueError('blob manifest length')
        root=registry[packet['root_ref']['digest']]['body']
        for field in ['path_refs','revision_refs']:
            if len({r['digest'] for r in root[field]})!=len(root[field]):raise ValueError('duplicate exchange reference')
        get=lambda b:json.loads(blob_bytes[b['digest']])
        baseline=get(root['baseline_packet_blob'])
        if root['baseline_packet_blob']['digest']!=baseline_packet_sha256:raise ValueError('baseline packet lock')
        if baseline['root_ref']!=root['baseline_export_ref']:raise ValueError('baseline root mismatch')
        if any(registry.get(h)!=r for h,r in baseline['record_registry'].items()):raise ValueError('baseline record altered')
        admitted=baseline_admitter(baseline,blob_bytes)
        if admitted['status']!='admitted_synthetic_archival':raise ValueError('baseline not admitted')
        base_export=registry[root['baseline_export_ref']['digest']]['body']
        base_path=get(base_export['path_blob'])
        source=blob_bytes[base_export['source_bundle_blob']['digest']]
        baseline_opening=base_path['initial_year']
        cases={};path_hashes=set();names=set();replayed=0
        for ref in root['path_refs']:
            body=registry[ref['digest']]['body'];path=get(body['path_blob']);run=get(body['result_blob'])
            if body['name'] in names or body['branch_sha256'] in path_hashes:raise ValueError('duplicate case')
            names.add(body['name']);path_hashes.add(body['branch_sha256'])
            if body['baseline_export_ref']!=root['baseline_export_ref']:raise ValueError('case baseline')
            for k in ['source','opening_digest','context','information','opening_claims','assets']:
                if path['initial_year'][k]!=baseline_opening[k]:raise ValueError('case opening changed')
            if not engine.verify_chain(path,run):raise ValueError('case result chain')
            if run['branch_sha256']!=body['branch_sha256'] or run['status']!=body['status'] or run['unexecuted']!=body['unexecuted']:raise ValueError('case outcome binding')
            if len(body['year_refs'])!=len(run['years']):raise ValueError('year coverage')
            for i,(yr,y) in enumerate(zip(body['year_refs'],run['years'])):
                item=registry[yr['digest']]['body'];complete=y['run']['status']=='complete_conditional'
                if item['index']!=i or item['period']!=y['period'] or item['year_result_sha256']!=y['result_sha256'] or item['path_input_sha256']!=run['branch_sha256']:raise ValueError('year identity')
                if item['predecessor_ref']!=(None if i==0 else body['year_refs'][i-1]):raise ValueError('year predecessor')
                if get(item['year_blob'])!=y:raise ValueError('year bytes binding')
                if item['outcome']!=('complete_conditional' if complete else 'partial'):raise ValueError('year outcome tag')
                if complete:
                    if item['closing_memory_blob'] is None or get(item['closing_memory_blob'])!=y['closing_memory']:raise ValueError('complete memory')
                elif item['closing_memory_blob'] is not None or 'closing_memory' in y:
                    raise ValueError('partial year has closing memory')
                elif y['report'].get('annual_complete') is True:
                    raise ValueError('partial report claims annual completion')
            if replay:
                if engine.wire(engine.execute(path,source))!=run:raise ValueError('local replay mismatch')
                replayed+=1
            cases[ref['digest']]=(path,run)
        if digest(base_path) not in path_hashes:raise ValueError('baseline case absent')
        for ref in root['revision_refs']:
            rev=registry[ref['digest']]['body']
            if rev['parent_ref']['digest'] not in cases or rev['child_ref']['digest'] not in cases:raise ValueError('revision case missing')
            parent,parent_run=cases[rev['parent_ref']['digest']];child,child_run=cases[rev['child_ref']['digest']]
            idx=rev['changed_year_index'];replacement=get(rev['replacement_blob'])
            if rev['parent_input_sha256']!=digest(parent) or rev['child_input_sha256']!=digest(child):raise ValueError('revision input identities')
            if not rev['reason'].strip() or rev['parent_input_sha256']==rev['child_input_sha256']:raise ValueError('empty revision')
            definitions=[parent['initial_year']]+parent['continuations']
            if not 0<=idx<len(definitions):raise ValueError('revision index')
            expected=deepcopy(parent)
            if idx==0:expected['initial_year']=replacement
            else:expected['continuations'][idx-1]=replacement
            if expected!=child:raise ValueError('undeclared revision changes')
            for k in ['source','opening_digest','context','period','information','opening_claims','assets'] if idx==0 else ['period']:
                if definitions[idx][k]!=replacement[k]:raise ValueError('revision opening or period changed')
            for i in range(min(idx,len(parent_run['years']),len(child_run['years']))):
                if parent_run['years'][i]['result_sha256']!=child_run['years'][i]['result_sha256']:raise ValueError('revision changed earlier result')
            if replay:
                recreated=engine.revise(parent,source,idx,replacement,rev['reason'])
                if recreated.get('path')!=child or engine.wire(recreated.get('result'))!=child_run:raise ValueError('revision replay mismatch')
        return {'status':'validated_synthetic_exchange','path_count':len(cases),
            'verification_level':'trusted_local_semantic_replay' if replay else 'content_binding_only',
            'revision_count':len(root['revision_refs']),'year_outcomes':sum(len(r['years']) for _,r in cases.values()),
            'partial_paths':sum(r['status']=='partial' for _,r in cases.values()),
            'replayed_paths':replayed,'historical_restatement':False,'transactional_storage':False,
            'scope':'synthetic archival outcome/revision consistency; no temporal assumption admission'}
    except Exception as exc:
        return {'status':'invalid','reason':'exchange_semantics','detail':type(exc).__name__+':'+str(exc).splitlines()[0][:500]}
