"""Finite P17 arithmetic worksheet. No AccDSL runtime or accounting approval.

Inputs/expected schedules are declarative and hashed. The worksheet independently
derives them using rational arithmetic and checks selected journal sums against
economic roll-forwards. Adverse cases check that balance alone misses bad methods.
"""
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
METHODS = ROOT / 'docs/design/proposal/methods'
FIXTURE = METHODS / 'method-cases-v1.json'
START = time.monotonic()
cases = json.loads(FIXTURE.read_text())['cases']
checks = []


def convert(x):
    if isinstance(x, dict):
        return {k: convert(v) for k, v in x.items()}
    if isinstance(x, list):
        return [convert(v) for v in x]
    return F(x)


def same(label, actual, expected):
    ok = actual == expected
    checks.append({'id': label, 'pass': ok, 'actual': actual, 'expected': expected})


def truth(label, actual):
    same(label, bool(actual), True)


def case(name):
    r = cases[name]
    return convert(r['inputs']), convert(r['expected'])


def results(name, actual):
    expected = convert(cases[name]['expected'])
    same(name + '.output_keys', set(actual), set(expected))
    for key, value in actual.items():
        same(name + '.' + key, value, expected.get(key))


def post(book, name, **lines):
    """Debit-positive journal. A separate economic derivation checks its meaning."""
    lines = {k: F(v) for k, v in lines.items()}
    same(name + '.journal_balance', sum(lines.values()), 0)
    for account, amount in lines.items():
        book[account] += amount


# Revenue: two independently ordered journals compared with the contract totals.
i, e = case('revenue')
rev, collection = i['revenue'], i['collection']
rev_out = {}
for bill in i['billings']:
    for order in ('perform_first', 'bill_first'):
        b = defaultdict(F)
        if order == 'perform_first':
            post(b, f'revenue.{bill}.{order}.perform', ca=rev, revenue=-rev)
            post(b, f'revenue.{bill}.{order}.bill', ar=bill, ca=-min(rev, bill), cl=-max(bill-rev, 0))
        else:
            post(b, f'revenue.{bill}.{order}.bill', ar=bill, cl=-bill)
            if bill == 80:
                rev_out['prebill80'] = [b['ar'], b['ca'], -b['cl'], b['cash'], -b['revenue']]
            post(b, f'revenue.{bill}.{order}.perform', cl=min(bill, rev), ca=max(rev-bill, 0), revenue=-rev)
        post(b, f'revenue.{bill}.{order}.collect', cash=collection, ar=-collection)
        row = [b['ar'], b['ca'], -b['cl'], b['cash'], -b['revenue']]
        same(f'revenue.{bill}.{order}.recurrence', row, [bill-collection, max(rev-bill, 0), max(bill-rev, 0), collection, rev])
        rev_out['bill'+str(bill)] = row
results('revenue', rev_out)
# The old balanced prebilling error preserves net assets but violates CA/CL.
truth('adverse.prebill_balanced_but_wrong', 80+60-80 == 60 and [60,80] != [0,20])

i, e = case('inventory')
qty = sum(q for q,c in i['lots']); cost = sum(q*c for q,c in i['lots'])
remaining = i['sold']; fifo = F(0)
for q,c in i['lots']:
    used = min(q, remaining); fifo += used*c; remaining -= used
stock = cost-fifo; average = cost/qty*i['sold']; n1,n2,n3=i['nrv']
results('inventory', dict(fifo_cost=fifo, fifo_stock=stock, average_cost=average,
    average_stock=cost-average, margins=[i['sales']-fifo,i['sales']-average],
    write_down=stock-n1, reversal=n2-n1, cap=min(stock,n3)))
i,e=case('ppe'); dep=(i['cost']-i['residual'])/i['life']
results('ppe', dict(first_charge=dep,next_charge=(i['cost']-dep-i['residual'])/i['new_remaining_life']))

