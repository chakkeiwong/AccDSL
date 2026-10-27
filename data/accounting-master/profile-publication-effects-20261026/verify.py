"""Deterministic documentary conformance, with separately checked crash worlds."""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import subprocess
import time
from descriptor import Descriptor, Refusal, canonical, refs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PDF = ROOT / 'docs/design/proposal/manuscript-authoring-scope-20261026/accounting-product-proposal.pdf'
PDF_HASH = 'e463820a696aefed8acdd5b142178bbbaa01eab2f0185b32ef4e21a84e7591eb'

def check(condition, message):
    if not condition:
        raise AssertionError(message)

def body(packet, ref):
    return packet['record_registry'][ref['digest']]['body']

def rebody(packet, ref, value):
    """Make a well-hashed changed record, avoiding digest-only negative tests."""
    record = deepcopy(packet['record_registry'][ref['digest']])
    record['body'] = value
    record['dependencies'] = sorted({canonical(r): r for r in refs(value)}.values(), key=canonical)
    digest = sha256(('accdsl.portable.v1/' + record['schema']).encode() + b'\x00' + canonical(record)).hexdigest()
    packet['record_registry'][digest] = record
    return dict(ref, digest=digest)

def replace_response(packet, lock, exchange, changed):
    response_ref = rebody(packet, exchange['response_ref'], changed)
    exchange['response_ref'] = response_ref
    reader = Descriptor(packet, lock)
    before, after = exchange['world_before'], exchange['world_after']
    key = reader.legacy_key(body(packet, exchange['request_ref']))
    idx = reader.config['index']
    if key not in before[idx] and key in after[idx]:
        entry = after[idx][key]
        entry['response_ref'] = response_ref
        entry['receipt_ref'] = changed.get('receipt_ref')
        after['published_records'] = sorted(set(before['published_records']) | set(reader.closure([response_ref])))

def check_effects(reader, exchange, described):
    before, after = exchange['world_before'], exchange['world_after']
    response = reader.body(exchange['response_ref'])
    check(described['request_ref'] == exchange['request_ref'], 'request lost')
    check(described['profile_ref'] == reader.profile_ref, 'profile lost')
    check(described['execution_admission'] is False, 'execution admitted')
    if exchange['response_ref']['kind'] == 'TransportObservation':
        check(described['publication_knowledge'] == 'unknown' and described['effects'] is None, 'unknown normalized')
        return
    effects = described['effects']
    index = reader.config['index']
    new_keys = set(after[index]) - set(before[index])
    check(effects['record_publication'] == bool(new_keys), 'publication differs from index')
    changed = {k for k in before if before[k] != after[k]}
    check(set(effects['world_changes']) == changed, 'world delta incomplete')
    check(set(effects['unchanged_world_fields']) == set(before) - changed, 'unchanged fields incomplete')
    for field in changed:
        check(effects['world_changes'][field] == {'before':before[field], 'after':after[field]}, 'world delta differs')
    check(effects['journal_additions'] == after['journals'][len(before['journals']):], 'journal delta differs')
    check(described['receipt_ref'] == response['receipt_ref'], 'receipt lost')
    if described['disposition'] in {'replayed', 'rejected'}:
        check(not changed and not effects['record_publication'] and not effects['query_publication'], 'retry/refusal effect')
    if reader.name.endswith('assessment'):
        check(effects['query_publication'] == bool(new_keys), 'query not represented')
        check(not effects['component_head_changes'] and not effects['legal_account_head_changed'] and not effects['journal_additions'], 'query posted')

