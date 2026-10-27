"""One-shot finite W05 comparison with frozen independent E01 paths."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from datetime import datetime,timezone
import importlib.util,json,os,platform,sys,time
import financing_contract as c

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
E01=HERE.parent/'gap-program-20261026'
spec=importlib.util.spec_from_file_location('financing_e01_fixture',E01/'settlement_cases.py')
e=importlib.util.module_from_spec(spec);spec.loader.exec_module(e)
OUT=HERE/'attempt-02'
checks=[];controls=[];outputs=[]
def sha(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def save(n,x):(OUT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+chr(10))
def check(n,a,b=True):
    ok=a==b;checks.append(dict(id=n,passed=ok,actual_sha256=c.digest(a),expected_sha256=c.digest(b)))
    if not ok:
        save('failed.json',dict(check=n,actual=a,expected=b));raise AssertionError(n)
def history(book):
    return dict(profile=c.HISTORY,status='complete',book_sha256=c.digest(book),
      debt_terms=deepcopy(book['memory']['debt_terms']),provenance='E01 independently authored complete supplied synthetic opening or prefix; no source admission')
def admit(k,b,h=None,selection=None,call=None):
    selection=c.digest(k) if selection is None else selection
    return c.admit(k,b,h,selection,call or c.make_call(k,b,h,selection))
def execute(k,b,h):return c.execute(k,b,h,c.digest(k),c.make_call(k,b,h,c.digest(k)))
def control(n,result,status='invalid'):
    check(n+'.status',result['status'],status)
    controls.append(dict(case=n,result=result))

def main():
    assert not OUT.exists(),'successful_or_failed_attempt_exists'
    OUT.mkdir();started=time.monotonic()
    pins=read(E01/'settlement-source-lock.json')
    for n,h in pins.items():assert sha(ROOT/n)==h,n
    source_files=[Path(m.__file__).resolve() for m in list(sys.modules.values())
                  if getattr(m,'__file__',None) and Path(m.__file__).resolve().is_relative_to(ROOT)]
    source_files += [HERE/'audit.md',ROOT/'docs/plans/accounting-financing-opening-invariants-20261026.md',
      E01/'settlement_cases.py',E01/'settlement-cases.json',E01/'settlement-controls.json',
      E01/'settlement-checks.json',E01/'settlement-run-manifest.json',E01/'settlement-result.md']
    pins.update({str(p.relative_to(ROOT)):sha(p) for p in source_files if p.is_file()})
    save('source-lock.json',pins)
    for name in ['financing_contract.py','verify.py','audit.md']:(OUT/name).write_bytes((HERE/name).read_bytes())
    frozen=read(E01/'settlement-cases.json')
    native=e.native.Engine.apply
    e.native.Engine.apply=lambda *args,**kwargs:(_ for _ in ()).throw(AssertionError('native financial fallback forbidden'))
    contracts={};states=0;comparisons=0
    try:
        for record in frozen:
            tag=record['case'];owner,path=tag.split('.')
            program,mapping=e.make(path,owner)
            check(tag+'.frozen_program',program,record['program'])
            k=c.make_contract(program,mapping);contracts[tag]=k
            check(tag+'.baseline_table',e.expected_path(program,mapping,path),record['independent_prefixes'])
            untouched=deepcopy(program);h=history(program['opening'])
            r=execute(k,program,h)
            check(tag+'.status',r['status'],'complete_selected_provisional')
            check(tag+'.input_unchanged',program,untouched)
            check(tag+'.trace_length',len(r['trace']),len(record['result']['trace']))
            before=program['opening']
            snapshots=[program['opening']]+[x['after'] for x in record['independent_prefixes']]+[record['result']['current']]
            for index,state in enumerate(snapshots):
                check(tag+'.snapshot.'+str(index),c.snapshot(k,state,program['schemas'])['status'],'requirements_satisfied')
                check(tag+'.history.'+str(index),c.assess_history(k,state,program['schemas'],history(state))['status'],'supplied_history_satisfied')
                imported=deepcopy(program);imported['opening']=deepcopy(state)
                opening_check=admit(k,imported,history(state))
                check(tag+'.imported.'+str(index),opening_check['status'],'selected_opening_satisfied' if index==0 else 'invalid')
                if index:
                    check(tag+'.imported_boundary.'+str(index),opening_check.get('reason'),'opening_report:opening_at_period_start')
                states+=1
            for i,want in enumerate(record['independent_prefixes']):
                got=r['trace'][i]['result']['transition']
                for part in ['after','journal','flows']:
                    check(tag+'.'+str(i)+'.'+part,got[part],want[part])
                check(tag+'.'+str(i)+'.continuous',r['trace'][i]['before_sha256'],c.digest(before))
                before=got['after'];comparisons+=1
            check(tag+'.report',r['trace'][-1]['result'],record['result']['trace'][-1]['result'])
            check(tag+'.final',r['current'],record['result']['current']);comparisons+=1
            check(tag+'.flags',all(r[x] is False for x in c.FLAGS))
            outputs.append(dict(case=tag,contract=k,history=h,result=r))

        base=frozen[1];program=deepcopy(base['program']);mapping=e.make('late')[1];k=contracts['alpha.late']
        opening=program['opening'];late=base['independent_prefixes'];schemas=program['schemas']
        def mutate_state(name,index,change):
            book=deepcopy(opening if index is None else late[index]['after']);change(book)
            r=c.snapshot(k,book,schemas);control(name,r)
            return book
        mutate_state('negative_face',None,lambda b:b['memory']['debt_terms'].update(original_face='-1/1'))
        mutate_state('claim_above_face',None,lambda b:b['memory']['debt_terms'].update(outstanding='101/1'))
        mutate_state('negative_shares',None,lambda b:b['memory']['debt_terms'].update(new_shares='-1/1'))
        mutate_state('arrears_above_claim',2,lambda b:b['memory']['debt_terms'].update(arrears='41/1'))
        mutate_state('lost_historical_miss',2,lambda b:b['memory']['debt_terms'].update(missed_amount='0/1'))
        mutate_state('missed_before_due',None,lambda b:b['memory']['debt_terms'].update(missed=True,missed_amount='100/1'))
        mutate_state('unmatured_after_due',None,lambda b:b.update(date='2027-07-01'))
        mutate_state('mature_carrying_mismatch',1,lambda b:b['balances'].update({mapping['debt']:'-39/1',mapping['cash']:'-1/1'}))
        mutate_state('missing_history_field',2,lambda b:b['memory']['debt_terms'].pop('missed_amount'))
        mutate_state('share_money_dimension',None,lambda b:b['memory_types'].update({'/debt_terms/new_shares':c.engine.money_type(b)}))
        mutate_state('unobserved_unpaid_after_due',1,lambda b:b.update(date='2027-07-01'))
        mutate_state('wrong_context',None,lambda b:b['context'].update(entity='Different-entity'))
        for label,hist in [('missing_history',None),('partial_history',dict(status='partial'))]:
            r=admit(k,program,hist);control(label,r,'unresolved');check(label+'.no_after','current' not in r)
        h=history(opening);h['provenance']=' '
        control('blank_history_provenance',admit(k,program,h))
        h=history(opening);h['debt_terms']['old_shares']='99/1'
        control('different_opening_history_fact',admit(k,program,h))
        h=history(opening)
        control('unselected_contract',admit(k,program,h,selection='0'*64))
        stale=c.make_call(k,program,h,c.digest(k));changed=deepcopy(program);changed['name']+='changed'
        control('stale_program_call',admit(k,changed,h,call=stale))
        k_wrong=deepcopy(k);k_wrong['roles']['cash']=mapping['debt']
        control('wrong_cash_selection',admit(k_wrong,program,h))

        # A consistent ending snapshot can conceal erased history; supplied opening evidence exposes it.
        paid=deepcopy(late[-1]['after']);erased=deepcopy(paid)
        erased['memory']['debt_terms'].update(missed=False,missed_amount='0/1')
        check('erased_paid_snapshot_can_be_consistent',c.snapshot(k,erased,schemas)['status'],'requirements_satisfied')
        imported=deepcopy(program);imported['opening']=erased
        control('erased_imported_history',c.assess_history(k,erased,schemas,history(paid)))

        # Snapshot alone cannot detect a plausible historical amount rewrite.
        before=late[3]['after'];after=deepcopy(late[4]['after']);event=program['commands'][4]['event']
        after['memory']['debt_terms']['missed_amount']='50/1'
        check('rewritten_miss_snapshot_consistent',c.snapshot(k,after,schemas)['status'],'requirements_satisfied')
        control('late_payment_rewrites_history',c.transition(k,'settle_late',before,event,after,schemas))
        after=deepcopy(late[4]['after']);after['memory']['debt_terms'].update(missed=False,missed_amount='0/1')
        control('late_payment_erases_history',c.transition(k,'settle_late',before,event,after,schemas))
        after=deepcopy(late[4]['after']);after['memory']['complement']['tag']='lost'
        control('unrelated_memory_loss',c.transition(k,'settle_late',before,event,after,schemas))
        after=deepcopy(late[4]['after']);after['seen']=after['seen'][1:]
        control('earlier_event_loss',c.transition(k,'settle_late',before,event,after,schemas))

        for name,method,field,index in [('omitted_share_write','equity','new_shares',3),
                                       ('omitted_miss_write','observe_missed','missed_amount',2)]:
            bad=deepcopy(program);entry=bad['registry']['entries'][method]
            entry['method']['memory']['definition']['operations']=[x for x in entry['method']['memory']['definition']['operations'] if x['path'][-1]!=field]
            entry['method_sha256']=c.digest(entry['method'])
            control(name+'.old_selection',admit(k,bad,history(opening)))
            prev=late[index-1]['after'];command=bad['commands'][index]
            proposed=c.runtime.methods.propose(prev,c.runtime.call(prev,bad['registry'],command))
            check(name+'.generic_proposes',proposed['status'],'proposed')
            control(name+'.semantic_check',c.transition(k,method,prev,command['event'],proposed['transition']['after'],schemas))
            # Explicit hypothetical re-selection of altered methods keeps the unchanged
            # financial relation; demonstrate no accepted after-state after its failure.
            selected=deepcopy(k);selected['registry_sha256']=c.digest(bad['registry'])
            r=execute(selected,bad,history(opening));control(name+'.execution',r,'stopped_selected_provisional')
            check(name+'.stop_index',r['stop']['index'],index)
            check(name+'.accepted_prefix',r['current'],prev)
            check(name+'.retained_commands',r['remaining_commands'],bad['commands'][index:])
            check(name+'.no_top_level_after','after' not in r)

        for label,index,change,status in [
            ('unknown_payment',1,lambda b:b['commands'][1]['event']['inputs']['amount'].update(value=dict(status='unknown',reason='missing instruction')),'unresolved'),
            ('unapproved_maturity',0,lambda b:b['commands'][0]['event']['inputs']['approved']['value'].update(value=False),'unsupported'),
            ('overspend',1,lambda b:b['commands'][1]['event']['inputs']['amount']['value'].update(value='100/1'),'invalid')]:
            b=deepcopy(program);change(b);r=execute(k,b,history(opening))
            control(label,r,'stopped_selected_provisional');check(label+'.refusal',r['stop']['status'],status)
            check(label+'.index',r['stop']['index'],index)
            check(label+'.prefix',r['current'],opening if index==0 else late[index-1]['after'])
        # Observation cannot advance an unpaid due-date snapshot beyond the due
        # date without an explicit missed-payment observation.
        b=deepcopy(program);b['commands']=b['commands'][:2]+[deepcopy(b['commands'][-1])]
        b['commands'][-1]['equity_movements']=[]
        r=execute(k,b,history(opening));control('report_skips_missed_observation',r,'stopped_selected_provisional')
        check('report_skips_missed_observation.index',r['stop']['index'],2)
        check('report_skips_missed_observation.prefix',r['current'],late[1]['after'])
        for n,h in pins.items():check('protected.'+n,sha(ROOT/n),h)
        save('contracts.json',contracts);save('cases.json',outputs);save('controls.json',controls)
        save('checks.json',dict(passed=True,comparisons=comparisons,states=states,controls=len(controls),assertions=len(checks),checks=checks))
        summary=dict(passed=True,comparisons=comparisons,states=states,controls=len(controls),assertions=len(checks),protected_files=len(pins))
        save('run-manifest.json',dict(**summary,command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 data/accounting-master/financing-opening-invariants-20261026/verify.py',
          git_commit='unusable repository marker; no commit invented',environment=dict(python=platform.python_version(),platform=platform.platform()),
          cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic',data_version=sha(E01/'settlement-cases.json'),
          plan='docs/plans/accounting-financing-opening-invariants-20261026.md',result='data/accounting-master/financing-opening-invariants-20261026/result.md',
          artifact_paths=['source-lock.json','contracts.json','cases.json','controls.json','checks.json'],
          wall_seconds=time.monotonic()-started,timestamp_utc=datetime.now(timezone.utc).isoformat()))
        print(json.dumps(summary))
    finally:e.native.Engine.apply=native

if __name__=='__main__':main()
