"""Freeze independent stage targets before writing the successor calculator."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PREV = ROOT / 'data/accounting-master/hedge-inventory-close-20261016'


def sale(id, day, quantity, cash):
    return dict(id=id, kind='sale', date=day, quantity=quantity, cash=cash,
                recognition_satisfied=True)


def nrv(id, day, value, recovery):
    return dict(id=id, kind='nrv', date=day, per_unit=value,
                valuation_satisfied=True, uniform_unit_nrv=True,
                recovery_conditions_met=recovery)


def target(quantity, gross, allowance, carrying, cash, profit, equity, cogs, expense):
    return dict(quantity=quantity, gross_cost=gross, allowance=allowance,
                inventory=carrying, cash=cash, cumulative_pretax_profit=profit,
                pretax_equity=equity, cost_of_sales=cogs, net_nrv_expense=expense,
                reserve='0', derivative='0')


def main():
    prior = json.loads((PREV / 'authored-cases.json').read_text())['cases']
    cases = []
    # Explicit amounts are authored without importing a calculator.
    for old in prior:
        gain = old['id'] == 'gain'
        req = deepcopy(old['request'])
        req.pop('sale')
        req['findings'].pop('all_units_sold')
        req['findings'].pop('sale_recognition_satisfied')
        req['findings'].update(interchangeable_uniform_batch=True,
                               no_other_inventory_or_purchases=True,
                               same_nature_and_use=True)
        req.update(wire='HedgeInventorySubsequent/1', cost_formula='weighted_average')
        days = ['2024-10-15','2024-10-31','2024-11-15','2024-11-30','2024-12-15','2024-12-31'] if gain else ['2025-01-02','2025-01-31','2025-02-15','2025-02-28','2025-03-15','2025-03-31']
        events = [sale('s1',days[0],'52','5800'), nrv('v1',days[1],'70',None),
                  sale('s2',days[2],'26','2900'), nrv('v2',days[3],'90',True),
                  sale('s3',days[4],'52','5800')]
        amounts = ([('9290','90','20090'),('15090','1570','21570'),('15090','550','20550'),
                    ('17990','1630','21630'),('17990','2310','22310'),('23790','3790','23790')] if gain else
                   [('9100','-100','19900'),('14900','1380','21380'),('14900','360','20360'),
                    ('17800','1440','21440'),('17800','2120','22120'),('23600','3600','23600')])
        shape = [('130','10800','0','10800','0','0'),('78','6480','0','6480','4320','0'),
                 ('78','6480','1020','5460','4320','1020'),('52','4320','680','3640','6140','1020'),
                 ('52','4320','0','4320','6140','340'),('0','0','0','0','10460','340')]
        targets = {}
        for id, dims, values in zip(['basis','s1','v1','s2','v2','s3'],shape,amounts):
            q,g,a,k,cogs,expense=dims; cash,profit,equity=values
            targets[id]=target(q,g,a,k,cash,profit,equity,cogs,expense)
        for name,n in [('unsold',0),('partial',1),('write_down_sale_recovery',5)]:
            r=deepcopy(req);r['events']=deepcopy(events[:n])
            cases.append(dict(id=old['id']+'_'+name,request=r,
                targets={k:v for k,v in targets.items() if k in ['basis']+[e['id'] for e in events[:n]]}))
        r=deepcopy(req);r['events']=[sale('all',days[0],'130','14500')]
        c,p,e=amounts[-1]
        cases.append(dict(id=old['id']+'_all',request=r,targets={'basis':targets['basis'],
            'all':target('0','0','0','0',c,p,e,'10800','0')}))
        if gain:
            r=deepcopy(req);r['events']=deepcopy(events[:3])+[
                nrv('v80',days[3],'80',True),nrv('v80_again',days[4],'80',None),
                nrv('v90',days[5],'90',True)]
            t={k:targets[k] for k in ['basis','s1','v1','s2']}
            t['v80']=target('52','4320','160','4160','17990','2150','22150','6140','500')
            t['v80_again']=deepcopy(t['v80'])
            t['v90']=targets['v2']
            cases.append(dict(id='gain_stepped_recovery',request=r,targets=t))
    authored=OUT/'authored-cases.json';assert not authored.exists()
    authored.write_text(json.dumps(dict(cases=cases),indent=2)+'\n')
    files=[OUT/'authored.py',authored,OUT/'source-reading.md',
           ROOT/'docs/plans/accounting-hedge-inventory-subsequent-20261016.md',
           ROOT/'docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt',
           PREV/'reference.py',PREV/'authored-cases.json',PREV/'input-lock.json',
           PREV/'attempt-01/exchanges.json',
           ROOT/'data/accounting-master/repeated-rebalancing-20261016/reference.py']
    # Pin the transitive source/fixture locks used by the protected hedge module.
    for name in ['input-lock.json','authored-cases.json']:
        files.append(ROOT/'data/accounting-master/repeated-rebalancing-20261016'/name)
    lock=OUT/'input-lock.json';assert not lock.exists()
    lock.write_text(json.dumps(dict(files=[dict(path=str(p.relative_to(ROOT)),
        sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]),indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),locked_files=len(files))))


if __name__ == '__main__':
    main()
