"""Deterministic temporal selection checks; read-only default."""
from copy import deepcopy
from datetime import datetime,timezone
import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from information import HERE,EXCHANGE,components,digest,select,query,schema,observation_schema
from fixtures import make
import support
from admission import information_view

ROOT=HERE.parents[2]


def conformance():
    previous,engine,validate=support.context()
    exchange=json.loads((EXCHANGE/'packet.json').read_text())
    raw=previous.load_blob_files(exchange);exchange_hash=digest(exchange)
    registry=exchange['record_registry'];root=registry[exchange['root_ref']['digest']]['body']
    cases={registry[r['digest']]['body']['name']:registry[r['digest']]['body'] for r in root['path_refs']}
    paths={name:json.loads(raw[body['path_blob']['digest']]) for name,body in cases.items()}
    fixture=make(paths['baseline'],exchange_hash)
    baseline=PathSupport.baseline_packet()
    original_root=baseline['record_registry'][baseline['root_ref']['digest']]['body']
    original_schema=json.loads((support.OLD/'record-schemas.json').read_text())
    closure=previous.validate_registry(baseline['record_registry'],
        [original_root['opening_ref'],original_root['synthetic_admission_ref']],original_schema,raw)
    def source(mode,cutoff):return information_view(baseline['record_registry'],closure['record_digests'],mode,cutoff)
    def evaluate(f=fixture,path=None,mode='investor_information',cutoff='2025-03-08T00:00:00Z'):
        return select(paths['baseline'] if path is None else path,f['declaration'],f['observations'],
                      set(f['trusted_observation_hashes']),exchange_hash,source,mode,cutoff)
    checks=[];witnesses={}
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    cases_to_check=[('before_source','investor_information','2025-01-01T00:00:00Z','ineligible'),
        ('source_only','investor_information','2025-03-03T00:00:00Z','ineligible'),
        ('before_publication','investor_information','2025-03-06T23:59:59Z','ineligible'),
        ('publication_midnight','investor_information','2025-03-07T00:00:00Z','unresolved'),
        ('publication_end','investor_information','2025-03-07T23:59:59Z','unresolved'),
        ('publication_next_day','investor_information','2025-03-08T00:00:00Z','eligible_synthetic'),
        ('before_authored','system_as_of','2025-03-06T08:59:59Z','ineligible'),
        ('before_ingested','system_as_of','2025-03-06T09:59:59Z','ineligible'),
        ('before_accepted','system_as_of','2025-03-06T10:59:59Z','ineligible'),
        ('acceptance_instant','system_as_of','2025-03-06T11:00:00Z','eligible_synthetic')]
    for name,mode,cutoff,status in cases_to_check:
        value=evaluate(mode=mode,cutoff=cutoff);witnesses[name]=value
        check('timing:'+name,value['status']==status)
        check('synthetic_only:'+name,value.get('real_world_admission') is False and value.get('forecast_admission') is False)
    archival=evaluate(mode='archival_exploration',cutoff=None);witnesses['archival']=archival
    check('archival_does_not_assert_time',archival['status']=='archival_synthetic' and not archival['temporal_admission'])
    check('source_passes_before_assumptions',witnesses['source_only']['source_timing']['status']=='eligible_synthetic')
    check('four_exact_components',components(paths['baseline'])==[
        {'slot':d['slot'],'sha256':d['component_sha256']} for d in fixture['declaration']['declarations']] and len(components(paths['baseline']))==4)
    original=deepcopy(fixture);evaluate();check('selector_is_pure',fixture==original)
    for event in ['authored','published','ingested','accepted']:
        f=deepcopy(fixture);f['declaration']['declarations'][1]['events'][event]={'status':'unknown','reason':'No timing evidence'}
        mode='system_as_of' if event in ['ingested','accepted'] else 'investor_information'
        value=evaluate(f,mode=mode);witnesses['missing_'+event]=value
        check('missing_'+event,value['status']=='unresolved' and any(v['reason']=='MISSING_OBSERVATION' for v in value['unresolved']))
    f=deepcopy(fixture);f['trusted_observation_hashes']=[]
    value=evaluate(f);witnesses['untrusted_all']=value
    check('self_authored_dates_not_accepted',value['status']=='unresolved' and len(value['unresolved'])==8)
    def change_observation(f,slot,event_key,**changes):
        item=next(d for d in f['declaration']['declarations'] if d['slot']==slot)
        ref=item['events'][event_key];old=ref['observation_sha256'];obj=deepcopy(f['observations'][old]);obj.update(changes)
        h=digest(obj);f['observations'][h]=obj;ref['observation_sha256']=h
        f['trusted_observation_hashes'].append(h)
    f=deepcopy(fixture);change_observation(f,'year:0','published',audience='internal')
    value=evaluate(f);check('private_not_public',value['status']=='unresolved' and any(v['reason']=='PUBLIC_AVAILABILITY_NOT_ESTABLISHED' for v in value['unresolved']))
    f=deepcopy(fixture);change_observation(f,'year:0','published',time='2025-03-07T15:00:00Z',precision='utc_instant')
    for cutoff,status in [('2025-03-07T14:59:59Z','ineligible'),('2025-03-07T15:00:00Z','unresolved')]:
        # Other annual components still have day-precision publication clocks.
        check('one_instant_does_not_resolve_other_days:'+cutoff,evaluate(f,cutoff=cutoff)['status']==status)
    f=deepcopy(fixture);change_observation(f,'year:0','published',time='2025-03-06',precision='calendar_day_utc')
    value=evaluate(f,cutoff='2025-03-08T00:00:00Z')
    check('overlapping_authoring_and_publication_days_unresolved',value['status']=='unresolved' and any(x['reason']=='CHRONOLOGY_ORDER_UNRESOLVED' for x in value['unresolved']))
    for d in f['declaration']['declarations']:
        change_observation(f,d['slot'],'published',time='2025-03-07T15:00:00Z',precision='utc_instant')
    check('all_exact_publication_boundary',evaluate(f,cutoff='2025-03-07T15:00:00Z')['status']=='eligible_synthetic')
    for name in ['second_year_price_revision','first_year_price_revision','unknown_middle_payroll','middle_supplier_failure']:
        changed=paths[name];old_components=components(paths['baseline']);new_components=components(changed)
        affected=[b['slot'] for a,b in zip(old_components,new_components) if a!=b]
        check('one_changed_component:'+name,affected==['year:0' if name=='first_year_price_revision' else 'year:1'])
        f=deepcopy(fixture);f['declaration']['path_sha256']=digest(changed)
        value=evaluate(f,path=changed);check('revision_cannot_reuse_old_definition:'+name,value['status']=='invalid' and 'exact component coverage' in value['detail'])
        replacement=make(changed,exchange_hash)
        for item in f['declaration']['declarations']:
            if item['slot'] in affected:
                item.update(deepcopy(next(d for d in replacement['declaration']['declarations'] if d['slot']==item['slot'])))
                for event in item['events'].values():
                    h=event['observation_sha256'];f['observations'][h]=replacement['observations'][h];f['trusted_observation_hashes'].append(h)
        check('revision_exact_component_replacement:'+name,evaluate(f,path=changed)['status']=='eligible_synthetic')
        for event in ['authored','published','ingested','accepted']:
            change_observation(f,affected[0],event,time={'authored':'2025-04-01T09:00:00Z','published':'2025-04-02','ingested':'2025-04-01T10:00:00Z','accepted':'2025-04-01T11:00:00Z'}[event])
        value=evaluate(f,path=changed);witnesses['late_revision:'+name]=value
        check('late_revision_is_ineligible:'+name,value['status']=='ineligible')
        check('later_revision_becomes_synthetic_eligible:'+name,evaluate(f,path=changed,cutoff='2025-04-03T00:00:00Z')['status']=='eligible_synthetic')
    def invalid(name,change,reason=None):
        f=deepcopy(fixture);change(f);value=evaluate(f);witnesses[name]=value
        check(name,value['status']=='invalid')
        if reason:check(name+':reason',reason in value.get('detail',''))
    invalid('duplicate_slot',lambda f:f['declaration']['declarations'].append(f['declaration']['declarations'][0]),'duplicate component slot')
    invalid('missing_component',lambda f:f['declaration']['declarations'].pop(),'exact component coverage')
    invalid('wrong_path_identity',lambda f:f['declaration'].update(path_sha256='0'*64),'path identity')
    invalid('wrong_exchange_identity',lambda f:f['declaration'].update(exchange_sha256='0'*64),'exchange identity')
    invalid('real_evidence_claim',lambda f:f['declaration'].update(evidence_class='historical_observation'))
    invalid('changed_observation_bytes',lambda f:next(iter(f['observations'].values())).update(time='1900-01-01'),'observation digest mismatch')
    invalid('missing_observation_bytes',lambda f:f['observations'].pop(next(iter(f['observations']))),'observation bytes missing')
    invalid('mismatched_observation_component',lambda f:change_observation(f,'year:0','published',component_sha256='0'*64),'observation component or event mismatch')
    invalid('mismatched_observation_event',lambda f:change_observation(f,'year:0','published',event='accepted'),'observation component or event mismatch')
    invalid('publication_before_authorship',lambda f:change_observation(f,'year:0','published',time='2025-03-01'),'impossible observation chronology')
    invalid('acceptance_before_ingestion',lambda f:change_observation(f,'year:0','accepted',time='2025-03-06T09:30:00Z'),'impossible observation chronology')
    invalid('wrong_date_precision',lambda f:change_observation(f,'year:0','published',time='2025-03-07T00:00:00Z'),'calendar day format')
    invalid('non_utc_observation',lambda f:change_observation(f,'year:0','accepted',time='2025-03-06T11:00:00+01:00'),'UTC instant format')
    for cutoff in [None,'2025-03-08','2025-03-08T00:00:00+00:00','2025-02-30T00:00:00Z']:
        check('invalid_cutoff:'+str(cutoff),evaluate(cutoff=cutoff)['status']=='invalid')
    check('archival_rejects_cutoff',evaluate(mode='archival_exploration')['status']=='invalid')
    check('unknown_view_refused',evaluate(mode='forecast')['status']=='invalid')
    for source_status,expected in [('ineligible','ineligible'),('unresolved','unresolved'),('invalid','invalid'),('unknown_status','invalid')]:
        value=select(paths['baseline'],fixture['declaration'],fixture['observations'],set(fixture['trusted_observation_hashes']),exchange_hash,
            lambda mode,cutoff:{'status':source_status,'real_world_admission':False},'investor_information','2025-03-08T00:00:00Z')
        check('source_cannot_be_bypassed:'+source_status,value['status']==expected)
    f=deepcopy(fixture);change_observation(f,'year:0','published',time='1900-01-01')
    h=f['declaration']['declarations'][1]['events']['published']['observation_sha256'];f['trusted_observation_hashes'].remove(h)
    value=evaluate(f);check('untrusted_backdate_never_grants_access',value['status']=='unresolved')
    for mode in ['investor_information','system_as_of']:
        f=deepcopy(fixture);f['declaration']['declarations'][2]['events']['authored']={'status':'unknown','reason':'Unknown authoring time'}
        check('authorship_required:'+mode,evaluate(f,mode=mode)['status']=='unresolved')
    for mode,cutoff,status in [('investor_information','2025-03-08T00:00:00Z','eligible_synthetic'),('system_as_of','2025-03-06T11:00:00Z','eligible_synthetic')]:
        value=query(exchange,raw,'baseline',fixture['declaration'],fixture['observations'],set(fixture['trusted_observation_hashes']),exchange_hash,validate,source,mode,cutoff)
        witnesses['integrated_'+mode]=value;check('integrated_'+mode,value['status']==status and not value['forecast_admission'])
    fake=deepcopy(exchange);fake['profile']='untrusted'
    value=query(fake,raw,'baseline',fixture['declaration'],fixture['observations'],set(fixture['trusted_observation_hashes']),exchange_hash,validate,source,'investor_information','2025-03-08T00:00:00Z')
    check('modified_exchange_refused',value['status']=='invalid' and 'trusted exchange lock' in value['detail'])
    for name,validator,reason in [('absent_path',validate,'path membership'),
        ('baseline',lambda p,b,r:{'status':'validated_synthetic_exchange','verification_level':'content_binding_only'},'exchange semantic admission')]:
        value=query(exchange,raw,name,fixture['declaration'],fixture['observations'],set(fixture['trusted_observation_hashes']),exchange_hash,validator,source,'investor_information','2025-03-08T00:00:00Z')
        check('integrated_refusal:'+reason,value['status']=='invalid' and reason in value['detail'])
    if (HERE/'baseline.json').exists():
        protected=json.loads((HERE/'baseline.json').read_text())
        check('protected_inputs_unchanged',all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in protected.items()))
    return {'checks':checks,'passed':all(c['passed'] for c in checks),'witnesses':witnesses},fixture


