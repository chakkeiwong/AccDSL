"""Record native group selectors once; replay without changing evidence."""
from hashlib import sha256
from pathlib import Path
import io
import json
import platform
import subprocess
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'tests'))
import native_group_binding_v1 as binding
from test_native_group_binding_v1 import fixture

def sha(path):return sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def run():
    start=time.monotonic();record='--record' in sys.argv
    if record and (HERE/'evidence.json').exists():raise SystemExit('Evidence exists; replay without --record')
    locks={};tests=[]
    def lock(path,expected=None):
        path=path if isinstance(path,Path) else ROOT/path
        actual=sha(path)
        if expected is not None:assert actual==expected,str(path)
        locks[str(path.relative_to(ROOT))]=actual
    for name in ['company-world-envelope-20261025','sector-reference-binding-20261025']:
        prior=ROOT/'data/accounting-master'/name/'source-lock.json';lock(prior)
        for path,expected in json.loads(prior.read_text()).items():lock(path,expected)
    for pattern in ['test_native_group_binding_v1.py','test_company_world_envelope_v1.py','test_sector_reference_binding_v1.py']:
        stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern)
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        assert result.wasSuccessful() and result.testsRun,stream.getvalue()
        tests.append({'pattern':pattern,'count':result.testsRun})
        if record:(HERE/(pattern+'.log')).write_text(stream.getvalue())
    parent=binding.FOLDER.parent;origin=json.loads((parent/'run-manifest.json').read_text())
    accepted=next(r for r in origin['runs'] if r['attempt']=='attempt-03')
    assert accepted['checks']==681 and accepted['failures']==0
    assert accepted['packet_sha256']==binding.PINS['portable-exchanges.json']
    lock(parent/'run-manifest.json');lock(accepted['validation'],accepted['validation_sha256'])
    validation=json.loads((ROOT/accepted['validation']).read_text())
    assert len(validation['checks'])==681 and validation['failed']==0
    assert all(r['passed'] is True for r in validation['checks'])
    assert validation['runtime_executed'] is False
    for key in ['packet_sha256','verifier_sha256','financial_sha256','migration_sha256']:assert validation[key]==accepted[key]
    assert len(accepted['input_snapshots'])==14
    for row in accepted['input_snapshots'].values():lock(row['path'],row['sha256'])
    for filename,expected in binding.PINS.items():lock(binding.FOLDER/filename,expected)
    cases={};counts={}
    for snapshot in ['initial','final']:
        request=fixture(snapshot);result=binding.bind(request)
        assert result['status']=='group_references_resolved' and binding.verify(request,result)
        assert result['world']==request['world'] and result['unresolved_obligations']==request['world']['obligations']
        assert all(result[k] is False for k in binding.FLAGS if k!='selected_references_resolved')
        assert result['selected_references_resolved'] is True
        cases[snapshot]={'request':request,'result':result}
        counts[snapshot]={'records':len(result['records']),'blobs':len(result['blobs']),
                          'bytes':sum(row['byte_length'] for row in result['blobs'].values())}
        for row in result['blobs'].values():lock(row['path'],row['sha256'])
    evidence={'tests':tests,'cases':cases,'closure_counts':counts,
              'native_preservation':{'checks':681,'failures':0,'inputs':14,'financial_checks_rerun':False},
              'scope':'Exact selected references and unchanged shared group context; no executable legal-book admission'}
    for path in ['scripts/native_group_binding_v1.py','tests/test_native_group_binding_v1.py',
                 'docs/plans/accounting-native-group-binding-20261025.md',
                 str((HERE/'audit.md').relative_to(ROOT)),str(Path(__file__).relative_to(ROOT))]:lock(path)
    if record:
        dump(HERE/'evidence.json',evidence);lock(HERE/'evidence.json')
        for item in tests:lock(HERE/(item['pattern']+'.log'))
        dump(HERE/'source-lock.json',locks)
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/native-group-binding-20261025/verify.py --record',
            'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU file/schema checks; no GPU framework imported',
            'seeds':'N/A: deterministic','data_version':binding.PINS,'wall_seconds':time.monotonic()-start,
            'plan':'docs/plans/accounting-native-group-binding-20261025.md','result':str((HERE/'result.md').relative_to(ROOT)),
            'source_lock_sha256':sha(HERE/'source-lock.json'),
            'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['evidence.json','source-lock.json']},
            'provenance':'Git identifies base; source locks identify the executed uncommitted bytes'})
    else:
        assert evidence==json.loads((HERE/'evidence.json').read_text()),'evidence replay'
        saved=json.loads((HERE/'source-lock.json').read_text())
        for path,expected in saved.items():assert sha(ROOT/path)==expected,path
        for path,expected in locks.items():assert saved[path]==expected,path
        manifest=json.loads((HERE/'run-manifest.json').read_text())
        for path,expected in manifest['artifacts'].items():assert sha(ROOT/path)==expected,path
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay','focused':tests[0]['count'],
                      'regressions':sum(r['count'] for r in tests[1:]),'closures':counts,'locked_files':len(json.loads((HERE/'source-lock.json').read_text()))}))

if __name__=='__main__':run()
