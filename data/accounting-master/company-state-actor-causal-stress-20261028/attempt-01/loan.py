"""Finite earmarked-reserve contract with supplied actor observations."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import sys
import information as info
BASE=Path(__file__).resolve().parent.parent/'observation-quotient-20261026'
sys.path.insert(0,str(BASE))
import fixtures as f

def source(kind):
    text='Synthetic signed loan: face100; '+kind+' coupon '+str(5 if kind=='fixed' else 7)+'.'
    digest=sha256(text.encode()).hexdigest()
    row=dict(id='terms.'+kind,source_sha256=digest,loan_id='loan1',loan_type=kind,
             authored='2026-01-01T00:00:00Z',effective='2026-01-01T00:00:00Z',
             published='2026-01-03T00:00:00Z',access=dict(
                 manager=dict(route='private_delivery',at='2026-01-01T00:00:00Z'),
                 analyst=dict(route='public_document',at='2026-01-03T12:00:00Z')))
    return [row],{digest:text}

def build(actor,cutoff):
    observations={}
    for kind in ['fixed','floating']:
        rows,sources=source(kind);v=info.view(rows,sources,actor,'loan1',cutoff)
        if v['status'] not in ['known','not_available']:return dict(status='unresolved_information',views=observations,refusal=v)
        observations[kind]=v
    dates=[dict(states=[],transitions=[]) for _ in range(3)]
    for kind,coupon in [('fixed',5),('floating',7)]:
        dates[0]['states'].append(f.state(kind,['reserve5','reserve7'],10))
        for reserve in [5,7]:
            ident=kind+'.'+str(reserve);paid=min(reserve,coupon)
            dates[1]['states'].append(f.state(ident,['settle'],10))
            dates[2]['states'].append(f.state(ident+'.done',[],10-paid))
            dates[0]['transitions'].append(f.transition(kind,'reserve'+str(reserve),[
                dict(next=ident,observation='reserve_recorded',output=dict(cash_flow=0,unpaid=0,unused_reserve=reserve))]))
            dates[1]['transitions'].append(f.transition(ident,'settle',[
                dict(next=ident+'.done',observation='coupon_settled',output=dict(cash_flow=-paid,unpaid=coupon-paid,unused_reserve=reserve-paid))]))
    model=f.model('relation',dates,[dict(state=k,observation=v['observation']) for k,v in observations.items()])
    model['requested_outputs']['step']=['cash_flow','unpaid','unused_reserve']
    return dict(status='constructed',model=model,views=observations)

def identity(model):return [{s['id']:s['id'] for s in d['states']} for d in model['dates']]
def informed(history):
    if len(history)>1:return 'settle'
    kind=history[0]['observation']['loan_type']
    if kind is None:raise ValueError('loan_terms_not_observed')
    return 'reserve5' if kind=='fixed' else 'reserve7'
def common(reserve):return lambda history:'settle' if len(history)>1 else 'reserve'+str(reserve)
