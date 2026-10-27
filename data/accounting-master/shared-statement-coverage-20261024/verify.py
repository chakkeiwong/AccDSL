"""Additive coverage review, exact identity preservation and source integrity."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,os,platform,subprocess,sys,time
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
from decisions import UPDATES,EVIDENCE
BASE=HERE.parent/'shared-book-coverage-20261024/inventory.json'
NEXT='docs/plans/accounting-shared-book-authoring-20261024.md'
def sha(p):return sha256(p.read_bytes()).hexdigest()
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def conformance():
    previous=json.loads(BASE.read_text());locks={str(BASE.relative_to(ROOT)):sha(BASE)};evidence={};checks=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    for key,package in EVIDENCE.items():
        folder=HERE.parent/package;manifest=folder/('run-manifest.json' if key in ['manuscript'] else 'manifest.json')
        m=json.loads(manifest.read_text());refs=[folder/'result.md',manifest]
        for n in ['design.md','checks.json','verification.json']:
            if (folder/n).exists():refs.append(folder/n)
        selected={}
        if key == 'manuscript':
            selected.update(m['output_artifacts'])
        else:
            for name,h in m.get('package_sha256',{}).items():
                selected[str((folder/name).relative_to(ROOT))]=h
            for group in ['files','implementation','outputs']:
                for name,h in m.get(group,{}).items():
                    if isinstance(h,str) and len(h)==64:selected[name]=h
        for p in refs:selected[str(p.relative_to(ROOT))]=sha(p)
        for name,h in selected.items():
            if name in locks:check('consistent_lock:'+name,locks[name]==h)
            locks[name]=h
        evidence[key]={'package':str(folder.relative_to(ROOT)),'result':str((folder/'result.md').relative_to(ROOT)),
            'manifest':str(manifest.relative_to(ROOT)),'checked_current_files':len(selected),
            'scope':'Current retained bytes and recorded result inspected; no fresh full prior-method execution'}
    for name in ['docs/plans/accounting-shared-statement-coverage-20261024.md',NEXT,
        'docs/design/proposal/architecture/history-families-contract-v1.md',
        'scripts/conditional_history_family_v1.py','scripts/typed_affine_history_v1.py',
        'scripts/rational_solver_v1.py','scripts/sequential_return_state_family_v1.py',
        'scripts/conditional_return_state_family_v2.py',
        'data/accounting-master/extended-method-exchanges-20261015/corporate-residuals/semantic-contract.md',
        'data/accounting-master/extended-method-exchanges-20261015/corporate-residuals/financial_checks.py',
        'data/accounting-master/extended-method-exchanges-20261015/corporate-residuals/authored_cases.py',
        'data/accounting-master/company-module-boundary-20261023/boundary.py',
        'scripts/company_persistence_v1.py','scripts/company_execution_v1.py','tests/test_accounting_p07.py',
        'data/accounting-master/company-return-execution-20261024/native_returns.py',
        'data/accounting-master/real-company-input-readiness-20261024/requirements.py',
        'data/accounting-master/source-constrained-state-20261024/design.md',
        'docs/design/research/actus-core-correspondence-20261023.md',
        'docs/design/proposal/manuscript-shared-statements-20261024/accounting-product-proposal.pdf',
        'data/financial-report-benchmark/documents/henkel/henkel-2025-annual/original.pdf',
        'data/financial-report-benchmark/documents/henkel/henkel-2025-annual/extracted-ba489941fc203f44fc470cd6488cc29cd06ccadb683f29861d895e4d012735bd.txt']:
        locks[name]=sha(ROOT/name)
    for name,h in locks.items():check('input_hash:'+name,sha(ROOT/name)==h)
    inventory={'date':'2026-10-24','candidate':'3.76','readiness':'not_ready','whole_rows_closed':0,
        'scope':'Additive documentary delta review; unchanged rows retained, no whole-manuscript or prior-method re-execution',
        'baseline':{'path':str(BASE.relative_to(ROOT)),'sha256':sha(BASE)},'evidence':evidence,
        'next_plan':NEXT,'unintegrated_composition':None}
    all_ids=set();changed={}
    for section,count in [('obligations',53),('interactions',6),('operations',46)]:
        rows=previous[section];ids=[r['id'] for r in rows]
        check(section+'_count_unique',len(rows)==count and len(set(ids))==count)
        inventory[section]=[];changed[section]=0
        for r in rows:
            key=r['id'];all_ids.add(key);delta=deepcopy(UPDATES.get(key))
            if delta is None:
                delta={'assessment':'prior_scope_retained_not_reaudited','advance':'No new method evidence attributed in this bounded review.',
                    'residual':deepcopy(r['update_20261024']['residual']),'next_action':'Continue the preserved row-specific next work when its dependencies are ready.',
                    'evidence':[],'full_requirement_closed':False,'acceptance':'not_promoted'}
            else:delta['assessment']='scoped_advance_remaining_open';changed[section]+=1
            new={'id':key,'prior_entry':deepcopy(r),'update_20261024':delta,'full_requirement_closed':False}
            inventory[section].append(new)
            check(key+'_exact_prior_record',canonical(new['prior_entry'])==canonical(r))
            check(key+'_evidence_keys',set(delta['evidence'])<=set(evidence))
            check(key+'_no_full_closure',new['full_requirement_closed'] is False and delta['full_requirement_closed'] is False)
        check(section+'_identities',[r['id'] for r in inventory[section]]==ids)
    check('all_decision_ids_accounted',set(UPDATES)<=all_ids)
    check('new_next_plan_exists',(ROOT/NEXT).exists())
    inventory['protected_prior_metadata']={k:deepcopy(v) for k,v in previous.items() if k not in ['obligations','interactions','operations']}
    check('prior_metadata_exact',canonical(inventory['protected_prior_metadata'])==canonical({k:v for k,v in previous.items() if k not in ['obligations','interactions','operations']}))
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'updated_rows':changed,'source_files':len(locks)},inventory,locks
def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'record exists'
    start=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for g in ['inputs','implementation','outputs']:
            for n,h in m[g].items():assert sha(ROOT/n)==h,n
    result,inventory,locks=conformance();obs={'mode':mode,'passed':result['passed'],'checks':len(result['checks']),
        'failed':[c['name'] for c in result['checks'] if not c['passed']],'updated_rows':result['updated_rows'],
        'protected_files':len(locks),'wall_seconds':time.monotonic()-clock}
    if not result['passed']:dump(HERE/('failed-checks-'+str(time.time_ns())+'.json'),result)
    elif mode=='--record':
        for n,x in [('inventory.json',inventory),('checks.json',result),('source-lock.json',locks)]:dump(HERE/n,x)
        outputs={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['inventory.json','checks.json','source-lock.json']}
        dump(HERE/'manifest.json',{'started_utc':start,'wall_seconds':obs['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 '+str(HERE.relative_to(ROOT)/'verify.py')+' --record','environment':'Python '+platform.python_version(),
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic documentary validation',
            'inputs':locks,'implementation':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},
            'outputs':outputs,'plan':'docs/plans/accounting-shared-statement-coverage-20261024.md','result':str(HERE.relative_to(ROOT)/'result.md')})
    elif mode=='--replay':
        assert canonical(result)==canonical(json.loads((HERE/'checks.json').read_text()))
        assert canonical(inventory)==canonical(json.loads((HERE/'inventory.json').read_text()))
    print(json.dumps(obs));return 0 if result['passed'] else 1
if __name__=='__main__':sys.exit(main())
