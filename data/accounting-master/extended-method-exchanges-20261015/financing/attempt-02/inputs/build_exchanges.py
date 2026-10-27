"""Author numbered documentary packets; never invoke an accounting service.

Expected financial effects come only from authored_cases. Independent checking
is in verify_exchanges.py and financial_checks.py; neither is imported here.
"""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import shutil
import time
from schema_design import schemas, sid, COMPONENTS, EVENTS, ACCOUNTS, PROFIT, OCI, EQUITY, CASH, OCI_MOVEMENTS, EQUITY_MOVEMENTS
from authored_cases import CASES
from adverse_cases import METHOD_REFUSALS, BOUNDARIES
from source_policy import SOURCES

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
REG,ALIASES,BLOBS,EX,STEPS,REPORTS={},{},{},[],[],[]
ART=None
def enc(v):return json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
def q(v):
    n=F(v);return {'n':str(n.numerator),'d':str(n.denominator)}
def number(v):return F(int(v['n']),int(v['d']))
def refs(v):
    if isinstance(v,dict):
        if set(v)=={'kind','schema','digest'}:yield v
        else:
            for x in v.values():yield from refs(x)
    elif isinstance(v,list):
        for x in v:yield from refs(x)
def add(kind,key,b):
    assert key not in ALIASES,key
    ds={enc(r):r for r in refs(b)}
    r=dict(kind=kind,schema=sid(kind),key=key,revision=0,body=b,dependencies=[ds[k] for k in sorted(ds)])
    d=hashlib.sha256(('accdsl.portable.v1/'+sid(kind)).encode()+b'\0'+enc(r)).hexdigest()
    REG[d]=r;ALIASES[key]=dict(kind=kind,schema=sid(kind),digest=d);return ALIASES[key]
def body(r):return REG[r['digest']]['body']
def blob(p):
    b=p.read_bytes();d=hashlib.sha256(b).hexdigest();BLOBS[d]=dict(path=str(p.relative_to(ROOT)),byte_length=len(b))
    return dict(kind='blob',algorithm='sha256',digest=d,byte_length=len(b))
def typed(s,v):
    if v is None:return None
    if s.get('type')=='object':
        if set(s['properties'])=={'n','d'}:return q(v)
        return {k:typed(t,v[k]) for k,t in s['properties'].items()}
    if s.get('type')=='array':return [typed(s['items'],x) for x in v]
    if 'anyOf' in s:return typed(s['anyOf'][0],v)
    return v
def vector(v,keys):return {k:q(v.get(k,0)) for k in keys}
def closure(roots):
    found=set()
    def visit(r):
        if r['digest'] in found:return
        found.add(r['digest'])
        for d in REG[r['digest']]['dependencies']:visit(d)
    for r in roots:visit(r)
    return sorted(found)
def owner(st):
    c=body(body(st)['context_ref']);return '/'.join(c[k] for k in ['entity_id','book_id','branch_key'])
def head(st):return dict(owner_key=owner(st),state_ref=st,generation=body(st)['sequence'])
def world(st):return dict(head=head(st),event_receipts={},journals=[],deltas=[],receipts=[],published_records=closure([st]),
    current_view_ref=body(st)['view_ref'],unaffected_owners={'Other/Legal':dict(generation=7,balance_digest='0'*64)})
