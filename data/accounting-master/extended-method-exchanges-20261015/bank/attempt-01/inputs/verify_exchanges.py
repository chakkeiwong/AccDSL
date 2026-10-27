"""Independent documentary conformance audit, not an accounting endpoint.

Never imports the packet builder or authored expected journals/states. Financial
effects are derived from economic inputs; the attempt's locked schema supplies
the wire types. Failed validation artifacts are retained under numbered names.
"""
from copy import deepcopy
from datetime import date
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
from jsonschema import Draft202012Validator, FormatChecker
from financial_checks import derive, check_component
from source_policy import SOURCES, supporting

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PREFIX='accdsl.bank-components.'
ASSETS=['cash','securities','gross_loan','allowance']
LIABILITIES=['deposits','funding','commitment_provision','fee_liability']
PROFIT=['interest_income','fee_income','recovery_income','other_gains','impairment_expense','modification_expense','deposit_interest_expense']
RESERVES=['fair_value_reserve']
CAPITAL=['capital','retained']
CASH=['operating','investing','financing','unclassified']
OCI=['fair_value']
EQUITY=['issue']
ACCOUNTS=ASSETS+LIABILITIES+PROFIT+RESERVES+CAPITAL

class Refusal(Exception):
    def __init__(self,code,status='rejected'):
        self.code,self.status=code,status
        super().__init__(code)

def require(condition,code,status='rejected'):
    if not condition:raise Refusal(code,status)

