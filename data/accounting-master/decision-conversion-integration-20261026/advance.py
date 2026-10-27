"""Advance reviewed local links and merge current notes without changing frozen phase bindings."""
from pathlib import Path
from hashlib import sha256
import json
import os
import integrate as integration

HERE,ROOT,TARGET=integration.HERE,integration.ROOT,integration.TARGET
RESULT='data/accounting-master/decision-conversion-integration-20261026/result.md'
REMAINING='data/accounting-master/decision-conversion-integration-20261026/remaining-work.md'
NEXT='docs/plans/accounting-dated-funding-bundle-20261026.md'
def digest(data):return sha256(data).hexdigest()


def main():
    assert not (HERE/'advancement.json').exists()
    verification=json.loads((HERE/'verification.json').read_text())
    assert verification['status']=='PASS' and (HERE/'review.md').exists()
    assert integration.sha(ROOT/'docs/AccDSL-latest.pdf')==integration.BASE
    assert integration.sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==integration.STANDALONE
    documents={row['document']:row for row in verification['documents']}
    main_pdf=documents['accounting-product-proposal'];sim=documents['simulation-foundations']
    assert integration.sha(ROOT/main_pdf['pdf'])==main_pdf['sha256'] and integration.sha(ROOT/sim['pdf'])==sim['sha256']
    shared=['MISSION_CONTROL.md','docs/plans/accounting-master-checkpoint.md','docs/plans/accounting-master-current.md',
            'docs/plans/accounting-product-design-checkpoint.md','docs/plans/accounting-mission-requirements.md',
            'data/accounting-master/next-plan.md','data/accounting-master/recovery-current-20261026.md',
            'scripts/accounting_master_catalog.json','data/accounting-master/next-plan.json']
    before={name:(ROOT/name).read_bytes() for name in shared}
    backup=HERE/'control-before';backup.mkdir(exist_ok=False)
    for name,data in before.items():
        path=backup/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    note=f'''## Current execution — 26 October 2026

Version 5.19 is the governing 760-page candidate, not_ready; the simulation
volume has 193 total / 175 body pages across 26 chapters. Stable PDF and TeX
links select the same protected source package. Actor-specific decisions,
two-date price/control and selected typed conversion are integrated.
Integration: {RESULT}.
Main SHA256: {main_pdf['sha256']}.
Standalone SHA256: {sim['sha256']}.
The integration passes 856 checks, protecting 242 sources and 60 evidence
files. Complete conversion cases pass 145 assertions/14 controls; the separate
finite price/control reference passes 139 assertions/28 controls.
Full program: data/accounting-master/gap-decision-refresh-20261026/closure-program.md.
Current remaining work: {REMAINING}.
Next plan: {NEXT}.
All 53 obligations, six interactions, 46 operations and 18 packages remain.
S1–S5 partial; S6 held; E3 deferred. Independent reader/domain and whole-document
acceptance remain pending. Preserve successful evidence; do not rerun writers.

'''
    updates={}
    for name in shared[:-2]:
        text=before[name].decode();first,sep,rest=text.partition('\n')
        updates[name]=(first+'\n\n'+note+(rest.lstrip() if 'recovery-current' not in name else '')).encode()
    catalog=json.loads(before['scripts/accounting_master_catalog.json'])
    current=catalog['active_execution_note']
    active=[p for p in current.get('active_work_plans',[]) if p not in ('docs/plans/accounting-conversion-rights-bridge-20261026.md',NEXT)]
    changed=dict(updated='2026-10-26',current_candidate='5.19;760 pages;not_ready',latest_result=RESULT,
                 current_pdf=main_pdf['pdf'],current_pdf_sha256=main_pdf['sha256'],standalone_pdf=sim['pdf'],standalone_pdf_sha256=sim['sha256'],
                 latest_internal_result='data/accounting-master/conversion-rights-bridge-20261026/result.md',
                 current_internal_status='Typed conversion and dated decision companions integrated; funding settlement is next; broader source and method work remains',
                 active_work_plan=NEXT,active_work_plans=[NEXT,*active],remaining_work=REMAINING,full_gap_remaining_work=REMAINING,
                 next=['Execute complete dated funding/counterparty settlement','Specify intervening measurement and carry, then terminal liquidation','Continue actual source access and the full open package queue'])
    current.update(changed)
    updates['scripts/accounting_master_catalog.json']=(json.dumps(catalog,indent=2,ensure_ascii=False)+'\n').encode()
    next_plan=json.loads(before['data/accounting-master/next-plan.json']);next_plan['active_execution'].update(changed)
    updates['data/accounting-master/next-plan.json']=(json.dumps(next_plan,indent=2,ensure_ascii=False)+'\n').encode()
    for name,data in before.items():assert (ROOT/name).read_bytes()==data,'concurrent control change:'+name
    assert integration.sha(ROOT/'docs/AccDSL-latest.pdf')==integration.BASE
    for name,data in updates.items():(ROOT/name).write_bytes(data)
    links={}
    for name,base,ext in [('AccDSL-latest.pdf','accounting-product-proposal','.pdf'),('AccDSL-latest.tex','accounting-product-proposal','.tex'),
                          ('AccDSL-simulation-foundations.pdf','simulation-foundations','.pdf'),('AccDSL-simulation-foundations.tex','simulation-foundations','.tex')]:
        link=ROOT/'docs'/name;assert link.is_symlink();old=os.readlink(link)
        temporary=link.with_name(link.name+'.decision-conversion-next');assert not temporary.exists()
        target=os.path.relpath(TARGET/(base+ext),link.parent);temporary.symlink_to(target);os.replace(temporary,link)
        links[str(link.relative_to(ROOT))]=dict(before=old,after=target)
    assert integration.sha(ROOT/'docs/AccDSL-latest.pdf')==main_pdf['sha256']
    assert integration.sha(ROOT/'docs/AccDSL-simulation-foundations.pdf')==sim['sha256']
    (HERE/'advancement.json').write_text(json.dumps(dict(status='PASS',before={k:digest(v) for k,v in before.items()},after={k:digest(v) for k,v in updates.items()},links=links,next_plan=NEXT),indent=2)+'\n')
    print(json.dumps(dict(status='PASS',candidate='5.19',controls=len(updates),links=len(links),next_plan=NEXT)))


if __name__=='__main__':main()