def identity(b):return enc([b['identity'][k] for k in ['entity_id','book_id','branch_key','business_event_id']]).decode()
def dump(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n')

def main():
    global ART
    started=time.monotonic();n=1
    while (OUT/f'attempt-{n:02}').exists():n+=1
    ART=OUT/f'attempt-{n:02}';ART.mkdir();(ART/'bytes').mkdir();(ART/'inputs').mkdir()
    for p in sorted(OUT.iterdir()):
        if p.is_file() and (p.suffix=='.py' or p.name in ['semantic-contract.md','source-reading.md','resume-audit.md']):
            shutil.copyfile(p,ART/'inputs'/p.name)
    schema=schemas();dump(ART/'record-schemas.json',schema)
    contract=ART/'inputs/semantic-contract.md'
    lock=add('SchemaLock','lock',dict(schema_blob=blob(ART/'record-schemas.json'),semantic_contract_blob=blob(contract),format='jsonschema2020-12'))
    ops=['accounting.authorize@1','accounting.propose@1','accounting.commit@1','report.build@1']
    profile=add('Profile','profile',dict(profile_id='FinancingComponents/1',schema_lock_ref=lock,operations=ops,
        book_mode='synthetic',execution_mode='specification_example',interest_cash_policy='historical_IAS7_operating_election'))
    payloads=[['PostingAuthorization'],['JournalProposal','EconomicDelta'],['StateTransitionReceipt'],['Report']]
    signatures={op:add('OperationSignature','signature.'+op,dict(operation=op,profile_ref=profile,arguments_definition='Arguments.'+op,
        payload_kinds=payloads[i],effects='accounting_transaction' if i==2 else 'read')) for i,op in enumerate(ops)}
    env=add('Environment','environment',dict(purpose='documentary_fixture',numerics='exact_rational',runtime_executed=False))
    decoder=add('Decoder','decoder',dict(media_type='application/json',canonical_encoding='accdsl.portable.v1'))
    sources={}
    for name,p in SOURCES.items():
        sources[name]=add('SourceSupport','source.'+name,dict(source_pdf=blob(ROOT/(p['base']+'.pdf')),
            source_text=blob(ROOT/(p['base']+'.txt')),method_text=blob(ROOT/p['method']),inspection_note=blob(ART/'inputs/source-reading.md'),
            anchors=p['anchors'],authority_scope='historical_not_current_admission',family=p['family'],
            period_start_inclusive=p['start'],period_start_exclusive=p['end']))
    view=add('View','view',dict(source_refs=list(sources.values()),revision=0,supersedes_ref=None,information_mode='archival_synthetic'))
    methods={}
    for m,(tag,_) in EVENTS.items():
        family=SOURCES[tag]['family'];methods[m]=add('MethodDefinition','method.'+m,dict(method_id=m,component_kind=tag,
            method_status='specified_finite',source_ref=sources[tag],supporting_source_refs=[sources['cash_'+family]],
            contract_blob=blob(contract),profile_ref=profile))

    def request(key,op,args,st=None,v=view,prof=profile,budget=1000):
        r=add('OperationRequest','request.'+key,dict(operation=op,request_id=key,workspace_key='FinancingComponents-specification',
            profile_ref=prof,signature_ref=signatures[op],view_ref=v,arguments=dict(tag=op,value=args),
            execution=dict(mode='specification_example',budget=dict(operation_count=budget,elapsed_seconds=60),environment_ref=env),
            expected_head=head(st) if st else None))
        p=ART/'bytes'/(key+'.json');p.write_bytes(enc(REG[r['digest']]))
        sub=add('Submission','submission.'+key,dict(blob_ref=blob(p),media_type='application/json',transport='authored_fixture',decoder_ref=decoder))
        return r,sub

    def response(key,rq,sub,disposition='completed',outputs=(),receipt=None,code=None,basis=None):
        dom=add('Domain','domain.'+key,dict(request_ref=rq,meaning='singleton_request_decision'))
        region=add('Region','region.'+key,dict(domain_ref=dom,predicate='this_request'))
        partial=disposition=='partial';unsupported=disposition=='unsupported'
        obligations=[add('Obligation','obligation.'+key,dict(code=code,required_input=code,basis_ref=basis))] if partial else []
        coverage=dict(domain_ref=dom,completed=[] if partial or unsupported else [region],unresolved=[region] if partial else [],
            unsupported=[region] if unsupported else [],infeasible=[],cancelled=[],relation='disjoint_exhaustive')
        return add('OperationResult','result.'+key,dict(submission_ref=sub,request_ref=rq,operation=body(rq)['operation'],
            input_view_ref=body(rq)['view_ref'],disposition=disposition,statuses=dict(structural_validity='valid',
                mathematical_status='unresolved' if partial else 'defined',computation_status='partial' if partial else
                'not_computed' if disposition in ['rejected','unsupported'] else 'complete',empirical_justification='not_established',
                capability_status='specified_only_no_runtime',accounting_validity='not_assessed',forecast_validity='not_assessed',
                product_readiness='not_implemented',human_acceptance='pending'),
            payload=dict(tag=body(rq)['operation'],result_refs=list(outputs),additional_commit=disposition=='completed' and receipt is not None),
            diagnostics=[] if not code else [dict(code=code,stage='binding_financial_or_owner_validation',record_ref=None,
                source_locator=None,field_path='arguments',affected_query_branch_ids=[],dependency_path=[],observed=code,
                expected_rule='FinancingComponents/1',retry_advice='repair_named_input_or_resubmit_exact_request',blocking_diagnostic_ids=[])],
            coverage=coverage,unresolved=obligations,continuation_ref=None,commit_observation='committed' if receipt else 'not_committed',
            receipt_ref=receipt,evidence_mode='specification_example'))

    def exchange(key,rq,sub,res,before,after,role='positive',method=None):
        EX.append(dict(id=key,role=role,method=method,request_ref=rq,submission_ref=sub,response_ref=res,
            world_before=deepcopy(before),world_after=deepcopy(after)))

    def auth_records(key,br):
        b=body(br);m=body(b['method_ref']);ev=body(b['event_ref'])
        adm=add('Admission','admission.'+key,dict(basis_ref=br,source_ref=m['source_ref'],context_ref=b['context_ref'],
            instant=ev['instant'],status='eligible',fact_basis='authored_synthetic',findings=[
                dict(name='conditional_source',status='satisfied',support_ref=m['source_ref']),
                dict(name='exact_context',status='satisfied',support_ref=b['context_ref']),
                dict(name='supplied_economic_facts',status='satisfied',support_ref=b['event_ref'])]))
        return add('PostingAuthorization','authorization.'+key,dict(basis_ref=br,admission_ref=adm,view_ref=b['view_ref'],posting_permitted=True))

    case_states={};representatives={};case_worlds={};recoveries=[];offers=[];challenges=[]
    for ca in CASES:
        name,tag=ca['id'],ca['tag'];family=ca['source_family'];first_year=int(ca['steps'][0]['event_date'][:4])
        context=add('Context','context.'+name,dict(entity_id='Synthetic-'+name,book_id='Legal',branch_key='base',currency=ca['currency'],
            basis='historical_EU_IFRS_conditional' if family=='EU_IFRS' else 'historical_AU_AASB_conditional',issuer_class='for_profit',calendar='dated_synthetic'))
        authority=add('Authority','authority.'+name,dict(source_ref=sources[tag],supporting_source_refs=[sources['cash_'+family]],
            context_ref=context,start_inclusive=0,end_exclusive=10000,evidence_class='synthetic_conditional_admission'))
        comp=add('ComponentState',name+'.component.0',dict(tag=tag,value=typed(COMPONENTS[tag],ca['opening_component'])))
        opening=add('CompanyState',name+'.state.0',dict(context_ref=context,view_ref=view,sequence=0,instant=0,as_of_date=f'{first_year}-01-01',
            component_ref=comp,balances=vector(ca['opening_balances'],ACCOUNTS),cash_movements=vector({},CASH),
            cash_receipts=vector({},CASH),cash_payments=vector({},CASH),oci_movements=vector({},OCI_MOVEMENTS),
            equity_movements=vector({},EQUITY_MOVEMENTS),tax_status='uncomputed'))
        w=world(opening);states=[opening];cs=[]
        for i,s in enumerate(ca['steps'],1):
            key=name+'.'+str(i);year=int(s['event_date'][:4]);m=s['method']
            event=add('EconomicEvent',key+'.event',dict(method_id=m,context_ref=context,instant=i*10,event_date=s['event_date'],
                reporting_period_start=f'{year}-01-01',reporting_period_end_exclusive=f'{year+1}-01-01',parameters=typed(EVENTS[m][1],s['parameters'])))
            basis=add('AccountingEventBasis',key+'.basis',dict(identity={**{k:body(context)[k] for k in ['entity_id','book_id','branch_key']},
                'business_event_id':key},opening_ref=opening,event_ref=event,method_ref=methods[m],authority_ref=authority,view_ref=view,context_ref=context))
            auth=auth_records(key,basis)
            component=add('ComponentState',key+'.component',dict(tag=tag,value=typed(COMPONENTS[tag],s['after'])))
            old=body(opening);new=deepcopy(old);new.update(sequence=i,instant=i*10,as_of_date=s['event_date'],component_ref=component)
            new['balances']={a:q(number(old['balances'][a])+s['journal'].get(a,0)) for a in ACCOUNTS}
            for dst,src in [('cash_movements','cash_change'),('oci_movements','oci_change'),('equity_movements','equity_change')]:
                new[dst]={a:q(number(v)+s[src].get(a,0)) for a,v in old[dst].items()}
            new['cash_receipts']={a:q(number(v)+max(F(0),s['cash_change'].get(a,0))) for a,v in old['cash_receipts'].items()}
            new['cash_payments']={a:q(number(v)+max(F(0),-s['cash_change'].get(a,0))) for a,v in old['cash_payments'].items()}
            closing=add('CompanyState',key+'.state',new)
            journal=add('JournalProposal',key+'.journal',dict(basis_ref=basis,mode='monetary' if any(s['journal'].values()) else 'state_only',
                currency=ca['currency'],lines=[dict(account=a,signed_amount=q(v)) for a,v in sorted(s['journal'].items()) if v]))
            delta=add('EconomicDelta',key+'.delta',dict(basis_ref=basis,opening_ref=opening,closing_ref=closing,cash_change=vector(s['cash_change'],CASH)))
            for op,suffix,args,outs in [
                ('accounting.authorize@1','authorize',dict(basis_ref=basis),[auth]),
                ('accounting.propose@1','propose',dict(basis_ref=basis,authorization_ref=auth),[journal,delta])]:
                label=key+'.'+suffix;rq,sub=request(label,op,args,opening);res=response(label,rq,sub,outputs=outs)
                exchange(label,rq,sub,res,w,w,method=m)
            args=dict(basis_ref=basis,authorization_ref=auth,journal_ref=journal,delta_ref=delta)
            rq,sub=request(key,'accounting.commit@1',args,opening)
            receipt=add('StateTransitionReceipt',key+'.receipt',dict(request_ref=rq,**args,opening_ref=opening,closing_ref=closing,generation=i,status='committed'))
            after=deepcopy(w);after['head']=head(closing);after['event_receipts'][identity(body(basis))]=dict(request_ref=rq,receipt_ref=receipt)
            for dst,r in [('journals',journal),('deltas',delta),('receipts',receipt)]:after[dst].append(r)
            after['published_records']=sorted(set(w['published_records'])|set(closure([receipt])))
            res=response(key,rq,sub,outputs=[receipt],receipt=receipt);exchange(key,rq,sub,res,w,after,method=m)
            t=dict(id=key,case_id=name,method=m,basis_ref=basis,authorization_ref=auth,journal_ref=journal,delta_ref=delta,
                opening_ref=opening,closing_ref=closing,receipt_ref=receipt,request_ref=rq,submission_ref=sub,
                world_before=deepcopy(w),world_after=deepcopy(after))
            STEPS.append(t);cs.append(t);representatives.setdefault(m,t)
            replay=key+'.exact-retry';rr=response(replay,rq,sub,'replayed',[receipt],receipt)
            exchange(replay,rq,sub,rr,after,after,'exact_retry',m)
            conflict=key+'.identity-conflict';cr,ss=request(conflict,'accounting.commit@1',args,opening)
            rr=response(conflict,cr,ss,'rejected',code='idempotency_conflict');exchange(conflict,cr,ss,rr,after,after,'identity_conflict',m)
            obs=add('TransportObservation',key+'.lost-ack',dict(submission_ref=sub,request_ref=rq,observation='acknowledgement_timeout',
                commit_observation='unknown',receipt_ref=None,next_action='resubmit_exact_original_request'))
            recoveries.append(dict(observation_ref=obs,retry_without_commit=key,retry_after_commit=replay,
                not_committed_world=deepcopy(w),committed_world=deepcopy(after)))
            opening,w=closing,after;states.append(closing)
        case_states[name]=states;case_worlds[name]=w

    def report(label,opening,closing,receipts,w,start,end):
        a,b=body(opening),body(closing);v0={k:number(v) for k,v in a['balances'].items()};v1={k:number(v) for k,v in b['balances'].items()}
        def eq(v):return -sum(v[k] for k in EQUITY+OCI+PROFIT)
        interest=0
        for rr in receipts:
            ev=body(body(body(rr)['basis_ref'])['event_ref'])
            if ev['method_id']=='cashflow.pay_interest':interest+=number(ev['parameters']['amount'])
        values=dict(cash=v1['cash'],assets=v1['cash']+v1['inventory']+max(F(0),v1['derivative']),
            liabilities=-sum(v1[k] for k in ['debt','bonus_payable','award_liability'])+max(F(0),-v1['derivative']),
            equity=eq(v1),profit=-sum(v1[k]-v0[k] for k in PROFIT),
            oci=sum(number(b['oci_movements'][k])-number(a['oci_movements'][k]) for k in OCI_MOVEMENTS),
            **{k:number(b['cash_movements'][k])-number(a['cash_movements'][k]) for k in CASH})
        rb=dict(opening_ref=opening,state_ref=closing,view_ref=view,period_start=start,period_end_exclusive=end,receipt_refs=receipts,
            currency=body(b['context_ref'])['currency'],values={k:q(v) for k,v in values.items()},
            cash_receipts={k:q(number(b['cash_receipts'][k])-number(a['cash_receipts'][k])) for k in CASH},
            cash_payments={k:q(number(b['cash_payments'][k])-number(a['cash_payments'][k])) for k in CASH},interest_paid=q(interest),
            income_statement={k:q(v1[k]-v0[k]) for k in PROFIT},
            oci_components={k:q(number(b['oci_movements'][k])-number(a['oci_movements'][k])) for k in OCI_MOVEMENTS},
            other_equity_movements={k:q(number(b['equity_movements'][k])-number(a['equity_movements'][k])) for k in EQUITY_MOVEMENTS},
            tax_status='uncomputed',complete_company_after_tax=False)
        rr=add('Report',label,rb);args={k:rb[k] for k in ['opening_ref','state_ref','view_ref','period_start','period_end_exclusive','receipt_refs']};args['require_current']=True
        rq,sub=request(label,'report.build@1',args);res=response(label,rq,sub,outputs=[rr]);exchange(label,rq,sub,res,w,w,'report')
        REPORTS.append(dict(id=label,report_ref=rr,request_ref=rq,world=deepcopy(w)))

    for ca in CASES:
        name=ca['id'];ts=[s for s in STEPS if s['case_id']==name];years=sorted({int(body(body(t['basis_ref'])['event_ref'])['event_date'][:4]) for t in ts})
        report(name+'.lifetime',ts[0]['opening_ref'],ts[-1]['closing_ref'],[t['receipt_ref'] for t in ts],case_worlds[name],f'{years[0]}-01-01',f'{years[-1]+1}-01-01')
        for year in years:
            ys=[t for t in ts if body(body(t['basis_ref'])['event_ref'])['event_date'].startswith(str(year))]
            report(name+'.annual-'+str(year),ys[0]['opening_ref'],ys[-1]['closing_ref'],[t['receipt_ref'] for t in ys],case_worlds[name],f'{year}-01-01',f'{year+1}-01-01')

    def changed_basis(t,key,parameters=None,event_patch=None,component_patch=None,basis_patch=None,authority_patch=None):
        b=deepcopy(body(t['basis_ref']));ev=deepcopy(body(b['event_ref']));m=ev['method_id']
        if parameters is not None:
            for k,v in parameters.items():ev['parameters'][k]=typed(EVENTS[m][1]['properties'][k],v)
        ev.update(event_patch or {});b['event_ref']=add('EconomicEvent',key+'.event',ev)
        if component_patch:
            sb=deepcopy(body(b['opening_ref']));cb=deepcopy(body(sb['component_ref']));tag=cb['tag']
            for k,v in component_patch.items():cb['value'][k]=typed(COMPONENTS[tag]['properties'][k],v)
            sb['component_ref']=add('ComponentState',key+'.component',cb);b['opening_ref']=add('CompanyState',key+'.opening',sb)
        if authority_patch:
            ab=deepcopy(body(b['authority_ref']));ab.update(authority_patch);b['authority_ref']=add('Authority',key+'.authority',ab)
        b['identity']['business_event_id']=key;b.update(basis_patch or {})
        return add('AccountingEventBasis',key+'.basis',b)

    def refused_basis(key,br,code,status='rejected',before=None,role='semantic_adverse'):
        st=body(br)['opening_ref'];w=before or world(st);rq,sub=request(key,'accounting.authorize@1',dict(basis_ref=br),st,v=body(br)['view_ref'])
        res=response(key,rq,sub,status,code=code,basis=br);exchange(key,rq,sub,res,w,w,role,body(body(br)['event_ref'])['method_id'])

    for m,(parameters,code,status) in METHOD_REFUSALS.items():
        t=representatives[m];key='method-refusal.'+m
        cp={'active':False} if m=='cashflow.discontinue' else None
        br=changed_basis(t,key,parameters=parameters,component_patch=cp);refused_basis(key,br,code,status)
    for label,case_id,m,pp,cp,date,code,status in BOUNDARIES:
        t=next(s for s in STEPS if s['case_id']==case_id and s['method']==m);key='boundary.'+label
        ep={'event_date':date} if date else None
        if date and date<body(t['opening_ref'])['as_of_date']:code='event_before_opening'
        br=changed_basis(t,key,parameters=pp,component_patch=cp,event_patch=ep);refused_basis(key,br,code,status)

    t=representatives['amendment.bind'];base=body(t['basis_ref'])
    other=add('Context','context.wrong-book',{**body(base['context_ref']),'book_id':'DifferentLegal'})
    generic=[('wrong-book',dict(basis_patch={'context_ref':other}),'basis_context_mismatch'),
        ('wrong-identity',dict(basis_patch={'identity':{**base['identity'],'book_id':'DifferentLegal'}}),'owner_identity_mismatch'),
        ('backdated-event',dict(event_patch={'event_date':'2023-12-31','reporting_period_start':'2023-01-01','reporting_period_end_exclusive':'2024-01-01'}),'event_before_opening'),
        ('wrong-annual-period',dict(event_patch={'reporting_period_start':'2023-01-01'}),'reporting_period_mismatch'),
        ('wrong-event-instant',dict(event_patch={'instant':0}),'event_instant_order'),
        ('authority-instant-expired',dict(authority_patch={'end_exclusive':1}),'authority_instant_scope'),
        ('wrong-source',dict(authority_patch={'source_ref':sources['option']}),'source_binding_mismatch'),
        ('wrong-support-source',dict(authority_patch={'supporting_source_refs':[]}),'source_binding_mismatch')]
    for label,kwargs,code in generic:
        key='binding.'+label;br=changed_basis(t,key,**kwargs);refused_basis(key,br,code,role='binding_adverse')
    for m in EVENTS:
        t=representatives[m];key='binding.wrong-method.'+m
        other_m=next(x for x in EVENTS if x!=m)
        br=changed_basis(t,key,basis_patch={'method_ref':methods[other_m]});refused_basis(key,br,'method_event_mismatch',role='binding_adverse')

    # Source-specific annual-start checks do not derive a validity window from
    # a method name or apply the AASB9 interval to AASB107.
    t=representatives['cashflow.measure']
    for label,date,code in [('before-AU-cash-scope','2023-06-30','source_period_scope'),('after-AU9-scope','2027-06-30','source_period_scope')]:
        key='binding.'+label;year=int(date[:4]);br=changed_basis(t,key,event_patch=dict(event_date=date,
            reporting_period_start=f'{year}-01-01',reporting_period_end_exclusive=f'{year+1}-01-01'))
        # Imported as-of state predates the test event, isolating source scope.
        b=deepcopy(body(br));st=deepcopy(body(b['opening_ref']));st['as_of_date']=f'{year}-01-01'
        b['opening_ref']=add('CompanyState',key+'.dated-opening',st);br=add('AccountingEventBasis',key+'.dated-basis',b)
        refused_basis(key,br,code,role='binding_adverse')

    newview=add('View','view.revised',dict(source_refs=list(sources.values()),revision=1,supersedes_ref=view,information_mode='archival_synthetic'))
    for t in STEPS:
        w=deepcopy(case_worlds[t['case_id']]);w['current_view_ref']=newview
        w['published_records']=sorted(set(w['published_records'])|set(closure([newview])))
        label=t['id']+'.retry-after-later-head-view';rr=response(label,t['request_ref'],t['submission_ref'],'replayed',[t['receipt_ref']],t['receipt_ref'])
        exchange(label,t['request_ref'],t['submission_ref'],rr,w,w,'replay_before_freshness',t['method'])
    t=STEPS[0];args=body(t['request_ref'])['arguments']['value']
    w=deepcopy(t['world_before']);w['current_view_ref']=newview;w['published_records']=sorted(set(w['published_records'])|set(closure([newview])))
    key='protocol.stale-view';rq,sub=request(key,'accounting.commit@1',args,t['opening_ref']);rr=response(key,rq,sub,'rejected',code='stale_dependency_view')
    exchange(key,rq,sub,rr,w,w,'protocol_adverse')
    key='protocol.stale-head';br=changed_basis(t,key);ar=auth_records(key,br)
    jr=add('JournalProposal',key+'.journal',{**body(t['journal_ref']),'basis_ref':br})
    dr=add('EconomicDelta',key+'.delta',{**body(t['delta_ref']),'basis_ref':br})
    rq,sub=request(key,'accounting.commit@1',dict(basis_ref=br,authorization_ref=ar,journal_ref=jr,delta_ref=dr),t['opening_ref'])
    w=case_worlds[t['case_id']];rr=response(key,rq,sub,'rejected',code='stale_head');exchange(key,rq,sub,rr,w,w,'protocol_adverse')
    key='protocol.exhausted-budget';rq,sub=request(key,'accounting.authorize@1',dict(basis_ref=t['basis_ref']),t['opening_ref'],budget=0)
    rr=response(key,rq,sub,'rejected',code='budget_exhausted');exchange(key,rq,sub,rr,t['world_before'],t['world_before'],'protocol_adverse')

    for require_current in [False,True]:
        r=REPORTS[0];rb=body(r['report_ref']);args={k:rb[k] for k in ['opening_ref','state_ref','view_ref','period_start','period_end_exclusive','receipt_refs']}
        args['require_current']=require_current;label='report.revised-view-'+str(require_current).lower();rq,sub=request(label,'report.build@1',args)
        w=deepcopy(r['world']);w['current_view_ref']=newview;w['published_records']=sorted(set(w['published_records'])|set(closure([newview])))
        rr=response(label,rq,sub,'rejected' if require_current else 'completed',outputs=[] if require_current else [r['report_ref']],
            code='stale_dependency_view' if require_current else None)
        exchange(label,rq,sub,rr,w,w,'report_freshness')

    # Reports cannot omit, reorder or borrow receipts, even with balanced totals.
    for label,patch,code in [
        ('missing-chain',{'receipt_refs':[]},'report_receipt_chain'),
        ('reversed-chain',{'receipt_refs':list(reversed(body(REPORTS[0]['report_ref'])['receipt_refs']))},'report_receipt_chain'),
        ('foreign-chain',{'receipt_refs':body(REPORTS[-1]['report_ref'])['receipt_refs']},'report_receipt_chain'),
        ('wrong-period',{'period_start':'2025-01-01','period_end_exclusive':'2026-01-01'},'report_event_period')]:
        key='report.'+label;r=REPORTS[0];rb=body(r['report_ref']);args={k:rb[k] for k in ['opening_ref','state_ref','view_ref','period_start','period_end_exclusive','receipt_refs']}
        args.update(patch);args['require_current']=True;rq,sub=request(key,'report.build@1',args);rr=response(key,rq,sub,'rejected',code=code)
        exchange(key,rq,sub,rr,r['world'],r['world'],'report_adverse')

    # Refuse proposed postings against independent economic effects, even when
    # the altered journal or closing ledger still balances.
    for m,t in representatives.items():
        key='financial.wrong-journal.'+m;br=changed_basis(t,key);ar=auth_records(key,br)
        jb=deepcopy(body(t['journal_ref']));jb['basis_ref']=br
        amounts={v['account']:number(v['signed_amount']) for v in jb['lines']}
        amounts['cash']=amounts.get('cash',F(0))+1
        amounts['other_gains']=amounts.get('other_gains',F(0))-1
        jb['lines']=[dict(account=a,signed_amount=q(v)) for a,v in sorted(amounts.items()) if v]
        jb['mode']='monetary'
        jr=add('JournalProposal',key+'.journal',jb)
        dr=add('EconomicDelta',key+'.delta',{**body(t['delta_ref']),'basis_ref':br})
        rq,sub=request(key,'accounting.commit@1',dict(basis_ref=br,authorization_ref=ar,journal_ref=jr,delta_ref=dr),t['opening_ref'])
        rr=response(key,rq,sub,'rejected',code='journal_financial_mismatch')
        exchange(key,rq,sub,rr,t['world_before'],t['world_before'],'financial_adverse',m)
    for field,code in [('balances','closing_financial_mismatch'),('cash_receipts','closing_financial_mismatch'),
                       ('oci_movements','closing_financial_mismatch'),('equity_movements','closing_financial_mismatch')]:
        t=representatives['cashflow.measure'];key='financial.wrong-closing-'+field
        br=changed_basis(t,key);ar=auth_records(key,br);sb=deepcopy(body(t['closing_ref']))
        k=next(iter(sb[field]));sb[field][k]=q(number(sb[field][k])+1)
        if field=='balances':sb[field]['other_gains']=q(number(sb[field]['other_gains'])-1)
        st=add('CompanyState',key+'.closing',sb)
        jr=add('JournalProposal',key+'.journal',{**body(t['journal_ref']),'basis_ref':br})
        dr=add('EconomicDelta',key+'.delta',{**body(t['delta_ref']),'basis_ref':br,'closing_ref':st})
        rq,sub=request(key,'accounting.commit@1',dict(basis_ref=br,authorization_ref=ar,journal_ref=jr,delta_ref=dr),t['opening_ref'])
        rr=response(key,rq,sub,'rejected',code=code)
        exchange(key,rq,sub,rr,t['world_before'],t['world_before'],'financial_adverse',t['method'])
    t=STEPS[0];key='binding.authorization-for-another-basis';br=changed_basis(t,key)
    rq,sub=request(key,'accounting.propose@1',dict(basis_ref=br,authorization_ref=t['authorization_ref']),t['opening_ref'])
    rr=response(key,rq,sub,'rejected',code='authorization_binding_mismatch')
    exchange(key,rq,sub,rr,t['world_before'],t['world_before'],'binding_adverse',t['method'])

    # Transport rejections contain no invented decoded request reference.
    def invalid_submission(key,raw,code):
        p=ART/'bytes'/(key+'.json');p.write_bytes(raw)
        sub=add('Submission','submission.'+key,dict(blob_ref=blob(p),media_type='application/json',transport='authored_fixture',decoder_ref=decoder))
        rb=deepcopy(body(EX[0]['response_ref']))
        rb.update(submission_ref=sub,request_ref=None,operation=None,input_view_ref=None,disposition='rejected',
            payload=None,coverage=None,unresolved=[],continuation_ref=None,commit_observation='not_committed',receipt_ref=None)
        rb['statuses'].update(structural_validity='invalid',mathematical_status='not_applicable',computation_status='not_computed')
        rb['diagnostics']=[dict(code=code,stage='decode_closed_profile',record_ref=None,source_locator=None,
            field_path='submission',affected_query_branch_ids=[],dependency_path=[],observed=code,
            expected_rule='FinancingComponents/1',retry_advice='repair_original_bytes',blocking_diagnostic_ids=[])]
        rr=add('OperationResult','result.'+key,rb)
        exchange(key,None,sub,rr,t['world_before'],t['world_before'],'structural_adverse')

    template=REG[t['request_ref']['digest']]
    invalid_submission('structural.duplicate-key',b'{"kind":"OperationRequest","kind":"OperationRequest"}', 'duplicate_key')
    invalid_submission('structural.invalid-json',b'{', 'invalid_json')
    invalid_submission('structural.float',b'{"value":1.0}', 'float_forbidden')
    invalid_submission('structural.nonfinite',b'{"value":NaN}', 'nonfinite_forbidden')
    for label,patch,code in [('extra-field',{'extra':True},'closed_record_shape'),
                             ('missing-field',None,'closed_record_shape')]:
        raw=deepcopy(template)
        if patch:raw.update(patch)
        else:del raw['body']['execution']
        invalid_submission('structural.'+label,enc(raw),code)
    raw=deepcopy(template);raw['body']['arguments']['value']['basis_ref']['digest']='f'*64
    raw['dependencies']=[dict(kind='AccountingEventBasis',schema=sid('AccountingEventBasis'),digest='f'*64),
        *[r for r in raw['dependencies'] if r['kind']!='AccountingEventBasis']]
    raw['dependencies']=sorted(raw['dependencies'],key=enc)
    invalid_submission('structural.missing-reference',enc(raw),'missing_reference')
    predecessors=[OUT.parent/p/'portable-exchanges.json' for p in ['corporate','corporate-v2','corporate-v3','corporate-v4','corporate-v5']]
    predecessors += [ROOT/'data/accounting-master'/p/'portable-exchanges.json' for p in [
        'corporate-portable-20261015','finite-method-decisions-20261015/group','p17-completion-20261014/P17-10/insurance-atomic']]
    for i,p in enumerate(predecessors,1):
        old=json.loads(p.read_text());d,rec=next((d,r) for d,r in old['record_registry'].items() if r['kind'] in ['Profile','PostingProfile'])
        offered=dict(kind=rec['kind'],schema=rec['schema'],digest=d)
        op=ART/'bytes'/f'offered-predecessor-{i}.json';op.write_bytes(enc(rec))
        offers.append(dict(predecessor_blob=blob(p),offered_record_blob=blob(op),offered_ref=offered,
            profile_id=rec['body'].get('profile_id',rec['kind'])))
        raw=deepcopy(template);raw['body']['profile_ref']=offered
        raw['dependencies']=sorted([offered,*[r for r in raw['dependencies'] if r['kind']!='Profile']],key=enc)
        invalid_submission(f'structural.predecessor-{i}',enc(raw),'profile_mismatch')

    # Corrupt output candidates are isolated from accepted exchanges. The
    # verifier must reject these complete worlds/reports, not merely count them.
    t=next(s for s in STEPS if s['method']=='cashflow.measure')
    for field in ['head','event_receipts','journals','deltas','receipts','published_records','unaffected_owners']:
        bad=deepcopy(t['world_after'])
        if field=='unaffected_owners':bad[field]['Other/Legal']['generation']+=1
        else:bad[field]=deepcopy(t['world_before'][field])
        challenges.append(dict(id='atomic.omitted-'+field,kind='atomic_world',request_ref=t['request_ref'],
            receipt_ref=t['receipt_ref'],world_before=t['world_before'],candidate=bad,expected_code='atomic_publication_mismatch'))
    for field in ['values','cash_receipts','cash_payments','interest_paid','income_statement','oci_components','other_equity_movements']:
        report_ref=next(r['report_ref'] for r in REPORTS if body(r['report_ref'])['interest_paid']!=q(0)) if field=='interest_paid' else REPORTS[0]['report_ref']
        rb=deepcopy(body(report_ref))
        if field=='interest_paid':rb[field]=q(number(rb[field])-1)
        else:
            k=next(iter(rb[field]));rb[field][k]=q(number(rb[field][k])+1)
        r=next(r for r in REPORTS if r['report_ref']==report_ref)
        challenges.append(dict(id='report.wrong-'+field,kind='report_output',request_ref=r['request_ref'],
            world=r['world'],candidate=rb,expected_code='report_financial_mismatch'))
    r=REPORTS[0]
    for field in ['event_receipts','journals','deltas','receipts','published_records']:
        w=deepcopy(r['world']);w[field]={} if field=='event_receipts' else []
        challenges.append(dict(id='report.unpublished-'+field,kind='report_input_world',request_ref=r['request_ref'],
            candidate=w,expected_code='report_receipt_unpublished'))
    for label,change,code in [
        ('invalid-calendar-date','date','closed_record_shape'),
        ('extra-event-field','extra','closed_record_shape'),
        ('nonreduced-rational','rational','noncanonical_rational'),
        ('missing-dependency','dependency','dependency_mismatch'),
        ('wrong-schema-id','schema','record_schema_mismatch')]:
        er=representatives['cashflow.measure']['basis_ref'];er=body(er)['event_ref'];rec=deepcopy(REG[er['digest']])
        if change=='date':rec['body']['event_date']='2024-02-30'
        elif change=='extra':rec['body']['parameters']['other']=1
        elif change=='rational':rec['body']['parameters']['D']={'n':'24','d':'2'}
        elif change=='dependency':rec['dependencies']=[]
        else:rec['schema']='accdsl.corporate.economicevent.v1'
        challenges.append(dict(id='record.'+label,kind='record_structure',candidate=rec,expected_code=code))

    for op in ops:
        example=next(e for e in EX if e['role']=='positive' and body(e['request_ref'])['operation']==op)
        for field,value in [('arguments_definition','Arguments.wrong@1'),
                ('payload_kinds',['Report'] if op!='report.build@1' else ['EconomicDelta']),
                ('effects','read' if op=='accounting.commit@1' else 'accounting_transaction')]:
            bad=deepcopy(body(signatures[op]));bad[field]=value
            challenges.append(dict(id='signature.'+op+'.'+field,kind='operation_signature',
                request_ref=example['request_ref'],candidate=bad,expected_code='operation_signature_mismatch'))

    packet=dict(profile='FinancingComponents/1',record_registry=REG,aliases=ALIASES,blobs=BLOBS,
        exchanges=EX,transitions=STEPS,reports=REPORTS,recoveries=recoveries,case_states=case_states,
        untrusted_profile_offers=offers,validation_challenges=challenges,
        status='authored_documentary_specification_not_runtime',build_wall_seconds=time.monotonic()-started,
        input_snapshots={p.name:dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted((ART/'inputs').iterdir())})
    dump(ART/'portable-exchanges.json',packet)
    print(json.dumps(dict(artifact=str(ART.relative_to(ROOT)),cases=len(CASES),methods=len(EVENTS),transitions=len(STEPS),
        records=len(REG),exchanges=len(EX),reports=len(REPORTS),runtime_executed=False)))

if __name__=='__main__':main()
