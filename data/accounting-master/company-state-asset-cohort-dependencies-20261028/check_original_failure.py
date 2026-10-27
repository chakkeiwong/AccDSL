"""Execute the exact original Machine20 memory discriminator."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import argparse,json,subprocess,sys,time
import cohorts
rel=cohorts.rel;ROOT=cohorts.ROOT
PLAN='docs/plans/company-state-failure-dispositions-20261028.md'
INPUT='data/accounting-master/company-operation-path-20261023/example.json'
FAILURES='data/accounting-master/unified-program-20261028/failure-map.json'

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    out=p.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    base=json.loads((ROOT/INPUT).read_text());source_path=base['initial_year']['source']['path'];source=(ROOT/source_path).read_bytes()
    row=next(r['original_row'] for r in json.loads((ROOT/FAILURES).read_text())['rows'] if r['original_row']['id']=='SIM-F043')
    checks=[];runs={}
    def check(n,a,b):checks.append(dict(name=n,passed=a==b,actual=a,expected=b))
    for life,charge in [('2/1','10/1'),('1/1','20/1')]:
        path=deepcopy(base);additions=[o for o in path['initial_year']['operations'] if o['kind']=='plant_addition']
        additions[0]['payload'].update(cost='20/1',life=life)
        additions[1]['payload'].update(cost='0/1')
        r=cohorts.inspect(path,source,rel.native.digest(path));n=r['relationship_result']['native_result']
        check(life+' complete',n['status'],'complete_conditional')
        a=next(a for a in r['year_ends'][0]['assets'] if a['id']=='capex-2025-a')
        check(life+' first carrying amount',[a['cost'],a['accumulated']],['20/1','0/1'])
        read=next(x for x in r['depreciation_dependencies'] if x['asset_id']=='capex-2025-a' and x['period_start']=='2026-01-01')
        check(life+' exact next charge',read['charge'],charge)
        check(life+' all nine cohorts retained',len(r['cohorts']),9)
        runs[life]=r
    a=runs['2/1']['relationship_result']['native_result'];b=runs['1/1']['relationship_result']['native_result']
    check('equal first-year financial reports',a['years'][0]['report']['lines'],b['years'][0]['report']['lines'])
    check('equal first-year balances',a['years'][0]['run']['closing_balances'],b['years'][0]['run']['closing_balances'])
    check('different complete year-two depreciation',[a['years'][1]['run']['income']['depreciation'],b['years'][1]['run']['income']['depreciation']],['23/1','33/1'])
    files={Path(__file__),Path(cohorts.__file__),Path(rel.__file__),ROOT/PLAN,ROOT/INPUT,ROOT/FAILURES,ROOT/source_path}
    for m in list(sys.modules.values())+[rel.native,rel.native.reports,rel.native.annual_path]:
        f=getattr(m,'__file__',None)
        if f and Path(f).is_file() and Path(f).resolve().is_relative_to(ROOT):files.add(Path(f).resolve())
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command=[sys.executable,*sys.argv],environment=sys.version,cpu_gpu='CPU-only exact rational arithmetic; no accelerator imports',
        random_seeds='N/A deterministic',data_version='Original SIM-F043 and native three-year authored path',
        utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,
        result_file='data/accounting-master/construction-continuation-20261028/failure-dispositions.md',
        source_hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
    failed=[x for x in checks if not x['passed']];v=dict(status='fail' if failed else 'pass',checks=len(checks),failed=failed,original_failure=row['id'])
    for name,value in [('results',runs),('checks',checks),('original-row',row),('verification',v),('run-manifest',manifest)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+chr(10))
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    print(json.dumps(v));return bool(failed)
if __name__=='__main__':raise SystemExit(main())
