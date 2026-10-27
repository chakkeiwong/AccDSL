"""One-time control refresh after immutable source-audit replay."""
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
REL=HERE.relative_to(ROOT).as_posix()
PLAN='docs/plans/accounting-module-invocation-20261024.md'

def sha(p): return sha256(p.read_bytes()).hexdigest()
def dump(p,d): p.write_text(json.dumps(d,indent=2)+'\n')

def main():
    assert not (HERE/'control-refresh.json').exists(),'already refreshed'
    replay=json.loads(subprocess.run([sys.executable,'-B',str(HERE/'verify.py'),'--replay'],cwd=ROOT,capture_output=True,text=True,check=True).stdout)
    assert (ROOT/PLAN).is_file()
    names=['docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md',
           'docs/plans/accounting-master-program.md','docs/plans/accounting-mission-requirements.md',
           'docs/plans/accounting-product-design-checkpoint.md','data/accounting-master/next-plan.md',
           'data/accounting-master/simulator-session-20261023.md','data/accounting-master/next-plan.json',
           'scripts/accounting_master_catalog.json']
    before={}
    for name in names:
        p=ROOT/name;before[name]=sha(p);backup=HERE/'control-before'/name
        backup.parent.mkdir(parents=True,exist_ok=True);backup.write_bytes(p.read_bytes())
    note=f'''## Existing module capabilities audited — 24 October 2026

Eight retained references distinguish measurement,report,proposal,pure apply
and fixed-engine database capabilities. Forty-four original-context probe checks
pass;26 inspected sources and executed local code remain protected.
Return and lease states are incompatible closed schemas; a caller interface
must preserve their native methods rather than merge openings or rename owners.
Result: {REL}/result.md. Inventory: {REL}/capabilities.json.
Next: {PLAN}. Specify and check a pinned common invocation/result envelope;
general shared-state composition and durability remain separate obligations.
Version3.74 remains470 pages,not_ready; S1-S5 partial,S6 held,S7 deferred.

'''
    for name in names:
        p=ROOT/name
        if name.endswith('.md'):
            title,rest=p.read_text().split('\n',1)
            if 'simulator-session' in name:
                rest='No command running. Begin with the audited module-invocation plan.\nPreserve frozen packages and unrelated work. No commit, agents, outreach or forecasting.\nModule capability audit is recorded; original methods remain unchanged.\n'
            p.write_text(title+'\n\n'+note+rest.lstrip('\n'))
    for name,key in [('data/accounting-master/next-plan.json','active_execution'),('scripts/accounting_master_catalog.json','active_execution_note')]:
        p=ROOT/name;d=json.loads(p.read_text());old={k:v for k,v in d.items() if k!=key};a=d[key]
        a.update(active_work_plan=PLAN,latest_result=REL+'/result.md',updated='2026-10-24')
        if key=='active_execution':
            a['latest_results'].append(REL+'/result.md')
            a['completed_increments'].append('Module audit:8 references;44 probe checks;26 sources;composition and durability distinguished')
            a['next'][0]='Implement the finite capability-aware module invocation reference'
        dump(p,d);assert old=={k:v for k,v in json.loads(p.read_text()).items() if k!=key}
    dump(HERE/'replay-observation.json',replay)
    dump(HERE/'coverage-delta.json',{'whole_rows_closed':0,'mc_scope':['MC01','MC02','MC03','MC04','MC05','MC06','MC08','MC11','MC13','MC16','MC17','MC24','MC26','MC28','MC35'],'latest_full_inventory':'data/accounting-master/henkel-lease-coverage-20261024/inventory.json','full_inventory_refresh_pending':True})
    dump(HERE/'control-refresh.json',{'before':before,'after':{n:sha(ROOT/n) for n in names},'legacy_json_fields_unchanged':True})
    print(json.dumps({'controls':len(names),'checks':replay['probe_checks'],'next':PLAN}))

if __name__=='__main__': main()
