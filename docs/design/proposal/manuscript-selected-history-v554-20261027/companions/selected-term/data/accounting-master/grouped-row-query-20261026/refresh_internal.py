"""Advance only internal work pointers; protect current manuscript controls."""
from pathlib import Path
from hashlib import sha256
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
old='docs/plans/accounting-nested-term-invariant-audit-20261026.md'
new='docs/plans/accounting-grouped-row-query-20261026.md'
result='data/accounting-master/nested-map-projection-20261026/result.md'
files=['MISSION_CONTROL.md','docs/plans/accounting-mission-requirements.md',
 'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-master-checkpoint.md',
 'docs/plans/accounting-master-current.md','docs/plans/accounting-master-program.md',
 'data/accounting-master/next-plan.md','data/accounting-master/recovery-current-20261026.md',
 'data/accounting-master/next-plan.json','scripts/accounting_master_catalog.json']
before={n:(ROOT/n).read_bytes() for n in files};after={}
note='''## Internal nested-state progress — 26 October 2026

The term-invariant audit and typed nested-map projection are complete within
their declared scope: 22 retained states, 44 exact projections, 19 controls and
213 assertions; 18 predecessor files protected. Group cardinality, exact
matching and greatest-applicable selection are next. MC20/24/25/28/33/34 remain
partial; no whole requirement closes. Governing Version 5.13, 741 pages, and
standalone literature Version 5.12 are unchanged. S6 held; E3 deferred.
Result: data/accounting-master/nested-map-projection-20261026/result.md.
Active plan: docs/plans/accounting-grouped-row-query-20261026.md.

'''
for n,b in before.items():
    if n.endswith('.json'):
        d=json.loads(b);a=d.get('active_execution',d.get('active_execution_note'))
        assert a['active_work_plan']==old,(n,'concurrent_plan_change')
        a.update(active_work_plan=new,latest_internal_result=result)
        a['next']=['Implement and verify typed grouped queries against original fixture dictionaries',
         'Audit guarded composition of empty, missing and ambiguous query outcomes',
         'Integrate a coherent nested-rule increment; preserve literature residuals; S6 held; E3 deferred']
        if 'completed_increments' in a:a['completed_increments'].append('Nested term audit and nested-map projection:22 states;44 exact projections;19 controls;213 assertions')
        after[n]=json.dumps(d,indent=2)+'\n'
    else:
        s=b.decode();assert old in s,(n,'expected_pointer_missing')
        s=s.replace(old,new,1)
        if n!='MISSION_CONTROL.md':
            first,rest=s.split('\n',1);s=first+'\n\n'+note+rest.lstrip('\n')
        s=s.replace('Current question: which nested claim-term and assessment relationships lack explicit declarative invariant support?',
          'Current question: can grouped queries preserve ownership, historical dates, ties and empty populations?')
        s=s.replace('Next action: execute '+old+'.','Next action: execute '+new+'.')
        s=s.replace('Next: nested term-invariant audit.','Next: typed grouped query verification, then guarded-rule composition.')
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
checks={n:{'before':sha256(before[n]).hexdigest(),'after':sha256((ROOT/n).read_bytes()).hexdigest()} for n in files}
(HERE/'control-refresh.json').write_text(json.dumps({'controls':checks,'unchanged_pdfs':pdfs},indent=2)+'\n')
print(json.dumps({'controls_refreshed':len(files),'active_plan':new,'governing_version':'5.13 unchanged'}))
