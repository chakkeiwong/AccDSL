"""Author finite immutable insurance exchanges; never execute a product service."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import shutil
import sys
import time
from fixtures import examples
from schema_design import schemas,sid,ROLES,OPS
from source_policy import RAW,TEXT,METHOD_FILES,ANCHORS

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[3]
REG={}; ALIAS={}; BLOBS={}; EX=[]; CRASH=[]; CASES=[]; CHALLENGES=[]
def enc(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(b): return hashlib.sha256(b).hexdigest()
def wire(v):
    if isinstance(v,F): return dict(n=str(v.numerator),d=str(v.denominator))
    if isinstance(v,dict): return {k:wire(x) for k,x in v.items()}
    if isinstance(v,list): return [wire(x) for x in v]
    return v
def refs(v):
    if isinstance(v,dict):
        if set(v)=={'kind','schema','digest'}: yield v
        else:
            for x in v.values(): yield from refs(x)
    elif isinstance(v,list):
        for x in v: yield from refs(x)
def unique(items): return [v for k,v in sorted({enc(x):x for x in items}.items())]
def add(kind,key,body):
    r=dict(kind=kind,schema=sid(kind),key=key,revision=0,body=wire(body),dependencies=unique(refs(body)))
    digest=sha(('accdsl.portable.v1/'+sid(kind)).encode()+b'\0'+enc(r)); REG[digest]=r
    ref=dict(kind=kind,schema=sid(kind),digest=digest); ALIAS[key]=ref; return ref
def body(r): return REG[r['digest']]['body']
def blob(path):
    b=path.read_bytes(); d=sha(b); BLOBS[d]=dict(path=str(path.relative_to(ROOT)),byte_length=len(b))
    return dict(kind='blob',algorithm='sha256',digest=d,byte_length=len(b))
def closure(roots):
    seen=set()
    def visit(r):
        if r['digest'] in seen:return
        seen.add(r['digest'])
        for x in REG[r['digest']]['dependencies']:visit(x)
    for r in roots: visit(r)
    return sorted(seen)
def write(p,v): p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def ident(r): return body(r)['client_id']+'/'+body(r)['request_id']
def ledger(c):
    old,new=c['opening'],c['closing']; delta=lambda role,k:new[role][k]-old[role][k]
    def liab(z):return z['lrc']+z['lic'] if z['model']=='PAA' else z['fcf']+z['csm']
    pairs=[('cash',delta('accounts','cash')),('underlying_asset',delta('accounts','underlying')),('derivative_asset',delta('accounts','derivative')),
      ('issued_acquisition_asset',delta('issued','acquisition_asset')),('replacement_acquisition_asset',delta('replacement','acquisition_asset')),
      ('issued_liability',liab(old['issued'])-liab(new['issued'])),('replacement_liability',liab(old['replacement'])-liab(new['replacement'])),
      ('held_asset',delta('held','fcf_asset')+delta('held','cost_csm')),
      ('insurance_service_result',-delta('accounts','profit')+delta('accounts','finance')+delta('accounts','held_result')),
      ('insurance_finance_result',-delta('accounts','finance')),('reinsurance_result',-delta('accounts','held_result')),('oci',-delta('accounts','oci'))]
    return [dict(account=k,signed_debit=v) for k,v in sorted(pairs) if v]

def main():
    global ART
    start=time.monotonic(); ART=HERE/sys.argv[1]; ART.mkdir(exist_ok=False); (ART/'wire').mkdir(); (ART/'inputs').mkdir()
    for p in sorted(HERE.iterdir()):
        if p.suffix in ('.py','.md'): shutil.copyfile(p,ART/'inputs'/p.name)
    shutil.copyfile(ROOT/'docs/plans/accounting-insurance-component-exchanges-20261015.md',ART/'inputs'/'plan.md')
    write(ART/'record-schemas.json',schemas())
    lock=add('SchemaLock','schema-lock',dict(profile_id='InsuranceComponents/1',schema_blob=blob(ART/'record-schemas.json'),semantic_contract_blob=blob(ART/'inputs/semantic-contract.md')))
    profile=add('Profile','profile',dict(profile_id='InsuranceComponents/1',schema_lock_ref=lock,operations=list(OPS),execution_mode='specification_example'))
    source=add('SourceSupport','source',dict(source_id='EU2023-1803-IFRS17',raw_blob=blob(ROOT/RAW),text_blob=blob(ROOT/TEXT),method_blobs=[blob(ROOT/p) for p in METHOD_FILES],anchors=sorted(set(ANCHORS.values()))))
    heads={}; worlds={}; contexts={}; views={}; later_views={}
    def request(key,op,arg,ctx,view,before,request_id=None):
        rq=add('OperationRequest','request.'+key,dict(profile_ref=profile,context_ref=ctx,view_ref=view,client_id='insurance-documentary-client',request_id=request_id or key,operation=op,arguments=arg,expected_heads=before,require_current=True))
        path=ART/'wire'/(key+'.json'); path.write_bytes(enc(body(rq)))
        sub=add('Submission','submission.'+key,dict(request_ref=rq,wire_blob=blob(path),decoder='canonical_JSON_exact_rationals_v1'))
        return rq,sub
    def response(key,rq,sub,output=None,receipt=None,disposition='completed',codes=(),published=None,additional=True):
        return add('OperationResult','response.'+key,dict(request_ref=rq,submission_ref=sub,disposition=disposition,diagnostics=list(codes),output_ref=output,receipt_ref=receipt,published_digests=published or [],additional_commit=additional))
    def exchange(key,role,rq,sub,res,before,after):EX.append(dict(id=key,role=role,request_ref=rq,submission_ref=sub,response_ref=res,world_before=deepcopy(before),world_after=deepcopy(after)))
    def publish(key,op,arg,ctx,view,before,after,output,base,late,codes=()):
        rq,sub=request(key,op,arg,ctx,view,before)
        status='report_published' if op==OPS[1] else ('unresolved_published' if codes else 'committed')
        receipt=add('Receipt','receipt.'+key,dict(request_ref=rq,output_ref=output,before_heads=before,after_heads=after,written_roles=[r for r in ROLES if before[r]!=after[r]],status=status))
        pub=closure([rq,sub,receipt]); res=response(key,rq,sub,output,receipt,'partial' if codes else 'completed',codes,pub)
        wb=deepcopy(base); wb['heads']=before; wb['current_view_ref']=view
        wa=deepcopy(wb); wa['heads']=after
        wa['published_records']=sorted(set(wb['published_records'])|set(closure([res])))
        if op==OPS[0] and body(output)['journal']:wa['journals'].append(dict(request_ref=rq,result_ref=output,lines=body(output)['journal']))
        wa['decisions'][ident(rq)]=dict(request_ref=rq,response_ref=res,output_ref=output,receipt_ref=receipt)
        exchange(key,'publication',rq,sub,res,wb,wa)
        replay=response(key+'.replay',rq,sub,output,receipt,'replayed',codes,pub,False)
        exchange(key+'.replay','exact_replay',rq,sub,replay,wa,wa)
        stale=deepcopy(wa); stale['current_view_ref']=late
        exchange(key+'.replay-new-view','replay_before_freshness',rq,sub,replay,stale,stale)
        cr,cs=request(key+'.conflict',op,arg,ctx,late,before,request_id=key)
        er=response(key+'.conflict',cr,cs,disposition='rejected',codes=['identity_conflict'],additional=False)
        exchange(key+'.conflict','identity_conflict',cr,cs,er,wa,wa)
        sr,ss=request(key+'.stale-view',op,arg,ctx,view,before)
        er=response(key+'.stale-view',sr,ss,disposition='rejected',codes=['stale_view'],additional=False)
        sw=deepcopy(wb); sw['current_view_ref']=late
        exchange(key+'.stale-view','new_stale_view',sr,ss,er,sw,sw)
        hr,hs=request(key+'.stale-head',op,arg,ctx,view,before)
        er=response(key+'.stale-head',hr,hs,disposition='rejected',codes=['stale_head'],additional=False)
        hw=deepcopy(wb); hw['heads']=dict(hw['heads'],accounts=before['held'])
        exchange(key+'.stale-head','new_stale_head',hr,hs,er,hw,hw)
        for committed in (False,True):
            ck=key+('.lost-ack-committed' if committed else '.lost-ack-uncommitted')
            ob=add('TransportObservation','transport.'+ck,dict(submission_ref=sub,outcome='acknowledgement_lost',commit_knowledge='unknown'))
            crash_before=wa if committed else wb
            recovered=replay if committed else res
            exchange(ck,'recovery',rq,sub,recovered,crash_before,wa)
            CRASH.append(dict(id=ck,observation_ref=ob,committed=committed,publication_id=key,recovery_id=ck,world_before=deepcopy(wb),world_after_crash=deepcopy(crash_before)))
        return wa
    for c in examples():
        key=c['id']; prior=c['prior']; root=contexts[prior] if prior else None
        ctx=root or add('Context','context.'+key,dict(entity_id='Insurer-Synthetic',branch_id=key,currency='USD',unit='illustrative_million',authority='historical_EU2023_IFRS17_scenario',tax='uncomputed',fx='none_supplied'))
        contexts[key]=ctx
        fp=ART/'inputs'/(key+'-facts.json'); write(fp,wire(dict(input=c['input'],opening=c['opening'])))
        ev=add('Evidence','evidence.'+key,dict(evidence_id=key,context_ref=ctx,available_at='2027-01-02T00:00:00Z',ingested_at='2027-01-02T01:00:00Z',content_blob=blob(fp),provenance='synthetic_supplied'))
        evidence=list(body(views[prior])['evidence_refs'])+[ev] if prior else [ev]
        view=add('View','view.'+key,dict(context_ref=ctx,evidence_refs=evidence,decision_at='2027-01-03T00:00:00Z',system_asof='2027-01-03T00:00:00Z',revision=len(evidence)-1))
        late=add('View','view.'+key+'.later',dict(context_ref=ctx,evidence_refs=evidence,decision_at='2027-01-04T00:00:00Z',system_asof='2027-01-04T00:00:00Z',revision=len(evidence)))
        views[key]=view; later_views[key]=late
        group_ids=dict(issued='issued-A',replacement='replacement-B',held='held-R',accounts='legal-book')
        opening=heads[prior] if prior else {r:add('OwnerState','opening.'+key+'.'+r,dict(context_ref=ctx,role=r,owner_id=body(ctx)['branch_id']+'/'+r,group_id=group_ids[r],generation=0,last_result_ref=None,balances=c['opening'][r])) for r in ROLES}
        assert {r:body(opening[r])['balances'] for r in ROLES}==wire(c['opening'])
        inp=add('MethodInput','input.'+key,c['input'])
        basis=add('MethodBasis','basis.'+key,dict(context_ref=ctx,view_ref=view,source_ref=source,input_ref=inp,evidence_ref=ev,opening_heads=opening,method_anchor=ANCHORS[c['input']['method_id']],measurement_date='2026-12-31'))
        result=add('ComponentResult','component.'+key,dict(basis_ref=basis,method_id=c['input']['method_id'],status=c['status'],diagnostics=c['diagnostics'],closing=c['closing'],detail=c['detail'],journal=ledger(c)))
        closing={r:(add('OwnerState','closing.'+key+'.'+r,dict(body(opening[r]),generation=body(opening[r])['generation']+1,last_result_ref=result,balances=c['closing'][r])) if wire(c['opening'][r])!=wire(c['closing'][r]) else opening[r]) for r in ROLES}
        heads[key]=closing
        auth=add('Authorization','authorization.'+key,dict(basis_ref=basis,opening_heads=opening,authority='authored_documentary_admission'))
        proposal=add('Proposal','proposal.'+key,dict(basis_ref=basis,result_ref=result,authorization_ref=auth,before_heads=opening,after_heads=closing))
        base=worlds[prior] if prior else dict(heads=opening,current_view_ref=view,journals=[],decisions={},published_records=closure(list(opening.values())),unrelated_heads={'Other-Entity':'preserved-head-9'})
        worlds[key]=publish(key,OPS[0],dict(proposal_ref=proposal),ctx,view,opening,closing,result,base,late,c['diagnostics'])
        row=dict(id=key,method_id=c['input']['method_id'],basis_ref=basis,result_ref=result,proposal_ref=proposal,publication_id=key)
        if c['status']=='resolved':
            report=add('ComponentReport','report.'+key,dict(context_ref=ctx,state_refs=closing,scope='component_states_not_whole_company_statements',tax_status='uncomputed'))
            publish(key+'.report',OPS[1],dict(state_refs=closing),ctx,view,closing,closing,report,worlds[key],late)
            row['report_ref']=report
        CASES.append(row)
    adversaries()
    snapshots={p.name:dict(sha256=sha(p.read_bytes()),original_path=str((HERE/p.name).relative_to(ROOT)) if (HERE/p.name).is_file() else ('docs/plans/accounting-insurance-component-exchanges-20261015.md' if p.name=='plan.md' else None)) for p in sorted((ART/'inputs').iterdir())}
    packet=dict(profile='InsuranceComponents/1',record_registry=REG,aliases=ALIAS,blobs=BLOBS,cases=CASES,exchanges=EX,crash_worlds=CRASH,challenges=CHALLENGES,input_snapshots=snapshots,predecessor_lock_blob=blob(HERE/'predecessor-lock.json'))
    write(ART/'portable-exchanges.json',packet)
    summary=dict(profile=packet['profile'],methods=len(set(c['method_id'] for c in CASES)),cases=len(CASES),records=len(REG),exchanges=len(EX),crash_worlds=len(CRASH),challenges=len(CHALLENGES),packet_sha256=sha((ART/'portable-exchanges.json').read_bytes()),wall_seconds=time.monotonic()-start,command=sys.argv,interpreter=sys.executable,hardware='CPU exact arithmetic; no GPU framework imported')
    write(ART/'build-result.json',summary); print(json.dumps(summary))

def adversaries():
    def add_ch(label,scope,case,mutations,code):
        CHALLENGES.append(dict(id=label,scope=scope,case_id=case,mutations=wire(mutations),expected_code=code))
    def mutation(path,value):return dict(path=path,value=value)
    def input_ch(label,key,path,value,code): add_ch(label,'input',key,[mutation(['input']+path,value)],code)
    input_ch('mixed-cohort','group-membership',['contracts',0,'cohort'],'2025','incompatible_membership')
    input_ch('mixed-issued-held','group-membership',['contracts',0,'contract_role'],'held','incompatible_membership')
    input_ch('acquisition-overallocated','acquisition-allocated',['allocations',0,'amount'],F(9),'allocation_not_conserved')
    input_ch('whole-group-loss-recovery','partial-treaty',['covered_loss'],F(20),'wrong_covered_loss')
    input_ch('cross-group-treaty','partial-treaty',['covered_group'],'another-group','wrong_coverage_join')
    input_ch('premature-treaty-recognition','partial-treaty',['recognition_date'],'2023-12-31','invalid_treaty_recognition')
    input_ch('new-terms-disguised-as-estimate','covered-estimate-change',['cause'],'new_terms','wrong_change_cause')
    input_ch('changed-quota-without-terms','covered-estimate-change',['share'],F(3,4),'treaty_lineage_mismatch')
    input_ch('unrelated-claim-estimate','covered-estimate-change',['old_covered_claims'],F(47),'treaty_lineage_mismatch')
    input_ch('existing-right-replacement','modification-replacement',['existing_right'],True,'modification_not_admitted')
    input_ch('unadmitted-paa','paa-deferred',['eligibility'],'unknown','paa_not_admitted')
    input_ch('paa-inception-rate','paa-lic-first-finance',['rate_origin'],'inception','wrong_rate_origin')
    input_ch('paa-rate-substitution','paa-lic-first-finance',['incurrence_rate'],F(1,20),'claim_rate_lineage_mismatch')
    input_ch('vfa-held-admission','vfa-recognized',['role'],'held','vfa_not_admitted')
    input_ch('pool-share-substitution','vfa-pool-appreciation',['policyholder_share'],F(3,4),'pool_share_lineage_mismatch')
    input_ch('late-mitigation-strategy','vfa-guarantee-mitigated',['strategy'],'later_documented','mitigation_not_admitted')
    input_ch('credit-dominant-unresolved','vfa-guarantee-mitigated',['credit_not_dominant'],'unknown','mitigation_not_admitted')
    input_ch('stale-variable-rate','variable-prospective-remeasurement',['allocation_rate'],F(1,10),'wrong_prospective_allocation_rate')
    input_ch('fixed-origin-variable-rate','variable-prospective-remeasurement',['allocation_basis'],'initial_fixed','wrong_allocation_origin')
    for c in CASES:
        r=body(c['result_ref'])
        if r['status']=='resolved':
            first=next((k for k,v in r['detail'].items() if isinstance(v,dict) and set(v)=={'n','d'}),None)
            if first:
                v=r['detail'][first]; changed=F(int(v['n']),int(v['d']))+1
                add_ch('wrong-finance-'+c['id'],'result',c['id'],[mutation(['detail',first],changed)],'financial_result_mismatch')
    add_ch('invented-deemed-cash','result','modification-replacement',[mutation(['closing','accounts','cash'],F(260))],'financial_result_mismatch')
    add_ch('investment-as-revenue','result','vfa-investment-repaid',[mutation(['closing','accounts','revenue'],F(120))],'financial_result_mismatch')
    add_ch('loss-recovery-double-asset','result','partial-treaty',[mutation(['closing','held','fcf_asset'],F(57,2))],'financial_result_mismatch')
    for key in ('covered-estimate-change','modification-replacement','joint-service-settlement'):
        row=next(e for e in EX if e['id']==key)
        for role in ROLES:
            if row['world_after']['heads'][role]!=row['world_before']['heads'][role]:
                add_ch('partial-publication-'+key+'-'+role,'world',key,[mutation(['heads',role],row['world_before']['heads'][role])],'partial_publication')
        add_ch('missing-journal-'+key,'world',key,[mutation(['journals'],row['world_before']['journals'])],'partial_publication')
        add_ch('missing-dependency-'+key,'world',key,[mutation(['published_records'],row['world_before']['published_records'])],'partial_publication')
    add_ch('wrong-source','binding','partial-treaty',[mutation(['source_ref'],ALIAS['profile'])],'source_binding')
    add_ch('unavailable-evidence','binding','partial-treaty',[mutation(['evidence_available_at'],'2028-01-01T00:00:00Z')],'future_evidence')
    add_ch('wrong-rule-anchor','binding','partial-treaty',[mutation(['method_anchor'],'IFRS17.53-59')],'method_source_binding')
    add_ch('wrong-issued-owner','binding','partial-treaty',[mutation(['issued_group'],'another-group')],'owner_group_binding')
    add_ch('wire-unreduced','shape','partial-treaty',[mutation(['input','share'],dict(n='2',d='4'))],'noncanonical_rational')
    add_ch('wire-open-payload','shape','partial-treaty',[mutation(['input','free_payload'],{})],'closed_record_shape')

if __name__=='__main__':main()
