"""Record finished companions and move to dated authority preparation."""
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
NEXT='docs/plans/accounting-contingent-conversion-authority-20261026.md'
FUNDING='data/accounting-master/dated-funding-bundle-20261026/result.md'
AUDIT='data/accounting-master/conversion-measurement-audit-20261026/result.md'
REMAINING='data/accounting-master/dated-funding-bundle-20261026/remaining-work.md'


def main():
    assert not (HERE/'refresh.json').exists()
    names=['MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-current.md',
           'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md',
           'data/accounting-master/next-plan.md','data/accounting-master/recovery-current-20261026.md',
           'scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json']
    before={name:(ROOT/name).read_bytes() for name in names};catalog=json.loads(before[names[-2]])
    current=catalog['active_execution_note'];assert current['current_candidate']=='5.19;760 pages;not_ready'
    assert sha256((ROOT/current['current_pdf']).read_bytes()).hexdigest()==current['current_pdf_sha256']
    backup=HERE/'control-before';backup.mkdir(exist_ok=False)
    for name,data in before.items():
        path=backup/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    note=f'''## Current internal continuation — 26 October 2026

Version 5.19 remains governing: main760 pages, simulation193 total/175 body
pages, not_ready. Its PDF/source links and hashes are unchanged. Dated funding
now passes four complete four-book cases,20 controls and232 assertions,
including all six transfer orders. Only the two receipt-before-payment
orders pass. Result: {FUNDING}.
The measurement audit passes15 exact/source-boundary checks and rejects
silent reuse of the older maturity-only accounting package and pricing rate.
Result: {AUDIT}.
These are checked companions after5.19; neither changes accounting admission.
Next: {NEXT}.
Current remaining work: {REMAINING}.
Full program: data/accounting-master/gap-decision-refresh-20261026/closure-program.md.
All53 obligations, six interactions,46 operations and18 packages remain;
S1–S5 partial, S6 held, E3 deferred. No successful evidence writer should rerun.

'''
    updates={}
    for name in names[:-2]:
        first,_,rest=before[name].decode().partition('\n')
        updates[name]=(first+'\n\n'+note+(rest.lstrip() if 'recovery-current' not in name else '')).encode()
    active=[p for p in current.get('active_work_plans',[]) if p not in ('docs/plans/accounting-dated-funding-bundle-20261026.md','docs/plans/accounting-conversion-measurement-audit-20261026.md',NEXT)]
    changes=dict(latest_internal_result=AUDIT,latest_internal_results=[FUNDING,AUDIT],active_work_plan=NEXT,active_work_plans=[NEXT,*active],remaining_work=REMAINING,full_gap_remaining_work=REMAINING,
                 current_internal_status='Dated funding checked; accounting measurement/source prerequisites remain explicit; source preparation is next',
                 next=['Inspect dated primary authority and conditional conversion terms','Integrate the checked funding and measurement companions','Continue actual source access and the full open-package queue'])
    current.update(changes);updates[names[-2]]=(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n').encode()
    nxt=json.loads(before[names[-1]]);nxt['active_execution'].update(changes);updates[names[-1]]=(json.dumps(nxt,indent=2,ensure_ascii=False)+'\n').encode()
    for name,data in before.items():assert (ROOT/name).read_bytes()==data,'concurrent change:'+name
    for name,data in updates.items():(ROOT/name).write_bytes(data)
    (HERE/'refresh.json').write_text(json.dumps(dict(status='PASS',before={k:sha256(v).hexdigest() for k,v in before.items()},after={k:sha256(v).hexdigest() for k,v in updates.items()},next_plan=NEXT),indent=2)+'\n')
    print(json.dumps(dict(status='PASS',controls=len(updates),candidate='5.19',next_plan=NEXT)))


if __name__=='__main__':main()
