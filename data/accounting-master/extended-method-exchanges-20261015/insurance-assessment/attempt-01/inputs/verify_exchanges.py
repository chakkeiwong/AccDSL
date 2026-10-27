"""Independent exact documentary auditor; no builder or fixture imports."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import time
from jsonschema import Draft202012Validator, FormatChecker
from mathematical_checks import derive, expected_model, num, Refusal as MathRefusal
from source_policy import SOURCES, METHOD_SOURCE, METHOD_ANCHOR
from schema_design import schemas, METHODS, OP

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
class Refusal(Exception):
    def __init__(self,code): self.code=code; super().__init__(code)
def need(ok,code):
    if not ok: raise Refusal(code)
def enc(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(v): return hashlib.sha256(v).hexdigest()
def pairs(rows):
    d={}
    for k,v in rows:
        need(k not in d,'DUPLICATE_KEY'); d[k]=v
    return d
def nofloat(v): raise Refusal('FLOAT_FORBIDDEN')
def nonfinite(v): raise Refusal('NONFINITE_FORBIDDEN')
def decode(raw):
    try: return json.loads(raw,object_pairs_hook=pairs,parse_float=nofloat,parse_constant=nonfinite)
    except (ValueError,UnicodeError): raise Refusal('INVALID_JSON')
def references(v):
    if isinstance(v,dict):
        if set(v)=={'kind','schema','digest'}: yield v
        else:
            for x in v.values(): yield from references(x)
    elif isinstance(v,list):
        for x in v: yield from references(x)
def blobs(v):
    if isinstance(v,dict):
        if set(v)=={'kind','algorithm','digest','byte_length'}: yield v
        else:
            for x in v.values(): yield from blobs(x)
    elif isinstance(v,list):
        for x in v: yield from blobs(x)
def unique(rs): return [v for k,v in sorted({enc(r):r for r in rs}.items())]
def hygiene(v):
    need(not isinstance(v,float),'FLOAT_FORBIDDEN')
    if isinstance(v,dict):
        if set(v)=={'n','d'}:
            try: num(v)
            except (MathRefusal,ValueError,ZeroDivisionError,TypeError): raise Refusal('NONCANONICAL_RATIONAL')
        for x in v.values(): hygiene(x)
    elif isinstance(v,list):
        for x in v: hygiene(x)
def instant(v): return datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(timezone.utc)

class Auditor:
    def __init__(self,attempt):
        self.attempt=attempt
        self.packet=decode((attempt/'portable-exchanges.json').read_bytes())
        self.reg=self.packet['record_registry']; self.alias=self.packet['aliases']; self.blobs=self.packet['blobs']
        self.schema=decode((attempt/'record-schemas.json').read_bytes())
        self.validators={k:Draft202012Validator(v,format_checker=FormatChecker()) for k,v in self.schema['$defs'].items()}
        self.checks=[]; self.source_cache={}
    def audit(self,label,fn):
        try: fn(); self.checks.append(dict(check=label,passed=True))
        except Exception as e: self.checks.append(dict(check=label,passed=False,diagnostic=getattr(e,'code',type(e).__name__),detail=str(e)[:240]))
    def record(self,r):
        need(r['digest'] in self.reg,'MISSING_REFERENCE'); v=self.reg[r['digest']]
        need(v['kind']==r['kind'] and v['schema']==r['schema'],'REFERENCE_TYPE_MISMATCH'); return v
    def body(self,r): return self.record(r)['body']
    def closure(self,roots):
        seen=set(); visiting=set()
        def visit(r):
            d=r['digest']
            if d in seen: return
            need(d not in visiting,'DEPENDENCY_CYCLE'); visiting.add(d)
            for child in self.record(r)['dependencies']: visit(child)
            visiting.remove(d); seen.add(d)
        for r in roots: visit(r)
        return sorted(seen)
    def blob_bytes(self,b):
        need(b['digest'] in self.blobs,'MISSING_BLOB'); meta=self.blobs[b['digest']]
        p=(ROOT/meta['path']).resolve(); need(p.is_relative_to(ROOT),'BLOB_PATH_SCOPE')
        raw=p.read_bytes(); need(sha(raw)==b['digest'] and len(raw)==b['byte_length']==meta['byte_length'],'BLOB_HASH_MISMATCH')
        return raw
    def shape(self,r,digest=None):
        need(set(r)=={'kind','schema','key','revision','body','dependencies'},'CLOSED_RECORD_SHAPE')
        k=r['kind']; need(k in self.validators and r['schema']==self.schema['schema_ids'][k],'CLOSED_RECORD_SHAPE')
        need(type(r['revision']) is int and r['revision']==0 and isinstance(r['key'],str) and re.fullmatch('[A-Za-z0-9_.:@/-]+',r['key']),'CLOSED_RECORD_SHAPE')
        need(not list(self.validators[k].iter_errors(r['body'])),'CLOSED_RECORD_SHAPE'); hygiene(r)
        need(r['dependencies']==unique(references(r['body'])),'DEPENDENCY_MISMATCH')
        for ref in references(r['body']): self.record(ref)
        for b in blobs(r['body']): self.blob_bytes(b)
        if digest is not None: need(sha(('accdsl.portable.v1/'+r['schema']).encode()+b'\0'+enc(r))==digest,'RECORD_DIGEST_MISMATCH')
    def preservation(self):
        raw=(HERE/'predecessor-lock.json').read_bytes()
        need(sha(raw)=='0791324322f4622ba9b14be7ff437c8eefd437181d9f5174d8ed416fe46b80d9','PROTECTION_LOCK_CHANGED')
        lock=decode(raw); original=ROOT/lock['original_protection_manifest']
        need(sha(original.read_bytes())==lock['original_manifest_sha256'],'ORIGINAL_MANIFEST_CHANGED')
        for row in decode(original.read_bytes())['files']:
            need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'ORIGINAL_CHANGED:'+row['path'])
            need(sha((ROOT/row['snapshot']).read_bytes())==row['sha256'],'SNAPSHOT_CHANGED:'+row['path'])
        for row in lock['predecessor_files']:
            need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'PREDECESSOR_CHANGED:'+row['path'])
        need(sha((ROOT/lock['previous_lock_path']).read_bytes())==lock['previous_lock_sha256'],'PREVIOUS_LOCK_CHANGED')
        need(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==lock['git_commit'],'HEAD_CHANGED')
        index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
        need(sha(index)==lock['index_sha256'] and len(index.splitlines())==lock['index_entries']==100,'STAGED_INDEX_CHANGED')
    def source_body(self,key):
        if key in self.source_cache: return self.source_cache[key]
        s=SOURCES[key]
        def b(path):
            raw=(ROOT/path).read_bytes(); return dict(kind='blob',algorithm='sha256',digest=sha(raw),byte_length=len(raw))
        need(sha((ROOT/s['raw']).read_bytes())==s['raw_sha'] and sha((ROOT/s['text']).read_bytes())==s['text_sha'],'PINNED_SOURCE_CHANGED')
        result=dict(raw_blob=b(s['raw']),text_blob=b(s['text']),method_blobs=[b(p) for p in s['methods']],anchors=s['anchors'],temporal_status='retained_historical')
        self.source_cache[key]=result; return result
    def structure(self):
        need(self.schema==schemas(),'SCHEMA_DEFINITION_CHANGED')
        for name,v in self.schema['$defs'].items(): Draft202012Validator.check_schema(v)
        need(len(self.alias)==len(self.reg),'ALIAS_COVERAGE')
        for key,r in self.alias.items(): need(self.record(r)['key']==key,'ALIAS_BINDING')
        for name,s in self.packet['input_snapshots'].items():
            p=ROOT/s['path']; need(p.name==name and sha(p.read_bytes())==s['sha256'],'INPUT_SNAPSHOT_CHANGED')
            need(sha((HERE/name).read_bytes())==s['sha256'],'BUILD_INPUT_CHANGED')
        profile=self.body(self.packet['profile_ref'])
        need(profile['methods']==list(METHODS) and profile['operation']==OP and profile['accounting_effect']=='none','PROFILE_METHODS')
        lock=self.body(profile['schema_lock_ref'])
        need(self.blob_bytes(lock['schema_blob'])==(self.attempt/'record-schemas.json').read_bytes(),'SCHEMA_LOCK_BINDING')
        need(self.blob_bytes(lock['semantic_contract_blob'])==(self.attempt/'inputs/semantic-contract.md').read_bytes(),'CONTRACT_LOCK_BINDING')
        self.blob_bytes(self.packet['predecessor_lock_blob'])
        need(self.packet['predecessor_lock_blob']['digest']==sha((HERE/'predecessor-lock.json').read_bytes()),'PROTECTION_BINDING')
    def basis(self,r):
        b=self.body(r); inp=self.body(b['input_ref']); m=inp['method_id']
        view=self.body(b['view_ref']); ev=self.body(b['evidence_ref']); head=self.body(b['expected_head'])
        need(b['context_ref']==view['context_ref']==ev['context_ref']==head['context_ref'],'CONTEXT_BINDING')
        context=self.body(b['context_ref'])
        need(head['owner_id']==context['entity_id']+'/'+context['book_id'],'CONTEXT_BINDING')
        need(b['evidence_ref'] in view['evidence_refs'],'EVIDENCE_VIEW_BINDING')
        need(instant(ev['available_at'])<=instant(view['decision_at']) and instant(ev['ingested_at'])<=instant(view['system_asof']),'EVIDENCE_NOT_AVAILABLE')
        need(self.blob_bytes(ev['facts_blob'])==enc(inp),'EVIDENCE_FACTS_BINDING')
        need(self.body(b['source_ref'])==self.source_body(METHOD_SOURCE[m]) and b['method_anchor']==METHOD_ANCHOR[m],'SOURCE_BINDING')
        need(b['method_anchor'] in self.body(b['source_ref'])['anchors'],'SOURCE_BINDING')
        need(self.body(b['model_ref'])==expected_model(inp),'MODEL_BINDING')
        priors=b['prior_assessment_refs']
        if m=='transition.opening@1' and num(inp['embedded_recovery'])!=0:
            need(len(priors)==1,'PRIOR_RECOVERY_BINDING'); p=self.body(priors[0])
            need(p['method_id']=='transition.recovery@1' and p['status']=='resolved','PRIOR_RECOVERY_BINDING')
            self.assessment(priors[0]); pb=self.body(p['basis_ref']); pi=self.body(pb['input_ref'])
            po=p['detail']; match=next((g for g in derive(inp)['detail']['groups'] if g['group_id']==pi['covered_group']),None)
            need(pb['context_ref']==b['context_ref'] and pi['mode']=='transition' and pi['transition_date']==inp['transition_date'],'PRIOR_RECOVERY_BINDING')
            need(match is not None and pi['group_loss']==match['loss_component'],'PRIOR_RECOVERY_BINDING')
            need(po['loss_recovery']==inp['embedded_recovery'] and po['measured_held_asset']==inp['new_held_asset'],'PRIOR_RECOVERY_BINDING')
            pv=self.body(pb['view_ref'])
            need(instant(pv['decision_at'])<=instant(view['decision_at']) and instant(pv['system_asof'])<=instant(view['system_asof']),'PRIOR_RECOVERY_BINDING')
        else: need(not priors,'PRIOR_RECOVERY_BINDING')
        return inp
    def assessment(self,r):
        out=self.body(r); inp=self.basis(out['basis_ref']); expected=derive(inp)
        need(out['method_id']==inp['method_id'] and {k:out[k] for k in ('status','diagnostics','detail')}==expected and out['accounting_effect']=='none','ASSESSMENT_MISMATCH')
        return expected
    def submission(self,r):
        b=self.body(r); raw=self.blob_bytes(b['wire_blob'])
        need(raw==enc(self.record(b['request_ref'])),'WIRE_BYTES_MISMATCH')
        need(decode(raw)==self.record(b['request_ref']),'WIRE_BYTES_MISMATCH')
    def request_bindings(self,r):
        req=self.body(r); b=self.body(req['basis_ref'])
        need(req['profile_ref']==self.packet['profile_ref'] and req['operation']==OP,'REQUEST_PROFILE_BINDING')
        need(req['context_ref']==b['context_ref'] and req['view_ref']==b['view_ref'] and req['expected_head']==b['expected_head'],'REQUEST_BASIS_BINDING')
        return req
    def exchange(self,x):
        req=self.request_bindings(x['request_ref']); sub=self.body(x['submission_ref'])
        need(sub['request_ref']==x['request_ref'],'SUBMISSION_BINDING'); self.submission(x['submission_ref'])
        before,after=x['world_before'],x['world_after']; response=self.record(x['response_ref']); res=response['body']
        fields={'accounting_heads','balances','journals','unrelated_owners','current_view_ref','query_index','published_records'}
        need(set(before)==set(after)==fields,'WORLD_SHAPE')
        for k in ('accounting_heads','balances','journals','unrelated_owners'):
            need(before[k]==after[k],'ACCOUNTING_MUTATION')
        need(before['current_view_ref']==after['current_view_ref'],'WORLD_VIEW_MUTATION')
        head=self.body(req['expected_head']); owner=head['owner_id']
        need(owner in before['accounting_heads'] and owner in before['balances'],'WORLD_OWNER_MISSING')
        current=self.body(before['accounting_heads'][owner])
        need(current['context_ref']==req['context_ref'] and current['balances_sha256']==sha(enc(before['balances'][owner])),'WORLD_HEAD_BALANCE_BINDING')
        if response['kind']=='TransportObservation':
            need(res==dict(submission_ref=x['submission_ref'],status='acknowledgement_lost',commit_knowledge='unknown'),'TRANSPORT_KNOWLEDGE')
            need(after==before,'TRANSPORT_MUTATION'); return
        need(response['kind']=='OperationResult' and res['request_ref']==x['request_ref'] and res['submission_ref']==x['submission_ref'],'RESPONSE_BINDING')
        need(res['additional_commit'] is False and res['accounting_effect']=='none','ACCOUNTING_MUTATION')
        key=enc([req['client_id'],req['request_id']]).decode(); old=before['query_index'].get(key)
        code=None
        if old is not None:
            if old['request_digest']==x['request_ref']['digest']:
                need(res['disposition']=='replayed' and res['output_ref']==old['output_ref'] and res['receipt_ref']==old['receipt_ref'],'REPLAY_BINDING')
                previous=self.body(old['response_ref'])
                need({k:v for k,v in res.items() if k!='disposition'}=={k:v for k,v in previous.items() if k!='disposition'},'REPLAY_BINDING')
                need(after==before,'REPLAY_MUTATION'); return
            code='REQUEST_IDENTITY_CONFLICT'
        elif req['require_current'] and req['view_ref']!=before['current_view_ref']: code='STALE_VIEW'
        elif req['expected_head']!=before['accounting_heads'][owner]: code='STALE_HEAD'
        else:
            try: expected=derive(self.basis(req['basis_ref']))
            except (Refusal,MathRefusal) as e: code=e.code
        if code:
            need(res['disposition']=='rejected' and res['diagnostics']==[code] and res['output_ref'] is None and res['receipt_ref'] is None and not res['published_digests'],'REJECTION_BINDING')
            need(after==before,'REJECTION_MUTATION'); return
        need(res['disposition']==('partial' if expected['status']=='unresolved' else 'completed') and res['diagnostics']==expected['diagnostics'],'RESULT_STATUS_BINDING')
        need(res['output_ref'] is not None and res['receipt_ref'] is not None,'PUBLICATION_CLOSURE')
        output=self.body(res['output_ref']); receipt=self.body(res['receipt_ref'])
        need(output['basis_ref']==req['basis_ref'],'OUTPUT_BASIS_BINDING'); self.assessment(res['output_ref'])
        need(receipt==dict(request_ref=x['request_ref'],output_ref=res['output_ref'],status='query_published',accounting_head=req['expected_head'],accounting_effect='none'),'RECEIPT_BINDING')
        need(res['published_digests']==self.closure([res['output_ref'],res['receipt_ref']]),'PUBLICATION_CLOSURE')
        need(after['published_records']==sorted(set(before['published_records'])|set(self.closure([x['response_ref']]))),'PUBLICATION_CLOSURE')
        idx=deepcopy(before['query_index']); idx[key]=dict(request_digest=x['request_ref']['digest'],output_ref=res['output_ref'],receipt_ref=res['receipt_ref'],response_ref=x['response_ref'])
        need(after['query_index']==idx,'PUBLICATION_INDEX')
    def challenge(self,c):
        try:
            kind=c['kind']
            if kind=='assessment': self.assessment(c['candidate_ref'])
            elif kind=='basis': self.basis(c['candidate_ref'])
            elif kind=='submission': self.submission(c['candidate_ref'])
            elif kind=='exchange': self.exchange(c['candidate_exchange'])
            elif kind=='record': self.shape(c['candidate_record'],c['digest'])
            elif kind=='json': decode(self.blob_bytes(c['raw_blob']))
            else: raise Refusal('UNKNOWN_CHALLENGE')
        except (Refusal,MathRefusal) as e:
            need(e.code==c['expected'],'WRONG_CHALLENGE_REFUSAL:'+e.code); return
        raise Refusal('ADVERSE_CANDIDATE_ACCEPTED')
    def case(self,c):
        req=self.body(c['request_ref']); need(req['basis_ref']==c['basis_ref'],'CASE_BASIS_BINDING')
        try: derive(self.basis(c['basis_ref'])); refusal=None
        except (Refusal,MathRefusal) as e: refusal=e.code
        need(refusal==c['refusal'],'CASE_REFUSAL_MISMATCH')
        xs={x['id']:x for x in self.packet['exchanges']}
        need(c['id'] in xs and xs[c['id']]['request_ref']==c['request_ref'],'CASE_EXCHANGE_MISSING')
        if refusal:
            need(xs[c['id']]['role']=='method_refusal','CASE_REFUSAL_ROLE'); return
        roles={'':'publication','.replay':'exact_replay','.stale-replay':'replay_before_freshness','.lost-before':'lost_ack_before','.retry-before':'retry_first_publication','.lost-after':'lost_ack_after','.retry-after':'retry_exact_replay','.conflict':'identity_conflict','.stale-view':'new_stale_view','.stale-head':'new_stale_head','.frozen':'frozen_view_publication','.frozen-stale-head':'frozen_stale_head'}
        for suffix,role in roles.items():
            need(c['id']+suffix in xs and xs[c['id']+suffix]['role']==role,'CASE_ROLE_MISSING:'+role)
        base=xs[c['id']]; before,after=base['world_before'],base['world_after']
        for suffix,w in [('.lost-before',before),('.lost-after',after)]:
            need(xs[c['id']+suffix]['world_before']==xs[c['id']+suffix]['world_after']==w,'LOST_ACK_WORLD')
        for suffix,left,right in [('.retry-before',before,after),('.retry-after',after,after)]:
            need(xs[c['id']+suffix]['world_before']==left and xs[c['id']+suffix]['world_after']==right,'RETRY_WORLD')
        stale=xs[c['id']+'.stale-replay']['world_before']
        need(stale['current_view_ref']!=before['current_view_ref'] and stale['accounting_heads']!=before['accounting_heads'],'REPLAY_FRESHNESS_CHALLENGE_MISSING')
    def crash(self,c):
        need(c['cuts']==['before_publication','after_publication'],'CRASH_CUT_COVERAGE')
        x=next(x for x in self.packet['exchanges'] if x['id']==c['id'])
        need(c['before']==x['world_before'] and c['after']==x['world_after'],'CRASH_WORLD_BINDING')
        res=self.body(c['response_ref'])
        need(c['request_ref']==x['request_ref'] and c['response_ref']==x['response_ref'] and c['output_ref']==res['output_ref'] and c['receipt_ref']==res['receipt_ref'],'CRASH_RESPONSE_BINDING')
        self.exchange(x)
    def coverage(self):
        for key in ('cases','exchanges','challenges','crash_worlds'):
            rows=self.packet[key]; need(len({r['id'] for r in rows})==len(rows),'DUPLICATE_'+key.upper())
        need({self.body(c['basis_ref'])['input_ref']['digest'] for c in self.packet['cases']},'NO_CASES')
        need({self.body(self.body(c['basis_ref'])['input_ref'])['method_id'] for c in self.packet['cases']}==set(METHODS),'METHOD_COVERAGE')
        positives={c['id'] for c in self.packet['cases'] if c['refusal'] is None}
        need({c['id'] for c in self.packet['crash_worlds']}==positives,'CRASH_CASE_COVERAGE')
        need(len(self.packet['exchanges'])==12*len(positives)+len(self.packet['cases'])-len(positives),'EXCHANGE_ROLE_COVERAGE')
        need({'pooled-groups','doubled-recovery','independent-fit-redraw','reciprocal-forward-mean','ultimate-center','cash-only-cdr','failed-fit.success-only-normalization'}<={c['id'] for c in self.packet['challenges']},'TARGET_ADVERSARY_COVERAGE')
        build=json.loads((self.attempt/'build-run.json').read_text())
        need(build['packet_sha256']==sha((self.attempt/'portable-exchanges.json').read_bytes()),'PACKET_CHANGED')
        for key in ('records','exchanges','challenges','cases'):
            need(build[key]==len(self.reg if key=='records' else self.packet[key]),'BUILD_COUNT_MISMATCH')
    def run(self):
        self.audit('protected-predecessors-head-index',self.preservation)
        self.audit('schemas-profile-locks-snapshots',self.structure)
        for key in SOURCES:
            self.audit('source.'+key,lambda key=key:need(self.body(self.alias['source.'+key])==self.source_body(key),'SOURCE_BINDING'))
        for digest,r in self.reg.items(): self.audit('record.'+r['key'],lambda r=r,digest=digest:self.shape(r,digest))
        for c in self.packet['cases']: self.audit('case.'+c['id'],lambda c=c:self.case(c))
        for x in self.packet['exchanges']: self.audit('exchange.'+x['id'],lambda x=x:self.exchange(x))
        for c in self.packet['challenges']: self.audit('adverse.'+c['id'],lambda c=c:self.challenge(c))
        for c in self.packet['crash_worlds']: self.audit('crash.'+c['id'],lambda c=c:self.crash(c))
        self.audit('coverage-and-packet-integrity',self.coverage)

def main():
    started=time.monotonic(); attempt=HERE/(sys.argv[1] if len(sys.argv)>1 else sorted(p.name for p in HERE.glob('attempt-*'))[-1])
    need(attempt.resolve().is_relative_to(HERE),'ATTEMPT_PATH_SCOPE')
    auditor=Auditor(attempt); auditor.run(); failed=[r for r in auditor.checks if not r['passed']]
    summary=dict(status='failed' if failed else 'passed',checks=len(auditor.checks),failures=len(failed),wall_seconds=time.monotonic()-started,packet_sha256=sha((attempt/'portable-exchanges.json').read_bytes()),evidence_mode='exact_documentary_examples_no_runtime_no_empirical_campaign',cpu_gpu='CPU exact arithmetic; no GPU framework imported',checks_detail=auditor.checks)
    p=attempt/'verification.json'
    with p.open('x') as f: json.dump(summary,f,indent=2); f.write('\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='checks_detail'}))
    if failed: print(json.dumps(failed[:5])); sys.exit(1)

if __name__=='__main__': main()