i,e=case('lease_tax')
payments=i['payments']; rate=i['rate']; tax=i['tax_rate']
pv=sum(c/(1+rate)**t for t,c in enumerate(payments,1)); dep=pv/len(payments)
liab=rou=pv; dta=dtl=pv*tax; cash=eq=i['opening_cash']; payable=F(0)
b=defaultdict(F, cash=cash, equity=-eq)
post(b,'lease.start',rou=pv,lease=-pv,dta=dta,dtl=-dtl)
actual=dict(initial=[pv,dta,dtl],interest=[],profit=[],pretax=[],tax=[],deferred_expense=[],ocf=[],closing=[])
for t,payment in enumerate(payments,1):
    interest=liab*rate; next_liab=liab+interest-payment; next_rou=rou-dep
    new_dta=next_liab*tax; new_dtl=next_rou*tax
    deferred=(dta-new_dta)-(dtl-new_dtl)
    current=(i['revenue']-i['cash_cost']-payment)*tax
    pretax=i['revenue']-i['cash_cost']-dep-interest; expense=current+deferred; profit=pretax-expense
    operating=i['revenue']-i['cash_cost']-payable
    cash+=operating-payment; eq+=profit
    post(b,f'lease.y{t}.ops',cash=i['revenue']-i['cash_cost'],income=-i['revenue'],opex=i['cash_cost'])
    post(b,f'lease.y{t}.interest',interest=interest,lease=-interest)
    post(b,f'lease.y{t}.pay',lease=payment,cash=-payment)
    post(b,f'lease.y{t}.dep',dep=dep,rou=-dep)
    post(b,f'lease.y{t}.tax_settle',tax_payable=payable,cash=-payable)
    post(b,f'lease.y{t}.current_tax',tax_expense=current,tax_payable=-current)
    post(b,f'lease.y{t}.deferred',dta=new_dta-dta,dtl=dtl-new_dtl,tax_expense=deferred)
    row=[cash,next_rou,new_dta,next_liab,new_dtl,current,eq]
    book_equity=-b['equity']-sum(b[a] for a in ('income','opex','interest','dep','tax_expense'))
    same(f'lease.y{t}.economic_vs_journal',row,[b['cash'],b['rou'],b['dta'],-b['lease'],-b['dtl'],-b['tax_payable'],book_equity])
    same(f'lease.y{t}.statement',cash+next_rou+new_dta,next_liab+new_dtl+current+eq)
    same(f'lease.y{t}.indirect_ocf',profit+dep+interest+deferred+current-payable,operating)
    for key,val in [('interest',interest),('profit',profit),('pretax',pretax),('tax',expense),('deferred_expense',deferred),('ocf',operating),('closing',row)]: actual[key].append(val)
    liab,rou,dta,dtl,payable=next_liab,next_rou,new_dta,new_dtl,current
modified=sum(c/(1+i['modified_rate'])**t for t,c in enumerate(i['modified_payments'],1))
base_year1=pv*(1+rate)-payments[0]
actual['modification']=[modified,modified-base_year1,pv-dep+modified-base_year1]
results('lease_tax',actual)
truth('adverse.expense_is_not_cash_tax',e['closing'][0][0]-e['tax'][0] != e['closing'][0][0])

i,e=case('debt'); p=i['proceeds']; r=i['rate']; terminal=i['terminal']; y1=p*(1+r)
newpv=i['substantial_terminal']/(1+r); modpv=i['reduced_terminal']/(1+r)
results('debt',dict(carrying=[p,y1,y1*(1+r)],interest=[p*r,y1*r],replacement_pv=newpv,
    difference_ratio=abs(newpv-y1)/y1,extinguishment_loss=i['new_fair_value']-y1,
    modified_pv=modpv,modification_gain=y1-modpv,modified_interest=modpv*r,
    repurchase_gain=y1-i['repurchase'],unpaid=terminal-i['cash_available']))
same('debt.original_pv',terminal/(1+r)**i['years'],p)
truth('adverse.fee_changes_eir',terminal/(1+r)**i['years'] != p-i['fee'])
i,e=case('shares')
results('shares',dict(cash_flows=[i['issued']*i['issue_price'],-i['repurchased']*i['repurchase_price'],i['reissued']*i['reissue_price']],
    outstanding=i['issued']-i['repurchased']+i['reissued'],treasury=i['repurchased']-i['reissued'],reissue_equity=i['reissued']*(i['reissue_price']-i['repurchase_price']),
    compound_equity=i['compound_proceeds']-i['compound_debt'],compound_interest=i['compound_proceeds']-i['compound_debt'],conversion_cash=F(0)))

i,e=case('group'); net=i['assets']-i['liabilities']; nci=net*(1-i['ownership']); goodwill=i['purchase']+nci-net
net_later=net+i['profit']; nci_later=net_later*(1-i['ownership']); transfer=net_later*i['extra_fraction']
results('group',dict(net_acquired=net,nci_initial=nci,goodwill=goodwill,profit_parent=i['profit']*i['ownership'],nci_later=nci_later,nci_transfer=transfer,
    parent_equity_reduction=i['extra_price']-transfer,nci_after_purchase=nci_later-transfer,
    sale_gain=i['sale_all']+nci_later-net_later-goodwill,partial_sale_gain=i['sale_partial']+i['retained_fv']+nci_later-net_later-goodwill))
