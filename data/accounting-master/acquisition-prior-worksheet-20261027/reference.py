from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from fractions import Fraction as F
import importlib.util,json
H=Path(__file__).resolve().parent;R=H.parents[2]
def load(name,folder):
    spec=importlib.util.spec_from_file_location(name,H.parent/folder/'reference.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
scope=load('prior_scope_v2','acquisition-prior-interest-scope-20261027');base=load('prior_comparator','acquisition-consideration-20261027')
h=scope.h;FLAGS=scope.FLAGS;num=base.number;fmt=base.fmt;serial=base.serial;PROFILE='ConditionalPriorEquityWorksheet/1'
BASE=json.loads((H.parent/'acquisition-consideration-20261027/attempt-01/cases.json').read_text())[0]
SCOPE=next(x for x in json.loads((H.parent/'acquisition-prior-interest-scope-20261027/attempt-01/cases.json').read_text()) if x['id']=='preserved/proportional/equity/fvtpl/none')
def report(body):
    try:
        h.need(len(json.dumps(body,allow_nan=False))<900000,'request_size');h.fields(body,['profile','payload','expected_payload_sha256'],'envelope');h.need(body['profile']==PROFILE,'profile');p=body['payload'];h.need(h.digest(p)==body['expected_payload_sha256'],'payload_binding')
        h.fields(p,['scope_request','scope_result_sha256','base_request','base_result_sha256','source_lock_sha256','schedule','source','books','books_sha256'],'payload')
        lock=H/'predecessor-lock.json';h.need(sha256(lock.read_bytes()).hexdigest()==p['source_lock_sha256'],'source_lock_binding')
        for path,d in json.loads(lock.read_text()).items():h.need(sha256((R/path).read_bytes()).hexdigest()==d,'protected_dependency:'+path)
        h.need(p['base_request']==BASE['request'],'selected_base_request');old=base.report(p['base_request']);h.need(old==BASE['result'] and h.digest(old)==p['base_result_sha256'],'base_result_binding')
        h.need(p['scope_request']==SCOPE['request'],'selected_scope_request');scoped=scope.derive(p['scope_request']);h.need(scoped==SCOPE['result'] and h.digest(scoped)==p['scope_result_sha256'],'scope_result_binding')
        h.need(scoped['status']=='conditional_prior_expressions','prior_scope')
        src=p['source'];h.fields(src,['text','subject','actor','available_at'],'source');h.text(src['text']);h.need(src['subject']==['P','S'] and src['actor']=='manager','source_context')
        deps=[]
        if src['available_at'] is None:deps.append('measurement_source_availability_unknown')
        elif h.moment(src['available_at'])>h.moment('2026-01-02T00:00:00Z'):deps.append('measurement_source_after_cutoff')
        s=p['schedule'];h.fields(s,['prior_carrying','prior_fair_value','new_cash','prior_fraction','new_fraction','combined_measurement','separate_books','tax','at','closing_at','currency','unit','premise','evidence_sha256'],'schedule')
        h.need(s['evidence_sha256']==h.digest(src),'schedule_source_binding');h.text(s['premise'])
        c=num(s['prior_carrying']);fair=num(s['prior_fair_value']);cash=num(s['new_cash']);gain=fair-c
        h.need(c in [F(35),F(40),F(45)] and fair==40 and cash==80,'selected_amounts')
        h.need(num(s['prior_fraction'])==F(1,5) and num(s['new_fraction'])==F(11,20),'ownership_schedule')
        h.need(s['at']=='2025-07-01T00:00:00Z' and s['closing_at']=='2026-01-01T00:00:00Z','schedule_dates')
        h.need(s['currency']=='USD' and s['unit']=='currency_unit','schedule_units')
        h.need(s['separate_books'] in ['supplied_aasb9_fvtpl','unresolved'],'separate_book_method')
        if s['separate_books']=='unresolved':deps.append('separate_books_method')
        h.need(s['tax'] in ['explicit_zero_current_and_deferred_on_prior_gain','unresolved'],'tax_disposition')
        if s['tax']=='unresolved':deps.append('prior_gain_tax_method')
        meas=s['combined_measurement'];h.need(type(meas) is dict and 'status' in meas,'combined_measurement')
        if meas['status']=='unresolved':h.fields(meas,['status'],'combined_measurement');deps.append('combined_investment_measurement')
        else:
            h.fields(meas,['status','acquisition','closing','premise'],'combined_measurement');h.need(meas['status']=='supplied','measurement_status');h.text(meas['premise'])
            h.need(num(meas['acquisition'])==120 and num(meas['closing'])==120,'combined_measurement_values')
        result=dict(profile=PROFILE,**FLAGS,request_sha256=h.digest(body),scope_result=deepcopy(scoped),schedule=deepcopy(s),source=deepcopy(src))
        if deps:return dict(result,status='method_required',dependencies=sorted(set(deps)),request=deepcopy(body))
        books=deepcopy(old['original_books'])
        for stage,snap in books['P']['snapshots'].items():
            snap['balances']=serial(dict(cash=300-c-(cash if stage!='opening' else 0),investment=c if stage=='opening' else fair+cash,capital=F(-300),prior_remeasurement_gain=F(0) if stage=='opening' else -gain))
        h.need(h.digest(p['books'])==p['books_sha256'],'books_binding');h.need(p['books']==books,'complete_legal_books')
        journals=[]
        def event(id,entity,at,entries,origin):
            h.need(sum(entries.values())==0,'journal_balance');journals.append(dict(id=id,entity=entity,at=at,origin=origin,entries=serial(entries)))
        for e in ['P','S']:event('opening-'+e,e,'2025-01-01T00:00:00Z',{k:num(v) for k,v in books[e]['snapshots']['opening']['balances'].items()},'Supplied opening state; prior investment already exists')
        event('precontrol-receipt','S','2025-06-29T00:00:00Z',dict(cash=F(20),revenue=F(-20)),'Supplied pre-control receipt')
        event('precontrol-close','S','2025-06-30T00:00:00Z',dict(revenue=F(20),retained_pre=F(-20)),'Supplied pre-control close')
        event('prior-equity-update','P',s['at'],dict(investment=gain,prior_remeasurement_gain=-gain),'Supplied prior FVTPL fair-value update; no cash')
        event('new-share-purchase','P',s['at'],dict(investment=cash,cash=-cash),'New cash paid to external former owners; separate from prior fair value')
        event('controlled-receipt','S','2025-08-01T00:00:00Z',dict(cash=F(40),revenue=F(-40)),'Supplied controlled receipt')
        event('legal-depreciation','S','2025-12-31T00:00:00Z',dict(depreciation=F(7),equipment=F(-7)),'Supplied legal equipment schedule')
        # Stable date ordering retains the explicit update-before-purchase order.
        journals.sort(key=lambda x:x['at'])
        for e in ['P','S']:
            for stage,snap in books[e]['snapshots'].items():
                state={k:F(0) for k in snap['balances']}
                for event in journals:
                    if event['entity']==e and h.moment(event['at'])<=h.moment(snap['at']):
                        for k,v in event['entries'].items():state[k]+=num(v)
                h.need(serial(state)==snap['balances'],'journal_snapshot:'+e+'/'+stage)
        worksheets={}
        for stage in ['acquisition','closing']:
            w=deepcopy(old[stage+'_worksheet']);raw={e+'.'+k:num(v) for e in ['P','S'] for k,v in books[e]['snapshots'][stage]['balances'].items()};adjusted=deepcopy(raw)
            for journal in w['journals']:
                for k,v in journal['entries'].items():adjusted[k]=adjusted.get(k,F(0))+num(v)
            h.need(sum(adjusted.values())==0,'worksheet_balance');totals={}
            for k,v in adjusted.items():
                e,n=k.split('.');n='parent_capital' if e=='P' and n=='capital' else n;totals[n]=totals.get(n,F(0))+v
            w.update(raw=serial(raw),adjusted=serial(adjusted),balances=serial({k:v for k,v in totals.items() if v}));worksheets[stage+'_worksheet']=w
        r=deepcopy(old['report'])
        for k in ['profit','owners_profit','owners_equity_closing','assets_closing','equity_closing']:r[k]=fmt(num(r[k])+gain)
        r.update(acquisition_balances=worksheets['acquisition_worksheet']['balances'],closing_balances=worksheets['closing_worksheet']['balances'])
        r['cash'].update(opening=fmt(300-c),consideration_paid=fmt(cash),acquisition_net=fmt(50-cash),closing=fmt(310-c))
        r['parent_equity'].update(owners_profit=r['owners_profit'],closing=r['owners_equity_closing'])
        r['prior_equity']=serial(dict(opening_carrying=c,acquisition_fair_value=fair,noncash_gain=gain,new_cash=cash,combined_investment=fair+cash))
        h.need(num(r['assets_closing'])-num(r['liabilities_closing'])==num(r['equity_closing']),'report_balance')
        h.need(num(r['owners_profit'])+num(r['nci_profit'])==num(r['profit']),'profit_attribution')
        h.need(num(r['owners_equity_closing'])+num(r['nci_closing'])==num(r['equity_closing']),'equity_attribution')
        return dict(result,status='conditional_prior_worksheet',original_books=books,legal_journals=journals,**worksheets,report=r,cash_origins=[dict(entity='P',counterparty='former_owners',at=s['at'],amount=fmt(-cash),classification='acquisition_consideration'),dict(entity='S',at=s['at'],amount='50/1',classification='cash_acquired'),dict(entity='S',at='2025-08-01T00:00:00Z',amount='40/1',classification='operating')],outstanding=['actual_relationship_classification_and_source','valuation_tax_and_separate_books_admission','fvoci_equity_method_debt_and_separate_transactions','general_acquisition_methods_and_notes'])
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:350] or type(exc).__name__)