def check_crashes(reader, packet, sink):
    by_id = {x['id']:x for x in packet['exchanges']}
    checks = []
    if reader.name in {'insurance','group'}:
        for crash in packet['crash_worlds']:
            original = by_id[crash['publication_id']]
            committed = crash.get('committed', crash.get('commit_happened'))
            hidden = crash.get('world_after_crash',crash.get('world_after'))
            retry = by_id[crash.get('recovery_id',crash.get('retry_exchange_id'))]
            check(crash['world_before'] == original['world_before'], 'crash baseline')
            check(hidden == original['world_after' if committed else 'world_before'], 'crash world mismatch')
            observation = reader.transport(crash['observation_ref'],original['request_ref'],original['submission_ref'])
            checks.append((crash['id'],committed,original,hidden,retry,observation))
    else:
        for crash in packet.get('crash_cuts', packet.get('crash_worlds')):
            original = by_id[crash['id']]
            check(crash['before'] == original['world_before'] and crash['after'] == original['world_after'], 'crash binding')
            for committed in (False,True):
                if reader.name == 'bank-assessment':
                    obs_id = crash['id'] + ('.lost-ack' if committed else '.lost-ack-before')
                    retry_id = crash['id'] + ('.recovery' if committed else '.recovery-before')
                else:
                    obs_id = crash['id'] + ('.lost-after' if committed else '.lost-before')
                    retry_id = crash['id'] + ('.retry-after' if committed else '.retry-before')
                obs = by_id[obs_id]
                hidden = crash['after' if committed else 'before']
                # The observation exchange starts after the hidden cut; it does
                # not itself perform the earlier possible publication.
                check(obs['world_before'] == hidden and obs['world_after'] == hidden, 'hidden observation world')
                checks.append((obs_id,committed,original,hidden,by_id[retry_id],reader.describe(obs)))
    for name,committed,original,hidden,retry,observation in checks:
        check(observation['publication_knowledge'] == 'unknown' and observation['effects'] is None, 'hidden state leaked')
        check(retry['request_ref'] == original['request_ref'] and retry['submission_ref'] == original['submission_ref'], 'retry changed identity')
        check(retry['world_before'] == hidden and retry['world_after'] == original['world_after'], 'retry world mismatch')
        d = reader.describe(retry)
        check(d['disposition'] == ('replayed' if committed else reader.body(original['response_ref'])['disposition']), 'retry disposition')
        check(d['effects']['record_publication'] is not committed, 'retry duplicates or loses publication')
        check(d['receipt_ref'] == reader.body(original['response_ref'])['receipt_ref'], 'retry receipt mismatch')
        sink.write(json.dumps({'id':name,'descriptor':observation},sort_keys=True)+'\n')
    return len(checks)