class PathSupport:
    @staticmethod
    def baseline_packet():return json.loads((support.BASE/'packet.json').read_text())


def main():
    p=argparse.ArgumentParser();p.add_argument('--record',action='store_true');args=p.parse_args()
    target=HERE/'checks.json'
    if args.record and target.exists():raise RuntimeError('Evidence exists; use read-only verification')
    if args.record:
        protected={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in EXCHANGE.iterdir() if p.is_file()}
        protected.update(json.loads((EXCHANGE/'baseline.json').read_text()))
        (HERE/'baseline.json').write_text(json.dumps(protected,indent=2)+'\n')
    started=datetime.now(timezone.utc).isoformat();clock=time.perf_counter();evidence,fixture=conformance()
    if args.record:
        for name,value in [('checks.json',evidence),('fixture.json',fixture),('schema.json',schema()),('observation-schema.json',observation_schema())]:
            (HERE/name).write_text(json.dumps(value,indent=2)+'\n')
        manifest={'started_utc':started,'wall_seconds':time.perf_counter()-clock,
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-information-20261023/verify.py --record',
            'environment':'system Python '+platform.python_version()+'; jsonschema; trusted local replay',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES='+str(os.environ.get('CUDA_VISIBLE_DEVICES')),
            'data_version':json.loads((HERE/'baseline.json').read_text()),'random_seeds':'N/A: deterministic',
            'plan':'docs/plans/accounting-company-information-20261023.md',
            'result':'data/accounting-master/company-information-20261023/result.md',
            'files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file()}}
        (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    elif target.exists():
        if evidence!=json.loads(target.read_text()):raise AssertionError('Evidence replay mismatch')
        if fixture!=json.loads((HERE/'fixture.json').read_text()):raise AssertionError('Fixture replay mismatch')
        if schema()!=json.loads((HERE/'schema.json').read_text()):raise AssertionError('Schema mismatch')
        if observation_schema()!=json.loads((HERE/'observation-schema.json').read_text()):raise AssertionError('Observation schema mismatch')
    failed=[x['name'] for x in evidence['checks'] if not x['passed']]
    print(json.dumps({'checks':len(evidence['checks']),'passed':not failed,'failed':failed,'recorded':args.record}))
    return bool(failed)


if __name__=='__main__':raise SystemExit(main())
