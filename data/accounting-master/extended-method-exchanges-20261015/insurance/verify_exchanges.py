"""Independent record, financial, lineage, publication and recovery audit."""
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
from jsonschema import Draft202012Validator,FormatChecker
from financial_checks import evaluate,unpack,wire,invariant,Refusal as FinanceRefusal
from source_policy import RAW,TEXT,RAW_SHA,TEXT_SHA,METHOD_FILES,ANCHORS

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]
PREFIX='accdsl.insurance-components.'; ROLES=('issued','replacement','held','accounts')
OPS=('insurance.components.commit@1','insurance.components.report@1')
LOCK='88a00cef72d3b3fb875dbf4f269030c4e01857b533dcda637ad48b9b26780dff'
class Refusal(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)
def need(ok,code):
    if not ok:raise Refusal(code)
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(v):return hashlib.sha256(v).hexdigest()
def refs(v):
    if isinstance(v,dict):
        if set(v)=={'kind','schema','digest'}:yield v
        else:
            for x in v.values():yield from refs(x)
    elif isinstance(v,list):
        for x in v:yield from refs(x)
def blobs(v):
    if isinstance(v,dict):
        if set(v)=={'kind','algorithm','digest','byte_length'}:yield v
        else:
            for x in v.values():yield from blobs(x)
    elif isinstance(v,list):
        for x in v:yield from blobs(x)
def unique(v):return [x for k,x in sorted({enc(x):x for x in v}.items())]
def pairs(items):
    d={}
    for k,v in items:need(k not in d,'duplicate_json_key');d[k]=v
    return d
def nofloat(v):raise Refusal('float_forbidden')
def decode(v):return json.loads(v,object_pairs_hook=pairs,parse_float=nofloat,parse_constant=nofloat)
def instant(v):return datetime.fromisoformat(v.replace('Z','+00:00'))
def hygiene(v):
    need(not isinstance(v,float),'float_forbidden')
    if isinstance(v,dict):
        if set(v)=={'n','d'}:unpack(v)
        for x in v.values():hygiene(x)
    elif isinstance(v,list):
        for x in v:hygiene(x)
def patch(v,changes):
    v=deepcopy(v)
    for c in changes:
        node=v
        for k in c['path'][:-1]:node=node[k]
        node[c['path'][-1]]=c['value']
    return v

