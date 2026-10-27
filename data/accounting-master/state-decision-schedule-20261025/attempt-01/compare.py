from copy import deepcopy
from examples import scheduler as m, start, root, decision_examples

def compare():
    checks=[];cases={};state=start()
    def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
    body=root(state);result=m.run(state,body);manual=deepcopy(state);requests=[];outcomes=[]
    for index,date in enumerate(['2027-01-02','2027-01-03','2027-01-04']):
        token=m.digest(['stock-calendar','daily-sale',index])
        request=decision_examples.request(manual,'scheduled-decision:'+token,date,demand='1/1')
        request['event']['id']='scheduled-event:'+token
        proposal=m.decision.propose(manual,request);outcome=m.decision.apply(manual,request,proposal)
        requests.append(request);outcomes.append(outcome);manual=outcome['after']
    sequence=m.decision.run_sequence(state,requests)
    for index,(request,outcome) in enumerate(zip(requests,outcomes)):
        check('manual_request:'+str(index),result['trace'][index]['request']==request)
        check('manual_outcome:'+str(index),result['trace'][index]['result']==outcome)
    for key in ['after','decision_cursor','fiscal_complete','recorded_statements']:
        check('complete_sequence:'+key,result[key]==sequence[key])
    for key,value in sequence['recorded_statements'].items():check('statement:'+key,result['recorded_statements'][key]==value)
    for key,value in {'cash':'949/2','inventory':'5/1'}.items():check('independent_balance:'+key,result['after']['after']['balances'][key]==value)
    for key,value in {'units':'1/2','carrying':'5/1','tax_base':'5/1'}.items():check('independent_lot:'+key,result['after']['after']['lots']['recovered'][key]==value)
    cases['recurring']={'request':body,'result':result,'manual_requests':requests,'manual_result':sequence}
    explicit=root(state,'explicit_dates');other=m.run(state,explicit)
    for key in ['calendar','trace','after','recorded_statements','decision_cursor']:check('explicit_recurring:'+key,result[key]==other[key])
    cases['explicit']={'request':explicit,'result':other}
    body=root(state,enabled=False);body['schedules'][0]['template']['bindings']['price']['available_on']='unknown';out=m.run(state,body)
    check('no_action:state',out['after']==state);check('no_action:cursor',out['decision_cursor']=='2027-01-04')
    cases['no_action']={'request':body,'result':out}
    body=root(state);body['schedules'][0]['template']['bindings']['reserve']['value']='0/1';out=m.run(state,body)
    check('depleted:cash',out['after']['after']['balances']['cash']=='482/1');check('depleted:carrying',out['after']['after']['lots']['recovered']['carrying']=='0/1')
    check('depleted:disposed',out['after']['after']['lots']['recovered']['disposed'] is True)
    cases['depleted']={'request':body,'result':out}
    body=root(state);body['schedules'][0]['calendar']={'kind':'explicit_dates','dates':['2027-01-02']}
    extra=deepcopy(body['schedules'][0]);extra['id']='missing';extra['calendar']['dates']=['2027-01-03','2027-01-04']
    extra['template']['event']['findings']['homogeneous_units']={'status':'unknown','reason':'Not supplied'};body['schedules'].append(extra)
    out=m.run(state,body)
    check('refusal:prefix',len(out['trace'])==1 and out['after']==out['trace'][0]['result']['after'])
    check('refusal:status',out['stop']['outcome']['status']=='unresolved')
    check('refusal:pending',out['remaining_occurrences']==out['calendar'][1:])
    check('refusal:current_hash',out['stop']['request']['expected_state_sha256']==m.digest(out['after']))
    check('refusal:proposal',out['stop']['outcome']['decision']['status']=='proposed')
    cases['refusal']={'request':body,'result':out}
    for name,case in cases.items():
        check(name+':flags',all(case['result'][key] is False for key in m.FLAGS))
        check(name+':not_fiscal_complete',case['result']['fiscal_complete'] is False)
    return {'opening':state,'checks':checks,'cases':cases}