i,e=case('intragroup'); margin=i['internal_price']-i['external_cost']
results('intragroup',dict(eliminated_profit=margin,group_inventory=i['internal_price']-margin,outside_profit=i['outside_sale']-i['external_cost'],dta=(i['tax_base']-i['external_cost'])*i['tax_rate']))
i,e=case('fx'); inv=i['purchase_foreign']*i['initial_rate']; payable=i['purchase_foreign']*i['closing_rate']; cash=i['purchase_foreign']*i['settlement_rate']
assets=(i['net_opening']+i['profit'])*i['closing_rate']; income=i['profit']*i['profit_rate']; oci=assets-i['net_opening']*i['initial_rate']-income
same('fx.oci_independent',oci,i['net_opening']*(i['closing_rate']-i['initial_rate'])+i['profit']*(i['closing_rate']-i['profit_rate']))
results('fx',dict(inventory=inv,payable_close=payable,fx_loss=payable-inv,cash_settlement=cash,settlement_gain=payable-cash,assets_translated=assets,profit_translated=income,oci=oci,parent_oci=oci*i['ownership'],nci_oci=oci*(1-i['ownership'])))

i,e=case('bank'); r=i['rate']; shortfall=i['terminal']-i['recovery']; initial=i['initial_default_masses'][0]*shortfall/(1+r)**2
gross1=i['loan']*(1+r); allowance1=i['later_pd']*shortfall/(1+r); impaired=gross1-i['recovery']/(1+r); interest=(gross1-impaired)*r
b=defaultdict(F,cash=i['opening_cash'],deposits=-i['deposits'],equity=-i['opening_equity']); rows=[]
def bank_row():
    eq=-b['equity']-b['impairment']-b['interest_income']
    row=[b['cash'],b['loan'],-b['allowance'],-b['deposits'],eq]
    same(f'bank.row{len(rows)}.statement',row[0]+row[1]-row[2],row[3]+row[4]); rows.append(row)
post(b,'bank.origination',loan=i['loan'],cash=-i['loan'])
post(b,'bank.initial_ecl',impairment=initial,allowance=-initial); bank_row()
post(b,'bank.y1_accrual',loan=i['loan']*r,interest_income=-i['loan']*r)
post(b,'bank.sicr',impairment=allowance1-initial,allowance=initial-allowance1); bank_row()
post(b,'bank.impairment',impairment=impaired-allowance1,allowance=allowance1-impaired); bank_row()
post(b,'bank.y2_accrual',loan=gross1*r,interest_income=-interest,allowance=interest-gross1*r); bank_row()
post(b,'bank.collect',cash=i['recovery'],loan=-i['recovery'])
post(b,'bank.writeoff',allowance=i['terminal']-i['recovery'],loan=i['recovery']-i['terminal']); bank_row()
results('bank',dict(initial_ecl=initial,initial_lifetime_ecl=sum(i['initial_default_masses'])*shortfall/(1+r)**2,
    survival_only_pd=i['initial_default_masses'][1]/(1-i['initial_default_masses'][0]),year1_ecl=allowance1,credit_impaired_allowance=impaired,net_interest=interest,
    allowance_accretion=gross1*r-interest,cash_end=b['cash'],total_interest=-b['interest_income'],total_impairment=b['impairment'],profit=-b['interest_income']-b['impairment'],rows=rows))
same('bank.lifetime_cash_loss',-b['interest_income']-b['impairment'],i['recovery']-i['loan'])
truth('adverse.gross_interest_after_impairment',gross1*r!=interest)
i,e=case('funding'); capital=i['equity']-i['deduction']
results('funding',dict(shortfall=max(i['withdrawal']-i['cash']-i['facility'],0),capital=capital,ratio=capital/i['rwa']))

i,e=case('insurance'); fcf=sum(i['claims'])-i['premium']+i['ra']; csm=-fcf; cash=i['premium']; lrc=cash; equity=F(0); rows=[]; revenues=[]; profits=[]
remaining_csm=csm; remaining_units=sum(i['service_units'])
for claim,ra,units in zip(i['claims'],i['ra_releases'],i['service_units']):
    release=remaining_csm*units/remaining_units; revenue=claim+ra+release; profit=revenue-claim
    remaining_csm-=release; remaining_units-=units; lrc-=revenue; cash-=claim; equity+=profit
    rows.append([cash,lrc,equity]); revenues.append(revenue); profits.append(profit); same(f'insurance.year{len(rows)}.statement',cash,lrc+equity)
