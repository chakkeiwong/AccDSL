"""Conditional synthetic cash-acquisition worksheet; never a registered method."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction
from copy import deepcopy
import importlib.util,json
H=Path(__file__).resolve().parent;R=H.parents[2]
SYMBOLIC=R/'data/accounting-master/acquisition-symbolic-20261027'
spec=importlib.util.spec_from_file_location('worksheet_symbolic',SYMBOLIC/'reference.py')
sym=importlib.util.module_from_spec(spec);spec.loader.exec_module(sym)
h=sym.h
PROFILE='ConditionalAcquisitionWorksheet/2'
FLAGS=dict(source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False,executed=False)
number=sym.scalar;fmt=sym.fmt
ACCOUNTS={'P':{'cash','investment','capital'},'S':{'cash','equipment','payable','capital','retained_pre','revenue','depreciation','operating_expense'}}
def serial(d):return {k:fmt(v) for k,v in sorted(d.items())}
def eval_expr(e,values):return Fraction(e['constant'])+sum(Fraction(c)*values[n] for n,c in e['coefficients'].items())
def report(body):
    try:
        pin=json.loads((SYMBOLIC/'attempt-01/source-lock.json').read_text())
        for p,d in pin.items():h.need(sha256((R/p).read_bytes()).hexdigest()==d,'symbolic_dependency:'+p)
        h.need(len(json.dumps(body,allow_nan=False))<450000,'request_size')
        h.fields(body,['profile','payload','expected_payload_sha256'],'envelope');h.need(body['profile']==PROFILE,'profile')
        p=body['payload'];h.need(h.digest(p)==body['expected_payload_sha256'],'payload_binding')
        h.fields(p,['symbolic_request','synthetic_premise','basis_premises','books','acquired_items','consideration','nci_fair_value','expense_adjustment','tax_release','operating_cash','expected_books_sha256'],'payload')
        h.need(p['synthetic_premise']=='Explicit synthetic engineering case; no company measurement or accounting admission','synthetic_case_required')
        sr=sym.derive(p['symbolic_request']);h.need(sr['status']=='conditional_expressions','symbolic:'+sr.get('reason',sr['status']))
        sp=p['symbolic_request']['payload'];h.need(sp['prior_interest']['kind']=='none','no_prior_interest_only')
        h.need(sp['route']['kind']=='ordinary_business_acquisition','ordinary_route_only')
        h.fields(p['basis_premises'],['recognition','tax','items','later_adjustments'],'basis_premises')
        for key in p['basis_premises']:h.text(p['basis_premises'][key])
        h.need(p['basis_premises']['recognition']=='Conditional synthetic positive-excess acquisition; facts and measurement stipulated','recognition_premise')
        # The small chart is intentional. It is not a general mapping algorithm.
        books=p['books'];h.fields(books,['P','S'],'books');h.need(h.digest(books)==p['expected_books_sha256'],'books_binding')
        expected_subject=sp['scope_request']['history_request']['subject'];h.need(expected_subject==['P','S'],'test_entities_only')
        start=sp['scope_request']['history_request']['interval']['start'];at=sp['acquisition']['at'];end=sp['scope_request']['history_request']['interval']['end_exclusive']
        currency=sp['acquisition']['currency'];unit=sp['acquisition']['unit'];f=number(sp['ownership']['fraction']);q=1-f
        stages={'P':['opening','acquisition','closing'],'S':['opening','acquisition','closing']};b={}
        for owner in ['P','S']:
            h.fields(books[owner],['entity','currency','unit','snapshots'],'book');bk=books[owner]
            h.need(bk['entity']==owner and bk['currency']==currency and bk['unit']==unit,'book_context')
            h.fields(bk['snapshots'],stages[owner],'snapshots');b[owner]={}
            for stage,when in [('opening',start),('acquisition',at),('closing',end)]:
                snap=bk['snapshots'][stage];h.fields(snap,['at','balances'],'snapshot');h.need(h.moment(snap['at'])==h.moment(when),'snapshot_date:'+owner+'/'+stage)
                h.need(type(snap['balances']) is dict and set(snap['balances'])==ACCOUNTS[owner],'account_population:'+owner+'/'+stage)
                balances={k:number(v) for k,v in snap['balances'].items()};h.need(sum(balances.values())==0,'legal_balance:'+owner+'/'+stage)
                h.need(balances['cash']>=0,'negative_cash_requires_method')
                if owner=='S':h.need(balances['equipment']>=0 and balances['payable']<=0,'legal_signs')
                h.need(balances['capital']<=0,'capital_sign');b[owner][stage]=balances
        # Fixed complete legal progression exposes pre-control profit leakage.
        po,pa,pc=[b['P'][k] for k in stages['P']];so,sa,sc=[b['S'][k] for k in stages['S']]
        h.fields(p['consideration'],['cash','new_parent_equity','kind','at','currency','unit','premise'],'consideration')
        c=p['consideration'];h.need(c['kind']=='cash_and_new_parent_equity','consideration_kind')
        h.need(h.moment(c['at'])==h.moment(at),'consideration_date')
        h.need(c['currency']==currency and c['unit']==unit,'consideration_unit');h.text(c['premise'])
        cash_consideration=number(c['cash']);equity_consideration=number(c['new_parent_equity'])
        h.need(cash_consideration>=0 and equity_consideration>=0,'negative_consideration')
        amount=cash_consideration+equity_consideration
        h.need(po['investment']==0 and pa['investment']==amount,'investment_binding')
        h.need(pa['cash']==po['cash']-cash_consideration and pa['capital']==po['capital']-equity_consideration,'parent_purchase_journal')
        h.need(pc==pa,'unexplained_parent_movement')
        h.need(all(so[k]==0 for k in ['retained_pre','revenue','depreciation','operating_expense']),'opening_income_state')
        h.need(all(sa[k]==0 for k in ['revenue','depreciation','operating_expense']),'acquisition_income_state')
        h.need(sa['capital']==so['capital'] and sa['equipment']==so['equipment'] and sa['payable']==so['payable'],'precontrol_other_change')
        h.need(sa['cash']-so['cash']==-sa['retained_pre'],'precontrol_cash_equity')
        h.need(sc['capital']==sa['capital'] and sc['retained_pre']==sa['retained_pre'],'precontrol_equity_preserved')
        h.need(sc['depreciation']>=0 and sc['operating_expense']>=0,'expense_sign')
        h.need(sc['equipment']==sa['equipment']-sc['depreciation'],'legal_equipment_roll')
        h.need(sc['payable']==sa['payable']-sc['operating_expense'],'legal_payable_roll')
        cash=number(p['operating_cash']);h.need(sc['cash']==sa['cash']+cash and cash==-sc['revenue'],'postcontrol_cash_revenue')
        items=p['acquired_items'];h.need(type(items) is list and len(items)==4,'acquired_item_population')
        indexed={x.get('id'):x for x in items};h.need(set(indexed)=={'cash','equipment','payable','deferred_tax'},'acquired_item_identity')
        acquired={}
        for key,item in indexed.items():
            h.fields(item,['id','kind','legal_account','legal_balance','recognised_balance','at','currency','unit','premise'],'acquired_item')
            h.text(item['premise']);h.need(h.moment(item['at'])==h.moment(at),'item_date')
            h.need(item['currency']==currency and item['unit']==unit,'item_unit')
            account=None if key=='deferred_tax' else key
            h.need(item['legal_account']==account,'item_account');legal=0 if account is None else sa[account]
            h.need(number(item['legal_balance'])==legal,'item_legal_balance')
            value=number(item['recognised_balance']);kind='asset' if key in ['cash','equipment'] else 'liability'
            h.need(item['kind']==kind and (value>=0 if kind=='asset' else value<=0),'item_kind_sign')
            if key in ['cash','payable']:h.need(value==legal,'unsupported_item_remeasurement')
            acquired[key]=value
        uplift=acquired['equipment']-sa['equipment'];h.need(uplift>=0,'positive_uplift_profile')
        dep=number(p['expense_adjustment']);release=number(p['tax_release'])
        h.need(0<=dep<=uplift and 0<=release<=-acquired['deferred_tax'],'adjustment_bounds')
        A=acquired['cash']+acquired['equipment'];L=-acquired['payable']-acquired['deferred_tax'];net=A-L
        election=sp['ownership']['nci_election']
        if election=='fair_value':nci=number(p['nci_fair_value']);h.need(nci>=0,'negative_nci_measurement')
        else:h.need(p['nci_fair_value'] is None,'unused_nci_measurement');nci=q*net
        goodwill=amount+nci-net;h.need(goodwill>0,'excess_requires_other_method')
        legal_profit=-(sc['revenue']+sc['depreciation']+sc['operating_expense'])
        values={'A':A,'L':L,'T':amount,'R':legal_profit,'D':dep-release,'O':Fraction(0),'U':Fraction(0)}
        if f<1:values.update(V=Fraction(0),M=Fraction(0))
        if election=='fair_value':values['Q']=nci
        symbol_values={sp['amounts'][role]['symbol']:value for role,value in values.items()}
        computed={k:eval_expr(e,symbol_values) for k,e in sr['expressions'].items()}
        h.need(computed['acquisition_excess']==goodwill and computed['nci_at_acquisition']==nci,'symbolic_amount_binding')
        # Journals combine equal accounting effects, while every origin is retained.
        acquisition_journal={'S.capital':-sa['capital'],'S.retained_pre':-sa['retained_pre'],'S.equipment':uplift,'group.goodwill':goodwill,'group.deferred_tax':acquired['deferred_tax'],'P.investment':-amount,'group.nci':-nci}
        h.need(sum(acquisition_journal.values())==0,'acquisition_journal_balance')
        later=[dict(id='basis-depreciation',origin='Supplied acquired equipment basis expense',at=end,entries=serial({'S.equipment':-dep,'group.depreciation':dep})),dict(id='tax-liability-release',origin=p['basis_premises']['tax'],at=end,entries=serial({'group.deferred_tax':release,'group.tax_expense':-release}))]
        journals=[dict(id='acquisition',origin='Conditional supplied item measurements and investment/equity elimination',at=at,entries=serial(acquisition_journal))]+later
        def worksheet(stage):
            raw={owner+'.'+account:value for owner in ['P','S'] for account,value in b[owner][stage].items()}
            adjusted=dict(raw);applied=journals[:1] if stage=='acquisition' else journals
            for journal in applied:
                for account,v in journal['entries'].items():adjusted[account]=adjusted.get(account,Fraction(0))+number(v)
            h.need(sum(adjusted.values())==0,'worksheet_balance')
            aggregated={}
            for account,value in adjusted.items():
                if value==0:continue
                owner,key=account.split('.');name='parent_capital' if owner=='P' and key=='capital' else key
                aggregated[name]=aggregated.get(name,Fraction(0))+value
            aggregated.setdefault('nci',Fraction(0))
            h.need(not any(k in aggregated for k in ['investment','capital','retained_pre']),'uneliminated_acquired_equity')
            return dict(raw=serial(raw),journals=deepcopy(applied),adjusted=serial(adjusted),balances=serial(aggregated))
        opening=worksheet('acquisition');closing=worksheet('closing')
        assets=sc['cash']+pc['cash']+sc['equipment']+uplift-dep+goodwill
        liabilities=-sc['payable']-acquired['deferred_tax']-release
        profit=computed['post_control_profit'];owners=-pc['capital']+computed['owners_profit'];nclose=computed['nci_closing']
        h.need(assets-liabilities==owners+nclose,'group_equity_reconciliation')
        cashclose=pc['cash']+sc['cash'];h.need(po['cash']-cash_consideration+sa['cash']+cash==cashclose,'group_cash_reconciliation')
        financial=dict(net_assets_at_acquisition=fmt(net),nci_at_acquisition=fmt(nci),goodwill=fmt(goodwill),acquisition_balances=opening['balances'],closing_balances=closing['balances'],profit=fmt(profit),owners_profit=fmt(computed['owners_profit']),nci_profit=fmt(computed['nci_profit']),nci_closing=fmt(nclose),owners_equity_closing=fmt(owners),assets_closing=fmt(assets),liabilities_closing=fmt(liabilities),equity_closing=fmt(owners+nclose),cash=serial(dict(opening=po['cash'],consideration_paid=cash_consideration,noncash_equity=equity_consideration,acquired=sa['cash'],acquisition_net=sa['cash']-cash_consideration,operating=cash,closing=cashclose)))
        financial['parent_equity']=serial(dict(opening=-po['capital'],new_equity=equity_consideration,owners_profit=computed['owners_profit'],closing=owners))
        h.need(-po['capital']+equity_consideration+computed['owners_profit']==owners,'parent_equity_roll')
        return dict(profile=PROFILE,status='conditional_worksheet',**FLAGS,request_sha256=h.digest(body),original_books=deepcopy(books),acquired_items=deepcopy(items),basis_premises=deepcopy(p['basis_premises']),consideration=deepcopy(c),symbolic_result=sr,conditional_measurements=serial(values),acquisition_worksheet=opening,closing_worksheet=closing,report=financial,scope='Explicit synthetic cash/new-parent-equity acquisition with supplied item/tax/rights premises; no actual measurement or complete statutory report.',outstanding=['source_and_accounting_admission','debt_conversion_and_prior_relationships','loss_and_ownership_changes','general_item_tax_elimination_methods','revisions_and_complete_notes'])
    except Exception as exc:return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:350] or type(exc).__name__)
