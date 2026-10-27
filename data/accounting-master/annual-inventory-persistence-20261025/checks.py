from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json, tempfile
from examples import m, requests, inventory
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]

def conformance():
    checks=[];cases=[]
    def check(name,value):checks.append({'name':name,'passed':bool(value)})
    lock=json.loads((HERE/'source-lock.json').read_text())
    for name,h in lock.items():check('protected:'+name,sha256((ROOT/name).read_bytes()).hexdigest()==h)
    tests=json.loads((HERE/'test-observation.json').read_text());check('tests_pass',tests['exit_code']==0)
    for name,h in tests['files'].items():check('tested_bytes:'+name,sha256((ROOT/name).read_bytes()).hexdigest()==h)
    with tempfile.TemporaryDirectory(prefix='accdsl-store-conformance-',dir='/tmp') as tmp:
        for row in requests():
            name=row['case'];q=row['request'];before=m.canonical(q);expected=m.runtime.run(q);path=Path(tmp)/(name+'.sqlite');snapshots=[]
            with m.Store(path,q) as store:
                initial=store.inspect();check(name+':initial_cursor',initial['cursor']==0)
                check(name+':zero_budget',store.advance(0,expected_cursor=0)==initial)
            cursor=0
            while True:
                with m.Store(path,q) as store:
                    previous=store.inspect()
                    if store.current['status']!='paused_provisional':final=previous;break
                    result=store.advance(1,expected_cursor=cursor);snapshots.append(result)
                    check(name+':attempt'+str(cursor)+':increment',result['cursor']==cursor+1)
                    check(name+':attempt'+str(cursor)+':retry',store.advance(1,expected_cursor=cursor)==result)
                    check(name+':attempt'+str(cursor)+':prefix',result['result']==m.prefix_result(q,cursor+1))
                    book=result['result'].get('period_book')
                    if book:
                        check(name+':attempt'+str(cursor)+':26_accounts',len(book['after']['balances'])==26)
                        check(name+':attempt'+str(cursor)+':balanced',set(result['result']['recorded_statements']['reconciliations'].values())=={'0/1'})
                    cursor=result['cursor']
            check(name+':complete_direct_equality',final['result']==expected)
            check(name+':input_unchanged',m.canonical(q)==before)
            with m.Store(path,q) as store:
                check(name+':terminal_idempotence',store.advance(20,expected_cursor=cursor)==final)
                records=[{'seq':a,'result':json.loads(b),'result_sha256':c,'previous_sha256':h} for a,b,c,h in store.db.execute('SELECT seq,payload,result_sha256,previous_sha256 FROM checkpoints ORDER BY seq')]
                check(name+':record_count',len(records)==cursor+1)
            cases.append({'case':name,'request':q,'snapshots':snapshots,'records':records,'result':final})
        carry=next(c for c in cases if c['case']=='residual_carry_and_sale');final=carry['result']['result'];book=final['period_book']
        check('carry_cash_control',book['after']['balances']['cash']=='482/1')
        check('carry_tax_payable_control',book['after']['balances']['income_tax_payable']=='-49/4')
        check('carry_residual_stock_archive',book['period_archive'][0]['after']['lots']['recovered']['units']=='1/1')
        check('carry_final_profit_control',final['recorded_statements']['recorded_profit']=='5/1')
        for case in cases:
            for key in ['annual_ready','source_admission','accounting_admission']:
                check(case['case']+':no_admission:'+key,case['result']['result'][key] is False)
    return checks,cases,tests,lock