csm1=csm*i['service_units'][1]/sum(i['service_units']); loss=max(i['future_increase']-csm1,0)
fcf1=i['claims'][1]+i['ra']-i['ra_releases'][0]+i['future_increase']; reversal=min(loss,i['future_decrease']); restored=i['future_decrease']-reversal
results('insurance',dict(initial_fcf=fcf,initial_csm=csm,revenue=revenues,profit=profits,rows=rows,loss_component=loss,onerous_lrc=fcf1,reversal=reversal,restored_csm=restored,revised_fcf=fcf1-i['future_decrease'],revised_lrc=fcf1-i['future_decrease']+restored,lic_change=i['incurred_increase']))
truth('adverse.loss_component_double_count',fcf1+loss!=fcf1)
i,e=case('insurance_nonzero'); r=i['rate']; pv=sum(c/(1+r)**t for t,c in enumerate(i['claims'],1)); csm=i['premium']-pv-i['ra']; initial_csm=csm
cash=i['premium']; ra=i['ra']; remaining_units=sum(i['units']); equity=F(0); rows=[]; revenues=[]; finances=[]; profits=[]; releases=[]
for claim,ra_release,units in zip(i['claims'],i['ra_releases'],i['units']):
    finance=pv*r+csm*r; pv=pv*(1+r)-claim; csm*=1+r; release=csm*units/remaining_units; csm-=release; remaining_units-=units
    revenue=claim+ra_release+release; profit=revenue-claim-finance; ra-=ra_release; cash-=claim; equity+=profit; liability=pv+ra+csm
    rows.append([cash,liability,equity]); revenues.append(revenue); finances.append(finance); profits.append(profit); releases.append(release)
    same(f'insurance_nonzero.year{len(rows)}.statement',cash,liability+equity)
results('insurance_nonzero',dict(claim_pv=sum(c/(1+r)**t for t,c in enumerate(i['claims'],1)),initial_csm=initial_csm,revenue=revenues,finance=finances,profit=profits,csm_release=releases,rows=rows,total_revenue=sum(revenues),total_finance=sum(finances)))
same('insurance_nonzero.revenue_cash_reconcile',sum(revenues)-sum(finances),i['premium'])
i,e=case('insurance_onerous'); lrc=i['future_claims']+i['ra']; ratio=i['loss_component']/lrc; allocation=[i['future_claims']*ratio,i['ra']*ratio]; reversal=sum(allocation); revenue=lrc-reversal; profit=revenue-i['future_claims']+reversal
results('insurance_onerous',dict(allocation=allocation,revenue=revenue,reversal=reversal,year2_profit=profit,cash_end=i['opening_cash']-i['future_claims'],equity_end=i['original_year1_profit']-i['loss_component']+profit,loss_component_end=i['loss_component']-reversal))
truth('adverse.onerous_revenue_double_reversal',lrc-i['future_claims']+reversal!=profit)
i,e=case('claims'); tri=i['triangle']; factors=[]
for k in range(max(map(len,tri))-1):
    matched=[row for row in tri if len(row)>k+1]; factors.append(sum(row[k+1] for row in matched)/sum(row[k] for row in matched))
ultimate=[]
for row in tri:
    amount=row[-1]
    for factor in factors[len(row)-1:]: amount*=factor
    ultimate.append(amount)
results('claims',dict(factors=factors,ultimate=ultimate,outstanding=sum(u-row[-1] for u,row in zip(ultimate,tri)),last_factor_observations=sum(len(row)>len(factors) for row in tri),reinsurance=i['gross_claim']*i['quota_share']*i['collectability']))

