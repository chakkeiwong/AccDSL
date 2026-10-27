"""Author immutable query exchanges. Does not import the independent oracle."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import re
import shutil
import sys
import time
from authored_cases import CASES
from schema_design import schemas, sid, METHODS, OP
from source_policy import SOURCES, METHOD_SOURCE, METHOD_ANCHOR
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
REG, ALIASES, BLOBS, EX, CHALLENGES, CRASHES, ROWS = {}, {}, {}, [], [], [], []
ART=None
def enc(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def sha(b): return hashlib.sha256(b).hexdigest()
def q(v):
    f=F(v); return dict(n=str(f.numerator),d=str(f.denominator))
def wire(v):
    if isinstance(v,str) and re.fullmatch(r'-?[0-9]+(?:/[0-9]+)?',v): return q(v)
    if isinstance(v,dict): return {k:wire(x) for k,x in v.items()}
    if isinstance(v,(tuple,list)): return [wire(x) for x in v]
    return v
def references(v):
    if isinstance(v,dict):
        if set(v)=={'kind','schema','digest'}: yield v
        else:
            for x in v.values(): yield from references(x)
    elif isinstance(v,list):
        for x in v: yield from references(x)
def unique(rs): return [r for k,r in sorted({enc(r):r for r in rs}.items())]
def add(kind,key,b):
    assert key not in ALIASES,key
    r=dict(kind=kind,schema=sid(kind),key=key,revision=0,body=b,dependencies=unique(references(b)))
    digest=sha(('accdsl.portable.v1/'+sid(kind)).encode()+b'\0'+enc(r))
    REG[digest]=r; ALIASES[key]=dict(kind=kind,schema=sid(kind),digest=digest); return ALIASES[key]
def body(r): return REG[r['digest']]['body']
def clone(key,r,**changes): return add(r['kind'],key,dict(deepcopy(body(r)),**changes))
def closure(roots):
    seen=set()
    def visit(r):
        if r['digest'] in seen: return
        seen.add(r['digest'])
        for x in REG[r['digest']]['dependencies']: visit(x)
    for r in roots: visit(r)
    return sorted(seen)
def write(p,v): p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def blob(p):
    raw=p.read_bytes(); d=sha(raw); BLOBS[d]=dict(path=str(p.relative_to(ROOT)),byte_length=len(raw))
    return dict(kind='blob',algorithm='sha256',digest=d,byte_length=len(raw))
def model(v):
    # Authored declarations; the auditor reconstructs every binding separately.
    m=v['method_id']; z='not_applicable'; g=z; cond=z; horizon=z
    if m=='transition.route@1': g='group.route'
    if m=='transition.recovery@1': g=v['covered_group']
    if m=='transition.opening@1': g='/'.join(sorted(x['group_id'] for x in v['groups']))
    if m in ('estimation.predict@1','reserve.error@1'): cond=v['conditioning']
    if m=='triangle.inspect@1': cond='full_triangle'
    if m=='backward.condition@1': cond='latest_diagonal'
    if m in ('triangle.inspect@1','estimation.predict@1','backward.condition@1','reserve.error@1'): horizon='lifetime_payments'
    if m=='cdr.one-year@1': horizon='one_year_reestimation'
    return dict(group_id=g,triangle_id=v.get('triangle_id',z),process_law_id=v.get('process_law_id',v.get('family_id',z)),backward_law_id=v.get('backward_law_id',z),conditioning=cond,horizon=horizon,calibration_status='not_evaluated')
def identity(rq):
    r=body(rq); return enc([r['client_id'],r['request_id']]).decode()
def main():
    global ART
    start=time.monotonic(); n=1
    while (HERE/f'attempt-{n:02}').exists(): n+=1
    ART=HERE/f'attempt-{n:02}'; ART.mkdir(); (ART/'inputs').mkdir(); (ART/'bytes').mkdir()
    for p in sorted(HERE.iterdir()):
        if p.is_file() and (p.suffix=='.py' or p.name in ('semantic-contract.md','source-reading.md')): shutil.copyfile(p,ART/'inputs'/p.name)
    write(ART/'record-schemas.json',schemas())
    lock=add('SchemaLock','schema-lock',dict(schema_blob=blob(ART/'record-schemas.json'),semantic_contract_blob=blob(ART/'inputs/semantic-contract.md')))
    profile=add('Profile','profile',dict(profile_id='InsuranceAssessment/1',operation=OP,methods=list(METHODS),schema_lock_ref=lock,accounting_effect='none'))
    context=add('Context','context',dict(entity_id='Synthetic',book_id='Legal',currency='USD',unit='illustrative_million',authority='historical_EU2023_IFRS17',actual_entity_admission='not_established'))
    foreign=clone('context.foreign',context,entity_id='Foreign')
    balances=wire(dict(assets='500',insurance_liabilities='220',equity='280'))
    head=add('AccountingHead','head',dict(context_ref=context,owner_id='Synthetic/Legal',generation=0,balances_sha256=sha(enc(balances))))
    later=clone('head.later',head,generation=1)
    src={}
    for key,s in SOURCES.items():
        assert sha((ROOT/s['raw']).read_bytes())==s['raw_sha'] and sha((ROOT/s['text']).read_bytes())==s['text_sha']
        src[key]=add('SourceSupport','source.'+key,dict(raw_blob=blob(ROOT/s['raw']),text_blob=blob(ROOT/s['text']),method_blobs=[blob(ROOT/p) for p in s['methods']],anchors=s['anchors'],temporal_status='retained_historical'))
    def request(key,basis,current=True,rid=None):
        b=body(basis)
        rq=add('OperationRequest','request.'+key,dict(profile_ref=profile,client_id='InsuranceAssessment-specification',request_id=rid or key,operation=OP,context_ref=b['context_ref'],view_ref=b['view_ref'],require_current=current,expected_head=b['expected_head'],basis_ref=basis))
        p=ART/'bytes'/(key+'.json'); p.write_bytes(enc(REG[rq['digest']]))
        sub=add('Submission','submission.'+key,dict(request_ref=rq,wire_blob=blob(p)))
        return rq,sub
    def response(key,rq,sub,output=None,receipt=None,disposition='completed',codes=()):
        return add('OperationResult','result.'+key,dict(request_ref=rq,submission_ref=sub,disposition=disposition,output_ref=output,receipt_ref=receipt,diagnostics=list(codes),published_digests=closure([output,receipt]) if output else [],additional_commit=False,accounting_effect='none'))
    def world(rq,sub):
        return dict(accounting_heads={'Synthetic/Legal':head},balances={'Synthetic/Legal':balances},journals=[],unrelated_owners={'Other/Book':dict(generation=7,balances_sha256='0'*64)},current_view_ref=body(rq)['view_ref'],query_index={},published_records=closure([rq,sub]))
    def exchange(key,rq,sub,res,before,after,role):
        EX.append(dict(id=key,role=role,request_ref=rq,submission_ref=sub,response_ref=res,world_before=deepcopy(before),world_after=deepcopy(after)))
    def challenge(key,kind,ref,code): CHALLENGES.append(dict(id=key,kind=kind,candidate_ref=ref,expected=code))
    outputs={}
    for c in CASES:
        key=c['id']; inp=wire(c['input']); m=inp['method_id']
        ir=add('AssessmentInput','input.'+key,inp)
        p=ART/'bytes'/(key+'.facts.json'); p.write_bytes(enc(inp))
        ev=add('Evidence','evidence.'+key,dict(context_ref=context,available_at='2026-10-14T00:00:00Z',ingested_at='2026-10-14T01:00:00Z',facts_blob=blob(p)))
        view=add('View','view.'+key,dict(context_ref=context,decision_at='2026-10-15T00:00:00Z',system_asof='2026-10-15T00:00:00Z',evidence_refs=[ev]))
        mr=add('ModelIdentity','model.'+key,model(inp))
        basis=add('AssessmentBasis','basis.'+key,dict(context_ref=context,view_ref=view,evidence_ref=ev,source_ref=src[METHOD_SOURCE[m]],model_ref=mr,input_ref=ir,expected_head=head,method_anchor=METHOD_ANCHOR[m],prior_assessment_refs=[outputs[k] for k in c['prior']]))
        rq,sub=request(key,basis); before=world(rq,sub)
        ROWS.append(dict(id=key,basis_ref=basis,request_ref=rq,refusal=c['refusal']))
        if c['refusal']:
            res=response(key,rq,sub,disposition='rejected',codes=[c['refusal']]); exchange(key,rq,sub,res,before,before,'method_refusal'); continue
        detail=wire(c['detail'])
        if m=='triangle.inspect@1': detail['triangle_sha256']=sha(enc(inp))
        out=add('AssessmentResult','output.'+key,dict(method_id=m,basis_ref=basis,status=c['status'],diagnostics=c['diagnostics'],detail=detail,accounting_effect='none')); outputs[key]=out
        receipt=add('PublicationReceipt','receipt.'+key,dict(request_ref=rq,output_ref=out,status='query_published',accounting_head=head,accounting_effect='none'))
        res=response(key,rq,sub,out,receipt,'partial' if c['diagnostics'] else 'completed',c['diagnostics'])
        after=deepcopy(before); after['published_records']=sorted(set(before['published_records'])|set(closure([res])))
        after['query_index'][identity(rq)]=dict(request_digest=rq['digest'],output_ref=out,receipt_ref=receipt,response_ref=res)
        exchange(key,rq,sub,res,before,after,'publication')
        replay=clone('result.'+key+'.replay',res,disposition='replayed')
        exchange(key+'.replay',rq,sub,replay,after,after,'exact_replay')
        newer=clone('view.'+key+'.later',view,decision_at='2026-10-15T01:00:00Z')
        stale=deepcopy(after); stale['current_view_ref']=newer; stale['accounting_heads']['Synthetic/Legal']=later
        exchange(key+'.stale-replay',rq,sub,replay,stale,stale,'replay_before_freshness')
        lost=add('TransportObservation','lost.'+key,dict(submission_ref=sub,status='acknowledgement_lost',commit_knowledge='unknown'))
        exchange(key+'.lost-before',rq,sub,lost,before,before,'lost_ack_before')
        exchange(key+'.retry-before',rq,sub,res,before,after,'retry_first_publication')
        exchange(key+'.lost-after',rq,sub,lost,after,after,'lost_ack_after')
        exchange(key+'.retry-after',rq,sub,replay,after,after,'retry_exact_replay')
        cr,cs=request(key+'.conflict',basis,False,rid=key)
        conflict=response(key+'.conflict',cr,cs,disposition='rejected',codes=['REQUEST_IDENTITY_CONFLICT'])
        exchange(key+'.conflict',cr,cs,conflict,after,after,'identity_conflict')
        nr,ns=request(key+'.stale-view',basis); w=world(nr,ns); w['current_view_ref']=newer
        rejected=response(key+'.stale-view',nr,ns,disposition='rejected',codes=['STALE_VIEW'])
        exchange(key+'.stale-view',nr,ns,rejected,w,w,'new_stale_view')
        hr,hs=request(key+'.stale-head',basis); w=world(hr,hs); w['accounting_heads']['Synthetic/Legal']=later
        rejected=response(key+'.stale-head',hr,hs,disposition='rejected',codes=['STALE_HEAD'])
        exchange(key+'.stale-head',hr,hs,rejected,w,w,'new_stale_head')
        fr,fs=request(key+'.frozen',basis,False); w=world(fr,fs); w['current_view_ref']=newer
        frec=clone('receipt.'+key+'.frozen',receipt,request_ref=fr)
        fres=response(key+'.frozen',fr,fs,out,frec,'partial' if c['diagnostics'] else 'completed',c['diagnostics'])
        wa=deepcopy(w); wa['published_records']=sorted(set(w['published_records'])|set(closure([fres])))
        wa['query_index'][identity(fr)]=dict(request_digest=fr['digest'],output_ref=out,receipt_ref=frec,response_ref=fres)
        exchange(key+'.frozen',fr,fs,fres,w,wa,'frozen_view_publication')
        CRASHES.append(dict(id=key,request_ref=rq,output_ref=out,receipt_ref=receipt,response_ref=res,before=before,after=after,cuts=['before_publication','after_publication']))
        bad=clone('bad.output-status.'+key,out,status='resolved' if c['status']=='unresolved' else 'unresolved')
        challenge(key+'.output-status','assessment',bad,'ASSESSMENT_MISMATCH')
        badbasis=clone('bad.source.'+key,basis,source_ref=src['estimation' if METHOD_SOURCE[m]!='estimation' else 'transition'])
        challenge(key+'.source-binding','basis',badbasis,'SOURCE_BINDING')
        badmodel=clone('bad.model.'+key,mr,horizon='one_year_reestimation' if model(inp)['horizon']!='one_year_reestimation' else 'lifetime_payments')
        badbasis=clone('bad.model-basis.'+key,basis,model_ref=badmodel)
        challenge(key+'.model-binding','basis',badbasis,'MODEL_BINDING')
        badbasis=clone('bad.context.'+key,basis,context_ref=foreign)
        challenge(key+'.context-binding','basis',badbasis,'CONTEXT_BINDING')
        badbasis=clone('bad.anchor.'+key,basis,method_anchor='Wrong.section')
        challenge(key+'.anchor-binding','basis',badbasis,'SOURCE_BINDING')
        badev=clone('bad.evidence.'+key,ev,available_at='2026-10-16T00:00:00Z')
        badview=clone('bad.evidence-view.'+key,view,evidence_refs=[badev])
        badbasis=clone('bad.evidence-basis.'+key,basis,evidence_ref=badev,view_ref=badview)
        challenge(key+'.future-evidence','basis',badbasis,'EVIDENCE_NOT_AVAILABLE')
        badbasis=clone('bad.view.'+key,basis,view_ref=newer,evidence_ref=ALIASES['evidence.route.full'] if key!='route.full' else badev)
        challenge(key+'.view-membership','basis',badbasis,'EVIDENCE_VIEW_BINDING')
        if key!='route.full':
            other='route.earlier' if inp==body(ALIASES['input.route.full']) else 'route.full'
            assert inp!=body(ALIASES['input.'+other]),'facts adversary must alter the facts'
            badbasis=clone('bad.facts.'+key,basis,evidence_ref=ALIASES['evidence.'+other],view_ref=ALIASES['view.'+other])
            challenge(key+'.facts-binding','basis',badbasis,'EVIDENCE_FACTS_BINDING')
        def numeric_paths(v,path=()):
            if isinstance(v,dict):
                if set(v)=={'n','d'}: yield path
                else:
                    for k,x in v.items(): yield from numeric_paths(x,path+(k,))
            elif isinstance(v,list):
                for i,x in enumerate(v): yield from numeric_paths(x,path+(i,))
        for j,path in enumerate(numeric_paths(detail)):
            altered=deepcopy(detail); target=altered
            for segment in path[:-1]: target=target[segment]
            old=target[path[-1]]; target[path[-1]]=q(F(int(old['n']),int(old['d']))+1)
            bad=clone('bad.numeric.'+key+'.'+str(j),out,detail=altered)
            challenge(key+'.numeric.'+str(j),'assessment',bad,'ASSESSMENT_MISMATCH')
        if inp['method_id']=='transition.opening@1' and inp['embedded_recovery']!=q(0):
            for label,refs in [('missing',[]),('unrelated',[outputs['route.full']]),('unresolved',[outputs['recovery.unknown-admission']])]:
                bad=clone('bad.prior.'+key+'.'+label,basis,prior_assessment_refs=refs)
                challenge(key+'.prior-'+label,'basis',bad,'PRIOR_RECOVERY_BINDING')
            dated=clone('bad.prior-date-input.'+key,ir,transition_date='2021-01-01')
            p=ART/'bytes'/(key+'.wrong-transition-date.facts.json'); p.write_bytes(enc(body(dated)))
            datedev=clone('bad.prior-date-evidence.'+key,ev,facts_blob=blob(p))
            datedview=clone('bad.prior-date-view.'+key,view,evidence_refs=[datedev])
            bad=clone('bad.prior-date-basis.'+key,basis,input_ref=dated,evidence_ref=datedev,view_ref=datedview)
            challenge(key+'.prior-transition-date','basis',bad,'PRIOR_RECOVERY_BINDING')
        # A frozen view still requires the exact financial head.
        fhr,fhs=request(key+'.frozen-stale-head',basis,False); w=world(fhr,fhs)
        w['current_view_ref']=newer; w['accounting_heads']['Synthetic/Legal']=later
        rejected=response(key+'.frozen-stale-head',fhr,fhs,disposition='rejected',codes=['STALE_HEAD'])
        exchange(key+'.frozen-stale-head',fhr,fhs,rejected,w,w,'frozen_stale_head')
        base=next(x for x in reversed(EX) if x['id']==key)
        for label,code in [('head','ACCOUNTING_MUTATION'),('balance','ACCOUNTING_MUTATION'),('journal','ACCOUNTING_MUTATION'),('other-owner','ACCOUNTING_MUTATION'),('dependency','PUBLICATION_CLOSURE'),('index','PUBLICATION_INDEX')]:
            bad=deepcopy(base); bad['id']=key+'.bad-world.'+label; w=bad['world_after']
            if label=='head': w['accounting_heads']['Synthetic/Legal']=later
            if label=='balance': w['balances']['Synthetic/Legal']['assets']=q(501)
            if label=='journal': w['journals']=[{'invented_posting':True}]
            if label=='other-owner': w['unrelated_owners']['Other/Book']['generation']=8
            if label=='dependency': w['published_records'].remove(out['digest'])
            if label=='index': w['query_index']={}
            CHALLENGES.append(dict(id=bad['id'],kind='exchange',candidate_exchange=bad,expected=code))
        bad=deepcopy(next(x for x in reversed(EX) if x['id']==key+'.replay'))
        bad['world_after']['published_records']=sorted(set(bad['world_after']['published_records'])|{badmodel['digest']})
        CHALLENGES.append(dict(id=key+'.replay-mutation',kind='exchange',candidate_exchange=bad,expected='REPLAY_MUTATION'))
        p=ART/'bytes'/(key+'.wrong-wire.json'); p.write_bytes(enc(REG[rq['digest']])+b' ')
        bad=clone('bad.wire.'+key,sub,wire_blob=blob(p))
        challenge(key+'.wrong-wire','submission',bad,'WIRE_BYTES_MISMATCH')
        if key=='predict.failed-fit-retained':
            bad=clone('bad.renormalization',out,detail=dict(detail,mean=q(2),variance=q(4),tail_probability=q(0),full_distribution=[dict(amount=q(0),probability=q('1/2')),dict(amount=q(4),probability=q('1/2'))]))
            challenge('failed-fit.success-only-normalization','assessment',bad,'ASSESSMENT_MISMATCH')
        for caseid,field,value,label in [('opening.groupwise','liability','210','pooled-groups'),('opening.with-embedded-recovery','held_asset','62','doubled-recovery'),('predict.shared-fit-two-cells','variance','38','independent-fit-redraw'),('backward.joint-law','mean','3/2','reciprocal-forward-mean'),('reserve.correct-center','reserve_error','-90','ultimate-center'),('cdr.reestimated','cdr','70','cash-only-cdr')]:
            if key==caseid:
                bad=clone('bad.target.'+label,out,detail=dict(detail,**{field:q(value)}))
                challenge(label,'assessment',bad,'ASSESSMENT_MISMATCH')
    finish(start,profile,head,outputs)

def finish(start,profile,head,outputs):
    for label,raw,code in [('duplicate',b'{"a":0,"a":1}','DUPLICATE_KEY'),('float',b'{"a":1.0}','FLOAT_FORBIDDEN'),('nonfinite',b'{"a":NaN}','NONFINITE_FORBIDDEN')]:
        p=ART/'bytes'/('invalid-'+label+'.json'); p.write_bytes(raw)
        CHALLENGES.append(dict(id='json.'+label,kind='json',raw_blob=blob(p),expected=code))
    for label,mutate,code in [
        ('unknown-field',lambda r:r['body'].update(unexpected=True),'CLOSED_RECORD_SHAPE'),
        ('dependencies',lambda r:r.update(dependencies=[]),'DEPENDENCY_MISMATCH'),
        ('digest',lambda r:r.update(key='changed-key'),'RECORD_DIGEST_MISMATCH')]:
        ref=ALIASES['output.opening.groupwise']; candidate=deepcopy(REG[ref['digest']]); mutate(candidate)
        CHALLENGES.append(dict(id='record.'+label,kind='record',candidate_record=candidate,digest=ref['digest'],expected=code))
    candidate=deepcopy(REG[ALIASES['output.opening.groupwise']['digest']]); candidate['body']['detail']['liability']={'n':'460','d':'2'}
    CHALLENGES.append(dict(id='record.unreduced-rational',kind='record',candidate_record=candidate,digest=None,expected='NONCANONICAL_RATIONAL'))
    snapshots={p.name:dict(path=str(p.relative_to(ROOT)),sha256=sha(p.read_bytes())) for p in sorted((ART/'inputs').iterdir())}
    packet=dict(profile_ref=profile,accounting_head_ref=head,record_registry=REG,aliases=ALIASES,blobs=BLOBS,exchanges=EX,challenges=CHALLENGES,crash_worlds=CRASHES,cases=ROWS,input_snapshots=snapshots,predecessor_lock_blob=blob(HERE/'predecessor-lock.json'),evidence_mode='specification_example_no_runtime')
    write(ART/'portable-exchanges.json',packet)
    summary=dict(artifact=str(ART.relative_to(ROOT)),wall_seconds=time.monotonic()-start,methods=len(METHODS),cases=len(ROWS),published_cases=len(outputs),records=len(REG),exchanges=len(EX),challenges=len(CHALLENGES),crash_worlds=2*len(CRASHES),packet_sha256=sha((ART/'portable-exchanges.json').read_bytes()))
    write(ART/'build-run.json',summary); print(json.dumps(summary))

if __name__=='__main__': main()
