from copy import deepcopy
from fractions import Fraction
from examples import timeline as m,start,root,scheduled

def manual_request(state,body):
    token=m.digest([body['id'],body['schedules'][0]['id'],0])
    template=deepcopy(body['schedules'][0]['template'])
    template['event'].update(id='scheduled-event:'+token,date='2027-01-02')
    return {'profile':m.decision.PROFILE,'id':'scheduled-decision:'+token,'expected_state_sha256':m.digest(state),
            'context':deepcopy(body['context']),'decision_date':'2027-01-02','scenario':deepcopy(body['scenario']),**template}

def compare():
    checks=[];cases={};state=start()
    def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
    for first,name,cash,inventory,lot,profit in [(True,'payment_first','463/1','70/1','10/1',5),(False,'decision_first','448/1','80/1','20/1',0)]:
        body=root(state,first);result=m.run(state,body);current=deepcopy(state);steps=[]
        for index,kind in enumerate(['native','decision'] if first else ['decision','native']):
            if kind=='native':
                step=m.runtime.transition(current,body['operations'][0]['operation'])
                check(name+':native_transition',step==result['trace'][index]['result']['transition'])
                current=step['after'];steps.append({'operation':body['operations'][0]['operation'],'result':step})
            else:
                request=manual_request(current,body);proposal=m.decision.propose(current,request)
                step=m.decision.apply(current,request,proposal)
                check(name+':decision_request',request==result['trace'][index]['request'])
                check(name+':decision_outcome',step==result['trace'][index]['result'])
                current=step['after'];steps.append({'request':request,'result':step})
        check(name+':complete_state',current==result['after'])
        report=m.runtime.annual.root.carry.statements(current['opening'],current['after'],current['account_classes'])
        for key,value in report.items():
            if key not in ['scope','unresolved']:check(name+':statement:'+key,result['recorded_statements'][key]==value)
        for key,value in {'cash':cash,'inventory':inventory,'income_tax_payable':'-25/4'}.items():check(name+':independent_balance:'+key,current['after']['balances'][key]==value)
        check(name+':independent_lot',current['after']['lots']['recovered']['carrying']==lot)
        check(name+':independent_vintages',[v['closing_payable'] for v in current['period_vintages']]==['5/4','5/1'])
        check(name+':historical_vintages_unchanged',current['historical_vintages']==state['historical_vintages'])
        journals=[x['result'].get('transition',{}).get('journal',{}) for x in result['trace']]
        check(name+':independent_profit',sum(-Fraction(x.get('revenue','0/1'))-Fraction(x.get('cogs','0/1')) for x in journals)==profit)
        check(name+':tax_expense_unchanged',all(x.get('current_tax','0/1')=='0/1' for x in journals))
        cases[name]={'request':body,'result':result,'manual_steps':steps,'manual_statements':report}
    for name,authorization,status in [('unknown_authorization',{'status':'unknown','reason':'Not supplied'},'unresolved'),('false_authorization',scheduled.decision_examples.native.previous.known(False),'unsupported')]:
        body=root(state);body['operations'][0]['operation']['event']['authorization']=authorization;result=m.run(state,body)
        check(name+':status',result['stop']['outcome']['status']==status);check(name+':unchanged',result['after']==state)
        check(name+':pending',result['remaining_actions']==result['calendar'])
        cases[name]={'request':body,'result':result}
    body=root(state);body['schedules'][0]['template']['bindings']['price']['available_on']='unknown';result=m.run(state,body)
    check('unknown_decision:prefix',len(result['trace'])==1 and result['after']['after']['balances']['cash']=='448/1')
    check('unknown_decision:status',result['stop']['outcome']['status']=='unresolved')
    check('unknown_decision:request_state',result['stop']['request']['expected_state_sha256']==m.digest(result['after']))
    cases['unknown_decision']={'request':body,'result':result}
    body=root(state);body['schedules']=[];operation=scheduled.decision_examples.native.sale('direct-sale','1/2','15/2');body['operations'][0]['operation']=operation
    result=m.run(state,body);native=m.runtime.transition(state,operation)
    check('native_sale:transition',result['trace'][0]['result']['transition']==native);check('native_sale:state',result['after']==native['after'])
    cases['native_sale']={'request':body,'result':result,'native':native}
    for name,row in cases.items():
        check(name+':flags',all(row['result'][key] is False for key in m.FLAGS))
        check(name+':incomplete_fiscal',row['result']['fiscal_complete'] is False)
    return {'opening':state,'checks':checks,'cases':cases}