i,e=case('pension'); dbo=i['dbo']+i['service']+i['dbo']*i['rate']-i['benefits']+i['actuarial_loss']; assets=i['assets']+i['actual_return']+i['contribution']-i['benefits']; expense=i['service']+(i['dbo']-i['assets'])*i['rate']; oci=i['actuarial_loss']-(i['actual_return']-i['assets']*i['rate']); pv=i['unit_benefit']/(1+i['unit_discount'])
same('pension.net_rollforward',dbo-assets,i['dbo']-i['assets']+expense+oci-i['contribution'])
results('pension',dict(dbo_end=dbo,assets_end=assets,net_liability=dbo-assets,expense=expense,oci_loss=oci,year1_unit_pv=pv,year2_unit_interest=pv*i['unit_discount'],unit_settlement=pv*(1+i['unit_discount'])+i['unit_benefit']))
i,e=case('impairment'); total=i['assets']+i['goodwill']-i['recoverable']; gw=min(i['goodwill'],total); standalone=i['standalone']-i['lower_recoverable']
results('impairment',dict(total_loss=total,goodwill_loss=gw,other_loss=total-gw,floor_remaining=total-gw-(i['assets']-i['floor']),standalone_loss=standalone,reversal_cap=min(i['later_recoverable'],i['standalone'])-i['lower_recoverable']))
i,e=case('awards'); eq=i['granted']*i['grant_fv']/i['years']; liability=i['granted']*i['cash_fv1']/i['years']; settle=i['vested']*i['cash_fv2']
results('awards',dict(equity_expenses=[eq,i['vested']*i['grant_fv']-eq],cash_expenses=[liability,settle-liability],cash_settlement=settle))
i,e=case('valuation')
results('valuation',dict(quoted_value=i['units']*i['quoted_price'],pv=i['payment']/(1+i['rate']),net_borrow_cost=i['borrowing']*i['borrow_rate']-i['temporary_income']))
i,e=case('lease_basis'); liability=rou=i['opening']; us=[]; reductions=[]; expenses=[]; finance=[]
for t,payment in enumerate(i['payments'],1):
    interest=liability*i['rate']; liability+=interest-payment; reduction=i['us_single_expense']-interest; rou-=reduction
    us.append(rou); reductions.append(reduction); finance.append(i['opening']*(1-F(t,len(i['payments'])))); expenses.append(i['opening']/len(i['payments'])+interest)
results('lease_basis',dict(us_rou=us,us_rou_reduction=reductions,finance_rou=finance,finance_expense=expenses))

i,e=case('finite_law'); joint=[p*l for p,l in zip(i['prior'],i['likelihood'])]; evidence=sum(joint); posterior=[x/evidence for x in joint]
results('finite_law',dict(evidence=evidence,posterior=posterior,unresolved_mass=posterior[1]))
truth('adverse.success_only_renormalization',posterior[0]!=1 and sum(posterior)==1)
i,e=case('gaussian'); precision=1/i['variance']+i['h']**2/i['noise_variance']; info=i['mean']/i['variance']+i['h']*i['observation']/i['noise_variance']; v=1/precision; m=info/precision
v2=1/(precision+i['h']**2/i['noise_variance']); m2=(info+i['h']*i['observation']/i['noise_variance'])*v2
results('gaussian',dict(mean=m,variance=v,cash_mean=i['cash_constant']+i['cash_slope']*m,cash_variance=i['cash_slope']**2*v,independent_second_mean=m2,independent_second_variance=v2))
truth('adverse.duplicate_observation_changes_target',[m,v]!=[m2,v2])
i,e=case('causal'); observed=i['x_coefficient']+i['u_coefficient']; intervened=i['x_coefficient']*i['intervene_x']+i['u_coefficient']*i['prob_u1']
results('causal',dict(observed_mean=observed,intervention_mean=intervened))

i,e=case('joint_forecast'); source=json.loads((ROOT/'docs/design/fixtures/northstar.json').read_text()); forecast=convert(source['forecast'] | {'start':'0','end_exclusive':'0'}); opening=convert(source['expected']['2024H2'])
actual={k:[] for k in e}
same('northstar.fixture_opening_cash',i['opening_cash'],opening['cash']); same('northstar.fixture_opening_equity',i['opening_equity'],opening['equity'])
for x in i['x']:
    sales=forecast['demand_units']*forecast['price']; cogs=forecast['demand_units']*forecast['unit_cost']; dep=opening['plant_net']+forecast['capex_at_period_end']-i['ppe']; interest=5+2*x
    profit=(sales-cogs-forecast['payroll']-dep-interest)*(1-forecast['tax_rate']); tax=profit*forecast['tax_rate']/(1-forecast['tax_rate'])
    ocf=sales*forecast['current_sales_collection_fraction']+forecast['legacy_receivable_collections']-forecast['old_payables_paid']-forecast['new_purchases_paid']-forecast['payroll']-interest-tax
    cash=opening['cash']+ocf-forecast['capex_at_period_end']-forecast['dividend']; equity=opening['equity']+profit-forecast['dividend']; assets=cash+i['ar']+i['inventory']+i['ppe']
    for k,val in dict(interest=interest,profit=profit,cash=cash,equity=equity,assets=assets).items(): actual[k].append(val)
    same(f'northstar.x{x}.statement',assets,i['ap']+i['debt']+equity)
