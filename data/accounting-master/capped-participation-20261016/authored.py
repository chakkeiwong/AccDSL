"""Freeze hand-derived class earnings and coupled EPS targets."""
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
CONTEXT=dict(entity='synthetic-issuer',book='group',currency='CU',ordinary_class='O',participating_class='P',
    start='2025-01-01',end_exclusive='2026-01-01',rule='EU2023/1803-original-IAS33')
FINDINGS=dict(equity_classification_admitted=True,senior_period_entitlement_complete=True,residual_profit_only=True,
    rights_fixed=True,no_other_dividends_or_attribution=True,total_equals_continuing=True,independent_gross_effects=True,
    inventory_complete=True,full_period_constant_population=True)

def vals(preferred,ordinary,denominator,eps):
    return {k:str(Q(str(v))) for k,v in dict(preferred=preferred,ordinary=ordinary,denominator=denominator,eps=eps).items()}
def series(id,a,b):return dict(id=id,gross_after_tax_adjustment=str(a),ordinary_share_increment=str(b),start='2025-01-01',end_exclusive='2026-01-01',
    findings=dict(all_direct_and_consequential_effects_complete=True,time_weighting_complete=True,no_conditional_exercise=True))

def main():
    base=dict(wire='CappedParticipationEPS/1',operation='report',context=CONTEXT,earnings='140',ordinary_shares='100',
        preferred_shares='20',residual_weight='1',senior_entitlement='20',total_preferred_cap='40',findings=FINDINGS,series=[])
    option=series('option',0,50);debt=series('debt',6,10);high=series('high',20,10)
    cases=[]
    def add(id,E,instruments,basic,final=None,selected=(),**override):
        r=deepcopy(base);r.update(earnings=str(E),series=deepcopy(instruments),**override)
        cases.append(dict(id=id,request=r,expected=dict(basic=basic,diluted=final or basic,selected=list(selected))))
    add('cap-kink',140,[],vals(40,100,100,1))
    add('below-cap',80,[],vals(30,50,100,'1/2'))
    add('above-cap',200,[],vals(40,160,100,'8/5'))
    add('just-below-kink',139,[],vals('239/6','595/6',100,'119/120'))
    add('just-above-kink',141,[],vals(40,101,100,'101/100'))
    add('priority-only',20,[option,debt],vals(20,0,100,0))
    add('zero-profit',0,[option,debt],vals(20,-20,100,'-1/5'))
    add('loss-no-participation',-40,[option,debt],vals(20,-60,100,'-3/5'))
    add('option-reallocates',140,[option],vals(40,100,100,1),vals('580/17','1800/17',150,'12/17'),['option'])
    add('debt-alone',140,[debt],vals(40,100,100,1),vals('512/13','1386/13',110,'63/65'),['debt'])
    add('both',140,[debt,option],vals(40,100,100,1),vals(34,112,160,'7/10'),['option','debt'])
    add('both-reversed',140,[option,debt],vals(40,100,100,1),vals(34,112,160,'7/10'),['option','debt'])
    add('high-ratio-excluded',140,[high,debt,option],vals(40,100,100,1),vals(34,112,160,'7/10'),['option','debt'])
    add('strict-equality',140,[series('equal',10,10)],vals(40,100,100,1))
    add('nonparticipating-limit',140,[option,debt],vals(20,120,100,'6/5'),vals(20,126,160,'63/80'),['option','debt'],residual_weight='0')
    add('proportional-limit',120,[],vals(20,100,100,1),preferred_shares='10',residual_weight='2',senior_entitlement='0',total_preferred_cap='200')
    add('cap-never-binds',200,[],vals(50,150,100,'3/2'),total_preferred_cap='200')
    add('zero-residual-cap',140,[option,debt],vals(20,120,100,'6/5'),vals(20,126,160,'63/80'),['option','debt'],total_preferred_cap='20')
    p=OUT/'authored-cases.json';assert not p.exists();p.write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    paths=[p,Path(__file__).resolve(),OUT/'source-reading.md',ROOT/'docs/plans/accounting-capped-participation-20261016.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        ROOT/'data/accounting-master/continuation-integrity-eps-20261016/ordered-eps/semantic-contract.md',
        ROOT/'docs/design/proposal/manuscript-fiscal-loss-closing-20261016/sections/awards-participation.tex']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),protected_files=len(paths))))

if __name__=='__main__':main()
