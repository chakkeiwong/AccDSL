"""Independent full-path oracle; does not import the quotient checker."""
from fractions import Fraction
import json

class PolicyRefusal(ValueError): pass

def encode(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)

def enumerate_paths(model, scenarios, policy, max_nodes=10000):
    if len(scenarios)!=model['horizon'] or any(s not in model['scenarios'] for s in scenarios):
        raise PolicyRefusal('scenario_scope')
    if type(policy) is not dict or set(policy)!= {'schema','actions'} or policy['schema']!='HistoryPolicy/1':
        raise PolicyRefusal('policy_interface')
    if type(policy['actions']) is not dict: raise PolicyRefusal('policy_actions')
    if type(max_nodes) is not int or max_nodes<0: raise PolicyRefusal('enumeration_budget')
    weighted=model['mode']=='probability'
    states=[{s['id']:s for s in d['states']} for d in model['dates']]
    kernels=[{(r['state'],r['action'],r['scenario']):r['outcomes'] for r in d['transitions']} for d in model['dates']]
    result={} if weighted else set()
    stack=[]
    for init in model['initial']:
        history=[{'observation':init['observation'],'current_output':states[0][init['state']]['current']}]
        stack.append((0,init['state'],history,Fraction(init['probability']) if weighted else None))
    visited=0
    while stack:
        if visited>=max_nodes:
            return {'status':'unknown','visited':visited,'unfinished':[{'date':t,'state':x,'history':h,**({'mass':str(p)} if weighted else {})} for t,x,h,p in stack], 'partial_paths':pack(result,weighted)}
        t,x,history,p=stack.pop(); visited+=1
        if t==model['horizon']:
            k=encode(history)
            if weighted: result[k]=result.get(k,Fraction(0))+p
            else: result.add(k)
            continue
        k=encode(history)
        if k not in policy['actions']: raise PolicyRefusal('missing_observable_history')
        a=policy['actions'][k]
        if a not in states[t][x]['actions']: raise PolicyRefusal('action_not_feasible')
        for out in kernels[t][x,a,scenarios[t]]:
            next_history=history+[{'action':a,'observation':out['observation'],'output':out['output'],'current_output':states[t+1][out['next']]['current']}]
            stack.append((t+1,out['next'],next_history,p*Fraction(out['probability']) if weighted else None))
    return {'status':'exact','visited':visited,'paths':pack(result,weighted)}

def pack(paths,weighted):
    return [{'history':json.loads(k),**({'probability':str(paths[k])} if weighted else {})} for k in sorted(paths)]

def supply_policy(model,scenarios,choose):
    """Materialize fixture choices from observable histories only."""
    actions={}
    states=[{s['id']:s for s in d['states']} for d in model['dates']]
    kernels=[{(r['state'],r['action'],r['scenario']):r['outcomes'] for r in d['transitions']} for d in model['dates']]
    frontier=[(0,i['state'],[{'observation':i['observation'],'current_output':states[0][i['state']]['current']}]) for i in model['initial']]
    while frontier:
        t,x,h=frontier.pop()
        if t==model['horizon']: continue
        a=choose(h)
        k=encode(h)
        if k in actions and actions[k]!=a: raise PolicyRefusal('inconsistent_history_policy')
        actions[k]=a
        if a not in states[t][x]['actions']: raise PolicyRefusal('action_not_feasible')
        for out in kernels[t][x,a,scenarios[t]]:
            frontier.append((t+1,out['next'],h+[{'action':a,'observation':out['observation'],'output':out['output'],'current_output':states[t+1][out['next']]['current']}]))
    return {'schema':'HistoryPolicy/1','actions':actions}
