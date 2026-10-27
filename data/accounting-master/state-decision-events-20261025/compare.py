from copy import deepcopy
from fractions import Fraction
from examples import decision as m, start, request, repeated, native


def compare():
    checks=[]; cases={}; state=start()
    def check(name, value): checks.append({'name':name,'passed':bool(value)})
    single=request(state); proposal=m.propose(state,single); applied=m.apply(state,single,proposal)
    operation=native.sale('decision-1-sale','3/2','45/2')
    manual=m.runtime.transition(state,operation)
    check('single:exact_operation',proposal['operation']==operation)
    check('single:complete_transition',applied['transition']==manual)
    check('single:complete_state',applied['after']==manual['after'])
    for account,value in {'cash':'45/2','revenue':'-45/2','inventory':'-15/1','cogs':'15/1'}.items():
        check('single:independent_journal:'+account,applied['transition']['journal'][account]==value)
    for account,value in applied['transition']['journal'].items():
        if account not in ['cash','revenue','inventory','cogs']:
            check('single:unaffected_account:'+account,value=='0/1')
    cases['single']={'request':single,'proposal':proposal,'result':applied,'manual_operation':operation,'manual_result':manual}
    requests=repeated(); sequence=m.run_sequence(state,requests); manual_state=deepcopy(state); native_steps=[]
    for operation in [native.sale('decision-1-sale'),native.sale('decision-2-sale','1/2','15/2','2027-01-03')]:
        step=m.runtime.transition(manual_state,operation);native_steps.append({'operation':operation,'transition':step});manual_state=step['after']
    check('repeated:complete_state',sequence['after']==manual_state)
    for index,step in enumerate(native_steps):
        check('repeated:transition:'+str(index),sequence['trace'][index]['result']['transition']==step['transition'])
    statements=m.runtime.annual.root.carry.statements(manual_state['opening'],manual_state['after'],manual_state['account_classes'])
    for name,value in statements.items():
        if name not in ['scope','unresolved']:
            check('repeated:full_statement_field:'+name,sequence['recorded_statements'][name]==value)
    check('repeated:scope',sequence['recorded_statements']['scope']=='Recorded conditional state after an authored decision prefix; not a complete fiscal event population')
    check('repeated:unresolved',sequence['recorded_statements']['unresolved']==m.runtime.annual.UNRESOLVED)
    check('repeated:statuses',[x['result']['status'] for x in sequence['trace']]==['applied_provisional','applied_provisional','no_action'])
    lot=manual_state['after']['lots']['recovered']
    for name,value in [('units','1/2'),('carrying','5/1'),('tax_base','5/1')]:check('repeated:independent_'+name,lot[name]==value)
    check('repeated:independent_cash',manual_state['after']['balances']['cash']=='949/2')
    check('repeated:independent_cost',sum(Fraction(x['transition']['journal']['cogs']) for x in native_steps)==15)
    check('repeated:independent_profit',sum(-Fraction(x['transition']['journal']['revenue'])-Fraction(x['transition']['journal']['cogs']) for x in native_steps)==Fraction(15,2))
    check('repeated:cursor',sequence['decision_cursor']=='2027-01-04')
    check('repeated:not_fiscal_complete',sequence['fiscal_complete'] is False)
    cases['repeated']={'requests':requests,'result':sequence,'manual_steps':native_steps,'manual_statements':statements}
    for name,field,value,available,enabled,status in [
        ('disabled_future_price','price','99/1','2027-01-03',False,'no_action'),
        ('unknown_guard','enabled','unknown','2027-01-01',True,'unresolved'),
        ('future_price','price','99/1','2027-01-03',True,'unresolved'),
        ('negative_proceeds','price','-1/1','2027-01-01',True,'invalid')]:
        body=request(state,enabled=enabled);body['bindings'][field].update(value=value,available_on=available)
        proposed=m.propose(state,body);result=m.apply(state,body,proposed)
        check(name+':status',result['status']==status)
        check(name+':flags',all(result[key] is False for key in m.FLAGS))
        if status=='no_action':check(name+':unchanged_state',result['after']==state)
        cases[name]={'request':body,'proposal':proposed,'result':result}
    requests=repeated();requests[1]['event']['findings']['homogeneous_units']={'status':'unknown','reason':'Missing authored finding'}
    result=m.run_sequence(state,requests)
    check('refused_prefix:state',result['after']==native_steps[0]['transition']['after'])
    check('refused_prefix:remaining',result['remaining_requests']==requests[1:])
    check('refused_prefix:status',result['stop']['outcome']['status']=='unresolved')
    check('refused_prefix:proposal_retained',result['stop']['outcome']['decision']['status']=='proposed')
    cases['refused_prefix']={'requests':requests,'result':result}
    body=request(state);body['model']['available_on']='unknown';result=m.propose(state,body)
    check('unknown_model:status',result['status']=='unresolved' and result['reason']=='model_not_available')
    cases['unknown_model']={'request':body,'result':result}
    return {'opening':state,'checks':checks,'cases':cases}
