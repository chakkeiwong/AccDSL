"""Full effects and composition checks for exact adopted-profile providers."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import ast
import json
import os
import subprocess
import sys
import time
import providers as p
from schema_descriptor import Refusal as SchemaRefusal

HERE, ROOT, MASTER, old = p.HERE, p.ROOT, p.MASTER, p.old

def dump(name, value):
    (HERE / name).write_text(json.dumps(value, indent=2) + '\n')

def main():
    start = time.monotonic()
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == '-1'
    checks, controls, compositions, effects = [], [], [], []
    def check(name, condition):
        checks.append({'check': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)
    def refused(name, action, expected=None):
        try:
            action()
        except (old.Invalid, old.Refusal, SchemaRefusal, p.insurance.n.Refusal, p.insurance.idx.Refusal, p.bank.n.Refusal) as error:
            code = getattr(error, 'code', str(error))
            controls.append({'control': name, 'observed': code})
            check(name, expected is None or code == expected)
        else:
            raise AssertionError(name + ':accepted')
    lock = json.loads((HERE / 'source-lock.json').read_text())
    def preserve():
        for name, h in lock.items():
            check('preserved:' + name, p.sha(ROOT / name) == h)
    preserve()
    delta = json.loads((HERE / 'reader-delta.json').read_text())
    original = (ROOT / delta['descriptor_source']).read_text()
    transformed = original.replace('class Descriptor:', 'class SchemaBoundDescriptor:', 1)
    for change in delta['schema_replacements']:
        check('schema_expression_count:' + change['old'], transformed.count(change['old']) == change['count'])
        transformed = transformed.replace(change['old'], change['new'])
    check('exact_descriptor_delta', (HERE / 'schema_descriptor.py').read_text() == transformed)
    original = (ROOT / delta['composition_source']).read_text()
    node = next(x for x in ast.parse(original).body if isinstance(x, ast.FunctionDef) and x.name == 'assess')
    original_function = '\n'.join(original.splitlines()[node.lineno-1:node.end_lineno])
    adapted = (HERE / 'composition_assess.py').read_text()
    node = next(x for x in ast.parse(adapted).body if isinstance(x, ast.FunctionDef) and x.name == 'assess')
    actual = '\n'.join(adapted.splitlines()[node.lineno-1:node.end_lineno])
    check('exact_composition_delta', actual == original_function.replace(delta['composition_inserted_before'], delta['composition_replacement']))

    library = p.Library()
    hashes = {e['name']: h for h,e in library.entries.items() if h not in library.adopted}
    # All previously saved source, source maps and complete assessments remain exact.
    legacy_files = sorted((MASTER / 'profile-composition-boundary-20261026/examples').glob('*.json'))
    for path in legacy_files:
        record = json.loads(path.read_text())
        source = path.with_suffix('.accdsl').read_text()
        got = p.compile_text(source, library)
        check('legacy_complete:' + path.stem, got == record)
    check('legacy_coverage', len(legacy_files) == 77)
    print(json.dumps({'phase':'legacy_composition','exact_results':len(legacy_files)}),flush=True)

    ih = library.insurance_hash
    reader = library.readers[ih]
    legacy_reader = library.readers[hashes['insurance']]
    legacy_effects = {row['id']:row['descriptor'] for row in map(json.loads,(MASTER/'profile-publication-effects-20261026/insurance-descriptors.jsonl').read_text().splitlines())}
    legacy_transport = {row['id']:row['descriptor'] for row in map(json.loads,(MASTER/'profile-publication-effects-20261026/insurance-crash-observations.jsonl').read_text().splitlines())}
    def pair_index(index):
        result = {}
        for entry in index.values():
            request = reader.body(entry['request_ref'])
            result[old.canonical([request['client_id'],request['request_id']]).decode()] = deepcopy(entry)
        return result
    insurer_counts = Counter()
    for key, exchange in reader.exchanges.items():
        descriptor = library.select({'packet_sha256': ih, 'exchange_id': key})[2]
        origin = reader.origins[id(exchange)]
        check('insurer_policy_visible:' + key, descriptor['execution_binding']['identity_policy_ref'] == reader.native.policy_ref)
        if origin['kind'] == 'native_transport':
            expected = deepcopy(legacy_transport[origin['label']])
            expected.update(schema='PublicationEffects/2', source_packet=descriptor['source_packet'], source_packet_sha256=ih, execution_binding=descriptor['execution_binding'])
            check('complete_transport:' + key, descriptor == expected and descriptor['effects'] is None and descriptor['publication_knowledge']=='unknown')
            insurer_counts['transport'] += 1
        elif origin['ordinal'] < 672:
            expected = deepcopy(legacy_effects[origin['label']])
            expected.update(schema='PublicationEffects/2', source_packet=descriptor['source_packet'], source_packet_sha256=ih, execution_binding=descriptor['execution_binding'],
                            world_before_sha256=sha256(old.canonical(exchange['world_before'])).hexdigest(),
                            world_after_sha256=sha256(old.canonical(exchange['world_after'])).hexdigest())
            expected['effects']['unchanged_world_fields'] = sorted(expected['effects']['unchanged_world_fields'] + ['identity_profile_ref'])
            if 'decisions' in expected['effects']['world_changes']:
                for field in ('before','after'):
                    expected['effects']['world_changes']['decisions'][field] = pair_index(expected['effects']['world_changes']['decisions'][field])
            check('complete_insurer_effects:' + key, descriptor == expected)
            insurer_counts['retained_exchanges'] += 1
        else:
            before,after = exchange['world_before'],exchange['world_after']
            expected_changes = {k:dict(before=deepcopy(before[k]),after=deepcopy(after[k])) for k in before if before[k]!=after[k]}
            check('new_complete_effects:' + key, descriptor['effects']['world_changes']==expected_changes and
                  descriptor['effects']['journal_additions']==after['journals'][len(before['journals']):])
            insurer_counts['new_exchanges'] += 1
        effects.append({'provider':ih,'exchange':key,'descriptor':descriptor})
    check('unique_ordinal_imports', len(reader.exchanges)==854 and len({old.canonical(x['descriptor']['execution_binding']['source_origin']) for x in effects})==854)
    print(json.dumps({'phase':'insurer_effects',**insurer_counts}),flush=True)

    bank_count=0
    for name,h in library.bank_hashes.items():
        for field in ('exchange','replay'):
            spec=library.adopted[h]
            packet=json.loads(spec['path'].read_text())
            if field not in packet:continue
            br,exchange,descriptor=library.select({'packet_sha256':h,'exchange_id':field})
            before,after=exchange['world_before'],exchange['world_after']
            changes={k:dict(before=deepcopy(before[k]),after=deepcopy(after[k])) for k in before if before[k]!=after[k]}
            check('bank_complete_world_effects:'+name+':'+field, descriptor['effects']['world_changes']==changes)
            check('bank_no_financial_effects:'+name+':'+field, not descriptor['effects']['component_head_changes'] and not descriptor['effects']['legal_account_head_changed'] and not descriptor['effects']['journal_additions'] and all(before[k]==after[k] for k in ('accounting_heads','journals','unrelated_owners')))
            check('bank_mixed_schema_binding:'+name+':'+field, descriptor['execution_binding']['schema_ids']['Submission']=='accdsl.bank-assessment.submission.v1' and descriptor['profile_ref']['schema']=='accdsl.bank-assessment-exact-time.profile.v1')
            check('bank_exact_native_metadata:'+name+':'+field, descriptor['native_metadata']=={k:deepcopy(br.body(exchange['response_ref'])[k]) for k in descriptor['native_metadata']})
            effects.append({'provider':h,'exchange':field,'descriptor':descriptor})
            bank_count+=1
    print(json.dumps({'phase':'bank_effects','packages':len(library.bank_hashes),'descriptions':bank_count}),flush=True)

    def stage(identity,h,key):return {'id':identity,'packet_sha256':h,'exchange_id':key}
    def edge(a,b,relation='sequence',left=None,right=None):return {'from':a,'to':b,'relation':relation,'produced_path':left or [],'consumed_path':right or []}
    def check_plan(name,stages,edges,expected):
        plan={'profile':old.PROFILE,'name':name,'stages':stages,'dependencies':edges}
        text=old.render(plan);typed=p.assess(plan,library);compiled=p.compile_text(text,library)
        check('text_typed:'+name, compiled['assessment']==typed and compiled['plan']==plan)
        check('composition_status:'+name, typed['status']==expected)
        check('source_CRLF:'+name, old.parse(text.replace('\n','\r\n'))[0]==plan)
        check('admission_false:'+name, not any(typed[k] for k in ('execution_admission','source_admission','accounting_admission','concurrent_execution_admission')))
        compositions.append({'plan':plan,'source':text,'source_map':compiled['source_map'],'assessment':typed})
        return typed
    # Reuse exact retained compatible chains with their policy and full worlds.
    first_keys={e['id']:key for key,e in list(reader.exchanges.items())[:672]}
    insurance_chains=0
    for path in legacy_files:
        record=json.loads(path.read_text());plan=record['plan']
        if not plan['name'].startswith('insurance:'):continue
        stages=[stage(s['id'],ih,first_keys[s['exchange_id']]) for s in plan['stages']]
        check_plan('adopted:'+plan['name'],stages,plan['dependencies'],'documentary_consistent')
        insurance_chains+=1
    for name,h in library.bank_hashes.items():
        packet=json.loads(library.adopted[h]['path'].read_text())
        if 'replay' not in packet:continue
        _,_,d=library.select(stage('a',h,'exchange'))
        expected='unresolved' if d['disposition']=='partial' else 'documentary_consistent'
        check_plan('bank-replay:'+name,[stage('a',h,'exchange'),stage('b',h,'replay')],[edge('a','b')],expected)
    akey=first_keys['acquisition-allocated'];reportkey=first_keys['acquisition-allocated.report']
    mismatch=check_plan('legacy_to_adopted_policy',[stage('old',hashes['insurance'],'acquisition-allocated'),stage('new',ih,reportkey)],[edge('old','new')],'unsupported')
    check('explicit_policy_mismatch_reason',mismatch['findings'][0]['reason']=='execution_policy_adapter_missing')
    check_plan('same_decision_across_policies',[stage('old',hashes['insurance'],'acquisition-allocated'),stage('new',ih,akey)],[],'invalid')
    unknown=next(k for k in reader.exchanges if k.startswith('transport.') and k.endswith('acquisition-allocated.lost-ack-committed'))
    recovery=first_keys['acquisition-allocated.lost-ack-committed'];replay=first_keys['acquisition-allocated.replay']
    chain=check_plan('adopted_unknown_propagation',[stage('a',ih,unknown),stage('b',ih,recovery),stage('c',ih,replay)],[edge('a','b'),edge('b','c')],'unresolved')
    check('unknown_all_dependents',all(x['status']=='unresolved' for x in chain['dependency_availability'].values()))
    check_plan('adopted_cross_profile_state',[stage('component',ih,akey),stage('assessment',hashes['insurance-assessment'],'route.full')],[edge('component','assessment','state',['heads','accounts'],['accounting_heads','Synthetic/Legal'])],'unsupported')
    check_plan('adopted_false_receipt_handoff',[stage('a',ih,akey),stage('b',ih,reportkey)],[edge('a','b','receipt')],'invalid')
    check_plan('adopted_partial_state',[stage('a',ih,first_keys['group-unknown']),stage('b',ih,reportkey)],[edge('a','b','state',['heads','accounts'],['heads','accounts'])],'unresolved')
    check_plan('adopted_refused_source',[stage('a',ih,first_keys['acquisition-allocated.conflict']),stage('b',ih,reportkey)],[edge('a','b')],'invalid')
    check_plan('adopted_unexplained_world_change',[stage('a',ih,akey),stage('b',ih,first_keys['gmm-half-service.report'])],[edge('a','b')],'invalid')

    refused('display_label_is_not_import_id',lambda:library.select(stage('a',ih,'identity-first')),'unresolved_exchange_import')
    refused('unknown_packet',lambda:library.select(stage('a','0'*64,'exchange')),'unresolved_packet_import')
    source=p.AdoptedReader(library.adopted[ih]['path'],'insurance')
    e=source.exchanges[first_keys['acquisition-allocated.replay']]
    e['world_before'].pop('identity_profile_ref');e['world_after'].pop('identity_profile_ref')
    refused('dropped_identity_binding',lambda:source.describe(e),'identity_policy_binding')
    source=p.AdoptedReader(library.adopted[ih]['path'],'insurance')
    e=source.exchanges[akey];e['world_after']['heads']['accounts']=e['world_before']['heads']['accounts']
    refused('hidden_financial_head_change',lambda:source.describe(e),'partial_publication')
    source=p.AdoptedReader(library.adopted[ih]['path'],'insurance')
    e=source.exchanges[first_keys['acquisition-allocated.replay']];e['world_after']['journals']+=deepcopy(e['world_after']['journals'])
    refused('duplicate_posting_on_replay',lambda:source.describe(e),'duplicate_commit')
    source=p.AdoptedReader(library.adopted[ih]['path'],'insurance')
    refused('unbound_exchange_copy',lambda:source.describe(deepcopy(source.exchanges[akey])),'unbound_provider_exchange')
    bank_path=library.adopted[library.bank_hashes['capital.final']]['path']
    source=p.AdoptedReader(bank_path,'bank');source.schema_ids['Submission']='accdsl.bank-assessment-exact-time.submission.v1'
    refused('invented_uniform_bank_schema',lambda:source.describe(source.exchanges['exchange']),'unsupported_submission_schema')
    source=p.AdoptedReader(bank_path,'bank');source.exchanges['exchange']['world_after']['journals'].append({'invented':'posting'})
    refused('bank_query_cannot_post',lambda:source.describe(source.exchanges['exchange']))
    # Validate artifacts by re-reading exact saved assessments and fresh readers.
    dump('compositions.json',compositions)
    with (HERE/'effects.jsonl').open('w') as stream:
        for row in effects:stream.write(json.dumps(row,sort_keys=True,separators=(',',':'))+'\n')
    fresh=p.Library()
    for row in json.loads((HERE/'compositions.json').read_text()):
        check('saved_composition_recomputed',p.compile_text(row['source'],fresh)=={'plan':row['plan'],'source_map':row['source_map'],'assessment':row['assessment']})
    saved_effects=0
    with (HERE/'effects.jsonl').open() as stream:
        for line in stream:
            row=json.loads(line)
            actual=fresh.select(stage('replay',row['provider'],row['exchange']))[2]
            check('saved_effect_recomputed',actual==row['descriptor'])
            saved_effects+=1
    preserve()
    result=dict(passed=True,legacy_complete_compositions=len(legacy_files),insurer_retained_effects=insurer_counts['retained_exchanges'],
                insurer_new_effects=insurer_counts['new_exchanges'],insurer_unknown_observations=insurer_counts['transport'],
                bank_packages=len(library.bank_hashes),bank_effects=bank_count,adopted_compositions=len(compositions),
                native_insurer_chains=insurance_chains,boundary_controls=len(controls),saved_effects_recomputed=saved_effects,
                protected_files=len(lock),source_admission=False,accounting_admission=False,execution_admission=False,
                checks=len(checks),production_ready=False)
    dump('checks.json',result);dump('controls.json',controls);dump('check-detail.json',checks)
    dump('run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/adopted-profile-effects-20261026/verify.py',
         environment=sys.version,cpu_gpu='CPU; GPU intentionally hidden; no GPU framework imported',random_seeds='N/A deterministic exact conformance',
         wall_seconds=time.monotonic()-start,timestamp_utc=datetime.now(timezone.utc).isoformat(),data_version=p.sha(HERE/'source-lock.json'),
         plan_file='docs/plans/accounting-adopted-profile-effects-20261026.md',result_file=str((HERE/'result.md').relative_to(ROOT)),
         artifact_paths=['effects.jsonl','compositions.json','checks.json','controls.json','source-lock.json','reader-delta.json']))
    print(json.dumps(result),flush=True)

if __name__=='__main__':
    try:main()
    except Exception as error:
        dump('last-failure.json',dict(type=type(error).__name__,code=getattr(error,'code',str(error))))
        raise