results('joint_forecast',actual)
truth('adverse.incompatible_marginal_maxima',1+1!=1)
i,e=case('rounding'); m=i['displayed']; s=i['scale']; value=i['literal_digits']*F(10)**i['scale_exponent']
results('rounding',dict(nearest_enclosure=[s*(m-F(1,2)),s*(m+F(1,2))],truncation_enclosure=[s*m,s*(m+1)],inline_value=value,double_scaled_value=value*F(10)**i['scale_exponent']))
i,e=case('roots'); same('roots.exact_half',i['half_factor']**2,1+i['rate_exact'])
same('roots.exact_interest',100*(i['half_factor']-1),e['exact_half_interest']); same('roots.proration',100*i['rate_exact']/2,e['incorrect_simple_interest'])
truth('roots.sqrt_enclosure',e['certified_sqrt_lower']**2<1+i['rate_irrational']<e['certified_sqrt_upper']**2)
lo,hi=i['root_bracket']; f=lambda r: i['payment']/(1+r)**2-i['proceeds_after_fee']
truth('roots.sign_bracket',f(lo)>0>f(hi))
for _ in range(int(i['bisect_steps'])):
    mid=(lo+hi)/2
    if f(mid)>0: lo=mid
    else: hi=mid
truth('roots.final_certificate',f(lo)>=0>=f(hi) and hi-lo<F(1,10**20))
truth('adverse.rounding_cell_crossed',F('1.0049')<F('1.005')<F('1.0051'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Source anchors and all frozen input bytes; these are provenance checks only.
register=json.loads((METHODS/'method-source-register-v1.json').read_text())
for source in register['sources']:
    same('source.'+source['id'],digest(ROOT/source['path']),source['sha256'])
for access in register['access']:
    for source in access['files']:
        same('access.'+source['path'],digest(ROOT/source['path']),source['sha256'])
for row in json.loads((METHODS/'source-translations-v1.json').read_text())['rows']:
    anchor=row['anchor']; path=ROOT/anchor['extraction_path']
    same('translation.'+row['id']+'.text_hash',digest(path),anchor['extraction_sha256'])
    same('translation.'+row['id']+'.original_hash',digest(ROOT/anchor['original_path']),anchor['original_sha256'])
    same('translation.'+row['id']+'.slice',path.read_text()[anchor['start']:anchor['end']],anchor['quote'])
baseline=json.loads((Path(__file__).parent/'baseline.json').read_text())
changed=[p for p,h in baseline['protected_hashes'].items() if not (ROOT/p).is_file() or digest(ROOT/p)!=h]
same('protected_files.changed',changed,[])
report={'schema':'accdsl.p17.document-diagnostic.v1','created_at':datetime.now(timezone.utc).isoformat(),
    'command':'python3 '+str(Path(__file__))+' '+sys.argv[1], 'environment':sys.version,
    'git_provenance':'frozen file hashes; no commit created', 'cpu_gpu':'CPU Fraction arithmetic; no GPU framework imported', 'seeds':'N/A deterministic arithmetic',
    'plan':'docs/plans/accounting-p17-direct-execution-20261006.md','wall_seconds':time.monotonic()-START,
    'remaining_campaign_hours':(1940875.230219879-time.monotonic())/3600,
    'script_sha256':digest(Path(__file__)), 'fixture_sha256':digest(FIXTURE),
    'inputs':{str(p.relative_to(ROOT)):digest(p) for p in sorted(METHODS.glob('*-v1.md'))+sorted(METHODS.glob('*-v1.json'))},
    'protected_files_verified':len(baseline['protected_hashes']), 'checks':checks,
    'pass':all(x['pass'] for x in checks),'count':len(checks),
    'scope':'Finite document calculations and source integrity only; no accounting authority, runtime conformance, empirical ranking or full-domain readiness.'}
destination=ROOT/sys.argv[1]
with destination.open('x') as f:
    json.dump(report,f,indent=2,ensure_ascii=False,default=lambda x:sorted(x) if isinstance(x,set) else str(x)); f.write('\n')
print(json.dumps({'pass':report['pass'],'checks':len(checks),'failed':[x for x in checks if not x['pass']], 'protected_files_verified':len(baseline['protected_hashes']),'report':str(destination)},default=str))
sys.exit(0 if report['pass'] else 1)
