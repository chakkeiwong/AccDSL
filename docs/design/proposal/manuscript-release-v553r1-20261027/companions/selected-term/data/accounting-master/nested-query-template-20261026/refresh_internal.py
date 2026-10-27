"""Record completed query phases without advancing the governing manuscript."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
old='docs/plans/accounting-grouped-row-query-20261026.md'
new='docs/plans/accounting-nested-query-template-20261026.md'
result='data/accounting-master/query-guard-composition-20261026/result.md'
files=['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md','docs/plans/accounting-product-design-checkpoint.md',
 'docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-current.md','docs/plans/accounting-master-program.md',
 'data/accounting-master/next-plan.md','data/accounting-master/recovery-current-20261026.md',
 'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
before={n:(ROOT/n).read_bytes() for n in files};after={}
note='''## Internal grouped-rule progress — 26 October 2026

Grouped queries pass 606 comparisons/37 controls/2,601 assertions. Guarded
composition passes 18 truth-table cases and 108 full comparisons/30 controls/
496 assertions, protecting 63 dependency files. Historical term ownership and
overdue remain exact; none, ambiguous, unknown and inactive remain distinct.
Next: generic typed per-parent/per-child query templates. No native financial
validator replacement, real-company completeness or whole requirement closure.
Governing Version 5.13 (741 pages) and standalone Version 5.12 remain unchanged.
MC20/24/25/28/33/34 partial; S6 held; E3 deferred.
Result: data/accounting-master/query-guard-composition-20261026/result.md.
Active plan: docs/plans/accounting-nested-query-template-20261026.md.

'''
for n,b in before.items():
    if n.endswith('.json'):
        d=json.loads(b);a=d.get('active_execution',d.get('active_execution_note'))
        assert a['active_work_plan']==old,(n,'concurrent_plan_change')
        a.update(active_work_plan=new,latest_internal_result=result)
        a['next']=['Verify typed per-parent/per-child query templates','Reconcile native term-state obligations and author remaining declarative rules','Integrate coherent increment; preserve literature residuals; S6 held; E3 deferred']
        if 'completed_increments' in a:a['completed_increments'].extend(['Grouped queries:606 complete comparisons;37 controls;2,601 assertions','Query-guard composition:18 truth-table cases;108 complete comparisons;30 controls;496 assertions'])
        after[n]=json.dumps(d,indent=2)+'\n'
    else:
        s=b.decode();assert old in s,(n,'expected_pointer_missing')
        s=s.replace(old,new,1)
        if n!='MISSION_CONTROL.md':
            first,rest=s.split('\n',1);s=first+'\n\n'+note+rest.lstrip('\n')
            s=s.replace('Next plan: '+old+'.','Next plan: '+new+'.',1)
        s=s.replace('Current question: can grouped queries preserve ownership, historical dates, ties and empty populations?',
          'Current question: can reviewed typed templates cover every supplied parent/child without hardcoded identities?')
        s=s.replace('Next action: execute '+old+'.','Next action: execute '+new+'.')
        s=s.replace('Next: typed grouped query verification, then guarded-rule composition.',
          'Next: typed nested query templates; grouped-query and guarded-composition evidence is frozen.')
        after[n]=s
backup=HERE/'control-before';assert not backup.exists(),'do_not_repeat_refresh'
pdfs={'docs/AccDSL-latest.pdf':'d3284ce5c52a6c0b4abebb9bb35f758f1dea7e11a1212b8d8784185f4b3002e7',
 'docs/AccDSL-simulation-foundations.pdf':'63bad80014136b6fa6e3cf1c984aa11df797fd33ac66ea56fb7ddbe7451846d5'}
for n,h in pdfs.items():assert sha256((ROOT/n).read_bytes()).hexdigest()==h,n
for n,b in before.items():assert (ROOT/n).read_bytes()==b,'concurrent_control_change:'+n
for n,b in before.items():
    p=backup/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
for n,s in after.items():
    assert (ROOT/n).read_bytes()==before[n],'concurrent_control_change:'+n
    (ROOT/n).write_text(s)
(HERE/'control-refresh.json').write_text(json.dumps({'controls':{n:{'before':sha256(before[n]).hexdigest(),
 'after':sha256((ROOT/n).read_bytes()).hexdigest()} for n in files},'unchanged_pdfs':pdfs},indent=2)+'\n')
print(json.dumps({'controls_refreshed':len(files),'active_plan':new,'governing_version':'5.13 unchanged'}))
