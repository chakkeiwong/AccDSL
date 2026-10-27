"""Record once; replay source contracts and frozen dependencies read only."""
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
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(HERE))
import examples as ex
import declared_receivable_text_v1 as command_text

PATTERNS=['test_receivable_source_contract_v1.py','test_declared_receivable_lifecycle_v1.py',
          'test_declared_receivable_text_v1.py','test_accounting_p06.py',
          'test_company_book_reports_v1.py','test_company_book_carry_v1.py',
          'test_company_book_transition_v2.py']


def sha(path): return sha256(path.read_bytes()).hexdigest()
def dump(path,value): path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+chr(10))
def ensure(condition,message):
    if not condition: raise RuntimeError(message)


def run():
    started=time.monotonic();record='--record' in sys.argv
    ensure(set(sys.argv[1:]) <= {'--record'},'unknown argument')
    ensure(not record or not (HERE/'evidence.json').exists(),'Evidence exists; replay without --record')
    locks={}
    prior=ROOT/'data/accounting-master/declared-collection-state-growth-20261025/source-lock.json'
    prior_locks=json.loads(prior.read_text())
    for name,expected in prior_locks.items():ensure(sha(ROOT/name)==expected,'predecessor changed: '+name)
    locks.update(prior_locks);locks[str(prior.relative_to(ROOT))]=sha(prior)
    if not record:
        for name,expected in json.loads((HERE/'source-lock.json').read_text()).items():
            ensure(sha(ROOT/name)==expected,'locked source changed: '+name)
    tests=[];logs={}
    for pattern in PATTERNS:
        stream=io.StringIO();suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'),pattern=pattern)
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        ensure(result.testsRun>0 and result.wasSuccessful(),pattern+chr(10)+stream.getvalue())
        tests.append({'pattern':pattern,'count':result.testsRun});logs[pattern+'.log']=stream.getvalue()
    cases={};artifacts={}
    for owner in ['alpha','beta']:
        for view in ['original','corrected']:
            request,roles,_=ex.fixture(owner)
            if view=='corrected':request['view']['cutoff']='2027-04-01T00:00:00Z'
            result=ex.source.run(request)
            ensure(result['status']=='conditional_execution','source compilation')
            ensure(result['execution']['status']=='complete_provisional','lifecycle completion')
            ensure(ex.source.verify(request,result),'exact replay')
            source,imports=command_text.from_program(result['program'])
            ensure(command_text.compile_text(source,imports)['program']==result['program'],'text roundtrip')
            ensure(command_text.execute_text(source,imports)==result['execution'],'text execution')
            name=owner+'-'+view
            case={'request':request,'result':result,'command_text':source,'imports':imports}
            artifacts[name+'.json']=case
            execution=result['execution'];annual=next(r['result'] for r in execution['reports'] if r['id']=='annual')
            cases[name]={'artifact':name+'.json','canonical_sha256':ex.source.core.digest(case),
                         'selected':result['selection']['selected_ids'],
                         'successful_commands':execution['successful_commands'],
                         'annual_balance_sheet':annual['balance_sheet'],'annual_income':annual['income'],
                         'final_balances':{k:execution['current']['balances'][roles[k]] for k in roles},
                         'assertions':len(request['assertions']),'claims':len(execution['current']['memory']['claims'])}
    evidence={'profile':ex.source.PROFILE,'tests':tests,'cases':cases,
              'flags':ex.source.FLAGS,'scope':'Constructed source spans and conditional histories; actual source and temporal admission remain false'}
    if record:
        for name,content in logs.items():(HERE/name).write_text(content)
        for name,value in artifacts.items():dump(HERE/name,value)
        dump(HERE/'evidence.json',evidence)
        # Capture every imported project module, including fixture dependencies.
        for module in tuple(sys.modules.values()):
            filename=getattr(module,'__file__',None)
            if not filename:continue
            path=Path(filename).resolve()
            if path.suffix=='.py' and path.is_relative_to(ROOT):locks[str(path.relative_to(ROOT))]=sha(path)
        for name in ['docs/plans/accounting-populated-source-contracts-20261025.md',
                     *[str((HERE/n).relative_to(ROOT)) for n in ['verify.py','audit.md','examples.py','evidence.json',*logs,*artifacts]]]:
            locks[name]=sha(ROOT/name)
        dump(HERE/'source-lock.json',dict(sorted(locks.items())))
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        dump(HERE/'run-manifest.json',{'git_commit':head,'worktree':'Uncommitted work present; source-lock.json identifies executed bytes',
             'command':'python3 -B data/accounting-master/populated-source-contracts-20261025/verify.py --record',
             'environment':sys.version,'platform':platform.platform(),
             'cpu_gpu':'CPU deterministic Python; no GPU framework imported','seeds':'N/A: deterministic',
             'data_version':'Constructed source documents retained in four case artifacts; not actual invoices',
             'wall_seconds':time.monotonic()-started,
             'plan':'docs/plans/accounting-populated-source-contracts-20261025.md',
             'result':str((HERE/'result.md').relative_to(ROOT)),
             'artifact_hashes':{name:sha(HERE/name) for name in ['source-lock.json','evidence.json',*artifacts,*logs]}})
    else:
        ensure(evidence==json.loads((HERE/'evidence.json').read_text()),'evidence differs')
        for name,value in artifacts.items():ensure(value==json.loads((HERE/name).read_text()),'case differs: '+name)
        manifest=json.loads((HERE/'run-manifest.json').read_text())
        for name,expected in manifest['artifact_hashes'].items():ensure(sha(HERE/name)==expected,'manifest artifact changed: '+name)
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay',
          'focused':tests[0]['count'],'regressions':sum(t['count'] for t in tests[1:]),
          'cases':len(cases),'locked_files':len(locks) if record else len(json.loads((HERE/'source-lock.json').read_text()))}))


if __name__=='__main__':run()
