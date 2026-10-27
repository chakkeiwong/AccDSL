"""Compare optional function authoring with the exact frozen company paths."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import company_functions_v1 as functions

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def compare():
    examples=load('pure_function_fixtures',HERE/'examples.py')
    baseline_dir=HERE.parent/'company-expressions-20261023'
    sys.path.insert(0,str(baseline_dir))
    baseline=load('frozen_expression_comparison',baseline_dir/'verify.py')
    path,policy,prior,source,engine,generate=baseline.context()
    manual=json.loads((baseline_dir/'fixture.json').read_text())
    mapping={'fraction':'fraction','installment_shares':['first_share','second_share']}
    checks=[];cases={};runs={}
    def check(name,condition):checks.append({'name':name,'passed':bool(condition)})
    variants=[('ordinary',True,'1/10','materialized_expression_policy'),
              ('stress',False,'1/10','materialized_expression_policy'),
              ('unused_unknown',False,'unknown','materialized_expression_policy'),
              ('unknown_guard','unknown','1/10','unresolved'),
              ('unknown_discount',True,'unknown','unresolved'),
              ('negative_fraction',True,'2/1','invalid')]
    for name,guard,discount,status in variants:
        request=examples.policy_program();request['inputs']['ordinary']['value']=guard;request['inputs']['discount']['value']=discount
        old=deepcopy(manual);old['inputs']=deepcopy(request['inputs'])
        before=deepcopy(request);compiled=functions.compile_program(request)
        joined=baseline.materialize(compiled['graph'],path,policy,mapping,generate)
        comparator=baseline.materialize(old,path,policy,mapping,generate)
        check(name+':status',joined['status']==comparator['status']==status)
        check(name+':evaluation_outputs',joined['evaluation']['outputs']==comparator['evaluation']['outputs'])
        check(name+':request_unchanged',before==request)
        check(name+':admission_false',all(joined[k] is False for k in functions.FLAGS))
        if status=='materialized_expression_policy':
            check(name+':exact_policy',joined['policy']==comparator['policy'])
            check(name+':exact_materialization',joined['materialization']==comparator['materialization'])
            result=engine.wire(engine.execute(joined['materialization']['path'],source))
            expected=engine.wire(engine.execute(comparator['materialization']['path'],source))
            check(name+':complete_financial_result',result==expected)
            check(name+':three_year_results_present',len(result['years'])==3 and all(y.get('report',{}).get('lines') for y in result['years']))
            runs[name]=result
            if name=='ordinary':
                check('ordinary:saved_policy',joined['policy']==policy)
                check('ordinary:saved_materialization',joined['materialization']==prior['materialization'])
                check('ordinary:saved_full_accounting',result==prior['generated_result'])
        else:
            check(name+':no_invented_path','materialization' not in joined)
        cases[name]={'request':request,'compilation':compiled,'materialization':joined}
    index=policy['year_index']
    original=runs['ordinary']['years'][index]['report']['lines']
    stress=runs['stress']['years'][index]['report']['lines']
    check('independent_cash_delta',Fraction(stress['cash']['value'])-Fraction(original['cash']['value'])==Fraction(-192,5))
    check('independent_receivables_delta',Fraction(stress['receivables']['value'])-Fraction(original['receivables']['value'])==Fraction(192,5))
    check('independent_profit_unchanged',stress['profit']==original['profit'])
    check('unused_unknown_same_finances',runs['unused_unknown']==runs['stress'])
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'cases':cases,'financial_results':runs}

if __name__=='__main__':
    result=compare()
    print(json.dumps({'passed':result['passed'],'checks':len(result['checks']),'cases':len(result['cases']),
                      'failed':[c['name'] for c in result['checks'] if not c['passed']]}))
    raise SystemExit(not result['passed'])
