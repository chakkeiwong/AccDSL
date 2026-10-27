"""Independent cohort arithmetic and retained native refusal controls."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time
import cohorts

rel=cohorts.rel
ROOT=cohorts.ROOT
HERE='data/accounting-master/company-state-asset-cohort-dependencies-20261028'
PLAN='docs/plans/company-state-asset-cohort-dependencies-20261028.md'
INPUT='data/accounting-master/company-operation-path-20261023/example.json'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();path=json.loads((ROOT/INPUT).read_text())
    source_path=path['initial_year']['source']['path'];source=(ROOT/source_path).read_bytes()
    checks,controls=[],{}
    def check(name,a,b):checks.append(dict(name=name,passed=a==b,actual=rel.wire(a),expected=rel.wire(b)))
    def inspect(p):return cohorts.inspect(p,source,rel.native.digest(p))
    def addition(p,year=0):return next(o for o in [p['initial_year'],*p['continuations']][year]['operations'] if o['kind']=='plant_addition')
    saved=deepcopy(path);result=inspect(path);native=result['relationship_result']['native_result']
    check('complete native path',native['status'],'complete_conditional')
    check('input immutable',path,saved)
    check('nine cohorts retained',len(result['cohorts']),9)
    check('six additions retained',len(result['addition_events']),6)
    check('all executed prefixes retained',len(result['prefixes']),63)
    check('all cohort-year reads retained',len(result['depreciation_dependencies']),21)
    check('all three years retained',len(result['year_ends']),3)
    check('no source admission',result['source_admission'],False)
    check('no reduced program',result['executable_reduction'],None)
    for yi,(expense,net,cost,accum,pop) in enumerate([(13,98,142,44,5),(15,93,152,59,7),(16,87,162,75,9)]):
        yr=result['year_ends'][yi];b=native['years'][yi]['run']['closing_balances']
        check('population '+str(yi),len(yr['assets']),pop)
        check('independent depreciation '+str(yi),Q(native['years'][yi]['run']['income']['depreciation']),Q(expense))
        check('independent cost '+str(yi),Q(b['plant_cost']),Q(cost))
        check('independent accumulation '+str(yi),-Q(b['accum_depreciation']),Q(accum))
        check('independent net plant '+str(yi),Q(b['plant_cost'])+Q(b['accum_depreciation']),Q(net))
        check('native complete assets '+str(yi),yr['assets'],native['years'][yi]['closing_memory']['assets'])
    for c in result['cohorts']:
        check('unknown identity '+c['id'],[c['physical_location'],c['legal_title'],c['source_support']],[None]*3)
    for row in result['depreciation_dependencies']:
        check('charge conserves cost '+row['event']+':'+row['asset_id'],
            Q(row['accumulated_after']),Q(row['accumulated_before'])+Q(row['charge']))
        check('never exceeds cost '+row['event']+':'+row['asset_id'],Q(row['accumulated_after'])<=Q(row['cost']),True)
    # Same current financial report, different future expense under supplied lives.
    shorter=deepcopy(path);addition(shorter)['payload']['life']='5/1'
    alt=inspect(shorter);an=alt['relationship_result']['native_result']
    check('life alternative complete',an['status'],'complete_conditional')
    check('same first-year statements',an['years'][0]['run']['statements'],native['years'][0]['run']['statements'])
    check('same first-year balances',an['years'][0]['run']['closing_balances'],native['years'][0]['run']['closing_balances'])
    check('same first-year report lines',an['years'][0]['report']['lines'],native['years'][0]['report']['lines'])
    check('different cohort memory',an['years'][0]['closing_memory']['assets']!=native['years'][0]['closing_memory']['assets'],True)
    check('next year changed depreciation',an['years'][1]['run']['income']['depreciation'],'16/1')
    check('third year changed depreciation',an['years'][2]['run']['income']['depreciation'],'17/1')
    controls['shorter_life_same_current_reports']=alt
    delayed=deepcopy(path);addition(delayed)['payload']['in_service']='2027-01-01'
    delay=inspect(delayed);dn=delay['relationship_result']['native_result']
    check('delayed service complete',dn['status'],'complete_conditional')
    check('delayed service same first report',dn['years'][0]['report']['lines'],native['years'][0]['report']['lines'])
    check('delayed service lower year-two depreciation',dn['years'][1]['run']['income']['depreciation'],'14/1')
    check('delayed service restores year-three charge',dn['years'][2]['run']['income']['depreciation'],'16/1')
    zero=[r for r in delay['depreciation_dependencies'] if r['asset_id']=='capex-2025-a' and r['period_start']=='2026-01-01'][0]
    check('zero charge retains service guard', [zero['eligible'],zero['charge'],zero['in_service']], [False,'0/1','2027-01-01'])
    controls['delayed_service']=delay
    capped=deepcopy(path);capped['initial_year']['assets'][0]['life']='1/1'
    cap=inspect(capped);cn=cap['relationship_result']['native_result']
    check('capped alternative complete',cn['status'],'complete_conditional')
    rows=[r for r in cap['depreciation_dependencies'] if r['asset_id']=='opening-plant']
    check('remaining-cost cap',rows[0]['charge'],'70/1')
    check('fully depreciated cohort stays',len(rows),3)
    check('fully depreciated subsequent zero charges',[r['charge'] for r in rows[1:]],['0/1','0/1'])
    check('cap independent annual expenses',[y['run']['income']['depreciation'] for y in cn['years']],['73/1','5/1','6/1'])
    controls['remaining_cost_cap']=cap
    mutations=[
        ('duplicate asset',lambda p:addition(p)['payload'].update(asset_id='opening-plant'),'invalid','duplicate_asset'),
        ('zero life',lambda p:addition(p)['payload'].update(life='0/1'),'invalid','asset_life'),
        ('service before acquisition',lambda p:addition(p)['payload'].update(in_service='2025-12-30'),'invalid','service_before_acquisition'),
        ('midyear service',lambda p:addition(p)['payload'].update(in_service='2025-12-31'),'unsupported','midyear_service_fraction'),
        ('unknown life',lambda p:addition(p)['payload'].update(life='unknown'),'unresolved','operation_inputs'),
        ('late duplicate',lambda p:addition(p,2)['payload'].update(asset_id='capex-2025-a'),'invalid','duplicate_asset'),
    ]
    for name,mutate,status,reason in mutations:
        p=deepcopy(path);mutate(p);r=inspect(p);n=r['relationship_result']['native_result'];run=n['years'][-1]['run']
        check(name+' partial',n['status'],'partial')
        check(name+' status',run['status'],status)
        check(name+' reason',run['reason'],reason)
        check(name+' no refused addition',any(e['event']==rel.event_key(n['stopped_index'],run['event']) for e in r['addition_events']),False)
        if name=='late duplicate':check('preserve first two years',n['years'][:2],native['years'][:2])
        controls[name]=r
    failed=[c for c in checks if not c['passed']]
    files={Path(__file__),Path(cohorts.__file__),Path(rel.__file__),ROOT/PLAN,ROOT/INPUT,ROOT/source_path}
    for m in list(sys.modules.values())+[rel.native,rel.native.reports,rel.native.annual_path]:
        f=getattr(m,'__file__',None)
        if f and Path(f).is_file() and Path(f).resolve().is_relative_to(ROOT):files.add(Path(f).resolve())
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],environment=sys.version,
        cpu_gpu='CPU-only exact rational inspection; no accelerator imports',random_seeds='N/A deterministic',
        data_version='Retained original three-year CompanyOperationPathDraft/1 and authored cohort alternatives',
        utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,
        plan_file=PLAN,result_file=HERE+'/result.md',
        source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
    verification=dict(status='fail' if failed else 'pass',checks=len(checks),failed=failed,
                      cohorts=len(result['cohorts']),annual_cohort_reads=len(result['depreciation_dependencies']),controls=len(controls))
    for name,data in [('inspection',result),('controls',controls),('checks',checks),('run-manifest',manifest),('verification',verification)]:
        (out/(name+'.json')).write_text(json.dumps(rel.wire(data),indent=2)+chr(10))
    for f in [Path(__file__),Path(cohorts.__file__)]: (out/f.name).write_bytes(f.read_bytes())
    print(json.dumps(verification));return bool(failed)


if __name__=='__main__':raise SystemExit(main())
