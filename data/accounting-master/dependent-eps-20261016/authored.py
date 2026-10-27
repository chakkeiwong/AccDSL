"""Freeze independently derived consequences and paragraph57 examples."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
CONTEXT=dict(entity='synthetic-issuer',book='group',currency='CU',ordinary_class='O',
             start='2025-01-01',end_exclusive='2026-01-01',rule='EU2023/1803-original-IAS33')
COMMON=dict(total_equals_continuing=True,nonparticipating_ordinary=True,inventory_complete=True,
            whole_period=True,no_other_earnings_effects=True)

def financial(profit,bonus,tax,earnings,shares,eps):
    return {k:str(Q(str(v))) for k,v in dict(pretax_before_bonus=profit,bonus=bonus,tax=tax,
        earnings=earnings,shares=shares,eps=eps).items()}

def main():
    a=dict(id='A',interest_saved='20',incremental_shares='20')
    b=dict(id='B',interest_saved='20',incremental_shares='20')
    base=dict(wire='ConsequentialEPSWorlds/1',operation='worlds',context=CONTEXT,
        pretax_before_bonus='90',bonus_threshold='100',bonus_rate='1/2',tax_rate='1/5',
        ordinary_shares='100',findings=dict(**COMMON,bonus_terms_complete=True,tax_effects_complete=True,
        independent_interest_savings=True),series=[a,b])
    cases=[]
    def add(id,vals,**changes):
        r=deepcopy(base);r.update(changes)
        keys=['','A','B','A+B'];cases.append(dict(id=id,request=r,expected=dict(zip(keys,[financial(*v) for v in vals]))))
    add('joint-threshold',[(90,0,18,72,100,'18/25'),(110,5,21,84,120,'7/10'),(110,5,21,84,120,'7/10'),(130,15,23,92,140,'23/35')])
    add('no-bonus-additive',[(90,0,18,72,100,'18/25'),(110,0,22,88,120,'11/15'),(110,0,22,88,120,'11/15'),(130,0,26,104,140,'26/35')],bonus_rate='0')
    add('at-threshold',[(100,0,20,80,100,'4/5'),(120,10,22,88,120,'11/15'),(120,10,22,88,120,'11/15'),(140,20,24,96,140,'24/35')],pretax_before_bonus='100')
    add('joint-minimum-is-not-selection',[(80,0,16,64,100,'16/25'),(100,0,20,80,120,'2/3'),(100,0,20,80,120,'2/3'),(120,10,22,88,140,'22/35')],pretax_before_bonus='80')
    add('zero-no-tax',[(0,0,0,0,100,0),(20,0,0,20,120,'1/6'),(20,0,0,20,120,'1/6'),(40,0,0,40,140,'2/7')],pretax_before_bonus='0',tax_rate='0')
    add('loss-no-tax',[(-40,0,0,-40,100,'-2/5'),(-20,0,0,-20,120,'-1/6'),(-20,0,0,-20,120,'-1/6'),(0,0,0,0,140,0)],pretax_before_bonus='-40',tax_rate='0')
    add('unequal-savings',[(90,0,18,72,100,'18/25'),(110,5,21,84,120,'7/10'),(130,15,23,92,140,'23/35'),(150,25,25,100,160,'5/8')],series=[a,dict(id='B',interest_saved='40',incremental_shares='40')])
    option=dict(wire='ContingentOptionEPS/1',operation='report',context=CONTEXT,earnings='100',ordinary_shares='100',
        average_market_price='10',findings=dict(**COMMON,similarity_admitted=True,no_service_proceeds=True,
        contingent_option_not_in_basic=True,no_other_dependencies=True),
        similar=dict(id='O',count='20',strike='6'),contingent=dict(id='C',count='20',strike='5'),
        condition=dict(kind='store_count',observed='5',required='5',observed_date='2025-12-31',
            agreement_start='2025-01-01',contingency_end='2026-12-31'))
    options=[]
    def opt(id,eps,selected,reason,change=lambda r:None):
        r=deepcopy(option);change(r)
        options.append(dict(id=id,request=r,expected=dict(eps=str(Q(str(eps))),selected=selected,contingent_reason=reason)))
    opt('eligible-linked','50/59',['O','C'],'selected')
    opt('condition-fails','25/27',['O'],'condition_not_satisfied',lambda r:r['condition'].update(observed='4'))
    opt('similar-out-of-money',1,[],'similar_not_assumed',lambda r:r['similar'].update(strike='12'))
    opt('similar-at-money',1,[],'similar_not_assumed',lambda r:r['similar'].update(strike='10'))
    opt('contingent-out-of-money','25/27',['O'],'no_increment',lambda r:r['contingent'].update(strike='12'))
    opt('zero-no-dilution',0,[],'similar_not_assumed',lambda r:r.update(earnings='0'))
    opt('loss-no-dilution',-1,[],'similar_not_assumed',lambda r:r.update(earnings='-100'))
    opt('same-strike','25/29',['O','C'],'selected',lambda r:r['contingent'].update(strike='6'))
    p=OUT/'authored-cases.json';assert not p.exists()
    p.write_text(json.dumps(dict(world_cases=cases,option_cases=options),indent=2)+'\n')
    paths=[p,Path(__file__).resolve(),OUT/'source-reading.md',ROOT/'docs/plans/accounting-dependent-eps-20261016.md',
        ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
        ROOT/'data/accounting-master/capped-participation-20261016/semantic-contract.md',
        ROOT/'data/accounting-master/continuation-integrity-eps-20261016/ordered-eps/semantic-contract.md']
    (OUT/'input-lock.json').write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in paths]),indent=2)+'\n')
    print(json.dumps(dict(world_cases=len(cases),option_cases=len(options),protected_files=len(paths))))

if __name__=='__main__':main()
