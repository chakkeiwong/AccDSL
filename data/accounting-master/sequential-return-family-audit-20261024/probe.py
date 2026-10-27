"""Two exact native paths diagnose intermediate-witness substitution."""
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import json,sys,os,time,platform,subprocess
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import conditional_return_state_family_v2 as family
from test_typed_return_transition_v1 import fixtures,raw_args
SOURCE=ROOT/'data/accounting-master/conditional-return-state-family-20261024-r2/cases.json'

def run():
    row=next(r for r in json.loads(SOURCE.read_text()) if r['case']=='uncertain_settlement_two_states')
    d,budget,result=row['request'],row['budget'],row['result']
    checks=[]
    def check(n,v):checks.append({'name':n,'passed':bool(v)})
    check('saved_native_family_replay',family.verify_result(d,budget,result))
    _,_,original_sale=next(x for x in fixtures.selected_cases() if x[2]['kind']=='sell')
    sale=deepcopy(original_sale);sale['date']=d['event']['date'];sale['lot_id']=d['event']['lot_id']
    paths=[]
    for branch in result['branches']:
        if branch['status']!='feasible':continue
        first=branch['replay'];middle=first['after']
        proposed=family.native.propose(*raw_args(middle,sale))
        check('native_sale_proposed_'+str(branch['index']),proposed['status']=='proposed')
        after,journal,flows=family.native.structure.native.transition(middle,sale)
        p=proposed['proposal'];check('both_originals_agree_'+str(branch['index']),
            (p['after'],p['journal'],p['flows'])==(after,journal,flows))
        combined={k:family.native.monetary.fmt(Q(first['journal'][k])+Q(journal[k])) for k in journal}
        check('complete_balance_rollforward_'+str(branch['index']),all(Q(d['state']['balances'][k])+Q(combined[k])==Q(after['balances'][k]) for k in combined))
        paths.append({'branch':branch['index'],'settlement_event':first['candidate_event'],'sale_event':sale,
            'middle':middle,'after':after,'settlement_journal':first['journal'],'sale_journal':journal,
            'combined_journal':combined,'middle_profit':family.native.monetary.fmt(family.native.structure.native.profit(middle['balances'])),
            'terminal_profit':family.native.monetary.fmt(family.native.structure.native.profit(after['balances']))})
    check('both_minimum_paths_retained',len(paths)==2)
    check('middle_inventory_differs',paths[0]['middle']['balances']['inventory']!=paths[1]['middle']['balances']['inventory'])
    check('middle_profit_differs',paths[0]['middle_profit']!=paths[1]['middle_profit'])
    check('same_terminal_balances',paths[0]['after']['balances']==paths[1]['after']['balances'])
    check('same_terminal_profit',paths[0]['terminal_profit']==paths[1]['terminal_profit'])
    selected=[p['branch'] for p in paths if p['middle']['balances']['inventory']=='65/1']
    check('intermediate_observation_selects_nonfirst_path',selected==[1])
    check('first_witness_would_lose_feasible_path',paths[0]['middle']['balances']['inventory']!='65/1')
    check('same_terminal_complete_state',paths[0]['after']==paths[1]['after'])
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'paths':paths,
            'intermediate_inventory_observation':'65/1','matching_branches':selected,
            'scope':'two exact witnesses diagnose dependence; not a complete sequential family'}

def main():
    mode=sys.argv[1] if len(sys.argv)>1 else '--check';assert mode in ['--check','--record','--replay']
    started=time.monotonic();r=run();assert r['passed'],[x for x in r['checks'] if not x['passed']]
    names=[str(SOURCE.relative_to(ROOT)),'scripts/conditional_return_state_family_v2.py',
        'scripts/typed_return_transition_v1.py','scripts/prerequisite_method_family_v1.py',
        'data/accounting-master/company-return-execution-20261024/native_returns.py',
        'tests/test_typed_return_transition_v1.py','data/accounting-master/typed-monetary-effects-20261024/examples.py',
        'docs/plans/accounting-sequential-return-family-audit-20261024.md']
    lock={n:sha256((ROOT/n).read_bytes()).hexdigest() for n in names}
    if mode=='--record':
        assert not (HERE/'audit.json').exists();(HERE/'audit.json').write_text(json.dumps(r,indent=2)+'\n')
        m={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
           'command':'python3 -B '+str(HERE.relative_to(ROOT)/'probe.py')+' --record',
           'environment':platform.python_version()+'; Z3 '+family.z3.get_version_string(),
           'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: exact deterministic probes',
           'wall_seconds':time.monotonic()-started,'data_version':lock,
           'plan':'docs/plans/accounting-sequential-return-family-audit-20261024.md','result':str(HERE.relative_to(ROOT)/'result.md'),
           'output':{n:sha256((HERE/n).read_bytes()).hexdigest() for n in ['audit.json','probe.py']}}
        (HERE/'probe-manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    if mode=='--replay':
        m=json.loads((HERE/'probe-manifest.json').read_text());assert m['data_version']==lock
        for n,digest in m['output'].items():assert sha256((HERE/n).read_bytes()).hexdigest()==digest
        assert r==json.loads((HERE/'audit.json').read_text())
    print(json.dumps({'passed':True,'checks':len(r['checks']),'protected_sources':len(lock),'mode':mode,
        'middle_profit':[p['middle_profit'] for p in r['paths']],'terminal_profit':[p['terminal_profit'] for p in r['paths']]}))
if __name__=='__main__':main()
