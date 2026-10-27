"""Text authoring versus sealed typed requests and full financial outcomes."""
from hashlib import sha256
from pathlib import Path
import importlib.util,json,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
import company_function_text_v1 as frontend

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def compare():
    prior=json.loads((HERE.parent/'company-functions-20261025/comparison.json').read_text())
    baseline_dir=HERE.parent/'company-expressions-20261023';sys.path.insert(0,str(baseline_dir))
    baseline=load('function_text_policy_comparator',baseline_dir/'verify.py')
    path,policy,_,source,engine,generate=baseline.context()
    mapping={'fraction':'fraction','installment_shares':['first_share','second_share']}
    checks=[];cases={}
    def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
    for name,case in prior['cases'].items():
        text=frontend.render(case['request']);parsed=frontend.lower(text)
        check(name+':request',parsed['request']==case['request'])
        check(name+':compilation',parsed['compilation']==case['compilation'])
        check(name+':canonical_render',frontend.render(parsed['request'])==text)
        check(name+':source_hash',parsed['source_sha256']==sha256(text.encode()).hexdigest())
        offset=0;spans=iter(parsed['declarations']);observed=0
        for number,line in enumerate(text.encode().splitlines(keepends=True),1):
            content=line.removesuffix(b'\n').removesuffix(b'\r');trimmed=content.strip(b' \t')
            if trimmed:
                span=next(spans);observed+=1;start=offset+content.index(trimmed)
                check(name+':span:'+str(number),(span['byte_start'],span['byte_end'],span['line'])==(start,start+len(trimmed),number)
                      and span['slice_sha256']==sha256(trimmed).hexdigest())
            offset+=len(line)
        check(name+':all_declarations',observed==len(parsed['declarations']))
        materialized=baseline.materialize(parsed['compilation']['graph'],path,policy,mapping,generate)
        check(name+':complete_materialization',materialized==case['materialization'])
        if name in prior['financial_results']:
            result=engine.wire(engine.execute(materialized['materialization']['path'],source))
            check(name+':full_financial_result',result==prior['financial_results'][name])
            check(name+':all_years_populated',len(result['years'])==3 and all(y.get('report',{}).get('lines') for y in result['years']))
        else:check(name+':no_invented_financial_result','materialization' not in materialized)
        check(name+':admission_false',all(parsed[k] is False for k in frontend.functions.FLAGS))
        cases[name]={'source':text,'parsed':parsed,'materialization':materialized}
    return {'passed':all(c['passed'] for c in checks),'checks':checks,'cases':cases}

if __name__=='__main__':
    r=compare();print(json.dumps({'passed':r['passed'],'checks':len(r['checks']),'cases':len(r['cases']),
                               'failed':[c['name'] for c in r['checks'] if not c['passed']]}));raise SystemExit(not r['passed'])