class Auditor:
    def __init__(self,attempt):
        self.attempt=attempt; self.p=decode((attempt/'portable-exchanges.json').read_bytes())
        self.reg=self.p['record_registry'];self.alias=self.p['aliases']; self.checks=[]
        self.schema=decode((attempt/'record-schemas.json').read_bytes())
        self.validators={k:Draft202012Validator(s,format_checker=FormatChecker()) for k,s in self.schema['$defs'].items()}
        self.cases={c['id']:c for c in self.p['cases']};self.exchanges={e['id']:e for e in self.p['exchanges']};self.valid_results=set();self.valid_states=set()
    def audit(self,label,fn):
        try:fn();self.checks.append(dict(check=label,passed=True))
        except Exception as e:self.checks.append(dict(check=label,passed=False,code=getattr(e,'code',type(e).__name__),detail=str(e)[:240]))
    def record(self,r):
        need(r['digest'] in self.reg,'missing_reference');z=self.reg[r['digest']]
        need(z['kind']==r['kind'] and z['schema']==r['schema'],'reference_type_mismatch');return z
    def body(self,r):return self.record(r)['body']
    def closure(self,roots):
        seen=set();active=set()
        def visit(r):
            d=r['digest']
            if d in seen:return
            need(d not in active,'reference_cycle');active.add(d)
            for x in self.record(r)['dependencies']:visit(x)
            active.remove(d);seen.add(d)
        for r in roots:visit(r)
        return sorted(seen)
    def blob(self,b):
        need(b['digest'] in self.p['blobs'],'missing_blob');v=self.p['blobs'][b['digest']];path=(ROOT/v['path']).resolve()
        need(path.is_relative_to(ROOT),'blob_scope');raw=path.read_bytes()
        need(sha(raw)==b['digest'] and len(raw)==b['byte_length']==v['byte_length'],'blob_hash');return raw
    def shape(self,r,digest):
        need(set(r)=={'kind','schema','key','revision','body','dependencies'},'closed_record_shape')
        k=r['kind'];need(k in self.validators,'unknown_record_kind')
        need(r['schema']==self.schema['schema_ids'][k]==PREFIX+k.lower()+'.v1','schema_namespace')
        need(type(r['revision']) is int and r['revision']==0 and isinstance(r['key'],str) and bool(r['key']),'record_identity')
        hygiene(r);need(not list(self.validators[k].iter_errors(r['body'])),'closed_record_shape')
        need(r['dependencies']==unique(refs(r['body'])),'dependency_closure')
        for x in refs(r['body']):self.record(x)
        for x in blobs(r['body']):self.blob(x)
        need(sha(('accdsl.portable.v1/'+r['schema']).encode()+b'\0'+enc(r))==digest,'record_digest')
    def preservation(self):
        raw=(HERE/'predecessor-lock.json').read_bytes();need(sha(raw)==LOCK,'lock_changed');lock=decode(raw)
        original=ROOT/lock['original_protection_manifest'];need(sha(original.read_bytes())==lock['original_manifest_sha256'],'original_manifest_changed')
        for p in decode(original.read_bytes())['files']:
            for k in ('path','snapshot'):need(sha((ROOT/p[k]).read_bytes())==p['sha256'],'protected_changed:'+p[k])
        for p in lock['predecessor_files']:need(sha((ROOT/p['path']).read_bytes())==p['sha256'],'predecessor_changed:'+p['path'])
        need(subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==lock['git_commit'],'head_changed')
        index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
        need(sha(index)==lock['index_sha256'] and len(index.splitlines())==lock['index_entries']==100,'index_changed')
    def sources(self):
        source=self.body(self.alias['source'])
        for field,path,digest in (('raw_blob',RAW,RAW_SHA),('text_blob',TEXT,TEXT_SHA)):
            need(source[field]['digest']==digest and self.blob(source[field])==(ROOT/path).read_bytes(),'source_binding')
        need(source['anchors']==sorted(set(ANCHORS.values())),'source_anchor_binding')
        need([self.blob(x) for x in source['method_blobs']]==[(ROOT/p).read_bytes() for p in METHOD_FILES],'method_bytes_binding')
        profile=self.body(self.alias['profile']);lock=self.body(profile['schema_lock_ref'])
        need(profile['operations']==list(OPS) and profile['profile_id']=='InsuranceComponents/1','profile_binding')
        need(self.blob(lock['schema_blob'])==(self.attempt/'record-schemas.json').read_bytes(),'schema_lock')
        need(self.blob(lock['semantic_contract_blob'])==(self.attempt/'inputs/semantic-contract.md').read_bytes(),'contract_lock')
        need(self.blob(self.p['predecessor_lock_blob'])==(HERE/'predecessor-lock.json').read_bytes(),'predecessor_lock_binding')
        for name,p in self.p['input_snapshots'].items():
            need(sha((self.attempt/'inputs'/name).read_bytes())==p['sha256'],'input_snapshot')
            if p['original_path']:need(sha((ROOT/p['original_path']).read_bytes())==p['sha256'],'input_changed')
        for s in self.schema['$defs'].values():Draft202012Validator.check_schema(s)
    def values(self,heads):
        need(set(heads)==set(ROLES),'owner_set')
        states={r:self.body(heads[r]) for r in ROLES}
        need(len({s['owner_id'] for s in states.values()})==4,'owner_aliasing')
        for r,s in states.items():need(s['role']==r,'owner_role')
        return {r:s['balances'] for r,s in states.items()}
    def history_input(self,head,method):
        seen=set();s=self.body(head)
        while s['last_result_ref']:
            rr=s['last_result_ref'];need(rr['digest'] not in seen,'history_cycle');seen.add(rr['digest'])
            result=self.body(rr);b=self.body(result['basis_ref']);e=self.body(b['input_ref'])
            if e['method_id']==method:return e
            s=self.body(b['opening_heads'][s['role']])
        return None
    def lineage(self,e,b):
        m=e['method_id']; heads=b['opening_heads']
        if m=='reinsurance.change@1':
            prior=self.history_input(heads['held'],'reinsurance.recognize@1');need(prior is not None,'treaty_lineage_missing')
            need(e['share']==prior['share'] and e['old_covered_claims']==prior['covered_claims'],'treaty_lineage_mismatch')
        if m=='paa.finance@1':
            prior=self.history_input(heads['issued'],'paa.claim@1');need(prior is not None,'claim_lineage_missing')
            need(all(e[k]==prior[k] for k in ('claim_date','rate_date','incurrence_rate','payment')),'claim_rate_lineage_mismatch')
        if m=='vfa.pool@1':
            prior=self.history_input(heads['issued'],'vfa.recognize@1');need(prior is not None,'pool_lineage_missing')
            need(e['policyholder_share']==prior['policyholder_share'],'pool_share_lineage_mismatch')
        if m=='finance.variable@1':need(e['allocation_basis']=='prospective_revised','wrong_allocation_origin')
    def bindings(self,b,e,override=None):
        o=override or {};view=self.body(b['view_ref']);ev=self.body(b['evidence_ref'])
        need(o.get('source_ref',b['source_ref'])==self.alias['source'],'source_binding')
        need(o.get('method_anchor',b['method_anchor'])==ANCHORS[e['method_id']],'method_source_binding')
        need(b['evidence_ref'] in view['evidence_refs'],'missing_evidence')
        need(view['context_ref']==ev['context_ref']==b['context_ref'],'context_binding')
        need(instant(o.get('evidence_available_at',ev['available_at']))<=instant(view['decision_at']) and instant(ev['ingested_at'])<=instant(view['system_asof']),'future_evidence')
        for r,h in b['opening_heads'].items():need(self.body(h)['context_ref']==b['context_ref'] and self.body(h)['role']==r,'owner_context')
        if e['method_id']=='reinsurance.recognize@1':need(e['issued_group']==o.get('issued_group',self.body(b['opening_heads']['issued'])['group_id']),'owner_group_binding')
        if e['method_id']=='acquisition.allocate@1':need(e['target_group']==self.body(b['opening_heads']['issued'])['group_id'],'owner_group_binding')
    def basis(self,br):
        b=self.body(br);e=self.body(b['input_ref']);self.bindings(b,e);self.lineage(e,b)
        facts=decode(self.blob(self.body(b['evidence_ref'])['content_blob']))
        need(facts==dict(input=e,opening=self.values(b['opening_heads'])),'evidence_fact_binding')
        for evr in self.body(b['view_ref'])['evidence_refs']:
            ev=self.body(evr);view=self.body(b['view_ref'])
            need(ev['context_ref']==b['context_ref'] and instant(ev['available_at'])<=instant(view['decision_at']) and instant(ev['ingested_at'])<=instant(view['system_asof']),'future_evidence')
        return b,e
    def result(self,rr):
        if rr['digest'] in self.valid_results:return
        r=self.body(rr);b,e=self.basis(r['basis_ref'])
        for h in b['opening_heads'].values():self.state(h)
        need(r['method_id']==e['method_id'],'method_binding')
        calculated=evaluate(e,self.values(b['opening_heads']))
        need({k:r[k] for k in calculated}==calculated,'financial_result_mismatch')
        self.valid_results.add(rr['digest'])
    def state(self,sr):
        if sr['digest'] in self.valid_states:return
        s=self.body(sr)
        if s['last_result_ref']:
            rr=s['last_result_ref'];self.result(rr);r=self.body(rr);b=self.body(r['basis_ref']);old=self.body(b['opening_heads'][s['role']])
            need(r['status']=='resolved' and s['generation']==old['generation']+1,'state_generation')
            need(all(s[k]==old[k] for k in ('context_ref','role','owner_id','group_id')),'state_identity')
            need(s['balances']==r['closing'][s['role']] and s['balances']!=old['balances'],'state_result_binding')
        else:need(s['generation']==0,'unsupported_opening_generation')
        self.valid_states.add(sr['digest'])
    def proposal(self,pr):
        p=self.body(pr);b=self.body(p['basis_ref']);r=self.body(p['result_ref']);a=self.body(p['authorization_ref'])
        need(r['basis_ref']==p['basis_ref']==a['basis_ref'],'proposal_basis')
        need(a['opening_heads']==p['before_heads']==b['opening_heads'],'authorization_read_set')
        self.result(p['result_ref'])
        for role in ROLES:
            old=p['before_heads'][role];new=p['after_heads'][role];self.state(new)
            if r['closing'][role]==self.body(old)['balances']:need(old==new,'unnecessary_write')
            else:need(self.body(new)['last_result_ref']==p['result_ref'],'missing_owner_write')
        return p
    def request(self,rq,sub,world):
        r=self.body(rq);s=self.body(sub)
        need(s['request_ref']==rq and self.blob(s['wire_blob'])==enc(r),'wire_binding')
        need(r['profile_ref']==self.alias['profile'],'request_profile')
        identity=r['client_id']+'/'+r['request_id']
        if identity in world['decisions']:
            prior=world['decisions'][identity]
            need(prior['request_ref']==rq,'identity_conflict')
            return dict(replay=prior)
        need(not r['require_current'] or r['view_ref']==world['current_view_ref'],'stale_view')
        need(r['expected_heads']==world['heads'],'stale_head')
        need(self.body(r['view_ref'])['context_ref']==r['context_ref'],'request_context')
        if r['operation']==OPS[0]:
            need(set(r['arguments'])=={'proposal_ref'},'operation_arguments');p=self.proposal(r['arguments']['proposal_ref']);b=self.body(p['basis_ref'])
            need(p['before_heads']==r['expected_heads'] and b['view_ref']==r['view_ref'] and b['context_ref']==r['context_ref'],'request_basis')
            return dict(output_ref=p['result_ref'],after_heads=p['after_heads'])
        need(r['operation']==OPS[1] and set(r['arguments'])=={'state_refs'},'operation_arguments')
        need(r['arguments']['state_refs']==r['expected_heads'],'report_heads')
        for h in r['expected_heads'].values():self.state(h)
        invariant(unpack(self.values(r['expected_heads'])))
        return dict(after_heads=r['expected_heads'])
    def exchange(self,e):
        rq,sub=e['request_ref'],e['submission_ref'];r=self.body(rq);res=self.body(e['response_ref']);before=e['world_before'];after=e['world_after']
        need(res['request_ref']==rq and res['submission_ref']==sub,'response_request_binding')
        try:answer=self.request(rq,sub,before)
        except (Refusal,FinanceRefusal) as error:
            need(res['disposition']=='rejected' and res['diagnostics']==[error.code],'wrong_rejection')
            need(res['output_ref'] is None and res['receipt_ref'] is None and res['published_digests']==[] and not res['additional_commit'],'rejection_payload')
            need(after==before,'rejection_mutated_world');return
        if 'replay' in answer:
            prior=self.body(answer['replay']['response_ref'])
            need(res['disposition']=='replayed' and not res['additional_commit'],'replay_disposition')
            need(all(res[k]==prior[k] for k in ('output_ref','receipt_ref','diagnostics','published_digests','request_ref','submission_ref')),'changed_replay_bytes')
            need(after==before,'duplicate_commit');return
        output=res['output_ref'];receipt=self.body(res['receipt_ref'])
        need(receipt['request_ref']==rq and receipt['output_ref']==output and receipt['before_heads']==before['heads'] and receipt['after_heads']==answer['after_heads'],'receipt_binding')
        need(receipt['written_roles']==[role for role in ROLES if before['heads'][role]!=answer['after_heads'][role]],'receipt_write_set')
        if r['operation']==OPS[0]:
            need(output==answer['output_ref'],'output_binding');result=self.body(output);codes=result['diagnostics'];status='unresolved_published' if codes else 'committed'
        else:
            report=self.body(output);need(output['kind']=='ComponentReport' and report['state_refs']==r['expected_heads'] and report['context_ref']==r['context_ref'],'report_binding');codes=[];status='report_published'
        need(receipt['status']==status and res['disposition']==('partial' if codes else 'completed') and res['diagnostics']==codes and res['additional_commit'],'result_status')
        need(res['published_digests']==self.closure([rq,sub,res['receipt_ref']]),'publication_dependencies')
        expected=deepcopy(before);expected['heads']=answer['after_heads'];expected['published_records']=sorted(set(before['published_records'])|set(self.closure([e['response_ref']])))
        if r['operation']==OPS[0] and self.body(output)['journal']:expected['journals'].append(dict(request_ref=rq,result_ref=output,lines=self.body(output)['journal']))
        identity=r['client_id']+'/'+r['request_id'];expected['decisions'][identity]=dict(request_ref=rq,response_ref=e['response_ref'],output_ref=output,receipt_ref=res['receipt_ref'])
        need(after==expected,'partial_publication')
    def crash(self,c):
        pub=self.exchanges[c['publication_id']];recovery=self.exchanges[c['recovery_id']];o=self.body(c['observation_ref'])
        need(o['submission_ref']==pub['submission_ref'] and o['commit_knowledge']=='unknown','transport_false_certainty')
        expected=pub['world_after'] if c['committed'] else pub['world_before']
        need(c['world_before']==pub['world_before'] and c['world_after_crash']==expected==recovery['world_before'],'invalid_crash_world')
        need(recovery['request_ref']==pub['request_ref'] and recovery['submission_ref']==pub['submission_ref'] and recovery['world_after']==pub['world_after'],'recovery_changed_request')
        self.exchange(recovery)
    def challenge(self,c):
        row=self.cases[c['case_id']];result=self.body(row['result_ref']);b=self.body(row['basis_ref']);e=self.body(b['input_ref']);scope=c['scope']
        try:
            if scope in ('input','shape'):
                changed=patch(dict(input=e),c['mutations'])['input'];hygiene(changed)
                need(not list(self.validators['MethodInput'].iter_errors(changed)),'closed_record_shape')
                self.lineage(changed,b);evaluate(changed,self.values(b['opening_heads']))
            elif scope=='result':
                changed=patch(result,c['mutations']);hygiene(changed)
                need(not list(self.validators['ComponentResult'].iter_errors(changed)),'closed_record_shape')
                calculated=evaluate(e,self.values(b['opening_heads']))
                need({k:changed[k] for k in calculated}==calculated,'financial_result_mismatch')
            elif scope=='world':
                exchange=deepcopy(self.exchanges[row['publication_id']]);exchange['world_after']=patch(exchange['world_after'],c['mutations']);self.exchange(exchange)
            elif scope=='binding':self.bindings(b,e,patch({},c['mutations']))
            else:raise AssertionError('unknown challenge scope')
        except (Refusal,FinanceRefusal) as error:
            need(error.code==c['expected_code'],'unexpected_adverse_code:'+error.code);return
        raise Refusal('adverse_not_rejected')
    def completeness(self):
        need(set(c['method_id'] for c in self.p['cases'])==set(ANCHORS),'method_coverage')
        need(len(self.cases)==len(self.p['cases']) and len(self.exchanges)==len(self.p['exchanges']),'duplicate_identifiers')
        for c in self.p['cases']:
            base=c['publication_id']
            for suffix in ('','.replay','.replay-new-view','.conflict','.stale-view','.stale-head','.lost-ack-committed','.lost-ack-uncommitted'):need(base+suffix in self.exchanges,'missing_exchange')
            if self.body(c['result_ref'])['status']=='resolved':need('report_ref' in c,'missing_component_report')
        need(len(self.p['challenges'])>=70,'missing_adverse_scope')
        need(len(self.p['crash_worlds'])==2*len([e for e in self.p['exchanges'] if e['role']=='publication']),'missing_crash_world')
        need(self.body(self.alias['component.joint-service-settlement'])['closing']['accounts']['cash']==dict(n='63',d='2'),'lifetime_reinsurance_cash')
        need(self.body(self.alias['component.modified-new-service'])['closing']['accounts']['cash']==dict(n='108',d='1'),'lifetime_modification_cash')
        need(self.body(self.alias['component.paa-claim-paid'])['closing']['accounts']['cash']==dict(n='1298',d='5'),'lifetime_paa_cash')
        need(self.body(self.alias['component.vfa-investment-repaid'])['closing']['accounts']['cash']==dict(n='214',d='1'),'lifetime_vfa_cash')
    def run(self):
        self.audit('preservation-before',self.preservation);self.audit('sources-schema-inputs',self.sources)
        for digest,r in self.reg.items():self.audit('record:'+r['key'],lambda r=r,d=digest:self.shape(r,d))
        for c in self.p['cases']:self.audit('financial:'+c['id'],lambda c=c:self.result(c['result_ref']))
        for e in self.p['exchanges']:self.audit('exchange:'+e['id'],lambda e=e:self.exchange(e))
        for c in self.p['crash_worlds']:self.audit('crash:'+c['id'],lambda c=c:self.crash(c))
        for c in self.p['challenges']:self.audit('adverse:'+c['id'],lambda c=c:self.challenge(c))
        self.audit('coverage-and-lifetime-checks',self.completeness);self.audit('preservation-after',self.preservation)

def main():
    start=time.monotonic();a=Auditor(HERE/sys.argv[1]);a.run();fail=[x for x in a.checks if not x['passed']]
    result=dict(passed=not fail,checks=len(a.checks),failures=len(fail),results=a.checks,wall_seconds=time.monotonic()-start,interpreter=sys.executable,command=sys.argv,packet_sha256=sha((a.attempt/'portable-exchanges.json').read_bytes()),hardware='CPU exact arithmetic; no GPU framework imported')
    with (a.attempt/'independent-checks.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(passed=result['passed'],checks=len(a.checks),failures=len(fail),first_failures=fail[:8],wall_seconds=result['wall_seconds'])))
    raise SystemExit(1 if fail else 0)

if __name__=='__main__':main()