def adversarial(packet, lock):
    reader = Descriptor(packet, lock)
    success = next(x for x in packet['exchanges'] if body(packet,x['response_ref']).get('disposition') in {'completed','partial'})
    replay = next(x for x in packet['exchanges'] if body(packet,x['response_ref']).get('disposition') == 'replayed')
    rejected = next(x for x in packet['exchanges'] if body(packet,x['response_ref']).get('disposition') == 'rejected')
    results = []
    def run(label, base, change, expected):
        altered = dict(packet,record_registry=dict(packet['record_registry']))
        exchange = deepcopy(base)
        change(altered,exchange)
        try:
            Descriptor(altered,lock).describe(exchange)
        except Refusal as exc:
            check(str(exc) == expected, label + ': wrong refusal ' + str(exc))
            results.append({'case':label,'refusal':str(exc)})
        else:
            raise AssertionError(label + ': accepted invalid effects')
    def response_change(change):
        def change_exchange(p,x):
            r=deepcopy(body(p,x['response_ref']));change(r);replace_response(p,lock,x,r)
        return change_exchange
    def flag(r):
        target = r['payload'] if lock['name'] in {'group','bank-assessment'} else r
        target['additional_commit'] = not target['additional_commit']
    run('well_hashed_native_flag',success,response_change(flag),'native_flag_mismatch')
    run('well_hashed_missing_receipt',success,response_change(lambda r:r.update(receipt_ref=None)),'missing_publication_receipt')
    run('well_hashed_replay_diagnostic',replay,response_change(lambda r:r.update(diagnostics=[{'code':'invented'}])),'changed_replay_metadata')
    run('replay_world_change',replay,lambda p,x:x['world_after']['published_records'].append('invented'),'replay_mutated_world')
    run('refusal_world_change',rejected,lambda p,x:x['world_after']['published_records'].append('invented'),'rejection_mutated_world')
    run('unknown_world_field',success,lambda p,x:x['world_after'].update(hidden_owner={}), 'world_shape')
    protected = 'unrelated_heads' if lock['name'] in {'insurance','group'} else 'accounting_heads'
    run('protected_owner_change',success,lambda p,x:x['world_after'][protected].update(invented={}), 'unauthorized_world_change')
    run('missing_published_record',success,lambda p,x:x['world_after']['published_records'].pop(), 'publication_closure')
    run('invented_journal',success,lambda p,x:x['world_after']['journals'].append({'invented':True}),
        'unauthorized_world_change' if lock['name'].endswith('assessment') else 'journal_delta')
    idx=reader.config['index']; key=reader.legacy_key(body(packet,success['request_ref']))
    def replace_index(p,x):
        prior=deepcopy(x['world_after'][idx][key]);x['world_before'][idx]['retained_previous']=prior
        x['world_after'][idx]['retained_previous']=dict(prior,receipt_ref=None)
    run('overwritten_previous_decision',success,replace_index,'overwritten_decision')
    def misbind(p,x):
        r=deepcopy(body(p,x['response_ref'])); rec=deepcopy(body(p,r['receipt_ref']))
        rec['request_ref']=rejected['request_ref']; r['receipt_ref']=rebody(p,r['receipt_ref'],rec)
        replace_response(p,lock,x,r)
    run('well_hashed_misbound_receipt',success,misbind,'receipt_request')
    def corrupt(p,x):
        ref=x['response_ref'];p['record_registry'][ref['digest']]=deepcopy(p['record_registry'][ref['digest']])
        p['record_registry'][ref['digest']]['body']['disposition']='invented'
    run('corrupt_digest',success,corrupt,'record_digest_mismatch')
    if lock['name'] in {'group','bank-assessment'}:
        run('well_hashed_false_commit_observation',success,response_change(lambda r:r.update(commit_observation='not_committed')),'native_commit_observation')
    # Observations have no success receipt, and neither hidden outcome is knowledge.
    obs_ref=next({'kind':r['kind'],'schema':r['schema'],'digest':d} for d,r in packet['record_registry'].items() if r['kind']=='TransportObservation')
    obs=body(packet,obs_ref); sub=obs['submission_ref']
    original=next(x for x in packet['exchanges'] if x['submission_ref']==sub)
    sample=dict(original,response_ref=obs_ref)
    knowledge='commit_knowledge' if 'commit_knowledge' in obs else 'commit_observation'
    for value in ('committed','not_committed'):
        run('unknown_ack_as_'+value,sample,response_change(lambda r,v=value:r.update({knowledge:v})),'unknown_acknowledgement_required')
    run('invented_transport_receipt',sample,response_change(lambda r:r.update(receipt_ref=body(packet,success['response_ref'])['receipt_ref'])),'fabricated_transport_receipt')
    hidden=deepcopy(sample);hidden['world_before']={'hidden':'unavailable'};hidden['world_after']={'committed':True}
    check(reader.describe(hidden)==reader.describe(sample),'descriptor inspected hidden worlds')
    results.append({'case':'hidden_world_independence','verdict':'same_unknown_descriptor'})
    # Replay still requires retained original publication evidence.
    def lose_prior(p,x):
        x['world_before']['published_records']=[];x['world_after']['published_records']=[]
    run('replay_missing_original_publication',replay,lose_prior,'replay_missing_publication')
    return results

