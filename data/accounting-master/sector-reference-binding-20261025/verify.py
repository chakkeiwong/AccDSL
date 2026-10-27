"""Exact retained-reference binding evidence; record once, replay read only."""
from hashlib import sha256
from pathlib import Path
import io
import json
import platform
import subprocess
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
import sector_reference_binding_v1 as binding
from test_sector_reference_binding_v1 import fixture


def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path,value): path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def run():
    start=time.monotonic(); record='--record' in sys.argv
    if record and (HERE/'evidence.json').exists(): raise SystemExit('Evidence exists; replay without --record')
    tests=[]
    for pattern in ['test_sector_reference_binding_v1.py','test_company_world_envelope_v1.py']:
        stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern)
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        assert result.wasSuccessful() and result.testsRun,stream.getvalue()
        tests.append({'pattern':pattern,'count':result.testsRun})
        if record:(HERE/(pattern+'.log')).write_text(stream.getvalue())
    prior=ROOT/'data/accounting-master/company-world-envelope-20261025/source-lock.json'
    for name,expected in json.loads(prior.read_text()).items():assert sha(ROOT/name)==expected,name
    locks={str(prior.relative_to(ROOT)):sha(prior)};cases={};counts={}
    for sector in ['bank','insurance']:
        request=fixture(sector);result=binding.bind(request)
        assert result['status']=='assessment_reference_resolved' and binding.verify(request,result)
        assert result['world']==request['world'] and not result['posting_authorized']
        assert result['component_status']=='unresolved' and result['unresolved_obligations']==request['world']['obligations']
        cases[sector]={'request':request,'result':result}
        counts[sector]={'records':len(result['records']),'blobs':len(result['blobs']),
                        'bytes':sum(row['byte_length'] for row in result['blobs'].values())}
        for row in result['blobs'].values():locks[row['path']]=row['sha256']
        entry=binding.CATALOG[sector]
        folder=ROOT/entry['directory'];parent=folder.parent
        origin=json.loads((parent/'run-manifest.json').read_text())
        if sector=='bank':
            validation=origin['validations'][-1]
            assert validation['packet_sha256']==entry['packet_sha256'] and validation['checks']==1693 and validation['failed']==0
            assert sha(ROOT/validation['artifact'])==validation['sha256']
            locks[validation['artifact']]=validation['sha256']
        else:
            accepted=next(row for row in origin['runs'] if row['attempt']=='attempt-02')
            assert accepted['verification']['packet_sha256']==entry['packet_sha256']
            assert accepted['verification']['checks']==2705 and accepted['verification']['failures']==0
        for name in ['portable-exchanges.json','record-schemas.json']:
            path=folder/name;locks[str(path.relative_to(ROOT))]=sha(path)
        for name in ['run-manifest.json','verify_exchanges.py','semantic-contract.md']:
            path=parent/name;locks[str(path.relative_to(ROOT))]=sha(path)
    evidence={'tests':tests,'cases':cases,'closure_counts':counts,
              'scope':'Selected native references and bytes only; native calculations not rerun'}
    if record:
        dump(HERE/'evidence.json',evidence)
        for name in ['scripts/sector_reference_binding_v1.py','tests/test_sector_reference_binding_v1.py',
                     'scripts/company_world_envelope_v1.py','scripts/method_requirements_v1.py',
                     'docs/plans/accounting-sector-reference-binding-20261025.md',
                     str((HERE/'verify.py').relative_to(ROOT)),str((HERE/'evidence.json').relative_to(ROOT))]:
            locks[name]=sha(ROOT/name)
        dump(HERE/'source-lock.json',locks)
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
             'command':'python3 -B data/accounting-master/sector-reference-binding-20261025/verify.py --record',
             'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU file/schema checks; no GPU framework imported',
             'seeds':'N/A: deterministic','data_version':binding.CATALOG,'wall_seconds':time.monotonic()-start,
             'plan':'docs/plans/accounting-sector-reference-binding-20261025.md',
             'result':str((HERE/'result.md').relative_to(ROOT)),
             'artifacts':[str((HERE/n).relative_to(ROOT)) for n in ['evidence.json','source-lock.json']]})
    else:
        assert evidence==json.loads((HERE/'evidence.json').read_text()),'evidence replay'
        for name,expected in json.loads((HERE/'source-lock.json').read_text()).items():assert sha(ROOT/name)==expected,name
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay',
                      'focused':tests[0]['count'],'regressions':tests[1]['count'],'closures':counts}))


if __name__=='__main__':run()
