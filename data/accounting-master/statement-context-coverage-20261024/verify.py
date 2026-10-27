"""Full statement evidence checks with independent retained-reading arithmetic."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from collections import Counter
import json,os,platform,subprocess,sys,time
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
from statement_context import (HERE,ROOT,RELATIONS,OPS,COMPOSED,prior,readiness,
    canonical,digest,schema,fixture,evaluate,verify_result,context_check)
from statement_text import render,lower
sha=prior.sha
PLAN='docs/plans/accounting-statement-context-coverage-20261024.md'
def dump(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')

def conformance():
    checks=[]
    def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
    def reject(name,fn):
        try:fn()
        except Exception:check(name,True)
        else:check(name,False)
    locks={};m=json.loads((RELATIONS/'manifest.json').read_text())
    for group in ['inputs','implementation','outputs']:locks.update(m[group])
    for p in [RELATIONS/'manifest.json',ROOT/PLAN,
        HERE.parent/'apple-statement-network-20261013/build_network.py',
        HERE.parent/'apple-interim-network-20261013/build_network.py']:
        locks[str(p.relative_to(ROOT))]=sha(p)
    for name,h in locks.items():check('protected:'+name,sha(ROOT/name)==h)
    requests={};outputs={}
    expected_counts={'annual':(129,69,2),'interim':(127,74,5),'combined':(256,143,2)}
    for target in [OPS,COMPOSED]:
        for view,(no,nr,nu) in expected_counts.items():
            key=target+':'+view;b=fixture(target,view);r=evaluate(b)
            requests[key]=b;outputs[key]=r
            check('matched_text:'+key,lower(render(b))==b)
            check('matched_result:'+key,evaluate(lower(render(b)))==r)
            check('counts:'+key,len(r['observations'])==no and len(r['relations'])==nr)
            check('unresolved:'+key,sum(x['arithmetic']['status']=='unresolved' for x in r['relations'])==nu)
            check('no_execution:'+key,r['executable_opening'] is None and not r['executed'] and r['actual_history']=='unknown' and r['joint_latent_feasibility']=='uncomputed')
            check('all_requirements:'+key,[x['id'] for x in r['requirements']]==b['requirement_ids'])
    b=requests[OPS+':combined'];r=outputs[OPS+':combined']
    values={};raw_rows={};p=readiness.load_packet()
    for group in ['annual','interim']:
        rows=json.loads((ROOT/p['source_inputs'][group+'-readings']).read_text())['rows']
        for row in rows:
            alias=group+'.'+row['id'];values[alias]=None if row['value'] is None else Q(row['value']);raw_rows[alias]=row
            if row['id'].startswith('balance.'):
                old=row['opening' if group=='annual' else 'comparison'];alias=group+'.opening.'+row['id'].split('.',1)[1]
                values[alias]=None if old['value'] is None else Q(old['value']);raw_rows[alias]=old
        original=prior.load_ledger(group)
        check('full_ledger:'+group,r['preserved_ledgers'][group]==original)
        compared=[x['original_record'] for x in r['relations'] if x['id'].startswith(group+'.')]
        check('full_order:'+group,compared==original['relations'])
    for alias,o in r['observations'].items():
        source=raw_rows[alias];v=o['observation']['record']['body']['value'];d=o['declaration']
        check('literal:'+alias,o['observation']['record']['body']['literal']==source['literal'])
        check('pointed_source:'+alias,o['measurement_time_source']==source)
        if values[alias] is None:check('dash:'+alias,v['tag']=='reported_dash')
        else:check('value:'+alias,Q(int(v['amount']['n']),int(v['amount']['d']))==values[alias])
        if d['measurement_time']['kind']=='instant':check('instant:'+alias,d['measurement_time']['at']==source.get('measurement_date',source.get('date',source.get('period'))))
    outcomes={x['id']:x for x in r['relations']}
    for rr in b['relations']:
        out=outcomes[rr['id']];terms=rr['lhs']+rr['rhs'];missing=[t['alias'] for t in terms if values.get(t['alias']) is None]
        if missing:check('independent_unresolved:'+rr['id'],out['arithmetic']['status']=='unresolved');continue
        lhs=sum((Q(t['coefficient'])*values[t['alias']] for t in rr['lhs']),Q(0))
        rhs=sum((Q(t['coefficient'])*values[t['alias']] for t in rr['rhs']),Q(0))
        if rr['comparison']=='derived_only':
            check('derived_subtotal:'+rr['id'],Q(out['arithmetic']['subtotal']['value'])==lhs and out['arithmetic']['independent_residual'] is None)
        else:check('independent_residual:'+rr['id'],Q(out['arithmetic']['residual'])==lhs-rhs)
    check('all_relation_statuses',Counter(x['arithmetic']['status'] for x in r['relations'])=={'displayed_difference':135,'unresolved':2,'derived_subtotal':6})
    check('dash_specific',sorted(x['id'] for x in r['relations'] if x['arithmetic']['status']=='unresolved')==['annual.diagnostic:term_debt','annual.financing_cash'])
    for group,v in [('annual','-5196/1'),('interim','9808/1')]:
        ar=outcomes[group+'.balance_changes']['arithmetic'];check('endpoint_difference:'+group,ar['lhs']['value']==v and ar['rhs']['value']==v and ar['residual']=='0/1')
    check('opening_cash_difference',outcomes['annual.diagnostic:opening_cash_population']['arithmetic']['residual']=='772/1')
    check('payable_difference',outcomes['annual.diagnostic:payables']['arithmetic']['residual']=='329/1')
    check('tax_cash_difference',outcomes['interim.diagnostic:tax_expense_cash']['arithmetic']['residual']=='-12397/1')
    check('zero_difference_not_identity',outcomes['annual.diagnostic:vendor_receivables']['arithmetic']['role']=='explanatory_only')
    check('six_role_corrections',sum('role_correction' in x for x in r['relations'])==6)
    check('five_omission_records',sum(bool(x['omitted_source_rows']) for x in r['relations'])==5)
    check('shares_separate',r['observations']['annual.operations.eps_basic']['declaration']['unit']=='USD per share')
    check('stock_time_not_reporting_period',r['observations']['annual.equity.opening']['declaration']['measurement_time']=={'kind':'instant','at':'2023-09-30'} and r['observations']['annual.equity.opening']['observation']['context']['period'].startswith('FY2024:'))
    # Check role rules directly, independently from exact source binding.
    observations=deepcopy(r['observations']);target=next(x for x in b['relations'] if x['id']=='annual.balance:current_assets')
    for field,value in [('unit','USD per share'),('perimeter','Apple legal'),('issuer','Other'),('basis','Other basis')]:
        bad=deepcopy(observations);bad['annual.balance.cash']['observation']['context'][field]=value
        reject('context_rule:'+field,lambda:context_check(target,bad))
    bad=deepcopy(observations);bad['annual.balance.cash']['declaration']['measurement_time']['at']='2024-09-27'
    reject('context_rule_date',lambda:context_check(target,bad))
    for label,mutate in [
        ('instant_to_period',lambda q:q['observations'][29].update(measurement_time={'kind':'period','start':'2023-10-01','end_exclusive':'2024-09-29'})),
        ('wrong_unit',lambda q:q['observations'][0].update(unit='USD per share')),
        ('drop_observation',lambda q:q['observations'].pop()),
        ('drop_relation',lambda q:q['relations'].pop()),
        ('drop_requirement',lambda q:q['requirement_ids'].pop()),
        ('changed_sign',lambda q:q['relations'][0]['lhs'][0].update(coefficient='-1/1')),
        ('alias_substitution',lambda q:q['relations'][0]['lhs'][0].update(alias='annual.operations.net_income')),
        ('false_identity_role',lambda q:next(x for x in q['relations'] if x['kind']=='derived_subtotal').update(kind='period_sum',comparison='zero')),
        ('lost_omission',lambda q:next(x for x in q['relations'] if x['omitted_source_rows']).update(omitted_source_rows=[])),
        ('multiline',lambda q:q.update(name='Apple\nother')),
        ('later_view',lambda q:q['source'].update(view='later'))]:
        bad=deepcopy(b);mutate(bad);reject('request_rejected:'+label,lambda:evaluate(bad))
    for label,mutate in [
        ('dash_zero',lambda q:q['observations']['annual.cash_flow.debt_issuance']['observation']['record']['body'].update(value={'tag':'known_displayed','amount':{'n':'0','d':'1'}})),
        ('derived_independence',lambda q:next(x for x in q['relations'] if x['kind']=='derived_subtotal')['arithmetic'].update(independent_residual='0/1')),
        ('dropped_source',lambda q:q['preserved_ledgers']['annual']['relations'].pop()),
        ('false_opening',lambda q:q.update(executable_opening={'cash':29943})),
        ('false_feasibility',lambda q:q.update(joint_latent_feasibility='feasible'))]:
        bad=deepcopy(r);mutate(bad);check('result_rejected:'+label,not verify_result(b,bad))
    unicode=deepcopy(b);unicode['name']='財務 Apple';check('unicode_roundtrip',lower(render(unicode))==unicode)
    for text in [render(b).replace('end_statement_context;',''),render(b)+'extra;',render(b).replace('source ','unknown ',1)]:reject('invalid_text:'+str(len(checks)),lambda:lower(text))
    check('honest_result',verify_result(b,r))
    return {'passed':all(c['passed'] for c in checks),'checks':checks},requests,outputs,locks

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'manifest.json').exists(),'already recorded'
    start=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
    if mode=='--replay':
        m=json.loads((HERE/'manifest.json').read_text())
        for group in ['inputs','implementation','outputs']:
            for name,h in m[group].items():assert sha(ROOT/name)==h,name
    checks,requests,outputs,locks=conformance()
    obs={'mode':mode,'passed':checks['passed'],'checks':len(checks['checks']),
        'failures':[c['name'] for c in checks['checks'] if not c['passed']],
        'protected_files':len(locks),'wall_seconds':time.monotonic()-clock}
    if not checks['passed']:dump(HERE/('failed-checks-'+str(time.time_ns())+'.json'),checks)
    elif mode=='--record':
        for n,x in [('checks.json',checks),('requests.json',requests),('statements.json',outputs),('schema.json',schema()),('source-lock.json',locks)]:dump(HERE/n,x)
        (HERE/'example.accdsl').write_text(render(requests[OPS+':combined']))
        dump(HERE/'manifest.json',{'started_utc':start,'wall_seconds':obs['wall_seconds'],
            'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'verify.py')+' --record',
            'environment':'Python '+platform.python_version(),'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1',
            'random_seeds':'N/A: deterministic source/context checks','data_version':sha(RELATIONS/'manifest.json'),
            'plan':PLAN,'result':str(HERE.relative_to(ROOT)/'result.md'),'inputs':locks,
            'implementation':{str(p.relative_to(ROOT)):sha(p) for p in HERE.iterdir() if p.suffix in ['.py','.md']},
            'outputs':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['checks.json','requests.json','statements.json','schema.json','source-lock.json','example.accdsl']}})
    elif mode=='--replay':
        assert checks==json.loads((HERE/'checks.json').read_text())
        assert requests==json.loads((HERE/'requests.json').read_text())
        assert outputs==json.loads((HERE/'statements.json').read_text())
    print(json.dumps(obs));return 0 if checks['passed'] else 1
if __name__=='__main__':sys.exit(main())