def main():
    started=time.monotonic()
    check(os.environ.get('CUDA_VISIBLE_DEVICES')=='-1','CPU hiding required')
    lock=json.loads((HERE/'source-lock.json').read_text())
    check(sha256(PDF.read_bytes()).hexdigest()==PDF_HASH,'governing PDF changed')
    files={p:h for e in lock['profiles'] for p,h in e['files'].items()}
    for p,h in files.items():check(sha256((ROOT/p).read_bytes()).hexdigest()==h,'source changed:'+p)
    profiles=[]
    for entry in lock['profiles']:
        packet=json.loads((ROOT/entry['packet']).read_text());reader=Descriptor(packet,entry)
        counts=Counter();effect_counts=Counter();wire_count=0
        for submission_ref in {x['submission_ref']['digest']:x['submission_ref'] for x in packet['exchanges']}.values():
            sub=reader.body(submission_ref); blob=sub.get('blob_ref',sub.get('wire_blob'))
            raw=(ROOT/packet['blobs'][blob['digest']]['path']).read_bytes()
            check(sha256(raw).hexdigest()==blob['digest'] and len(raw)==blob['byte_length'],'wire blob changed');wire_count+=1
        output=HERE/(entry['name']+'-descriptors.jsonl')
        with output.open('w') as sink:
            for exchange in packet['exchanges']:
                d=reader.describe(exchange);check_effects(reader,exchange,d);counts[d['disposition']]+=1
                if d['effects'] is not None:
                    for field in ('record_publication','query_publication','component_head_changes','legal_account_head_changed','journal_additions'):
                        effect_counts[field]+=bool(d['effects'][field])
                sink.write(json.dumps({'id':exchange['id'],'descriptor':d},sort_keys=True)+'\n')
        with (HERE/(entry['name']+'-crash-observations.jsonl')).open('w') as sink:
            crashes=check_crashes(reader,packet,sink)
        negative=adversarial(packet,entry)
        profiles.append({'profile':entry['name'],'exchanges':len(packet['exchanges']),'dispositions':dict(counts),
            'invocation_effect_counts':dict(effect_counts),'verified_submission_blobs':wire_count,
            'crash_worlds_and_retries':crashes,'adversarial':negative,'descriptor_file':str(output.relative_to(ROOT))})
    for p,h in files.items():check(sha256((ROOT/p).read_bytes()).hexdigest()==h,'source changed after run:'+p)
    check(sha256(PDF.read_bytes()).hexdigest()==PDF_HASH,'governing PDF changed after run')
    report={'status':'passed_bounded_documentary_conformance','profiles':profiles,'source_files_preserved':len(files),
        'total_exchanges':sum(p['exchanges'] for p in profiles),'total_crash_worlds':sum(p['crash_worlds_and_retries'] for p in profiles),
        'adversarial_checks':sum(len(p['adversarial']) for p in profiles),'governing_pdf_sha256':PDF_HASH,'readiness':'not_ready'}
    (HERE/'checks.json').write_text(json.dumps(report,indent=2)+'\n')
    artifacts={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in HERE.iterdir() if p.is_file() and p.suffix in {'.py','.jsonl'} or p.is_file() and p.name in {'checks.json','source-lock.json','contract.md','recovery-note.md'}}
    manifest={'git_commit':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip(),
        'command':'CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/profile-publication-effects-20261026/verify.py',
        'environment':{'python':platform.python_version(),'executable':__import__('sys').executable,'libraries':'standard library'},
        'cpu_gpu':'CPU only; GPU intentionally hidden; no GPU libraries imported','random_seeds':'N/A: deterministic',
        'wall_seconds':round(time.monotonic()-started,3),'data_version':'exact retained packets in source-lock.json',
        'plan':lock['plan'],'result':'data/accounting-master/profile-publication-effects-20261026/result.md','artifacts':artifacts}
    (HERE/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='profiles'},sort_keys=True))

if __name__=='__main__':
    main()
