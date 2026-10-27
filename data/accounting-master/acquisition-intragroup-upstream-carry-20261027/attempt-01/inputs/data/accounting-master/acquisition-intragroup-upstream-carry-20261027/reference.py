"""Two-year group opening bridge and retained inventory-margin realisation."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from copy import deepcopy
import importlib.util,json
H=Path(__file__).resolve().parent;R=H.parents[2];S=H.parent/'acquisition-intragroup-upstream-20261027'
spec=importlib.util.spec_from_file_location('carry_prior',S/'reference.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
h=base.h;num=base.num;fmt=base.fmt;serial=base.serial;FLAGS=base.FLAGS
PROFILE='ConditionalUpstreamCarry/1'
INCOME={'revenue','merchandise_revenue','cost_of_sales','depreciation','operating_expense','current_tax_expense','intragroup_deferred_tax_expense','tax_expense','inventory_tax_reversal_expense'}
def close_accounts(balances,group=False,nci_profit=F(0)):
    out={k:num(v) for k,v in balances.items()};out.setdefault('P.retained_post',F(0));out.setdefault('S.retained_post',F(0))
    for key in list(out):
        owner,name=key.split('.')
        if name in INCOME:
            target=('S' if owner=='group' else owner)+'.retained_post'
            out[target]+=out[key];out[key]=F(0)
    if group:out['S.retained_post']+=nci_profit;out['group.nci']-=nci_profit
    return out
def aggregate(adjusted):
    out={}
    for key,value in adjusted.items():
        if not value:continue
        entity,name=key.split('.')
        if name=='capital' and entity=='P':name='parent_capital'
        if name=='retained_post':name=entity+'_retained_post'
        out[name]=out.get(name,F(0))+value
    return serial({k:v for k,v in out.items() if v})
def report(body):
    try:
        h.fields(body,['profile','payload','expected_payload_sha256'],'envelope');h.need(body['profile']==PROFILE,'profile');p=body['payload']
        h.need(len(json.dumps(body,allow_nan=False))<1000000,'request_size');h.need(h.digest(p)==body['expected_payload_sha256'],'payload_binding')
        h.fields(p,['prior_request','prior_result_sha256','source_lock_sha256','opening_legal','opening_group','opening_sha256','period','ownership','sale','equipment','tax_continuation'],'payload')
        lock=H/'predecessor-lock.json';h.need(sha256(lock.read_bytes()).hexdigest()==p['source_lock_sha256'],'source_lock_binding')
        for path,d in json.loads(lock.read_text()).items():h.need(sha256((R/path).read_bytes()).hexdigest()==d,'protected_dependency:'+path)
        prior=base.report(p['prior_request']);h.need(prior['status'] in ['conditional_upstream_worksheet','tax_method_required'],'prior:'+prior.get('reason',prior['status']))
        h.need(h.digest(prior)==p['prior_result_sha256'],'prior_binding')
        bp=p['prior_request']['payload'];sp=bp['base_request']['payload']['symbolic_request']['payload']
        h.need(sp['ownership']['fraction']=='3/4' and sp['ownership']['nci_election']=='proportional' and num(bp['base_request']['payload']['consideration']['cash'])==120,'selected_prior_scope')
        h.need(p['ownership']=='unchanged_75_percent_ordinary_control_through_2026','ownership_continuity')
        h.need(p['period']==dict(start='2026-01-01T00:00:00Z',end_exclusive='2027-01-01T00:00:00Z'),'period')
        h.need(all(prior['original_books'][e]['snapshots']['closing']['at']==p['period']['start'] for e in ['P','S']),'prior_closing_date')
        h.need(p['equipment']==dict(legal_depreciation='14/1',additional_depreciation='4/1',tax_release='1/1',premise='Supplied full-year equipment and tax schedules; no inferred useful life'),'equipment_schedule_required')
        earlier=num(p['prior_request']['payload']['external_sale']['fraction']);h.need(earlier in [F(0),F(1,2)],'selected_prior_resale')
        sale=p['sale'];h.fields(sale,['id','at','fraction_of_remaining','receipts','legal_cost','currency','unit','recognition'],'sale')
        h.need(sale['id']=='external-year2-P-X' and sale['at']=='2026-06-01T00:00:00Z','sale_identity_date')
        h.need(sale['currency']=='USD' and sale['unit']=='currency_unit','sale_units')
        fraction=num(sale['fraction_of_remaining']);h.need(fraction in [F(0),F(1,2),F(1)],'selected_sale_fraction')
        sold=(1-earlier)*fraction;h.need(num(sale['receipts'])==40*sold and num(sale['legal_cost'])==30*sold,'sale_amounts')
        h.need(sale['recognition']=='Stipulated qualifying external control transfer at fixed cash price','revenue_premise')
        h.need(p['tax_continuation'] in ['supplied_same_rates_recoverability_and_upstream_allocation','unresolved'],'tax_continuation')
        if prior['status']=='tax_method_required' or p['tax_continuation']=='unresolved':
            return dict(profile=PROFILE,status='tax_method_required',**FLAGS,prior_result=deepcopy(prior),request=deepcopy(body),outstanding=['complete_known_tax_opening_and_second_year_method'])
        recognised=bp['tax']['recognition']=='stipulated_recoverable'
        reversal=F(5,2)*sold if recognised else F(0)
        raw={e+'.'+k:v for e in ['P','S'] for k,v in prior['original_books'][e]['snapshots']['closing']['balances'].items()}
        legal=close_accounts(raw);group=close_accounts(prior['closing_worksheet']['adjusted'],True,num(prior['report']['nci_profit']))
        legal_expected=serial(legal);group_expected=serial(group)
        h.need(h.digest(dict(legal=p['opening_legal'],group=p['opening_group']))==p['opening_sha256'],'opening_binding')
        h.need(p['opening_legal']==legal_expected and p['opening_group']==group_expected,'complete_opening_carry')
        h.need(sum(legal.values())==0 and sum(group.values())==0,'opening_balance')
        h.need(-group['P.capital']-group['P.retained_post']-group['S.retained_post']==num(prior['report']['owners_equity_closing']),'opening_owners')
        h.need(-group['group.nci']==num(prior['report']['nci_closing']),'opening_nci')
        bridge={k:group.get(k,F(0))-legal.get(k,F(0)) for k in sorted(set(group)|set(legal))}
        h.need(sum(bridge.values())==0,'bridge_balance')
        events=[]
        def add(id,entries,origin):
            h.need(sum(entries.values())==0,'event_balance')
            events.append(dict(id=id,at=sale['at'] if id=='outside-sale' else '2026-12-31T00:00:00Z',origin=origin,entries=serial(entries)))
        if sold:add('outside-sale',{'P.cash':40*sold,'P.merchandise_revenue':-40*sold,'P.cost_of_sales':30*sold,'P.inventory':-30*sold},sale['id'])
        add('legal-depreciation',{'S.depreciation':F(14),'S.equipment':F(-14)},'Supplied year2 legal schedule')
        add('buyer-current-tax',{'P.current_tax_expense':F(5,2)*sold,'P.current_tax_payable':-F(5,2)*sold},'Supplied year2 buyer tax')
        closing=deepcopy(legal)
        for event in events:
            for key,value in event['entries'].items():closing[key]+=num(value)
        journals=[dict(id='carried-opening-bridge',at=p['period']['start'],origin='Exact prior-year closed group minus closed legal accounts; no new acquisition',entries=serial(bridge))]
        def adjustment(id,entries,attribution,origin):
            h.need(sum(entries.values())==0,'adjustment_balance')
            journals.append(dict(id=id,at='2026-12-31T00:00:00Z',origin=origin,profit_attribution=attribution,entries=serial(entries)))
        adjustment('inventory-margin-release',{'P.inventory':10*sold,'S.cost_of_sales':-10*sold},'subsidiary_ordinary_rights','Release carried upstream inventory adjustment')
        adjustment('inventory-tax-reversal',{'group.inventory_deferred_tax_asset':-reversal,'S.inventory_tax_reversal_expense':reversal},'subsidiary_ordinary_rights','Use carried deductible inventory difference')
        adjustment('acquired-basis-depreciation',{'S.equipment':F(-4),'group.depreciation':F(4)},'subsidiary_ordinary_rights','Supplied continuing acquisition basis')
        adjustment('acquired-tax-release',{'group.deferred_tax':F(1),'group.tax_expense':F(-1)},'subsidiary_ordinary_rights','Supplied continuing acquisition tax schedule')
        adjusted=deepcopy(closing)
        for entry in journals:
            for key,value in entry['entries'].items():adjusted[key]=adjusted.get(key,F(0))+num(value)
        h.need(sum(adjusted.values())==0,'closing_balance')
        profit=-sum(v for k,v in adjusted.items() if k.split('.')[1] in INCOME)
        subsidiary=10*sold-reversal-17;nci_profit=subsidiary/4;owners_profit=profit-nci_profit
        assets=sum(v for k,v in adjusted.items() if k.split('.')[1] in ['cash','equipment','inventory','investment','receivable','goodwill','inventory_deferred_tax_asset'])
        liabilities=-sum(v for k,v in adjusted.items() if k.split('.')[1] in ['payable','intragroup_payable','current_tax_payable','deferred_tax'])
        owners=num(prior['report']['owners_equity_closing'])+owners_profit;nci=num(prior['report']['nci_closing'])+nci_profit
        h.need(assets-liabilities==owners+nci,'group_equity_roll')
        cash=sum(adjusted[e+'.cash'] for e in ['P','S']);h.need(cash==num(prior['report']['cash']['closing'])+40*sold,'cash_roll')
        financial=serial(dict(profit=profit,owners_profit=owners_profit,nci_profit=nci_profit,assets=assets,liabilities=liabilities,equity=owners+nci,owners_equity=owners,nci=nci,cash=cash,inventory=20*(1-earlier-sold),equipment=F(63),goodwill=F(135,4),inventory_deferred_tax_asset=F(5,2)*(1-earlier-sold) if recognised else F(0),acquired_deferred_tax_liability=F(7,2),current_tax_payable=F(5,2)*(1+earlier+sold)))
        return dict(profile=PROFILE,status='conditional_carry_worksheet',**FLAGS,request_sha256=h.digest(body),prior_result_sha256=h.digest(prior),opening_legal=legal_expected,opening_group=group_expected,opening_bridge=serial(bridge),legal_journals=events,closing_legal=serial(closing),group_journals=journals,closing_adjusted=serial(adjusted),closing_balances=aggregate(adjusted),report=financial,prior_report=deepcopy(prior['report']),cash_origins=[] if not sold else [dict(entity='P',counterparty='X',at=sale['at'],amount=fmt(40*sold),classification='operating',origin=sale['id'])],outstanding=['actual_tax_revenue_and_depreciation_facts','multi_lot_impairment_fx_ownership','general_calendar_source_actor_and_complete_reports'])
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:350] or type(exc).__name__)
