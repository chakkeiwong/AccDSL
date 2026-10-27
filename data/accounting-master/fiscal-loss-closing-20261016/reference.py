"""Exact read-only successor of the closed P5 legal/group books."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PACKET='data/accounting-master/company-composition-20261016/attempt-03/portable-exchanges.json'
SOURCE='docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'
FINDINGS={'continued_control','unchanged_ownership_policies_currency','outside_basis_exception',
    'complete_book_tax_inventory','book_tax_depreciation_equal','no_group_relief_or_offset_right',
    'no_other_operations_or_instruments','all_new_origins_profit','loss_usable_only_by_P',
    'no_carryback','short_period_tax_law_admitted','all_cash_costs_expensed'}
SHARES={'complete_history','unchanged_ordinary_shares','no_potential_shares'}
PL={'revenue','cogs','selling_expense','wages','depreciation','finance_expense','current_tax','deferred_tax','cash_expense'}

class Refusal(Exception):
    def __init__(self,status,reason):self.status=status;self.reason=reason
def fail(reason,status='rejected'):raise Refusal(status,reason)
def shape(x,keys,reason):
    if not isinstance(x,dict) or set(x)!=set(keys):fail(reason)
def q(x,name,signed=False):
    if x is None:fail('missing_'+name,'unresolved')
    try:
        if not isinstance(x,str):raise ValueError()
        value=Q(x)
        if str(value)!=x:raise ValueError()
    except (ValueError,ZeroDivisionError):fail('number_encoding')
    if value<0 and not signed:fail('number_domain')
    return value
def day(x):
    try:
        d=date.fromisoformat(x)
        if d.isoformat()!=x:raise ValueError()
    except (TypeError,ValueError):fail('date_encoding')
    return d
def boolean(x,name,required=False):
    if x is None:fail('missing_'+name,'unresolved')
    if not isinstance(x,bool):fail('finding_encoding')
    if required and not x:fail('outside_'+name,'unsupported')
    return x
def required(x,keys):
    shape(x,keys,'finding_shape')
    for k in sorted(keys):boolean(x[k],k,True)
def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,list):return [encode(v) for v in x]
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    return x
def equity(b):return -(b['capital']+b.get('original_equity',Q(0))+b['retained'])

def present_offset(r):
    try:
        shape(r,{'category','asset','liability','asset_entity','liability_entity','same_authority','legal_current_offset_right',
                 'intends_net_or_simultaneous','each_future_recovery_period'},'offset_shape')
        if r['category'] not in ('current','deferred'):fail('mixed_current_deferred_offset','unsupported')
        a=q(r['asset'],'asset');l=q(r['liability'],'liability')
        for k in ('asset_entity','liability_entity'):
            if not isinstance(r[k],str) or not r[k]:fail('entity_identity')
        for k in ('same_authority','legal_current_offset_right','intends_net_or_simultaneous','each_future_recovery_period'):boolean(r[k],k)
        if r['category']=='current':net=r['legal_current_offset_right'] and r['intends_net_or_simultaneous']
        else:net=r['legal_current_offset_right'] and r['same_authority'] and (r['asset_entity']==r['liability_entity'] or
            (r['intends_net_or_simultaneous'] and r['each_future_recovery_period']))
        deduction=min(a,l) if net else Q(0)
        return encode(dict(status='conditional_complete',presentation=dict(asset=a-deduction,liability=l-deduction,offset=net),gross=dict(asset=a,liability=l),mutations=[]))
    except Refusal as e:return dict(status=e.status,reason=e.reason,presentation=None,gross=None,mutations=[])

def calculate(r,reader=lambda p:p.read_bytes()):
    empty=dict(opening=None,reports=[],journals=[],cash_flows=[],closing_books=None,mutations=[])
    try:
        locks={x['path']:x['sha256'] for x in json.loads((OUT/'input-lock.json').read_text())['files']}
        blobs={}
        for name in (PACKET,SOURCE):
            try:raw=reader(ROOT/name)
            except FileNotFoundError:fail('missing_source_or_baseline','unresolved')
            if hashlib.sha256(raw).hexdigest()!=locks[name]:fail('changed_source_or_baseline')
            blobs[name]=raw
        shape(r,{'wire','operation','base_packet','base_sha256','opening','ordinary_shares','share_findings','calendar','loss_expiry_exclusive','periods'},'request_shape')
        if r['wire']!='FiscalLossClosing/1':fail('wire')
        if r['operation']!='report':fail('report_only')
        if r['base_packet']!=PACKET or r['base_sha256']!=locks[PACKET]:fail('baseline_reference')
        required(r['share_findings'],SHARES);shares=q(r['ordinary_shares'],'ordinary_shares')
        if shares<=0 or shares.denominator!=1:fail('share_domain')
        shape(r['calendar'],{'stub_reason','short_comparatives_not_annualised'},'calendar_shape')
        if not isinstance(r['calendar']['stub_reason'],str) or not r['calendar']['stub_reason'].strip():fail('missing_stub_reason','unresolved')
        boolean(r['calendar']['short_comparatives_not_annualised'],'short_comparatives_not_annualised',True)
        expiry=day(r['loss_expiry_exclusive'])
        if expiry!=date(2028,7,1):fail('different_expiry_law','unsupported')
        packet=json.loads(blobs[PACKET]);source=packet['record_registry'][packet['states'][-1]['digest']]['body']
        if source['date']!='2025-12-31' or source['parent_fraction']!='9/10' or source['compound']['phase']!='ended' or source['lot']['sold_fraction']!='1':fail('unsupported_opening','unsupported')
        books={e:{k:Q(v) for k,v in b.items()} for e,b in source['books'].items()}
        journals=[];flows=[];reports=[]
        def post(period,entity,kind,entries):
            entries={k:v for k,v in entries.items() if v}
            if sum(entries.values(),Q(0))!=0:fail('journal_balance')
            for k,v in entries.items():books[entity][k]=books[entity].get(k,Q(0))+v
            journals.append(dict(period=period,entity=entity,kind=kind,entries=entries))
        def close(period,entity):
            b=books[entity];entries={k:-b[k] for k in PL if b.get(k,Q(0))};entries['retained']=-sum(entries.values(),Q(0))
            post(period,entity,'close_income_to_retained',entries)
        for e in ('P','S'):
            if sum(books[e].values(),Q(0))!=0:fail('opening_balance')
            if any(books[e].get(k,Q(0)) for k in ('inventory','recovery_asset','dta','dtl','refund_liability','debt','receivable','payable')):fail('unmapped_opening_balance','unsupported')
            close('prior2025',e)
            books[e]['current_tax_payable']=Q(0)
        p,s=books['P'],books['S'];parent_fraction=Q(source['parent_fraction']);reserve=-Q(source['ownership_purchase']['parent_equity_debit'])
        group_equity=equity(p)+equity(s)-p['investment'];nci=(1-parent_fraction)*equity(s);parent=group_equity-nci
        parent_retained=parent-(-p['capital']-p['original_equity'])-reserve
        opening=dict(P={k:(-p[k] if k in ('capital','original_equity','retained') else p[k]) for k in ('cash','ppe','investment','capital','original_equity','retained')},
            S={k:(-s[k] if k in ('capital','retained') else s[k]) for k in ('cash','capital','retained')},
            group=dict(equity=group_equity,parent_equity=parent,nci=nci,parent_retained=parent_retained,ownership_reserve=reserve))
        if r['opening']!=encode(opening):fail('opening_projection')
        initial=deepcopy(opening);previous_group_equity=group_equity;previous_cash=p['cash']+s['cash']
        previous_dta=Q(0);previous_payable=Q(0);previous_rate=Q('1/4');loss=Q(0);recognised=Q(0);last=date(2026,1,1);seen=set()
        if not isinstance(r['periods'],list) or not 1<=len(r['periods'])<=3:fail('period_list','unsupported')
        for index,period in enumerate(r['periods']):
            shape(period,{'id','start','end_exclusive','information_date','findings','P','S','tax','recovery'},'period_shape')
            id=period['id']
            if not isinstance(id,str) or not id or id in seen:fail('period_identity')
            seen.add(id);start=day(period['start']);end=day(period['end_exclusive']);info=day(period['information_date'])
            if start!=last or end<=start:fail('period_gap_overlap')
            desired=date(2026,7,1) if index==0 else date(start.year+1,7,1)
            if end!=desired or (index>0 and (start.month,start.day)!=(7,1)):fail('fiscal_calendar','unsupported')
            if not start<=info<=end:fail('information_cutoff')
            required(period['findings'],FINDINGS)
            tax=period['tax'];shape(tax,{'current_rate','recovery_rate','law_date','effective_from','law_id','enacted','complete_fiscal_terms'},'tax_shape')
            boolean(tax['enacted'],'enacted',True);boolean(tax['complete_fiscal_terms'],'complete_fiscal_terms',True)
            rate=q(tax['current_rate'],'current_rate');recovery_rate=q(tax['recovery_rate'],'recovery_rate')
            if rate>1 or recovery_rate>1:fail('rate_domain','unsupported')
            if recovery_rate!=rate:fail('different_recovery_schedule','unsupported')
            if day(tax['law_date'])>start or day(tax['effective_from'])>start:fail('law_timing')
            if not isinstance(tax['law_id'],str) or not tax['law_id']:fail('law_identity')
            recovery=period['recovery'];shape(recovery,{'supported_loss','assessment_complete','convincing_next_period_evidence','evidence_id','taxable_entity','authority','usable_before_expiry'},'recovery_shape')
            boolean(recovery['assessment_complete'],'assessment_complete',True);convincing=boolean(recovery['convincing_next_period_evidence'],'convincing_next_period_evidence')
            boolean(recovery['usable_before_expiry'],'usable_before_expiry',True)
            if recovery['taxable_entity']!='P' or recovery['authority']!='P-tax':fail('recovery_owner')
            if not isinstance(recovery['evidence_id'],str) or not recovery['evidence_id']:fail('recovery_evidence')
            target=q(recovery['supported_loss'],'supported_loss')
            if target>0 and not convincing:fail('unsupported_loss_recovery','unsupported')
            old_loss=loss;old_rec=recognised;rate_expense=previous_dta-old_rec*rate
            if rate_expense:post(id,'P','tax_rate_remeasurement',dict(dta=-rate_expense,deferred_tax=rate_expense))
            profit={};ops={};tax_current={};tax_paid={}
            for entity in ('P','S'):
                x=period[entity];shape(x,{'receipts','cash_costs','depreciation','tax_paid'},'operations_shape')
                v={k:q(value,k) for k,value in x.items()};ops[entity]=v;b=books[entity]
                if v['depreciation']>b['ppe']:fail('depreciation_exceeds_asset')
                if b['cash']+v['receipts']<v['cash_costs']+v['tax_paid']:fail('cash_funding_required','unsupported')
                post(id,entity,'cash_revenue',dict(cash=v['receipts'],revenue=-v['receipts']))
                post(id,entity,'cash_operating_cost',dict(cash=-v['cash_costs'],cash_expense=v['cash_costs']))
                post(id,entity,'depreciation',dict(ppe=-v['depreciation'],depreciation=v['depreciation']))
                pretax=v['receipts']-v['cash_costs']-v['depreciation'];profit[entity]=pretax
                if entity=='P':
                    if index==0 and pretax<0:loss+=-pretax
                    elif pretax<0:fail('multiple_loss_origins','unsupported')
                    used=min(loss,max(pretax,Q(0)));loss-=used
                    taxable=max(pretax,Q(0))-used
                else:
                    if pretax<0:fail('subsidiary_loss_method','unsupported')
                    taxable=pretax
                charge=taxable*rate;tax_current[entity]=charge;tax_paid[entity]=v['tax_paid']
                post(id,entity,'current_tax',dict(current_tax=charge,current_tax_payable=-charge))
                if v['tax_paid']>-b['current_tax_payable']:fail('tax_overpayment','unsupported')
                post(id,entity,'tax_settlement',dict(current_tax_payable=v['tax_paid'],cash=-v['tax_paid']))
                for kind,amount in [('customer_receipt',v['receipts']),('operating_cost',-v['cash_costs']),('tax_payment',-v['tax_paid'])]:
                    if amount:flows.append(dict(period=id,entity=entity,kind=kind,amount=amount,activity='operating'))
            consumed_rec=min(old_rec,used);unrecognised_benefit=(used-consumed_rec)*rate
            surviving_rec=old_rec-consumed_rec;expired=Q(0);expired_rec=Q(0)
            if end>=expiry:expired=loss;loss=Q(0);expired_rec=surviving_rec;surviving_rec=Q(0)
            if target>loss:fail('recovery_exceeds_usable_loss')
            use_expense=consumed_rec*rate;expiry_expense=expired_rec*rate;recovery_expense=(surviving_rec-target)*rate
            for kind,amount in [('loss_asset_consumed',use_expense),('loss_asset_expired',expiry_expense),('loss_recovery_reassessment',recovery_expense)]:
                post(id,'P',kind,dict(dta=-amount,deferred_tax=amount))
            recognised=target;new_dta=target*rate;deferred=rate_expense+use_expense+expiry_expense+recovery_expense
            if p['dta']!=new_dta or deferred!=previous_dta-new_dta:fail('tax_origin_identity')
            profit['P']-=tax_current['P']+deferred;profit['S']-=tax_current['S']
            for entity in ('P','S'):close(id,entity)
            legal={}
            for entity in ('P','S'):
                b=books[entity]
                if sum(b.values(),Q(0))!=0 or any(b.get(k,Q(0)) for k in PL):fail('closed_book_identity')
                legal[entity]=dict(cash=b['cash'],ppe=b['ppe'],investment=b['investment'],dta=b['dta'],current_tax_payable=-b['current_tax_payable'],
                    equity=equity(b),retained=-b['retained'],profit=profit[entity],pretax=ops[entity]['receipts']-ops[entity]['cash_costs']-ops[entity]['depreciation'],
                    current_tax_expense=tax_current[entity],deferred_tax_expense=deferred if entity=='P' else Q(0),tax_paid=tax_paid[entity])
            group_equity=equity(p)+equity(s)-p['investment'];nci=(1-parent_fraction)*equity(s);parent=group_equity-nci
            group_profit=profit['P']+profit['S'];nci_profit=(1-parent_fraction)*profit['S'];parent_profit=group_profit-nci_profit
            parent_retained+=parent_profit;cash=p['cash']+s['cash'];payable=-p['current_tax_payable']-s['current_tax_payable']
            direct=sum(v['receipts']-v['cash_costs']-v['tax_paid'] for v in ops.values())
            indirect=group_profit+sum(v['depreciation'] for v in ops.values())-(new_dta-previous_dta)+(payable-previous_payable)
            if group_equity!=previous_group_equity+group_profit or cash+p['ppe']+new_dta-payable!=group_equity:fail('group_identity')
            if parent!=-p['capital']-p['original_equity']+parent_retained+reserve:fail('parent_equity_origin')
            if direct!=indirect or cash!=previous_cash+direct:fail('cash_identity')
            days=(end-start).days
            report=dict(id=id,start=period['start'],end_exclusive=period['end_exclusive'],days=days,
                period_comparability='short_period_not_annualised' if index==0 else ('different_prior_length' if index==1 else 'annual_comparison'),
                comparative_period='prior2025' if index==0 else reports[-1]['id'],
                P=legal['P'],S=legal['S'],group=dict(cash=cash,ppe=p['ppe'],dta=new_dta,current_tax_payable=payable,equity=group_equity,
                    profit=group_profit,parent_equity=parent,nci=nci,parent_profit=parent_profit,nci_profit=nci_profit,parent_retained=parent_retained,
                    ownership_reserve=reserve,ordinary_shares=shares,basic_eps=parent_profit/shares,diluted_eps=parent_profit/shares,oci=Q(0),
                    direct_operating_cash=direct,indirect_operating_cash=indirect),
                loss=dict(opening=old_loss,new=max(-legal['P']['pretax'],Q(0)),used=used,expired=expired,remaining=loss,
                    recognised_quantity=target,unrecognised_quantity=loss-target,rate_effect=rate_expense,consumption_expense=use_expense,
                    expiry_expense=expiry_expense,reassessment_expense=recovery_expense,unrecognised_used_benefit=unrecognised_benefit,
                    authority='P-tax',taxable_entity='P',expiry_exclusive=r['loss_expiry_exclusive'],evidence_id=recovery['evidence_id']),
                law=dict(id=tax['law_id'],current_rate=rate,recovery_rate=rate,origin='profit'),closed_books=deepcopy(books))
            reports.append(report);previous_dta=new_dta;previous_payable=payable;previous_group_equity=group_equity;previous_cash=cash;previous_rate=rate;last=end
        return encode(dict(status='conditional_complete',reason='finite_company_successor',opening=initial,reports=reports,journals=journals,
            cash_flows=flows,closing_books=books,mutations=[]))
    except Refusal as e:return dict(status=e.status,reason=e.reason,**empty)
