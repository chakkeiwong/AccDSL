"""Explicit hypothetical finite company-state cases, not empirical data."""
from copy import deepcopy
from fractions import Fraction
from quotient import INFORMATION

def state(x,actions,cash): return {'id':x,'actions':actions,'current':{'cash':cash}}
def out(x,o,y,p=None):
    result={'next':x,'observation':o,'output':{'cash_flow':y}}
    if p is not None: result['probability']=str(p)
    return result
def transition(x,a,outs,s='base'): return {'state':x,'action':a,'scenario':s,'outcomes':outs}
def model(mode,dates,initial):
    return {'schema':'FiniteCompanyModel/1','mode':mode,'horizon':len(dates)-1,
            'scenarios':['base'],'information':deepcopy(INFORMATION),
            'requested_outputs':{'current':['cash'],'step':['cash_flow']},
            'dates':dates,'initial':initial}

def signals(qx=Fraction(9,10),qy=Fraction(9,10)):
    dates=[{'states':[state('x',['observe'],10),state('y',['observe'],10)],'transitions':[]},
           {'states':[state('good',['lend','wait'],10),state('bad',['lend','wait'],10)],'transitions':[]},
           {'states':[state('gain',[],12),state('loss',[],6),state('unchanged',[],10)],'transitions':[]}]
    for x,q in [('x',qx),('y',qy)]:
        dates[0]['transitions'].append(transition(x,'observe',[
            out('good','green',0,q/2),out('bad','red',0,q/2),
            out('good','red',0,(1-q)/2),out('bad','green',0,(1-q)/2)]))
    dates[1]['transitions']=[transition('good','lend',[out('gain','settled',2,1)]),
                            transition('bad','lend',[out('loss','settled',-4,1)]),
                            transition('good','wait',[out('unchanged','settled',0,1)]),
                            transition('bad','wait',[out('unchanged','settled',0,1)])]
    m=model('probability',dates,[{'state':'x','observation':'start','probability':'1/3'},
                                 {'state':'y','observation':'start','probability':'2/3'}])
    p=[{'x':'root','y':'root'},{'good':'good','bad':'bad'},{'gain':'gain','loss':'loss','unchanged':'unchanged'}]
    return m,p

def choose_signal(h):
    return 'observe' if len(h)==1 else ('lend' if h[-1]['observation']=='green' else 'wait')

def duplicate_successors():
    m,p=signals()
    # Replace a single successor by duplicate full states, splitting its mass.
    m['dates'][1]['states'].append(state('good_copy',['lend','wait'],10))
    for tr in list(m['dates'][1]['transitions']):
        if tr['state']=='good':
            c=deepcopy(tr);c['state']='good_copy';m['dates'][1]['transitions'].append(c)
    p[1]['good_copy']='good'
    for tr in m['dates'][0]['transitions']:
        revised=[]
        for o in tr['outcomes']:
            if o['next']=='good':
                a=deepcopy(o); b=deepcopy(o); a['probability']=b['probability']=str(Fraction(o['probability'])/2);b['next']='good_copy'
                revised.extend([a,b])
            else: revised.append(o)
        tr['outcomes']=revised
    return m,p

def persistent_type():
    dates=[]
    for t in range(3):
        dates.append({'states':[state('fixed'+str(t),['pay'] if t<2 else [],100-5*t),
                                state('floating'+str(t),['pay'] if t<2 else [],100-7*t)],'transitions':[]})
        if t<2:
            dates[t]['transitions']=[transition('fixed'+str(t),'pay',[out('fixed'+str(t+1),'paid',-5)]),
                                    transition('floating'+str(t),'pay',[out('floating'+str(t+1),'paid',-7)])]
    m=model('relation',dates,[{'state':'fixed0','observation':'start'},{'state':'floating0','observation':'start'}])
    fine=[{s['id']:s['id'] for s in d['states']} for d in dates]
    coarse=[{s['id']:'all' for s in d['states']} for d in dates]
    return m,fine,coarse

def joint_only():
    dates=[{'states':[state('x',['pay'],10),state('y',['pay'],10)],'transitions':[]},
           {'states':[state('end',[],10)],'transitions':[]}]
    dates[0]['transitions']=[transition('x','pay',[out('end','green',1,'1/2'),out('end','red',-1,'1/2')]),
                           transition('y','pay',[out('end','green',-1,'1/2'),out('end','red',1,'1/2')])]
    return model('probability',dates,[{'state':'x','observation':'start','probability':'1/2'},
                                      {'state':'y','observation':'start','probability':'1/2'}]), [{'x':'root','y':'root'},{'end':'end'}]
