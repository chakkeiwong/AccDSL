"""Portable closure and timing conformance; read-only default."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import time
from admission import (admit_packet,validate_registry,information_view,extension_schemas,
    canonical,digest,record_digest,dependencies,blobs,refs)

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
JOIN=HERE.parent/'company-operation-path-20261023'
BASE=HERE.parent/'corporate-portable-20261015'


def load_local_engine():
    spec=importlib.util.spec_from_file_location('admission_trusted_composition',JOIN/'composition.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def load_blob_files(packet):
    data={}
    for h,meta in packet['blobs'].items():
        path=Path(meta['path'])
        if path.is_absolute() or not (ROOT/path).resolve().is_relative_to(ROOT):
            raise ValueError('blob path outside project')
        data[h]=(ROOT/path).read_bytes()
    return data


def rekey(packet):
    """Recompute record digests after a semantic mutation; no source blobs changed."""
    old=deepcopy(packet['record_registry']);fresh={};mapped={}
    def replace(value):
        if isinstance(value,dict):
            if set(value)=={'kind','schema','digest'}:
                return visit(value['digest'])
            return {k:replace(v) for k,v in value.items()}
        if isinstance(value,list):return [replace(v) for v in value]
        return value
    def visit(h):
        if h in mapped:return mapped[h]
        entry=deepcopy(old[h]);entry['body']=replace(entry['body']);entry['dependencies']=dependencies(entry['body'])
        nh=record_digest(entry);fresh[nh]=entry
        ref={'kind':entry['kind'],'schema':entry['schema'],'digest':nh};mapped[h]=ref
        return ref
    root=visit(packet['root_ref']['digest']);packet['record_registry']=fresh;packet['root_ref']=root
    return packet


def conformance():
    packet=json.loads((HERE/'packet.json').read_text());raw=load_blob_files(packet)
    old_schema=(BASE/'record-schemas.json').read_bytes();path_schema=(JOIN/'schema.json').read_bytes()
    lock=json.loads((HERE/'reference-locks.json').read_text())
    engine=load_local_engine()
    checks=[];witnesses={}
    def check(name,passed):checks.append({'name':name,'passed':bool(passed)})
    def admit(p=packet,b=raw,mode='archival_exploration',cutoff=None):
        return admit_packet(p,b,old_schema,path_schema,lock['engine'],lock['methods'],engine.verify_chain,mode,cutoff)
    original=deepcopy(packet);accepted=admit()
    check('archival_packet_admitted',accepted['status']=='admitted_synthetic_archival')
    check('expected_record_method_year_operation_counts',all(accepted.get(k)==v for k,v in [('record_count',42),('method_count',14),('year_count',3),('operation_count',63)]))
    check('packet_validation_is_pure',packet==original)
    check('extension_schema_matches',extension_schemas()==json.loads((HERE/'extension-schemas.json').read_text()))
    root=packet['record_registry'][packet['root_ref']['digest']]['body'];registry=packet['record_registry']
    get=lambda b:json.loads(raw[b['digest']])
    path=get(root['path_blob']);stored=get(root['result_blob'])
    actual=engine.execute(path,raw[root['source_bundle_blob']['digest']])
    check('trusted_local_semantic_replay',engine.wire(actual)==stored)
    check('replayed_chain_valid',engine.verify_chain(path,actual))
    check('conditional_closings_not_facts',all(registry[r['digest']]['kind']=='ConditionalClose' and registry[r['digest']]['body']['historical_admission'] is False for r in root['closing_refs']))
    for r in root['method_refs']:
        m=registry[r['digest']]['body'];contract=get(m['contract_blob'])
        check('method:'+m['operation_kind'],contract['method_id']==m['method_id'] and m['implementation_blob']['digest']==lock['engine']['operations'] and digest(contract['payload_schema'])==m['payload_schema_sha256'])
    roots=[root['opening_ref'],root['synthetic_admission_ref']]
    closure=validate_registry(registry,roots,json.loads(old_schema),raw)
    check('historical_root_closure',closure['status']=='validated' and len(closure['record_digests'])==21 and len(closure['blob_digests'])==2)
    temporal=[('pre_year','investor_information','2025-01-01T00:00:00Z','ineligible',7,0),
        ('publication_midnight','investor_information','2025-03-02T00:00:00Z','unresolved',0,7),
        ('publication_noon','investor_information','2025-03-02T12:00:00Z','unresolved',0,7),
        ('publication_next_day','investor_information','2025-03-03T00:00:00Z','eligible_synthetic',0,0),
        ('before_ingestion','system_as_of','2025-03-05T11:59:59Z','ineligible',9,0),
        ('after_ingestion_before_acceptance','system_as_of','2025-03-05T12:30:00Z','ineligible',2,0),
        ('acceptance_boundary','system_as_of','2025-03-05T13:00:00Z','eligible_synthetic',0,0)]
    for name,mode,cutoff,status,unavailable,unknown in temporal:
        v=information_view(registry,closure['record_digests'],mode,cutoff);witnesses[name]=v
        check('source_timing:'+name,v['status']==status and len(v['unavailable'])==unavailable and len(v['unresolved'])==unknown and not v['real_world_admission'])
    for mode,cutoff in [('investor_information','2025-03-03T00:00:00Z'),('system_as_of','2025-03-05T13:00:00Z')]:
        v=admit(mode=mode,cutoff=cutoff);witnesses['path_'+mode]=v
        check('eligible_source_does_not_admit_path:'+mode,v['status']=='unresolved' and v['reason']=='path_assumption_information_not_admitted')
    check('early_path_ineligible',admit(mode='investor_information',cutoff='2025-01-01T00:00:00Z')['status']=='ineligible')
    check('same_day_path_unresolved',admit(mode='investor_information',cutoff='2025-03-02T23:59:59Z')['status']=='unresolved')
    check('archival_cutoff_rejected',admit(cutoff='2025-01-01T00:00:00Z')['status']=='invalid')
    check('invalid_timezone_rejected',information_view(registry,closure['record_digests'],'system_as_of','2025-03-05T13:00:00+01:00')['status']=='invalid')
    source_id=next(h for h in closure['record_digests'] if registry[h]['kind']=='SourceUnit')
    for field,value,mode,reason in [('public_bytes_verified',False,'investor_information','PUBLICATION_UNVERIFIED'),('public_date',None,'investor_information','PUBLICATION_UNVERIFIED'),('ingestion_verified',False,'system_as_of','INGESTION_UNVERIFIED')]:
        modified=deepcopy(registry);modified[source_id]['body'][field]=value
        v=information_view(modified,closure['record_digests'],mode,'2026-01-01T00:00:00Z')
        check('missing_timing:'+field,v['status']=='unresolved' and any(x['reason']==reason for x in v['unresolved']))
    def invalid(name,change,rehash=False):
        p=deepcopy(packet);b=dict(raw);change(p,b)
        if rehash:
            p=rekey(p)
            used={x['digest'] for entry in p['record_registry'].values() for x in blobs(entry)}
            p['blobs']={h:meta for h,meta in p['blobs'].items() if h in used}
        value=admit(p,b);witnesses[name]=value;check(name,value['status']=='invalid')
    def record(p,kind):return next(r for r in p['record_registry'].values() if r['kind']==kind)
    invalid('changed_record_bytes',lambda p,b:record(p,'SourceUnit')['body'].update(locator='changed'))
    invalid('missing_dependency',lambda p,b:p['record_registry'].pop(source_id))
    invalid('missing_blob',lambda p,b:b.pop(next(iter(b))))
    invalid('changed_blob_bytes',lambda p,b:b.update({root['path_blob']['digest']:b[root['path_blob']['digest']]+b' '}))
    invalid('omitted_declared_dependency',lambda p,b:record(p,'CompanyState')['dependencies'].pop())
    invalid('wrong_reference_type',lambda p,b:record(p,'CompanyState')['body']['source_ref'].update(kind='View'))
    invalid('changed_method_rehashed',lambda p,b:record(p,'PathMethod')['body'].update(method_id='northstar.fake@draft1'),True)
    invalid('wrong_method_payload_rehashed',lambda p,b:record(p,'PathMethod')['body'].update(payload_schema_sha256='0'*64),True)
    invalid('conditional_as_historical_rehashed',lambda p,b:record(p,'ConditionalClose')['body'].update(historical_admission=True),True)
    invalid('wrong_year_index_rehashed',lambda p,b:record(p,'ConditionalClose')['body'].update(year_index=9),True)
    invalid('wrong_predecessor_rehashed',lambda p,b:record(p,'ConditionalClose')['body'].update(path_input_sha256='0'*64),True)
    def remove_method(p,b):
        record(p,'PathExport')['body']['method_refs'].pop()
        # Remove orphan contract blob entries after rekey for a fair semantic test.
    invalid('missing_method_rehashed',remove_method,True)
    invalid('changed_source_record_rehashed',lambda p,b:record(p,'SourceUnit')['body'].update(locator='changed'),True)
    invalid('wrong_engine_lock_rehashed',lambda p,b:record(p,'PathExport')['body']['engine_files'][0].update(role='unknown-role'),True)
    check('missing_method_hits_coverage_check','method coverage' in witnesses['missing_method_rehashed'].get('detail',''))
    check('changed_method_hits_identity_lock','method coverage' in witnesses['changed_method_rehashed'].get('detail',''))
    check('wrong_payload_hits_identity_lock','method lock mismatch' in witnesses['wrong_method_payload_rehashed'].get('detail',''))
    check('original_rehash_cannot_change_source','opening binding' in witnesses['changed_source_record_rehashed'].get('detail',''))
    def replace_export_blob(p,b,key,value):
        data=canonical(value);h=hashlib.sha256(data).hexdigest();b[h]=data
        root_body=record(p,'PathExport')['body']
        root_body[key]={'kind':'blob','algorithm':'sha256','digest':h,'byte_length':len(data)}
        p['blobs'][h]={'path':'in-memory-mutated-test.json','byte_length':len(data),'label':'adverse fixture'}
    def change_path(p,b):
        new_path=deepcopy(path)
        next(o for o in new_path['continuations'][0]['operations'] if o['kind']=='delivery')['payload']['unit_price']='99/1'
        replace_export_blob(p,b,'path_blob',new_path)
    invalid('changed_path_blob_rehashed',change_path,True)
    check('changed_path_detects_result_binding','conditional result chain' in witnesses['changed_path_blob_rehashed'].get('detail',''))
    def change_report(p,b):
        rr=record(p,'PathReport');value=json.loads(b[rr['body']['report_blob']['digest']])
        value['lines']['cash']['value']='999/1';data=canonical(value);h=hashlib.sha256(data).hexdigest();b[h]=data
        rr['body']['report_blob']={'kind':'blob','algorithm':'sha256','digest':h,'byte_length':len(data)}
        p['blobs'][h]={'path':'in-memory-report.json','byte_length':len(data),'label':'adverse fixture'}
    invalid('changed_report_blob_rehashed',change_report,True)
    check('changed_report_detects_semantic_binding','report binding' in witnesses['changed_report_blob_rehashed'].get('detail',''))
    def change_schema(p,b):
        altered=json.loads(old_schema);altered['$defs']['CompanyState']['required']=[]
        replace_export_blob(p,b,'schema_lock_blob',altered)
    invalid('changed_schema_blob_rehashed',change_schema,True)
    check('changed_schema_detects_trusted_lock','schema lock mismatch' in witnesses['changed_schema_blob_rehashed'].get('detail',''))
    p=deepcopy(packet);h=next(iter(p['blobs']));p['blobs'][h]['path']='../outside-project'
    try:load_blob_files(p);rejected=False
    except ValueError:rejected=True
    check('blob_path_traversal_refused',rejected)
    p=deepcopy(packet);p['blobs'][h]['path']='/etc/passwd'
    try:load_blob_files(p);rejected=False
    except ValueError:rejected=True
    check('absolute_blob_path_refused',rejected)
    protected=json.loads((HERE/'baseline.json').read_text())
    check('protected_evidence_unchanged',all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in protected.items()))
    return {'checks':checks,'passed':all(c['passed'] for c in checks),'admission':accepted,
        'opening_closure':closure,'witnesses':witnesses,'replayed_branch_sha256':actual['branch_sha256']}


def main():
    p=argparse.ArgumentParser();p.add_argument('--record',action='store_true');args=p.parse_args()
    start=datetime.now(timezone.utc).isoformat();clock=time.perf_counter();evidence=conformance();target=HERE/'checks.json'
    if args.record:
        if target.exists():raise RuntimeError('Existing evidence')
        target.write_text(json.dumps(evidence,indent=2)+'\n')
        manifest={'started_utc':start,'wall_seconds':time.perf_counter()-clock,
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-path-admission-20261023/verify.py --record',
            'environment':'system Python '+platform.python_version()+'; jsonschema; local trusted replay',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES='+str(os.environ.get('CUDA_VISIBLE_DEVICES')),
            'data_version':json.loads((HERE/'baseline.json').read_text()),'random_seeds':'N/A: deterministic',
            'plan':'docs/plans/accounting-company-path-admission-20261023.md',
            'result':'data/accounting-master/company-path-admission-20261023/result.md',
            'files':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in HERE.iterdir() if f.is_file()}}
        (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    elif target.exists() and evidence!=json.loads(target.read_text()):raise AssertionError('Evidence replay mismatch')
    failed=[x['name'] for x in evidence['checks'] if not x['passed']]
    print(json.dumps({'checks':len(evidence['checks']),'passed':not failed,'failed':failed,'recorded':args.record}))
    return bool(failed)


if __name__=='__main__':raise SystemExit(main())
