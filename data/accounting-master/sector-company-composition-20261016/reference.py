"""Finite composition of immutable bank/insurance outputs into shared books."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import importlib.util,hashlib,json,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
SOURCE='docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'
BANK=OUT.parent/'dated-credit-schedules-20261016';INS=OUT.parent/'insurance-service-finance-origins-20261016'
FINDINGS={'compatible_historical_profiles','legal_opening_supported','control_retained','equal_ordinary_rights','no_goodwill_or_purchase_difference','event_rates_exact','tax_law_supplied','loss_dta_recovery_supported','guarantee_tax_deductible_as_booked','outside_basis_exception_supported','no_tax_on_translation','deposit_cash_equivalent','deposit_counterpart_verified','no_deposit_interest_or_movements','no_other_events','parent_cost_investment_policy','guarantee_ifrs9_scope','guarantee_ecl_supported','guarantee_service_release_supported','operating_cash_policy_supported'}
class Refusal(Exception):
    def __init__(self,status,reason):self.status=status;self.reason=reason
FINDINGS.update({'contractual_cash_allocation_supported','opening_guarantee_measurement_supported'})
def fail(reason,status='rejected'):raise Refusal(status,reason)
def shape(x,keys,reason):
    if not isinstance(x,dict) or set(x)!=set(keys):fail(reason)
def num(x):
    if x is None:fail('missing_amount','unresolved')
    if not isinstance(x,str) or len(x)>80:fail('number_encoding')
    try:q=Q(x)
    except (ValueError,ZeroDivisionError):fail('number_encoding')
    if str(q)!=x or abs(q)>10**12:fail('number_encoding')
    return q
def nn(x):
    q=num(x)
    if q<0:fail('negative_amount')
    return q
def findings(f,keys):
    shape(f,keys,'finding_shape')
    for k,v in f.items():
        if v is None:fail('missing_'+k,'unresolved')
        if type(v)!=bool:fail('finding_encoding')
        if not v:fail('outside_'+k,'unsupported')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def enc(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,list):return [enc(v) for v in x]
    if isinstance(x,dict):return {k:enc(v) for k,v in x.items()}
    return x
def point(x):
    if x['lower']!=x['upper']:fail('nonexact_component_outside_join','unsupported')
    return Q(x['lower'])
def component_reports():
    module('bounds',BANK/'bounds.py');bank=module('join_bank_reference',BANK/'reference.py');ins=module('join_insurance_reference',INS/'reference.py')
    # Adapt a protected performing request only by the documented annual event path.
    q=deepcopy(next(c['request'] for c in json.loads((BANK/'authored-cases.json').read_text())['cases'] if c['id']=='performing-prepayment'))
    e=deepcopy(q['events'][-1]);e.update(id='first',date='2026-01-01',information_date='2026-01-01',amount='55',close=False)
    f=deepcopy(e);f.update(id='final',date='2027-01-01',information_date='2027-01-01',amount='121/2',close=True);q['events']=[e,f]
    b=bank.calculate(q)
    iq=deepcopy(next(c['request'] for c in json.loads((INS/'authored-cases-v2.json').read_text())['cases'] if c['id']=='loss-service-finance'))
    i=ins.calculate(iq)
    if b['status']!='conditional_complete' or i['status']!='conditional_complete':fail('component_not_admitted','unsupported')
    return dict(bank=dict(request=q,result=b),insurance=dict(request=iq,result=i))
def tax(profit,loss,tau):
    old_dta=loss*tau;taxable=max(profit-loss,Q(0));new_loss=max(loss-profit,Q(0));current=taxable*tau;dta=new_loss*tau
    expense=current+old_dta-dta
    return dict(pretax=profit,current=current,deferred_expense=old_dta-dta,expense=expense,aftertax=profit-expense,loss=new_loss,dta=dta)
def calculate(req,reader=None):
    try:return enc(run(req,reader or (lambda p:(ROOT/p).read_bytes())))
    except Refusal as e:return dict(status=e.status,reason=e.reason,report=None,components=None,posts=False,mutations=[])
    except (ValueError,ZeroDivisionError):return dict(status='rejected',reason='numeric_domain',report=None,components=None,posts=False,mutations=[])
def run(q,reader):
    for x in json.loads((OUT/'input-lock.json').read_text())['files']:
        try:raw=reader(x['path'])
        except FileNotFoundError:fail('missing_protected_input','unresolved')
        if hashlib.sha256(raw).hexdigest()!=x['sha256']:fail('changed_protected_input')
    shape(q,{'wire','operation','context','opening','rates','tax_rate','ownership','deposit','guarantee','loan_cash_allocation','component_maps','findings'},'request_shape')
    if q['wire']!='SectorCompany/1' or q['operation']!='report':fail('wire_or_operation')
    shape(q['context'],{'group','parent','bank','insurer','presentation_currency','foreign_currency','rule','periods'},'context_shape')
    cx=q['context']
    if cx!=dict(group='G',parent='P',bank='B',insurer='I',presentation_currency='USD',foreign_currency='FCU',rule='EU2023/1803-original',periods=['2025-01-01/2026-01-01','2026-01-01/2027-01-01']):fail('context')
    findings(q['findings'],FINDINGS)
    op=q['opening'];shape(op,{'parent_cash','bank_cash','bank_deposits','insurer_cash','insurance_liability','parent_investment_bank','parent_investment_insurer'},'opening_shape')
    op={k:nn(v) for k,v in op.items()}
    if op['bank_cash']!=300 or op['bank_deposits']!=200 or op['insurer_cash']!=200 or op['insurance_liability']!=100:fail('component_opening_binding')
    rates=q['rates'];shape(rates,{'opening','period1_event','period1_close','period2_event','period2_close'},'rates_shape')
    rates={k:nn(v) for k,v in rates.items()}
    if any(v<=0 for v in rates.values()):fail('rate_domain')
    tau=nn(q['tax_rate'])
    if tau!=Q(1,5):fail('tax_rate_profile','unsupported')
    own=q['ownership'];shape(own,{'bank_initial','insurer','bank_after','purchase_price','purchase_timing'},'ownership_shape')
    bown=nn(own['bank_initial']);iown=nn(own['insurer']);after=nn(own['bank_after']);purchase=nn(own['purchase_price'])
    if not Q(1,2)<bown<=after<=1 or not Q(1,2)<iown<=1 or own['purchase_timing']!='after_period1_close':fail('ownership_profile','unsupported')
    if after==bown and purchase:fail('purchase_without_change')
    if after>bown and not purchase:fail('missing_purchase_consideration')
    if op['parent_investment_bank']!=100*bown*rates['opening'] or op['parent_investment_insurer']!=100*iown*rates['opening']:fail('investment_opening_binding')
    deposit=q['deposit'];shape(deposit,{'bank_record','insurer_record'},'deposit_shape')
    for name,row in deposit.items():
        shape(row,{'id','creditor','debtor','currency','amount','cutoff'},'deposit_record_shape')
        if row['id']!='D1' or row['creditor']!='I' or row['debtor']!='B' or row['currency']!='FCU' or row['cutoff']!='both-period-closes':fail('deposit_identity')
    if deposit['bank_record']!=deposit['insurer_record']:fail('deposit_mismatch')
    dep=nn(deposit['bank_record']['amount'])
    if dep!=20:fail('deposit_population','unsupported')
    guarantee=q['guarantee'];shape(guarantee,{'id','beneficiary','opening_unamortized','income_releases','ecl'},'guarantee_shape')
    if guarantee['id']!='EXT-G1' or guarantee['beneficiary']!='external_creditor':fail('guarantee_identity')
    g0=nn(guarantee['opening_unamortized'])
    if g0!=6 or guarantee['income_releases']!=['2','2'] or guarantee['ecl']!=['7','3']:fail('guarantee_profile','unsupported')
    maps=q['component_maps'];shape(maps,{'bank','insurance'},'map_shape')
    allocation=q['loan_cash_allocation']
    if not isinstance(allocation,list) or len(allocation)!=2:fail('loan_allocation_shape')
    for row in allocation:shape(row,{'principal','coupon_interest'},'loan_allocation_shape')
    if sum(nn(x['principal']) for x in allocation)!=102 or [nn(x['principal'])+nn(x['coupon_interest']) for x in allocation]!=[Q(55),Q(121,2)]:fail('loan_cash_allocation')
    if maps!=dict(bank=dict(source_entity='Synthetic Bank',target_entity='B',source_currency='CU',target_currency='FCU',unit_scale='1',opening_capital_action='ignore_component_capital'),insurance=dict(source_entity='Synthetic Insurer',target_entity='I',source_currency='CU',target_currency='FCU',unit_scale='1',opening_capital_action='ignore_component_capital')):fail('component_context_mapping')
    components=component_reports();br=components['bank']['result'];ir=components['insurance']['result']['report']
    bstages={s['id']:s for s in br['stages']};opening_equity_P=op['parent_cash']+op['parent_investment_bank']+op['parent_investment_insurer']-g0
    opening_nci=(200-100*bown-100*iown)*rates['opening'];opening_eq=opening_equity_P+opening_nci
    opening_cash=op['parent_cash']+(op['bank_cash']+op['insurer_cash']-dep)*rates['opening']
    group_cash=opening_cash;group_equity=opening_eq;parent_equity=opening_equity_P;nci=opening_nci
    Pcash=op['parent_cash'];Bcash=op['bank_cash'];Icash=op['insurer_cash'];Peq=opening_equity_P;Beq=Ieq=Q(100);investment=op['parent_investment_bank']+op['parent_investment_insurer']
    losses=dict(P=Q(0),B=Q(0),I=Q(0));g=g0;unam=g0;overlay=Q(0);rows=[];flow_records=[];last_interest=Q(0);last_loan_cash=Q(300);last_ins_cash=Q(200);last_rate=rates['opening']
    for idx in range(2):
        closing_rate=rates['period1_close' if idx==0 else 'period2_close'];event_rate=rates['period1_event' if idx==0 else 'period2_event']
        b=bstages['first' if idx==0 else 'final'];i=ir['rows'][idx]
        bprofit=point(b['interest'])-last_interest;last_interest=point(b['interest']);loan=point(b['net'])
        bank_component_cash=point(b['cash']);bflow=bank_component_cash-last_loan_cash;last_loan_cash=bank_component_cash
        iflow=num(i['cash'])-last_ins_cash;last_ins_cash=num(i['cash']);iprofit=num(i['profit'])
        unam-=num(guarantee['income_releases'][idx]);newg=max(unam,num(guarantee['ecl'][idx]));newoverlay=newg-unam
        service=num(guarantee['income_releases'][idx]);impairment=newoverlay-overlay;pprofit=service-impairment;g=newg;overlay=newoverlay
        tx={k:tax(v,losses[k],tau) for k,v in [('P',pprofit),('B',bprofit),('I',iprofit)]}
        for k in losses:losses[k]=tx[k]['loss']
        Bopening=Bcash;Iopening=Icash;Bcash+=bflow-tx['B']['current'];Icash+=iflow-tx['I']['current'];Pcash-=tx['P']['current']
        if min(Bcash,Icash,Pcash)<0:fail('legal_cash_funding','unsupported')
        boci=Beq*(closing_rate-last_rate)+tx['B']['aftertax']*(closing_rate-event_rate)
        ioci=Ieq*(closing_rate-last_rate)+tx['I']['aftertax']*(closing_rate-event_rate)
        Beq+=tx['B']['aftertax'];Ieq+=tx['I']['aftertax'];Peq+=tx['P']['aftertax']
        if Bcash+loan+tx['B']['dta']-op['bank_deposits']!=Beq or Icash+tx['I']['dta']-num(i['liability'])!=Ieq:fail('legal_financial_identity')
        bp=tx['B']['aftertax']*event_rate;ip=tx['I']['aftertax']*event_rate;profit=tx['P']['aftertax']+bp+ip;oci=boci+ioci
        nci_profit=(1-bown)*bp+(1-iown)*ip;nci_oci=(1-bown)*boci+(1-iown)*ioci
        parent_profit=profit-nci_profit;parent_oci=oci-nci_oci;nci+=nci_profit+nci_oci;parent_equity+=parent_profit+parent_oci
        nci_removed=Q(0);parent_transaction=Q(0);financing=Q(0)
        if idx==0 and after>bown:
            nci_removed=(after-bown)*Beq*closing_rate;parent_transaction=nci_removed-purchase;nci-=nci_removed;parent_equity+=parent_transaction
            Pcash-=purchase;investment+=purchase;financing=-purchase;bown=after
            if Pcash<0:fail('purchase_funding','unsupported')
        if Pcash+investment+tx['P']['dta']-g!=Peq:fail('parent_legal_identity')
        legal=dict(P=dict(cash=Pcash,investments=investment,dta=tx['P']['dta'],guarantee=g,equity=Peq),B=dict(cash=Bcash,loan=loan,dta=tx['B']['dta'],deposits=op['bank_deposits'],equity=Beq),I=dict(cash=Icash,dta=tx['I']['dta'],insurance_liability=num(i['liability']),equity=Ieq))
        cash=Pcash+(Bcash+Icash-dep)*closing_rate;assets=cash+(loan+tx['B']['dta']+tx['I']['dta'])*closing_rate+tx['P']['dta'];liabilities=(op['bank_deposits']-dep+num(i['liability']))*closing_rate+g;equity=assets-liabilities
        if equity!=parent_equity+nci or equity!=group_equity+profit+oci+financing:fail('group_equity_identity')
        if nci!=(1-bown)*Beq*closing_rate+(1-iown)*Ieq*closing_rate:fail('nci_close_identity')
        # Cash-origin translation: origination occurs at opening, all other events at the supplied period rate.
        bank_event=bflow+100 if idx==0 else bflow
        operating=(bank_event-tx['B']['current']+iflow-tx['I']['current'])*event_rate-tx['P']['current']-(100*rates['opening'] if idx==0 else 0)
        bfx=Bopening*(closing_rate-last_rate)+(bank_event-tx['B']['current'])*(closing_rate-event_rate)-(100*(closing_rate-rates['opening']) if idx==0 else 0)
        ifx=Iopening*(closing_rate-last_rate)+(iflow-tx['I']['current'])*(closing_rate-event_rate)
        eliminated_fx=dep*(closing_rate-last_rate);fx=bfx+ifx-eliminated_fx
        if group_cash+operating+financing+fx!=cash:fail('cash_fx_identity')
        flows=[dict(owner='B',kind='principal_receipt',amount=nn(allocation[idx]['principal']),rate=event_rate),dict(owner='B',kind='coupon_interest_receipt',amount=nn(allocation[idx]['coupon_interest']),rate=event_rate),dict(owner='B',kind='current_tax',amount=-tx['B']['current'],rate=event_rate),dict(owner='I',kind='claim_payment',amount=iflow,rate=event_rate),dict(owner='I',kind='current_tax',amount=-tx['I']['current'],rate=event_rate),dict(owner='P',kind='current_tax',amount=-tx['P']['current'],rate=Q(1))]
        if idx==0:flows=[dict(owner='B',kind='advance',amount=Q(-102),rate=rates['opening']),dict(owner='B',kind='integral_fee',amount=Q(2),rate=rates['opening'])]+flows
        if financing:flows.append(dict(owner='P',kind='nci_purchase',amount=financing,rate=Q(1)))
        flow_records.extend(flows)
        rows.append(dict(period=idx+1,legal=legal,tax=tx,guarantee=dict(unamortized=unam,ecl=num(guarantee['ecl'][idx]),liability=g,service_income=service,impairment=impairment,pretax=pprofit),
            group=dict(cash=cash,assets=assets,liabilities=liabilities,equity=equity,parent_equity=parent_equity,nci=nci,profit=profit,oci=oci,parent_profit=parent_profit,nci_profit=nci_profit,parent_oci=parent_oci,nci_oci=nci_oci,bank_profit=bp,bank_oci=boci,insurer_profit=ip,insurer_oci=ioci),
            ownership=dict(bank_fraction=bown,nci_removed=nci_removed,parent_equity_transaction=parent_transaction,cash=financing),
            deposit_elimination=dict(id='D1',cash=dep*closing_rate,deposits=dep*closing_rate,cash_fx=eliminated_fx),
            cash_flow=dict(opening=group_cash,operating=operating,financing=financing,fx=fx,closing=cash,origins=flows)))
        group_cash=cash;group_equity=equity;last_rate=closing_rate
    return dict(status='conditional_complete',reason='finite_shared_sector_close',posts=False,mutations=[],components=components,
        report=dict(opening=dict(cash=opening_cash,equity=opening_eq,parent_equity=opening_equity_P,nci=opening_nci),rows=rows,closing=rows[-1]['group'],component_maps=maps,
        legal_mutations=[],worksheet_only=True,cash_origins=flow_records,limits=['synthetic tax and valuations','no guarantee settlement','no prudential capital admission','finite constant deposit','no general runtime adapter']))
