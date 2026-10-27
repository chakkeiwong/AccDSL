"""Create a separate cash/equity profile; keep the cash-only reference frozen."""
from pathlib import Path
from hashlib import sha256
import json
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-worksheet-20261027'
assert not (H/'reference.py').exists()
v=json.loads((S/'attempt-01/verification.json').read_text());assert v['status']=='PASS'
for p,d in json.loads((S/'attempt-01/source-lock.json').read_text()).items():assert sha256((R/p).read_bytes()).hexdigest()==d
code=(S/'reference.py').read_text().replace('ConditionalAcquisitionWorksheet/1','ConditionalAcquisitionWorksheet/2')
replacements=[
 ("amount=number(p['consideration']);h.need(amount>=0,'negative_consideration')","""h.fields(p['consideration'],['cash','new_parent_equity','kind','at','currency','unit','premise'],'consideration')
        c=p['consideration'];h.need(c['kind']=='cash_and_new_parent_equity','consideration_kind')
        h.need(h.moment(c['at'])==h.moment(at),'consideration_date')
        h.need(c['currency']==currency and c['unit']==unit,'consideration_unit');h.text(c['premise'])
        cash_consideration=number(c['cash']);equity_consideration=number(c['new_parent_equity'])
        h.need(cash_consideration>=0 and equity_consideration>=0,'negative_consideration')
        amount=cash_consideration+equity_consideration"""),
 ("pa['cash']==po['cash']-amount and pa['capital']==po['capital']","pa['cash']==po['cash']-cash_consideration and pa['capital']==po['capital']-equity_consideration"),
 ("po['cash']-amount+sa['cash']+cash==cashclose","po['cash']-cash_consideration+sa['cash']+cash==cashclose"),
 ("consideration_paid=amount,acquired=sa['cash'],acquisition_net=sa['cash']-amount","consideration_paid=cash_consideration,noncash_equity=equity_consideration,acquired=sa['cash'],acquisition_net=sa['cash']-cash_consideration"),
 ("return dict(profile=PROFILE,status='conditional_worksheet'","financial['parent_equity']=serial(dict(opening=-po['capital'],new_equity=equity_consideration,owners_profit=computed['owners_profit'],closing=owners))\n        h.need(-po['capital']+equity_consideration+computed['owners_profit']==owners,'parent_equity_roll')\n        return dict(profile=PROFILE,status='conditional_worksheet'"),
 ("basis_premises=deepcopy(p['basis_premises']),symbolic_result","basis_premises=deepcopy(p['basis_premises']),consideration=deepcopy(c),symbolic_result"),
 ('Explicit synthetic cash-only acquisition with supplied item/tax/rights premises','Explicit synthetic cash/new-parent-equity acquisition with supplied item/tax/rights premises'),
 ("'noncash_and_prior_relationships'","'debt_conversion_and_prior_relationships'")]
for old,new in replacements:
    assert old in code,old;code=code.replace(old,new)
(H/'reference.py').write_text(code)
(H/'predecessor-lock.json').write_text(json.dumps({str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in S.rglob('*') if p.is_file() and 'inputs' not in p.parts and '__pycache__' not in p.parts},indent=2)+'\n')
print('Created /2 candidate and frozen cash-only predecessor identities.')
