"""Exact interoperable semantics, source identity and unchanged prior evidence."""
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import io,json,os,platform,subprocess,sys,time,unittest
os.environ['CUDA_VISIBLE_DEVICES']='-1'
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
from examples import core,versions,text,binder,fixture,exchange,packet,assess
PLAN='docs/plans/accounting-requirement-version-interoperability-20261024.md'
NEXT='docs/plans/accounting-requirement-successors-integration-20261024.md'


def sha(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')


def conformance():
    checks,rows,cases=[],[],[]
    def check(name,value):
        checks.append({'name':name,'passed':bool(value)})
    for n in [1,2,3]:
        d,v=fixture(n)
        cases.append(('independent.'+str(n),d,v,None,'constructed language example'))
    base=HERE.parent
    old=json.loads((base/'method-requirements-20261024/examples.json').read_text())
    for name,case in old.items():
        cases.append(('v1.'+name,case['manifest'],case['values'],None,'retained typed example'))
    for directory,prefix in [('dimensional-requirements-20261024','v2'),
                             ('guarded-requirements-20261024','v3')]:
        for case in json.loads((base/directory/'equation-cases.json').read_text()):
            cases.append((prefix+'.'+case['case'],case['manifest'],case['values'],case['result'],
                          'retained supplied-input equation case'))
    for name,d,values,saved,provenance in cases:
        baseline=versions.assess(d,values,d['capabilities'])
        if saved is not None:
            check(name+'.frozen_result',baseline==saved)
        ex=exchange(d,values)
        authored=text.render(ex)
        check(name+'.typed_text',text.lower(authored)==ex)
        check(name+'.strict_exchange',text.decode_exchange(core.canonical(ex).decode())==ex)
        check(name+'.text_semantics',text.assess_exchange(text.lower(authored))==baseline)
        p=packet(d,values)
        bound=assess(p)
        check(name+'.bound',bound['status']=='bound')
        selected=p['manifests'][p['plan']['manifest_digest']]
        check(name+'.bound_values',bound.get('values')==values)
        check(name+'.bound_semantics',bound.get('assessment')==versions.assess(selected,values,d['capabilities']))
        check(name+'.source_identity',all(item['source_ref']==selected['inputs'][key]['source_ref']
              and item['schema_digest']==p['plan']['records'][item['record']]['schema_digest']
              and item['type']==d['inputs'][key]['type'] for key,item in bound.get('lineage',{}).items()))
        check(name+'.no_admission',all(bound[k] is False and bound['assessment'][k] is False
              for k in ['executed','source_admission','accounting_admission','method_eligible']))
        rows.append({'case':name,'provenance':provenance,
                     'binding_record':'explicit canonical derived projection of supplied values; not original source bytes',
                     'original_definition_digest':core.digest(d),'exchange':ex,'authoring':authored,
                     'original_assessment':baseline,'bound_definition':selected,
                     'plan':p['plan'],'schemas':p['schemas'],
                     'raw_records_utf8':{h:raw.decode() for h,raw in p['blobs'].items()},'binding_result':bound})
    suite=unittest.TestSuite()
    for pattern in ['test_method_requirements_v1.py','test_method_requirement_text_v1.py',
                    'test_method_input_binding_v1.py','test_method_requirements_v2.py',
                    'test_method_requirements_v3.py','test_method_requirement_interoperability.py']:
        suite.addTests(unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern))
    captured=io.StringIO()
    result=unittest.TextTestRunner(stream=captured,verbosity=1).run(suite)
    check('combined_59_unit_methods',result.wasSuccessful() and result.testsRun==59)
    if not result.wasSuccessful():
        print(captured.getvalue(),file=sys.stderr)
    prior=base/'guarded-requirements-20261024'
    old=json.loads((prior/'manifest.json').read_text())
    locks={}
    for group in ['inputs','implementation','outputs']:
        locks.update(old[group])
    for path in [ROOT/PLAN,ROOT/NEXT,prior/'manifest.json']:
        name=str(path.relative_to(ROOT))
        if name in locks:
            check('consistent_lock:'+name,locks[name]==sha(path))
        else:
            locks[name]=sha(path)
    for name,h in locks.items():
        check('protected_input:'+name,sha(ROOT/name)==h)
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'unit_tests':result.testsRun,
            'cases':len(rows),'retained_cases':len(rows)-3},rows,locks


def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check'
    assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'record exists'
    started=datetime.now(timezone.utc).isoformat()
    clock=time.monotonic()
    if mode=='--replay':
        manifest=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in manifest[group].items():
                assert sha(ROOT/name)==h,name
    result,rows,locks=conformance()
    observation={'mode':mode,'passed':result['passed'],'checks':len(result['checks']),
                 'unit_tests':result['unit_tests'],'cases':result['cases'],
                 'retained_cases':result['retained_cases'],'protected_inputs':len(locks),
                 'failed':[c['name'] for c in result['checks'] if not c['passed']],
                 'wall_seconds':time.monotonic()-clock}
    if not result['passed']:
        dump(HERE/('failed-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        for name,value in [('checks.json',result),('cases.json',rows),('source-lock.json',locks)]:
            dump(HERE/name,value)
        files=[p for p in HERE.iterdir() if p.is_file() and p.suffix in ['.py','.md']]
        files.extend(ROOT/p for p in ['scripts/method_requirement_versions.py',
                     'scripts/method_requirement_text_v2.py','scripts/method_input_binding_v2.py',
                     'tests/test_method_requirement_interoperability.py'])
        dump(HERE/'manifest.json',{'started_utc':started,'wall_seconds':observation['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version()+'; preserved requirement v1/v2/v3 modules',
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic conformance',
            'data_version':'exact upstream identities in source-lock.json; constructed projections labeled separately',
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),'inputs':locks,
            'implementation':{str(p.relative_to(ROOT)):sha(p) for p in files},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','cases.json','source-lock.json']}})
    elif mode=='--replay':
        assert result==json.loads((HERE/'checks.json').read_text())
        assert rows==json.loads((HERE/'cases.json').read_text())
        assert locks==json.loads((HERE/'source-lock.json').read_text())
    print(json.dumps(observation))
    return 0 if result['passed'] else 1


if __name__=='__main__':
    sys.exit(main())
