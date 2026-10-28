"""Supplied finite mechanisms; cash observation is not a complete balance sheet."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'data/accounting-master/observation-quotient-20261026'
sys.path.insert(0,str(BASE))
import fixtures as f

TYPES=['clear','guarantee','private_covenant','withdrawal']
def identity(model):return [{s['id']:s['id'] for s in d['states']} for d in model['dates']]
def mechanisms(types):
    if not types or len(set(types))!=len(types) or not set(types)<=set(TYPES):raise ValueError('supplied_types')
    dates=[dict(states=[],transitions=[]) for _ in range(4)]
    def outcome(n,observation,flow,unpaid=0):
        return dict(next=n,observation=observation,output=dict(cash_flow=flow,unpaid=unpaid))
    for kind in types:
        suffix=20 if kind=='guarantee' else 25 if kind=='withdrawal' else 0
        cash=30-suffix;pay=min(cash,20);remaining=cash-pay
        for t in [0,1]:dates[t]['states'].append(f.state(kind+str(t),['wait' if t==0 else 'settle'],30))
        actions=['pay_required']+([] if kind=='private_covenant' else ['distribute'])
        dates[2]['states'].append(f.state(kind+'2',actions,cash))
        dates[3]['states'].append(f.state(kind+'.paid',[],remaining))
        dates[0]['transitions'].append(f.transition(kind+'0','wait',[outcome(kind+'1','quiet',0)]))
        observation='guarantee_call' if kind=='guarantee' else 'customer_withdrawal' if kind=='withdrawal' else 'stable'
        dates[1]['transitions'].append(f.transition(kind+'1','settle',[outcome(kind+'2',observation,-suffix)]))
        dates[2]['transitions'].append(f.transition(kind+'2','pay_required',[outcome(kind+'.paid','payment',-pay,20-pay)]))
        if kind!='private_covenant':
            dates[3]['states'].append(f.state(kind+'.distributed',[],cash-5))
            dates[2]['transitions'].append(f.transition(kind+'2','distribute',[outcome(kind+'.distributed','distribution',-5)]))
    model=f.model('relation',dates,[dict(state=t+'0',observation='opening_cash') for t in types])
    model['requested_outputs']['step']=['cash_flow','unpaid']
    return model

def choose(history):return ['wait','settle','pay_required'][len(history)-1]
def distribute_if_stable(history):
    return 'distribute' if len(history)==3 and history[-1]['observation']=='stable' else choose(history)

def encodings(duplicate=False,equal_weights=False,alter=False,relation=False):
    ids=['high_a','high_b','low'] if duplicate else ['high_a','low']
    masses=['1/3']*3 if equal_weights else ['1/4','1/4','1/2'] if duplicate else ['1/2','1/2']
    dates=[dict(states=[],transitions=[]),dict(states=[f.state('high',[],100),f.state('low',[],60)],transitions=[])]
    for ident in ids:
        high=ident.startswith('high');n='high' if high else 'low';cash=100 if high else 60
        if alter and ident=='high_b':n='low';cash=60
        dates[0]['states'].append(f.state(ident,['wait'],0))
        dates[0]['transitions'].append(f.transition(ident,'wait',[f.out(n,'settled',cash,None if relation else Q(1))]))
    initial=[dict(state=x,observation='same_opening',**({} if relation else dict(probability=m))) for x,m in zip(ids,masses)]
    model=f.model('relation' if relation else 'probability',dates,initial)
    partition=[{x:'high' if x.startswith('high') else 'low' for x in ids},{'high':'high','low':'low'}]
    return model,partition