def enc(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def q(v):
    n=F(v);return {'n':str(n.numerator),'d':str(n.denominator)}
def value(v):return F(int(v['n']),int(v['d']))
def exact(v):
    if isinstance(v,dict):
        if set(v)=={'n','d'}:return value(v)
        return {k:exact(x) for k,x in v.items()}
    if isinstance(v,list):return [exact(x) for x in v]
    return v
def rational_vector(v):return {k:q(x) for k,x in v.items()}
def references(v):
    if isinstance(v,dict):
        if set(v)=={'kind','schema','digest'}:yield v
        else:
            for x in v.values():yield from references(x)
    elif isinstance(v,list):
        for x in v:yield from references(x)
def blobs(v):
    if isinstance(v,dict):
        if set(v)=={'kind','algorithm','digest','byte_length'} and v['kind']=='blob':yield v
        else:
            for x in v.values():yield from blobs(x)
    elif isinstance(v,list):
        for x in v:yield from blobs(x)
def pairs(items):
    out={}
    for k,v in items:
        require(k not in out,'duplicate_key');out[k]=v
    return out
def forbidden_float(v):raise Refusal('float_forbidden')
def forbidden_constant(v):raise Refusal('nonfinite_forbidden')
def decode(raw,strict=True):
    try:return json.loads(raw,object_pairs_hook=pairs,parse_float=forbidden_float if strict else float,parse_constant=forbidden_constant)
    except (ValueError,UnicodeError):raise Refusal('invalid_json')
def numeric_hygiene(v):
    require(not isinstance(v,float),'float_forbidden')
    if isinstance(v,dict):
        if set(v)=={'n','d'}:
            try:require(q(value(v))==v,'noncanonical_rational')
            except (ValueError,ZeroDivisionError,TypeError):raise Refusal('noncanonical_rational')
        for x in v.values():numeric_hygiene(x)
    elif isinstance(v,list):
        for x in v:numeric_hygiene(x)

class Auditor:
    def __init__(self,attempt):
        self.attempt=attempt
        self.packet=decode((attempt/'portable-exchanges.json').read_bytes(),False)
        self.reg=self.packet['record_registry'];self.alias=self.packet['aliases'];self.blobs=self.packet['blobs']
        self.schema=decode((attempt/'record-schemas.json').read_bytes())
        self.validators={k:Draft202012Validator(v,format_checker=FormatChecker()) for k,v in self.schema['$defs'].items()}
        self.checks=[];self._closure={}
    def audit(self,label,fn):
        try:fn();self.checks.append(dict(check=label,passed=True))
        except Exception as e:self.checks.append(dict(check=label,passed=False,diagnostic=getattr(e,'code',type(e).__name__),detail=str(e)[:280]))
    def expected(self,fn,code,status='rejected'):
        try:fn()
        except Refusal as e:
            require((e.code,e.status)==(code,status),'wrong_refusal:'+e.code+':'+e.status)
            return
        raise Refusal('invalid_candidate_accepted')
    def record(self,r):
        require(r['digest'] in self.reg,'missing_reference')
        rec=self.reg[r['digest']]
        require(rec['kind']==r['kind'] and rec['schema']==r['schema'],'reference_type_mismatch')
        return rec
    def body(self,r):return self.record(r)['body']
    def blob_bytes(self,b):
        require(b['digest'] in self.blobs,'missing_blob')
        meta=self.blobs[b['digest']];p=ROOT/meta['path']
        require(p.is_relative_to(ROOT),'blob_path_scope')
        raw=p.read_bytes()
        require(len(raw)==meta['byte_length']==b['byte_length'] and digest(raw)==b['digest'],'blob_hash_mismatch')
        return raw
    def closure(self,roots):
        seen=set();visiting=set()
        def visit(r):
            d=r['digest']
            if d in seen:return
            require(d not in visiting,'cyclic_dependency');visiting.add(d)
            for rr in self.record(r)['dependencies']:visit(rr)
            visiting.remove(d);seen.add(d)
        for r in roots:visit(r)
        return sorted(seen)
    def record_shape(self,r,expected_digest=None):
        require(set(r)=={'kind','schema','key','revision','body','dependencies'},'closed_record_shape')
        require(r['kind'] in self.validators,'closed_record_shape')
        require(r['schema']==self.schema['schema_ids'][r['kind']],'record_schema_mismatch')
        require(isinstance(r['key'],str) and r['key'] and type(r['revision']) is int and r['revision']==0,'closed_record_shape')
        require(not list(self.validators[r['kind']].iter_errors(r['body'])),'closed_record_shape')
        numeric_hygiene(r)
        deps={enc(x):x for x in references(r['body'])}
        require(r['dependencies']==[deps[k] for k in sorted(deps)],'dependency_mismatch')
        for x in deps.values():self.record(x)
        for b in blobs(r['body']):self.blob_bytes(b)
        if expected_digest:require(digest(('accdsl.portable.v1/'+r['schema']).encode()+b'\0'+enc(r))==expected_digest,'record_digest_mismatch')
    def source_checks(self):
        for name,p in SOURCES.items():
            b=self.body(self.alias['source.'+name])
            for k,path in [('source_pdf',p['base']+'.pdf'),('source_text',p['base']+'.txt'),('method_text',p['method'])]:
                require(b[k]['digest']==digest((ROOT/path).read_bytes()),'source_bytes_binding')
            require(b['inspection_note']['digest']==digest((self.attempt/'inputs/source-reading.md').read_bytes()),'inspection_note_binding')
            require(b['family']==p['family'] and b['anchors']==p['anchors'],'source_anchor_binding')
            require((b['period_start_inclusive'],b['period_start_exclusive'])==(p['start'],p['end']),'source_period_binding')
        profile=self.body(self.alias['profile']);lock=self.body(profile['schema_lock_ref'])
        require(profile['profile_id']=='BankComponents/1','profile_mismatch')
        require(self.blob_bytes(lock['schema_blob'])==(self.attempt/'record-schemas.json').read_bytes(),'schema_lock_mismatch')
        require(self.blob_bytes(lock['semantic_contract_blob'])==(self.attempt/'inputs/semantic-contract.md').read_bytes(),'contract_lock_mismatch')
        for name,meta in self.packet['input_snapshots'].items():
            require(digest((ROOT/meta['path']).read_bytes())==meta['sha256'],'input_snapshot_hash')
            require((self.attempt/'inputs'/name).read_bytes()==(ROOT/meta['path']).read_bytes(),'input_snapshot_path')
    def preservation(self):
        lock=decode((HERE/'predecessor-lock.json').read_bytes())
        original=ROOT/lock['original_protection_manifest']
        require(digest(original.read_bytes())==lock['original_manifest_sha256'],'protection_manifest_changed')
        for r in decode(original.read_bytes())['files']:
            require(digest((ROOT/r['path']).read_bytes())==r['sha256'],'protected_original_changed:'+r['path'])
            require(digest((ROOT/r['snapshot']).read_bytes())==r['sha256'],'protected_snapshot_changed:'+r['path'])
        for r in lock['predecessor_files']:
            require(digest((ROOT/r['path']).read_bytes())==r['sha256'],'predecessor_changed:'+r['path'])
        commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
        index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
        require(commit==lock['git_commit'],'head_changed')
        require(digest(index)==lock['index_sha256'],'staged_index_changed')
        require(len(index.splitlines())==lock['index_entries'],'staged_count_changed')
    def owner(self,st):
        c=self.body(self.body(st)['context_ref']);return '/'.join(c[k] for k in ['entity_id','book_id','branch_key'])
    def head(self,st):return dict(owner_key=self.owner(st),state_ref=st,generation=self.body(st)['sequence'])
    def identity(self,b):return enc([b['identity'][k] for k in ['entity_id','book_id','branch_key','business_event_id']]).decode()

    def basis_effects(self,br):
        b=self.body(br);o=self.body(b['opening_ref']);ev=self.body(b['event_ref']);md=self.body(b['method_ref'])
        au=self.body(b['authority_ref']);ctx=self.body(b['context_ref']);comp=self.body(o['component_ref']);view=self.body(b['view_ref'])
        require(o['context_ref']==ev['context_ref']==au['context_ref']==b['context_ref'],'basis_context_mismatch')
        require(all(b['identity'][k]==ctx[k] for k in ['entity_id','book_id','branch_key']),'owner_identity_mismatch')
        require(md['method_id']==ev['method_id'],'method_event_mismatch')
        tag=comp['tag'];require(md['component_kind']==tag==ev['method_id'].split('.')[0],'component_method_mismatch')
        family=SOURCES[tag]['family']
        require(md['source_ref']==au['source_ref']==self.alias['source.'+tag] and
            md['supporting_source_refs']==au['supporting_source_refs']==[self.alias['source.'+x] for x in supporting(tag)],'source_binding_mismatch')
        require(md['profile_ref']==self.alias['profile'],'profile_mismatch')
        lock=self.body(self.body(md['profile_ref'])['schema_lock_ref'])
        require(md['contract_blob']==lock['semantic_contract_blob'],'method_contract_mismatch')
        require(b['view_ref']==o['view_ref'],'basis_view_mismatch')
        require(view['information_mode']=='archival_synthetic','information_mode_unadmitted')
        require(ctx['basis']==('historical_EU_IFRS_conditional' if family=='EU_IFRS' else 'historical_AU_AASB_conditional'),'source_jurisdiction_mismatch')
        require(ctx['currency']=='USD','functional_currency_mismatch')
        require(ev['event_date']>=o['as_of_date'],'event_before_opening')
        require(ev['instant']>o['instant'],'event_instant_order')
        year=int(ev['event_date'][:4])
        require((ev['reporting_period_start'],ev['reporting_period_end_exclusive'])==(f'{year}-01-01',f'{year+1}-01-01'),'reporting_period_mismatch')
        require(au['start_inclusive']<=ev['instant']<au['end_exclusive'],'authority_instant_scope')
        for sr in [md['source_ref'],*md['supporting_source_refs']]:
            require(sr in view['source_refs'],'source_not_in_view');s=self.body(sr)
            require(s['family']==family,'source_jurisdiction_mismatch')
            start,end=s['period_start_inclusive'],s['period_start_exclusive'];period=ev['reporting_period_start']
            require((start is None or period>=start) and (end is None or period<end),'source_period_scope')
        balances=exact(o['balances']);original=exact(comp['value'])
        require(sum(balances.values())==0,'opening_ledger_unbalanced')
        try:check_component(tag,original,balances)
        except AssertionError:raise Refusal('opening_component_mismatch')
        after,j,cash,oci,equity=derive(tag,original,ev['method_id'],exact(ev['parameters']),ev['event_date'],require)
        closing=deepcopy(o)
        closing.update(sequence=o['sequence']+1,instant=ev['instant'],as_of_date=ev['event_date'])
        closing['balances']=rational_vector({k:balances[k]+j.get(k,0) for k in ACCOUNTS})
        for k,mov in [('cash_movements',cash),('oci_movements',oci),('equity_movements',equity)]:
            closing[k]=rational_vector({a:value(v)+mov[a] for a,v in o[k].items()})
        for k,sign in [('cash_receipts',1),('cash_payments',-1)]:
            closing[k]=rational_vector({a:value(v)+max(F(0),sign*cash[a]) for a,v in o[k].items()})
        expected_journal=dict(basis_ref=br,mode='monetary' if j else 'state_only',currency=ctx['currency'],
            lines=[dict(account=a,signed_amount=q(v)) for a,v in sorted(j.items())])
        try:check_component(tag,after,exact(closing['balances']))
        except AssertionError:raise Refusal('derived_component_mismatch')
        require(sum(exact(closing['balances']).values())==0,'derived_closing_unbalanced')
        return closing,dict(tag=tag,value=after),expected_journal,cash

    def authorization(self,ar,br):
        a=self.body(ar);b=self.body(br);ad=self.body(a['admission_ref']);md=self.body(b['method_ref']);ev=self.body(b['event_ref'])
        require(a['basis_ref']==br and a['view_ref']==b['view_ref'] and a['posting_permitted'],'authorization_binding_mismatch')
        require(ad['basis_ref']==br and ad['source_ref']==md['source_ref'] and ad['context_ref']==b['context_ref'] and
            ad['instant']==ev['instant'] and ad['status']=='eligible','authorization_admission_mismatch')
        expected=[dict(name=n,status='satisfied',support_ref=r) for n,r in [
            ('conditional_source',md['source_ref']),('exact_context',b['context_ref']),('supplied_economic_facts',b['event_ref'])]]
        require(ad['findings']==expected,'authorization_findings_mismatch')

    def posting(self,args):
        br=args['basis_ref'];closing,component,journal,cash=self.basis_effects(br)
        self.authorization(args['authorization_ref'],br)
        if 'journal_ref' not in args:return
        require(self.body(args['journal_ref'])==journal,'journal_financial_mismatch')
        d=self.body(args['delta_ref']);b=self.body(br)
        require(d['basis_ref']==br and d['opening_ref']==b['opening_ref'],'delta_basis_mismatch')
        actual=self.body(d['closing_ref']);closing['component_ref']=actual['component_ref']
        require(actual==closing and exact(self.body(actual['component_ref']))==component,'closing_financial_mismatch')
        require(d['cash_change']==rational_vector(cash),'delta_cash_mismatch')

    def receipt_publication(self,rr,w,financial=True):
        r=self.body(rr);rq=self.body(r['request_ref']);args=rq['arguments']['value'];b=self.body(r['basis_ref'])
        require(rr in w['receipts'] and r['journal_ref'] in w['journals'] and r['delta_ref'] in w['deltas'],'report_receipt_unpublished')
        require(w['event_receipts'].get(self.identity(b))==dict(request_ref=r['request_ref'],receipt_ref=rr),'report_receipt_unpublished')
        require(set(self.closure([rr]))<=set(w['published_records']),'report_receipt_unpublished')
        require(rq['operation']=='accounting.commit@1' and all(r[k]==args[k] for k in ['basis_ref','authorization_ref','journal_ref','delta_ref']),'receipt_binding_mismatch')
        d=self.body(r['delta_ref']);o=self.body(r['opening_ref']);s=self.body(r['closing_ref'])
        require(r['opening_ref']==b['opening_ref']==d['opening_ref'] and r['closing_ref']==d['closing_ref'],'receipt_state_mismatch')
        require(r['generation']==s['sequence']==o['sequence']+1 and rq['expected_head']==self.head(r['opening_ref']),'receipt_generation_mismatch')
        if financial:self.posting(args)

    def atomic_world(self,rqref,rr,before,candidate):
        rq=self.body(rqref);args=rq['arguments']['value'];b=self.body(args['basis_ref']);r=self.body(rr)
        require(r['request_ref']==rqref and all(r[k]==args[k] for k in ['basis_ref','authorization_ref','journal_ref','delta_ref']),'receipt_binding_mismatch')
        d=self.body(args['delta_ref'])
        require(r['opening_ref']==d['opening_ref']==b['opening_ref'] and r['closing_ref']==d['closing_ref'],'receipt_state_mismatch')
        require(r['generation']==self.body(d['closing_ref'])['sequence'],'receipt_generation_mismatch')
        expected=deepcopy(before);expected['head']=self.head(d['closing_ref'])
        expected['event_receipts'][self.identity(b)]=dict(request_ref=rqref,receipt_ref=rr)
        for k,ref in [('journals',args['journal_ref']),('deltas',args['delta_ref']),('receipts',rr)]:expected[k].append(ref)
        expected['published_records']=sorted(set(before['published_records'])|set(self.closure([rr])))
        require(candidate==expected,'atomic_publication_mismatch')

    def report_inputs(self,args,w):
        opening,closing=args['opening_ref'],args['state_ref'];o=self.body(opening);c=self.body(closing)
        start,end=args['period_start'],args['period_end_exclusive'];receipts=args['receipt_refs']
        require(o['context_ref']==c['context_ref'] and o['view_ref']==c['view_ref']==args['view_ref'],'report_context_mismatch')
        require(self.owner(opening)==w['head']['owner_key'],'report_context_mismatch')
        if args['require_current']:require(args['view_ref']==w['current_view_ref'],'stale_dependency_view')
        require(start<end and start.endswith('-01-01') and end.endswith('-01-01'),'report_event_period')
        current=opening
        for rr in receipts:
            r=self.body(rr)
            require(r['opening_ref']==current,'report_receipt_chain')
            require(self.owner(r['opening_ref'])==self.owner(opening),'report_receipt_chain')
            self.receipt_publication(rr,w)
            ev=self.body(self.body(r['basis_ref'])['event_ref'])
            require(start<=ev['event_date']<end,'report_event_period')
            current=r['closing_ref']
        require(current==closing and bool(receipts),'report_receipt_chain')
        require(o['as_of_date']<=start and c['as_of_date']<end,'report_event_period')
        all_period=[]
        for rr in w['receipts']:
            r=self.body(rr);ev=self.body(self.body(r['basis_ref'])['event_ref'])
            if self.owner(r['opening_ref'])==self.owner(opening) and start<=ev['event_date']<end:all_period.append(rr)
        require(receipts==all_period,'report_receipt_chain')
        require(set(self.closure([opening,closing]))<=set(w['published_records']),'report_receipt_unpublished')

    def report_values(self,args,w,candidate):
        self.report_inputs(args,w)
        o=self.body(args['opening_ref']);c=self.body(args['state_ref']);a,b=exact(o['balances']),exact(c['balances'])
        income={k:b[k]-a[k] for k in PROFIT}
        oci={k:value(c['oci_movements'][k])-value(o['oci_movements'][k]) for k in OCI}
        equity={k:value(c['equity_movements'][k])-value(o['equity_movements'][k]) for k in EQUITY}
        cash={k:value(c['cash_movements'][k])-value(o['cash_movements'][k]) for k in CASH}
        interest=F(0);unallocated=F(0)
        for rr in args['receipt_refs']:
            ev=self.body(self.body(self.body(rr)['basis_ref'])['event_ref']);p=ev['parameters']
            if ev['method_id'] in ['loan.collect','fee.collect']:
                if p['interest_component'] is None:unallocated+=value(p['amount'])
                else:interest+=value(p['interest_component'])
            elif ev['method_id']=='loan.recovery':unallocated+=value(p['amount'])
        def book_equity(v):return -sum(v[k] for k in CAPITAL+RESERVES+PROFIT)
        values=dict(cash=b['cash'],assets=sum(b[k] for k in ASSETS),
            liabilities=-sum(b[k] for k in LIABILITIES),
            equity=book_equity(b),profit=-sum(income.values()),oci=sum(oci.values()),**cash)
        receipts={k:value(c['cash_receipts'][k])-value(o['cash_receipts'][k]) for k in CASH}
        payments={k:value(c['cash_payments'][k])-value(o['cash_payments'][k]) for k in CASH}
        expected={k:args[k] for k in ['opening_ref','state_ref','view_ref','period_start','period_end_exclusive','receipt_refs']}
        expected.update(currency=self.body(c['context_ref'])['currency'],values=rational_vector(values),
            cash_receipts=rational_vector(receipts),cash_payments=rational_vector(payments),interest_paid=q(0),interest_received=q(interest),unallocated_credit_receipts=q(unallocated),credit_receipt_allocation='unresolved' if unallocated else 'complete',
            income_statement=rational_vector(income),oci_components=rational_vector(oci),other_equity_movements=rational_vector(equity),
            tax_status='uncomputed',complete_company_after_tax=False)
        require(candidate==expected,'report_financial_mismatch')
        require(values['assets']-values['liabilities']==values['equity'],'report_balance_sheet')
        require(book_equity(b)-book_equity(a)==values['profit']+values['oci']+sum(equity.values()),'report_equity_bridge')
        require(b['cash']-a['cash']==sum(cash.values())==sum(receipts.values())-sum(payments.values()),'report_cash_bridge')
        require(all(receipts[k]>=0 and payments[k]>=0 and receipts[k]-payments[k]==cash[k] for k in CASH),'report_gross_cash')

    def decode_submission(self,sub):
        raw=self.blob_bytes(self.body(sub)['blob_ref']);r=decode(raw)
        # Refuse a foreign profile before resolving any of its references.
        if isinstance(r,dict):
            pr=r.get('body',{}).get('profile_ref',{})
            if pr and (pr.get('kind')!='Profile' or pr.get('schema')!=self.schema['schema_ids']['Profile']):raise Refusal('profile_mismatch')
        require(isinstance(r,dict),'closed_record_shape');self.record_shape(r)
        require(r['kind']=='OperationRequest','closed_record_shape')
        require(raw==enc(r),'noncanonical_request_bytes')
        return r

    def signature_contract(self,rq,sig):
        op=rq['operation'];profile=self.body(rq['profile_ref'])
        require(rq['arguments']['tag']==op and sig['operation']==op and sig['profile_ref']==rq['profile_ref'] and op in profile['operations'],'operation_signature_mismatch')
        require(sig['arguments_definition']=='Arguments.'+op,'operation_signature_mismatch')
        payloads={'accounting.authorize@1':['PostingAuthorization'],
            'accounting.propose@1':['JournalProposal','EconomicDelta'],
            'accounting.commit@1':['StateTransitionReceipt'],'report.build@1':['Report']}
        require(sig['payload_kinds']==payloads[op] and
            sig['effects']==('accounting_transaction' if op=='accounting.commit@1' else 'read'),'operation_signature_mismatch')

    def dispatch(self,rqref,w):
        rq=self.body(rqref);op=rq['operation'];args=rq['arguments']['value']
        require(rq['profile_ref']==self.alias['profile'],'profile_mismatch')
        self.signature_contract(rq,self.body(rq['signature_ref']))
        require(self.body(rq['execution']['environment_ref'])['runtime_executed'] is False,'environment_mismatch')
        if op=='accounting.commit@1':
            b=self.body(args['basis_ref']);stored=w['event_receipts'].get(self.identity(b))
            if stored:
                require(stored['request_ref']==rqref,'idempotency_conflict')
                self.receipt_publication(stored['receipt_ref'],w,financial=False)
                return 'replayed',None,stored['receipt_ref']
        require(rq['execution']['budget']['operation_count']>0 and rq['execution']['budget']['elapsed_seconds']>0,'budget_exhausted')
        if op=='report.build@1':
            require(rq['view_ref']==args['view_ref'],'report_context_mismatch')
            self.report_inputs(args,w);return 'completed',None,None
        b=self.body(args['basis_ref'])
        require(rq['view_ref']==b['view_ref']==w['current_view_ref'],'stale_dependency_view')
        require(rq['expected_head']==w['head']==self.head(b['opening_ref']),'stale_head')
        self.basis_effects(args['basis_ref'])
        if op!='accounting.authorize@1':self.posting(args)
        return 'completed',None,None

    def world_shape(self,w):
        require(set(w)=={'head','event_receipts','journals','deltas','receipts','published_records','current_view_ref','unaffected_owners'},'world_shape')
        require(w['head']==self.head(w['head']['state_ref']),'world_head_mismatch')
        require(w['published_records']==sorted(set(w['published_records'])),'world_publication_order')
        require(set(self.closure([w['head']['state_ref'],w['current_view_ref']]))<=set(w['published_records']),'world_head_unpublished')
        for k in ['journals','deltas','receipts']:
            require(len({enc(r) for r in w[k]})==len(w[k]),'world_duplicate_effect')
        for r in references(w):self.record(r)

    def exchange(self,e):
        before,after=e['world_before'],e['world_after'];self.world_shape(before);self.world_shape(after)
        res=self.body(e['response_ref'])
        require(res['submission_ref']==e['submission_ref'],'response_submission_binding')
        if res['statuses']['structural_validity']=='invalid':
            require(e['request_ref'] is None and res['request_ref'] is None and res['operation'] is None and
                res['input_view_ref'] is None and res['coverage'] is None and res['payload'] is None,'invalid_decode_has_request')
            require(len(res['diagnostics'])==1,'missing_structural_diagnostic')
            self.expected(lambda:self.decode_submission(e['submission_ref']),res['diagnostics'][0]['code'])
            require(before==after and res['disposition']=='rejected' and not res['unresolved'] and
                res['receipt_ref'] is None and res['commit_observation']=='not_committed','invalid_decode_mutated_world')
            return
        rec=self.decode_submission(e['submission_ref']);rqref=e['request_ref'];rq=self.body(rqref);op=rq['operation'];args=rq['arguments']['value']
        require(rec==self.record(rqref),'submission_request_bytes_mismatch')
        require(res['request_ref']==rqref and res['operation']==op and res['input_view_ref']==rq['view_ref'],'response_request_binding')
        try:status,code,receipt=self.dispatch(rqref,before)
        except Refusal as err:status,code,receipt=err.status,err.code,None
        require(res['disposition']==status,'wrong_disposition:'+status)
        require([x['code'] for x in res['diagnostics']]==([] if code is None else [code]),'wrong_diagnostic:'+str(code))
        cov=res['coverage'];domain=self.body(cov['domain_ref'])
        require(domain['request_ref']==rqref,'coverage_request_binding')
        groups=['completed','unresolved','unsupported','infeasible','cancelled']
        group='unresolved' if status=='partial' else 'unsupported' if status=='unsupported' else 'completed'
        require(len(cov[group])==1 and all(not cov[g] for g in groups if g!=group),'coverage_partition')
        require(self.body(cov[group][0])['domain_ref']==cov['domain_ref'],'coverage_domain_binding')
        if status=='partial':
            require(res['statuses']['mathematical_status']=='unresolved' and res['statuses']['computation_status']=='partial','partial_status')
            require(len(res['unresolved'])==1,'missing_obligation');ob=self.body(res['unresolved'][0])
            require(ob['code']==code and ob['basis_ref']==args['basis_ref'],'obligation_binding')
        else:require(not res['unresolved'],'spurious_obligation')
        payload=res['payload'];require(payload['tag']==op,'payload_operation_mismatch')
        if status not in ['completed','replayed']:
            require(before==after and not payload['result_refs'] and not payload['additional_commit'] and
                res['receipt_ref'] is None and res['commit_observation']=='not_committed','refusal_mutated_world')
            return
        outs=payload['result_refs']
        if status=='replayed':
            require(before==after and outs==[receipt] and res['receipt_ref']==receipt and not payload['additional_commit'] and
                res['commit_observation']=='committed','replay_additional_effect')
            # A replay must still succeed when financial derivation is forbidden.
            original=self.basis_effects
            def forbidden(*_):raise Refusal('replay_rederived_finances')
            self.basis_effects=forbidden
            try:require(self.dispatch(rqref,before)==('replayed',None,receipt),'replay_precedence')
            finally:self.basis_effects=original
        elif op=='accounting.commit@1':
            require(len(outs)==1 and outs[0]['kind']=='StateTransitionReceipt' and outs[0]==res['receipt_ref'] and
                payload['additional_commit'] and res['commit_observation']=='committed','commit_result_mismatch')
            self.atomic_world(rqref,outs[0],before,after);self.receipt_publication(outs[0],after)
        else:
            require(before==after and not payload['additional_commit'] and res['receipt_ref'] is None and
                res['commit_observation']=='not_committed','read_operation_mutated_world')
            if op=='accounting.authorize@1':
                require(len(outs)==1 and outs[0]['kind']=='PostingAuthorization','authorization_payload')
                self.authorization(outs[0],args['basis_ref'])
            elif op=='accounting.propose@1':
                require([r['kind'] for r in outs]==['JournalProposal','EconomicDelta'],'proposal_payload')
                self.posting({**args,'journal_ref':outs[0],'delta_ref':outs[1]})
            else:
                require(len(outs)==1 and outs[0]['kind']=='Report','report_payload')
                self.report_values(args,before,self.body(outs[0]))

    def recovery(self,r):
        obs=self.body(r['observation_ref']);by_id={e['id']:e for e in self.packet['exchanges']}
        first=by_id[r['retry_without_commit']];retry=by_id[r['retry_after_commit']]
        require(obs['submission_ref']==first['submission_ref']==retry['submission_ref'] and
            obs['request_ref']==first['request_ref']==retry['request_ref'],'lost_ack_bytes_mismatch')
        require(obs['commit_observation']=='unknown' and obs['receipt_ref'] is None and
            obs['next_action']=='resubmit_exact_original_request','transport_invents_commit')
        require(r['not_committed_world']==first['world_before'] and r['committed_world']==first['world_after']==retry['world_before']==retry['world_after'],'lost_ack_world_mismatch')
        require(self.dispatch(obs['request_ref'],r['not_committed_world'])[0]=='completed','lost_ack_no_commit_retry')
        require(self.dispatch(obs['request_ref'],r['committed_world'])[0]=='replayed','lost_ack_committed_retry')

    def challenge(self,c):
        kind=c['kind']
        if kind=='record_structure':fn=lambda:self.record_shape(c['candidate'])
        elif kind=='atomic_world':fn=lambda:self.atomic_world(c['request_ref'],c['receipt_ref'],c['world_before'],c['candidate'])
        elif kind=='report_input_world':fn=lambda:self.report_inputs(self.body(c['request_ref'])['arguments']['value'],c['candidate'])
        elif kind=='report_output':fn=lambda:self.report_values(self.body(c['request_ref'])['arguments']['value'],c['world'],c['candidate'])
        elif kind=='operation_signature':fn=lambda:self.signature_contract(self.body(c['request_ref']),c['candidate'])
        else:raise Refusal('unknown_challenge_kind')
        self.expected(fn,c['expected_code'])

    def offers(self):
        offered=self.packet['untrusted_profile_offers'];require(len(offered)==9,'predecessor_offer_coverage')
        profiles=[]
        for o in offered:
            rec=decode(self.blob_bytes(o['offered_record_blob']));r=o['offered_ref'];old=decode(self.blob_bytes(o['predecessor_blob']),False)
            require(rec==old['record_registry'][r['digest']] and rec['kind']==r['kind'] and rec['schema']==r['schema'],'predecessor_offer_binding')
            require(r['digest'] not in self.reg,'foreign_profile_registered')
            profiles.append(o['profile_id'])
        require('FinancingComponents/1' in profiles,'financing_predecessor_coverage')
        require(all('CorporateComponents/'+str(i) in profiles for i in range(1,6)),'corporate_predecessor_coverage')
        require('CorporateJointHistory/1' in profiles and 'GroupForeignOperation/1' in profiles and 'authored.insurance.close.v1' in profiles,'original_predecessor_coverage')

    def coverage(self):
        methods={self.body(r)['method_id'] for r in self.alias.values() if r['kind']=='MethodDefinition'}
        positives={e['method'] for e in self.packet['exchanges'] if e['role']=='positive'}
        refusals={e['method'] for e in self.packet['exchanges'] if e['id'].startswith('method-refusal.')}
        wrong_journals={e['method'] for e in self.packet['exchanges'] if e['id'].startswith('financial.wrong-journal.')}
        require(len(methods)==28 and methods==positives==refusals==wrong_journals,'method_coverage')
        transitions=self.packet['transitions'];require(len(self.packet['recoveries'])==len(transitions),'recovery_coverage')
        require(len({e['id'] for e in self.packet['exchanges']})==len(self.packet['exchanges']),'exchange_id_duplicate')
        by_id={e['id']:e for e in self.packet['exchanges']}
        for t in transitions:
            require(all(t[k]==by_id[t['id']][k] for k in ['request_ref','submission_ref','world_before','world_after']),'transition_exchange_binding')
            for suffix in ['.exact-retry','.identity-conflict','.retry-after-later-head-view']:
                require(t['id']+suffix in by_id,'transition_replay_coverage')
        for name,states in self.packet['case_states'].items():
            ts=[t for t in transitions if t['case_id']==name]
            require(states==[ts[0]['opening_ref'],*[t['closing_ref'] for t in ts]],'case_state_chain')
            require(all(ts[i]['closing_ref']==ts[i+1]['opening_ref'] for i in range(len(ts)-1)),'case_transition_chain')
            years={self.body(self.body(t['basis_ref'])['event_ref'])['event_date'][:4] for t in ts}
            labels={r['id'] for r in self.packet['reports']}
            require(name+'.lifetime' in labels and all(name+'.annual-'+y in labels for y in years),'annual_report_coverage')

    def run(self):
        self.audit('protected-inputs-predecessors-head-index',self.preservation)
        if not self.checks[-1]['passed']:return self.checks
        self.audit('source-specific-bindings-and-input-lock',self.source_checks)
        for d,r in self.reg.items():self.audit('record:'+r['key'],lambda d=d,r=r:self.record_shape(r,d))
        for key,r in self.alias.items():self.audit('alias:'+key,lambda key=key,r=r:require(self.record(r)['key']==key,'alias_key_mismatch'))
        self.audit('full-reference-closure',lambda:self.closure(list(self.alias.values())))
        for e in self.packet['exchanges']:self.audit('exchange:'+e['id'],lambda e=e:self.exchange(e))
        for r in self.packet['recoveries']:self.audit('recovery:'+r['retry_without_commit'],lambda r=r:self.recovery(r))
        for c in self.packet['validation_challenges']:self.audit('challenge:'+c['id'],lambda c=c:self.challenge(c))
        self.audit('predecessor-closed-profile-refusals',self.offers)
        self.audit('method-and-period-coverage',self.coverage)
        return self.checks

def main():
    started=time.monotonic();attempt=HERE/sys.argv[1]
    auditor=Auditor(attempt);checks=auditor.run();failed=[c for c in checks if not c['passed']]
    n=1
    while (attempt/f'validation-{n:02}.json').exists():n+=1
    out=attempt/f'validation-{n:02}.json'
    result=dict(evidence_mode='independent_documentary_check_not_runtime',checks=checks,failed=len(failed),
        wall_seconds=time.monotonic()-started,environment='CPU-only Python; CUDA_VISIBLE_DEVICES=-1; no GPU framework imported',
        packet_sha256=digest((attempt/'portable-exchanges.json').read_bytes()),verifier_sha256=digest(Path(__file__).read_bytes()),
        derivation_sha256=digest((HERE/'financial_checks.py').read_bytes()))
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(artifact=str(out.relative_to(ROOT)),checks=len(checks),failed=len(failed),failures=failed[:12])))
    raise SystemExit(bool(failed))

if __name__=='__main__':main()
