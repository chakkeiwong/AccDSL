"""Exact authored funded-year diagnostic; preserves all frozen source records."""
from copy import deepcopy
from datetime import date, datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOURCE = ROOT / 'data/accounting-master/corporate-portable-20261015/portable-exchanges.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(value):
    return Q(int(value['n']), int(value['d']))


def affine(value, share):
    return q(value['constant']) + share*q(value['coefficient_x'])


def settle_claim(claims, identity, amount):
    """Explicit partial-settlement lifecycle, a successor to the full-payment draft."""
    if identity not in claims or amount <= 0 or amount > claims[identity]['outstanding']:
        raise ValueError('invalid_claim_settlement')
    successor = deepcopy(claims)
    successor[identity]['outstanding'] -= amount
    successor[identity]['settled'] += amount
    return successor


def principal_payment(outstanding, amount):
    if amount <= 0 or amount > outstanding:
        raise ValueError('invalid_principal_payment')
    return outstanding-amount


def claim(amount):
    return {'recognised':amount, 'settled':Q(0), 'outstanding':amount}


def main():
    started=datetime.now(timezone.utc).isoformat(); timer=time.perf_counter()
    source_hash=digest(SOURCE); source=json.loads(SOURCE.read_text()); records=source['record_registry']
    checks=[]; runs=[]

    def check(name, condition):
        checks.append({'name':name,'passed':bool(condition)})

    dates={'purchase':'2025-01-02','delivery':'2025-01-03','facility_draw':'2025-01-04',
           'supplier_payment':'2025-01-04','collection':'2025-01-05',
           'facility_interest':'2025-01-06','facility_repayment':'2025-01-06','payroll':'2025-01-07'}
    order=['purchase','delivery','facility_draw','supplier_payment','collection','facility_interest',
           'facility_repayment','payroll','plant_addition','depreciation','interest','tax','dividend','close']
    day_count=(date.fromisoformat(dates['facility_repayment'])-date.fromisoformat(dates['facility_draw'])).days
    principal=Q(427,5); tax_rate=q(records[source['aliases']['economic-facts']['digest']]['body']['forecast']['tax_rate'])
    check('explicit_contract_day_count',day_count==2)
    for scenario in ['stress7','stress9']:
        projection=records[source['aliases']['projection.'+scenario]['digest']]['body']
        opening={k:q(v) for k,v in records[projection['opening_ref']['digest']]['body']['balances'].items()}
        classes={e['event_kind']:e['cash_class'] for e in projection['event_plan']}
        classes.update(facility_draw='financing',facility_repayment='financing',facility_interest='operating')
        for share in [Q(0),Q(1,2),Q(1)]:
            baseline_journals={j['event_kind']:{l['account']:affine(l['signed_amount'],share) for l in j['lines']} for j in projection['proposed_journals']}
            expected={k:affine(v,share) for k,v in projection['closing_balances'].items()}
            original_lines={k:affine(v,share) for k,v in projection['lines'].items()}
            original=deepcopy(opening)
            for journal in projection['proposed_journals']:
                for account,delta in baseline_journals[journal['event_kind']].items(): original[account]+=delta
            check(scenario+':'+str(share)+':baseline_reproduced',original==expected)
            for rate in [Q(0),Q(1,20),Q(7,100)]:
                name=scenario+':share='+str(share)+':facility_rate='+str(rate)
                interest=principal*rate*Q(day_count,365); tax_saving=interest*tax_rate; after_tax=interest-tax_saving
                journals=deepcopy(baseline_journals)
                journals['facility_draw']={'cash':principal,'debt':-principal}
                journals['facility_interest']={'interest':interest,'cash':-interest}
                journals['facility_repayment']={'debt':principal,'cash':-principal}
                journals['tax']['tax']-=tax_saving; journals['tax']['cash']+=tax_saving
                journals['close']['interest']-=interest
                journals['close']['tax']+=tax_saving
                journals['close']['retained']+=after_tax
                if original_lines['profit_before_tax']-interest < 0:
                    raise ValueError('Loss tax method outside the declared profile')
                balances=deepcopy(opening); flows={k:Q(0) for k in ('operating','investing','financing')}
                receivables={'opening':claim(Q(35))}; payables={'opening':claim(Q(30))}
                facility_outstanding=Q(0); schedule=[]; min_cash=balances['cash']; prior=None
                for event in order:
                    lines=journals[event]
                    assert sum(lines.values(),Q(0))==0,(name,event,'unbalanced')
                    # Validate claim/principal changes before posting the corresponding journal.
                    next_r,next_p,next_fac=deepcopy(receivables),deepcopy(payables),facility_outstanding
                    if event=='purchase': next_p['purchase']=claim(Q(170))
                    elif event=='delivery': next_r['sales']=claim(Q(300))
                    elif event=='supplier_payment': next_p=settle_claim(payables,'purchase',Q(160))
                    elif event=='collection':
                        next_r=settle_claim(receivables,'opening',Q(10))
                        next_r=settle_claim(next_r,'sales',Q(270))
                    elif event=='facility_draw': next_fac+=principal
                    elif event=='facility_repayment': next_fac=principal_payment(facility_outstanding,principal)
                    cash_delta=lines.get('cash',Q(0))
                    assert balances['cash']+cash_delta>=0,(name,event,'cash_shortfall')
                    for account,delta in lines.items(): balances[account]+=delta
                    receivables,payables,facility_outstanding=next_r,next_p,next_fac
                    if cash_delta: flows[classes[event]]+=cash_delta
                    min_cash=min(min_cash,balances['cash'])
                    assert sum((c['outstanding'] for c in receivables.values()),Q(0))==balances['receivables']
                    assert sum((c['outstanding'] for c in payables.values()),Q(0))==-balances['payables']
                    assert all(c['outstanding']==c['recognised']-c['settled'] for c in list(receivables.values())+list(payables.values()))
                    schedule.append({'event':event,'date':dates.get(event,'2025-12-31'),
                                     'after':[] if prior is None else [prior], 'journal':lines,
                                     'cash_class':classes[event], 'cash_after':balances['cash'],
                                     'facility_principal_after':facility_outstanding})
                    prior=event
                changed=deepcopy(expected); changed['cash']-=after_tax; changed['retained']+=after_tax
                profit=original_lines['profit']-after_tax
                assets=sum(balances[k] for k in ('cash','receivables','inventory','plant_cost','accum_depreciation','tax_prepaid'))
                liabilities=-(balances['payables']+balances['debt']); equity=-(balances['capital']+balances['retained'])
                indirect=profit+original_lines['depreciation']-(balances['receivables']-opening['receivables'])-(balances['inventory']-opening['inventory'])+(-balances['payables']+opening['payables'])-(balances['tax_prepaid']-opening['tax_prepaid'])
                check(name+':closing_accounts',balances==changed)
                check(name+':balance_sheet',assets==liabilities+equity)
                check(name+':equity_bridge',equity==original_lines['opening_equity']+profit-original_lines['dividends'])
                check(name+':direct_indirect_cfo',flows['operating']==original_lines['operating_cash']-after_tax==indirect)
                check(name+':cash_bridge',opening['cash']+sum(flows.values(),Q(0))==balances['cash'])
                check(name+':financing_gross_not_income',flows['financing']==original_lines['financing_cash'] and journals['facility_draw']['cash']==-journals['facility_repayment']['cash'] and balances['debt']==opening['debt'])
                check(name+':temporary_accounts_closed',all(balances[k]==0 for k in ('revenue','cost_of_sales','payroll','depreciation','interest','tax')))
                check(name+':cash_feasible',min_cash==0)
                check(name+':claims_close',receivables['opening']['outstanding']==25 and receivables['sales']['outstanding']==30 and payables['opening']['outstanding']==30 and payables['purchase']['outstanding']==10)
                check(name+':facility_closed',facility_outstanding==0)
                runs.append({'name':name,'contract':{'principal':principal,'annual_rate':rate,'day_count':'Actual/365 calendar dates','days':day_count,'fees':Q(0),'interest':interest},
                             'journals':schedule,'closing_balances':balances,'claims':{'receivables':receivables,'payables':payables},
                             'statements':{'assets':assets,'liabilities':liabilities,'equity':equity,'profit':profit,'cash':balances['cash'],'cash_flows':flows},
                             'difference_from_original':{'interest':interest,'tax':-tax_saving,'profit':-after_tax,'cash':-after_tax,'equity':-after_tax},
                             'minimum_cash':min_cash,'status':'conditional_synthetic_path_not_committed'})
    claims={'invoice':claim(Q(160))}; before=deepcopy(claims)
    for value in [Q(161),Q(-1),Q(0)]:
        try: settle_claim(claims,'invoice',value)
        except ValueError: refused=True
        else: refused=False
        check('refuse_invalid_claim_'+str(value),refused and claims==before)
    try: principal_payment(principal,principal+1)
    except ValueError: refused=True
    else: refused=False
    check('refuse_excess_principal',refused)
    check('preserve_source_bytes',digest(SOURCE)==source_hash)
    report={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'runs':runs,'checks':checks,
            'scope':'Exact conditional documentary year; no production simulation or empirical forecast'}
    (OUT/'checks.json').write_text(json.dumps(report,indent=2,default=str)+chr(10))
    manifest={'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
              'command':'env CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 -B data/accounting-master/funded-year-20261023/verify.py',
              'environment':{'executable':sys.executable,'python':platform.python_version(),'dependencies':'standard library'},
              'cpu_gpu':'CPU only; GPU intentionally hidden; no ML framework imported','cuda_visible_devices':os.environ.get('CUDA_VISIBLE_DEVICES'),
              'random_seeds':'N/A: deterministic authored cases','data_version':source_hash,'started_utc':started,'wall_seconds':time.perf_counter()-timer,
              'plan_file':'docs/plans/accounting-funded-year-design-20261023.md','result_file':str((OUT/'result.md').relative_to(ROOT)),
              'artifacts':{p.name:digest(p) for p in [Path(__file__),OUT/'checks.json']}}
    (OUT/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+chr(10))
    print(json.dumps({'passed':report['passed'],'paths':len(runs),'checks':len(checks),'failures':[c for c in checks if not c['passed']]}))
    if not report['passed']: raise SystemExit(1)


if __name__=='__main__':
    main()
