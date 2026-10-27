"""Stipulated independent legal histories; no actual-company observations."""
from pathlib import Path
from copy import deepcopy
import json
H=Path(__file__).resolve().parent
SAVED=json.loads((H.parent/'acquisition-symbolic-20261027/attempt-01/cases.json').read_text())
def payload(election='proportional',loss=False):
    symbolic=deepcopy(next(r['request'] for r in SAVED if r['id']==election+'/none'))
    def snapshot(at,balances):return dict(at=at,balances=balances)
    start='2025-01-01T00:00:00Z';at='2025-07-01T00:00:00Z';end='2026-01-01T00:00:00Z'
    p0={'cash':'300/1','investment':'0/1','capital':'-300/1'}
    p1={'cash':'180/1','investment':'120/1','capital':'-300/1'}
    s0={'cash':'30/1','equipment':'70/1','payable':'-20/1','capital':'-80/1','retained_pre':'0/1','revenue':'0/1','depreciation':'0/1','operating_expense':'0/1'}
    s1={'cash':'50/1','equipment':'70/1','payable':'-20/1','capital':'-80/1','retained_pre':'-20/1','revenue':'0/1','depreciation':'0/1','operating_expense':'0/1'}
    s2={'cash':'90/1','equipment':'63/1','payable':'-220/1' if loss else '-20/1','capital':'-80/1','retained_pre':'-20/1','revenue':'-40/1','depreciation':'7/1','operating_expense':'200/1' if loss else '0/1'}
    books={owner:dict(entity=owner,currency='USD',unit='currency_unit',snapshots=dict(opening=snapshot(start,deepcopy(a)),acquisition=snapshot(at,deepcopy(b)),closing=snapshot(end,deepcopy(c)))) for owner,a,b,c in [('P',p0,p1,p1),('S',s0,s1,s2)]}
    items=[]
    for name,kind,account,legal,recognised in [('cash','asset','cash','50/1','50/1'),('equipment','asset','equipment','70/1','90/1'),('payable','liability','payable','-20/1','-20/1'),('deferred_tax','liability',None,'0/1','-5/1')]:
        items.append(dict(id=name,kind=kind,legal_account=account,legal_balance=legal,recognised_balance=recognised,at=at,currency='USD',unit='currency_unit',premise='Stipulated synthetic '+name+' amount, not an actual-company measurement'))
    return dict(symbolic_request=symbolic,synthetic_premise='Explicit synthetic engineering case; no company measurement or accounting admission',basis_premises=dict(recognition='Conditional synthetic positive-excess acquisition; facts and measurement stipulated',tax='Stipulated tax liability and later release; no tax recognition/rate inference',items='Complete only for the declared four-item synthetic chart',later_adjustments='Additional depreciation2 and tax release1/2 are supplied synthetic premises'),books=books,acquired_items=items,consideration='120/1',nci_fair_value='40/1' if election=='fair_value' else None,expense_adjustment='2/1',tax_release='1/2',operating_cash='40/1',expected_books_sha256='')
