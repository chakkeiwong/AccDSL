"""Independent retained-row comparisons and adversarial readiness checks."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json, os, platform, subprocess, sys, time
os.environ['CUDA_VISIBLE_DEVICES']='-1'
sys.dont_write_bytecode=True
from readiness import (HERE,ROOT,PACKET,PACKET_SHA,GROUPS,TARGETS,OPS,COMPOSED,
                       canonical,fixture,evaluate,verify_result,schema,record)
from requirements import REQUIREMENTS
PLAN='docs/plans/accounting-real-company-input-readiness-20261024.md'

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def conformance():
    checks=[]
    def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError,TypeError,jsonschema.ValidationError):check(name,True)
        else:check(name,False)
    import jsonschema
    packet=json.loads(PACKET.read_text())
    locks={str(PACKET.relative_to(ROOT)):PACKET_SHA}
    parent=PACKET.parent
    old=json.loads((parent/'run-manifest.json').read_text())
    for entry in old['artifacts']+old['source_blobs']:
        name=entry['path'];h=entry['sha256']
        if name in locks:check('consistent_source_lock:'+name,locks[name]==h)
        locks[name]=h
    for name in [PLAN,str((parent/'run-manifest.json').relative_to(ROOT)),
        'data/accounting-master/company-inputs-20261023/authoring.py',
        'data/accounting-master/company-composed-profile-20261024/schema.json',
        'data/accounting-master/company-composed-profile-20261024/manifest.json',
        'data/accounting-master/language-coverage-refresh-20261024/inventory.json']:
        locks[name]=sha(ROOT/name)
    for p in TARGETS.values():locks[str(p.relative_to(ROOT))]=sha(p)
    for name,h in locks.items():check('source_hash:'+name,sha(ROOT/name)==h)
    check('packet_hash',sha(PACKET)==PACKET_SHA)
    for h,r in packet['record_registry'].items():
        check('record_hash:'+r['key'],sha256(('accdsl.portable.v1/'+r['schema']).encode()+b'\0'+canonical(r)).hexdigest()==h)
    body=lambda key:packet['record_registry'][packet['aliases'][key]['digest']]['body']
    base=body('apple.reported-statements');pkg=body('apple.package')
    request=fixture();result=evaluate(request)
    cases={OPS:result,COMPOSED:evaluate(fixture(COMPOSED))}
    check('inventory_count',len(result['preserved_package']['inventory'])==139)
    for i,ref in enumerate(pkg['inventory_refs']):
        check('inventory_exact:'+str(i),result['preserved_package']['inventory'][i]=={'ref':ref,'record':packet['record_registry'][ref['digest']]})
    check('all_original_groups',result['preserved_package']['original_statement_collections']=={k:base[k] for k in GROUPS})
    for k,n in zip(GROUPS,[102,100,27,27]):check('original_count:'+k,len(base[k])==n)
    for group,source_key in [('annual_refs','annual-readings'),('interim_refs','interim-readings')]:
        rows=json.loads((ROOT/packet['source_inputs'][source_key]).read_text())['rows']
        indexed={r['id']:r for r in rows}
        for o in result['known_evidence'][group]:
            b=o['record']['body'];r=indexed[b['row_id']];v=b['value']
            check('reading_identity:'+group+':'+b['row_id'],b['literal']==r['literal'] and b['precision']==r['precision'])
            expected={'issuer':'Apple','perimeter':r['entity'],'basis':r['basis'],
                'period':r['period'],'unit':r['unit'],'measurement_kind':r['measurement_kind']}
            check('reading_context:'+group+':'+b['row_id'],o['context']==expected)
            if v['tag']=='known_displayed':
                check('reading_amount:'+group+':'+b['row_id'],Fraction(int(v['amount']['n']),int(v['amount']['d']))==Fraction(r['value']))
            else:check('literal_dash:'+group+':'+b['row_id'],v=={'tag':'reported_dash','literal':r['literal']} and r['value'] is None)
    for group,alias,piece in [('annual_opening_refs','annual-readings','opening'),('interim_comparison_refs','interim-readings','comparison')]:
        rows=json.loads((ROOT/packet['source_inputs'][alias]).read_text())['rows']
        by_id={r['id']:r for r in rows}
        for o in result['known_evidence'][group]:
            b=o['record']['body'];r=by_id[b['row_id']];p=r[piece]
            check('comparison_literal:'+group+':'+b['row_id'],b['literal']==p['literal'])
            check('comparison_amount:'+group+':'+b['row_id'],Fraction(**{})==0 if False else Fraction(int(b['value']['amount']['n']),int(b['value']['amount']['d']))==Fraction(p['value']))
    available_ids={o['record']['body']['row_id'] for g in GROUPS for o in result['known_evidence'][g]}
    check('catalog_caption_ids',all(set(r['row_ids'])<=available_ids for r in REQUIREMENTS))
    check('catalog_unique',len({r['id'] for r in REQUIREMENTS})==len(REQUIREMENTS))
    sys.path.insert(0,str(HERE.parent/'company-operations-20261023'))
    import operations
    target_fields={OPS:set(operations.schema()['required']),COMPOSED:set(json.loads((HERE.parent/'company-composed-profile-20261024/schema.json').read_text())['required'])}
    for target,r in cases.items():
        check('target_fields:'+target,{f for d in r['dependencies'] for f in d['target_fields']}==target_fields[target])
        check('no_execution:'+target,r['status']=='blocked' and r['executable_opening'] is None and r['executed'] is False)
        check('independent_blockers:'+target,bool(r['unavailable_required_state']) and bool(r['unsupported_target_scope']))
        check('family_unresolved:'+target,r['preserved_package']['family']['body']==body('apple.family'))
        check('conditional_results_preserved:'+target,r['preserved_package']['connected_result']['body']==body('apple.connected'))
        for dep in r['dependencies']:
            check('dependency_has_evidence_or_reason:'+target+':'+dep['id'],bool(dep['evidence_refs'] or dep['obligation_refs']))
            check('dependency_next_and_consequences:'+target+':'+dep['id'],bool(dep['next'] and dep['affects']))
    for view,counts in [('annual',[102,0,27,0]),('interim',[0,100,0,27]),('combined',[102,100,27,27])]:
        r=evaluate(fixture(view=view));check('view_counts:'+view,[len(r['known_evidence'][g]) for g in GROUPS]==counts)
        permitted={x['digest'] for x in body('view.'+view)['source_refs']}
        check('view_sources:'+view,all(o['record']['body']['source_ref']['digest'] in permitted for g in GROUPS for o in r['known_evidence'][g]))
    check('annual_term_captions',result['conditional_derivations'][0]['amount']=={'n':'96662','d':'1'})
    check('interim_term_captions',result['conditional_derivations'][1]['amount']=={'n':'94804','d':'1'})
    for key,change in [
        ('issuer',lambda q:q.update(issuer='JPMorgan')),
        ('unknown_target',lambda q:q.update(target='WholeCompany/1')),
        ('later_view',lambda q:q.update(view_ref=packet['aliases']['view.later'])),
        ('foreign_package',lambda q:q.update(package_ref=packet['aliases']['jpmorgan.source'])),
        ('asof',lambda q:q.update(information_mode='historical_asof')),
        ('packet_hash',lambda q:q.update(packet_sha256='0'*64)),
        ('target_hash',lambda q:q.update(target_implementation_sha256='0'*64)),
        ('false_zero',lambda q:q.update(opening_balances={'cash':0})),
        ('calendar_relabel',lambda q:q.update(period={'start':'2025-01-01','end':'2026-01-01'}))]:
        q=deepcopy(request);change(q);reject('request_reject:'+key,lambda:evaluate(q))
    reject('packet_bytes_changed',lambda:evaluate(request,PACKET.read_bytes()+b' '))
    assumption={'id':'proposed-1','requirement_id':'inventory','statement':'Assume one homogeneous inventory pool.',
        'provenance':'Adversarial check only; not a company fact.','disposition':'proposed_not_admitted'}
    q=deepcopy(request);q['assumptions']=[assumption];r=evaluate(q)
    check('assumption_separate',r['explicit_assumptions']==[assumption] and r['known_evidence']==result['known_evidence'])
    check('assumption_not_resolution',r['unavailable_required_state']==result['unavailable_required_state'] and r['unsupported_target_scope']==result['unsupported_target_scope'])
    q['assumptions']*=2;reject('duplicate_assumption',lambda:evaluate(q))
    for field,value in [('status','ready'),('executable_opening',{'cash':0}),('executed',True),('unavailable_required_state',[]),('unsupported_target_scope',[])]:
        bad=deepcopy(result);bad[field]=value;check('forged_result:'+field,not verify_result(request,bad))
    for label,mutate in [
        ('legal_relabel',lambda r:r['known_evidence']['annual_refs'][0]['context'].update(perimeter='Apple legal book')),
        ('date_relabel',lambda r:r['known_evidence']['annual_refs'][0]['context'].update(period='2024-01-01 through 2024-12-31')),
        ('false_zero',lambda r:r['known_evidence']['annual_refs'][0]['record']['body'].update(value={'tag':'known_displayed','amount':{'n':'0','d':'1'}})),
        ('dependency_omission',lambda r:r['dependencies'].pop()),
        ('dependency_repair',lambda r:r['dependencies'][0].update(unavailable_state=None)),
        ('inventory_omission',lambda r:r['preserved_package']['inventory'].pop()),
        ('later_leak',lambda r:r['known_evidence']['annual_refs'][0].update(ref=packet['aliases']['view.later']))]:
        bad=deepcopy(result);mutate(bad);check('mutation_reject:'+label,not verify_result(request,bad))
    bad=deepcopy(result)
    dash=next(o for o in bad['known_evidence']['annual_refs'] if o['record']['body']['row_id']=='cash_flow.debt_issuance')
    dash['record']['body']['value']={'tag':'known_displayed','amount':{'n':'0','d':'1'}}
    check('dash_coercion_rejected',not verify_result(request,bad))
    check('exact_result_accepted',verify_result(request,result))
    return {'passed':all(c['passed'] for c in checks),'checks':checks},cases,locks

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check'
    assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'record already exists'
    start=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
    if mode=='--replay':
        old=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in old[group].items():assert sha(ROOT/name)==h,name
    checks,cases,locks=conformance()
    obs={'mode':mode,'passed':checks['passed'],'checks':len(checks['checks']),
        'failures':[c['name'] for c in checks['checks'] if not c['passed']],
        'protected_files':len(locks),'wall_seconds':time.monotonic()-clock}
    if not checks['passed']:dump(HERE/('failed-checks-'+str(time.time_ns())+'.json'),checks)
    elif mode=='--record':
        for name,data in [('checks.json',checks),('readiness.json',cases),('request-schema.json',schema()),('source-lock.json',locks)]:dump(HERE/name,data)
        outputs={str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','readiness.json','request-schema.json','source-lock.json']}
        dump(HERE/'manifest.json',{'started_utc':start,'wall_seconds':obs['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version(),'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1',
            'random_seeds':'N/A: deterministic reference checks','inputs':locks,
            'data_version':PACKET_SHA,'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),
            'implementation':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},'outputs':outputs})
    elif mode=='--replay':
        assert checks==json.loads((HERE/'checks.json').read_text())
        assert cases==json.loads((HERE/'readiness.json').read_text())
    print(json.dumps(obs));return 0 if checks['passed'] else 1
if __name__=='__main__':sys.exit(main())
