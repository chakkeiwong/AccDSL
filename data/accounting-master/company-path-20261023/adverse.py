"""Counterexamples to resetting or mixing conditional company years."""
from copy import deepcopy
from fractions import Fraction as Q
from path_semantics import execute, verify_chain, report_view, revise


def inspect_adverse(path, source, result, check, case, witnesses, expected):
    original=deepcopy(path)
    first,second=result['years']
    cash2,profit2=expected['cash'],expected['profit']
    replacement=deepcopy(path['continuations'][0]); replacement['inventory']['price']='12/1'
    late=revise(path,source,1,replacement,'Second-year price hypothesis')
    lr=late['result']; witnesses['second_year_revision']=late
    check('revision_preserves_first_year_identity',lr['years'][0]['result_sha256']==first['result_sha256'])
    check('revision_changes_suffix_identity',lr['years'][1]['result_sha256']!=second['result_sha256'] and verify_chain(late['path'],lr))
    changed=lr['years'][1]['annual_run']
    check('second_year_revision_profit_cash_claims',changed['statements']['profit']-profit2==Q(128,5) and changed['statements']['cash']-cash2==Q(112,5) and changed['closing_balances']['receivables']-expected['receivables']==Q(16,5))
    replacement=deepcopy(path['initial_year']); replacement['inventory']['price']='11/1'
    early=revise(path,source,0,replacement,'First-year price hypothesis; fixed later settlements')
    er=early['result']; witnesses['first_year_revision']=early
    check('early_revision_recomputes_both_years',all(a['result_sha256']!=b['result_sha256'] for a,b in zip(er['years'],result['years'])))
    changed=er['years'][1]
    check('early_revision_cash_receivable_carry',changed['annual_run']['statements']['cash']-cash2==21 and changed['closing_memory']['claims']['sales-ar']['outstanding']==3 and changed['annual_run']['statements']['profit']==profit2)
    check('original_branch_immutable',path==original and execute(path,source)==result)
    check('revision_not_historical_restatement',not early['historical_restatement'] and not late['historical_restatement'])
    check('report_names_branch_and_period',report_view(path,result,'2026-01-01')['year_result_sha256']==second['result_sha256'])
    check('changed_body_rejects_old_run',report_view(late['path'],result,'2026-01-01')['status']=='invalid')
    mixed=deepcopy(er); mixed['years'][1]=deepcopy(second)
    check('stale_suffix_rejected',not verify_chain(early['path'],mixed))
    mixed=deepcopy(result); mixed['years'][1]['annual_report']['lines']['cash']['value']+=1
    check('changed_report_rejected',not verify_chain(path,mixed))
    mixed=deepcopy(result); mixed['years'].pop()
    check('truncated_complete_path_rejected',not verify_chain(path,mixed))
    check('unrequested_period_not_fabricated',report_view(path,result,'2030-01-01')['status']=='invalid')
    invalids=[
        ('missing_allocation',lambda p:p['continuations'][0]['opening_settlements'].pop(),'opening_claim_allocation_set'),
        ('duplicate_allocation',lambda p:p['continuations'][0]['opening_settlements'].append(deepcopy(p['continuations'][0]['opening_settlements'][0])),'opening_claim_allocation_set'),
        ('period_gap',lambda p:p['continuations'][0]['period'].update(start='2026-02-01'),'nonconsecutive_periods'),
        ('extra_opening_assets',lambda p:p['continuations'][0].update(assets=[]),'path_schema'),
        ('facility_replaced',lambda p:p['continuations'][0]['facility'].update(id='new'),'facility_identity_changed'),
        ('duplicate_year_name',lambda p:p['continuations'][0].update(name=p['initial_year']['name']),'duplicate_year_name')]
    for name,change,reason in invalids:
        _,r=case(name,change)
        check(name+':rejected',r['status']=='invalid' and r['reason']==reason)
    partials=[
        ('over_settlement',lambda p:p['continuations'][0]['opening_settlements'][0].update(amount='26/1'),'invalid','opening_over_settlement'),
        ('reused_claim',lambda p:p['continuations'][0]['trade'].update(sales_claim_id='sales-ar'),'invalid','duplicate_claim'),
        ('reused_asset',lambda p:p['continuations'][0]['cash'].update(capex_id='capex-2025'),'invalid','duplicate_asset'),
        ('changed_costing',lambda p:p['continuations'][0]['inventory'].update(method='fifo'),'unsupported','method'),
        ('unknown_price',lambda p:p['continuations'][0]['inventory'].update(price='unknown'),'unresolved',None),
        ('partial_year',lambda p:p['continuations'][0]['period'].update(end_exclusive='2026-07-01'),'unsupported','full_calendar_year_required')]
    for name,change,status,reason in partials:
        pp,r=case(name,change); annual=r['years'][-1]['annual_run']
        check(name+':prior_year_preserved',r['status']=='partial' and r['years'][0]['result_sha256']==first['result_sha256'] and annual['status']==status and (reason is None or annual['reason']==reason) and 'closing_memory' not in r['years'][-1])
        check(name+':chain_valid',verify_chain(pp,r))
    def fail_first(p):
        events=p['initial_year']['events']
        next(e for e in events if e['kind']=='payroll')['at']='2025-01-04T13:00:00Z'
        events.sort(key=lambda e:e['at'])
    fp,fr=case('first_year_payroll_failure',fail_first)
    check('failed_first_year_blocks_second',len(fr['years'])==1 and len(fr['unexecuted'])==1 and fr['stopped_status']=='funding_failure' and verify_chain(fp,fr))
    check('failed_prefix_stays_dated',fr['years'][0]['annual_report']['prefix_snapshot']['as_of']=='2025-01-04T12:00:00Z' and not fr['years'][0]['annual_report']['annual_complete'])
    check('unexecuted_report_unresolved',report_view(fp,fr,'2026-01-01')['status']=='unresolved')
    def fail_second(p):
        events=p['continuations'][0]['events']
        next(e for e in events if e['kind']=='collection')['at']='2026-01-05T09:00:00Z'
        events.sort(key=lambda e:e['at'])
    sp,sr=case('second_year_supplier_failure',fail_second)
    check('second_year_failure_preserves_first',sr['status']=='partial' and sr['years'][0]['result_sha256']==first['result_sha256'] and sr['stopped_status']=='funding_failure')
    check('failed_supplier_mutates_no_claim',sr['years'][1]['annual_run']['claims']['purchase-ap-2026']['settled']==0 and sr['years'][1]['annual_run']['balances']['cash']==expected['opening_cash'])
    check('failure_annual_cash_unresolved',sr['years'][1]['annual_report']['lines']['cash']['status']=='unresolved')
    check('revision_no_change_rejected',revise(path,source,1,path['continuations'][0],'same')['reason']=='unchanged_revision')
    changed=deepcopy(path['initial_year']);changed['opening_digest']='0'*64
    check('revision_cannot_change_historical_source',revise(path,source,0,changed,'bad')['reason']=='revision_changes_historical_binding')
    check('malformed_revision_rejected',revise(path,source,1,None,'bad')['status']=='invalid')
    check('empty_revision_reason_rejected',revise(path,source,1,replacement,'')['status']=='invalid')
    third=deepcopy(path['continuations'][0])
    third.update(name='NorthstarOperatingYear2027', period={'start':'2027-01-01','end_exclusive':'2028-01-01'})
    third['inventory'].update(demand_units='34/1',price='12/1',target_units='12/1')
    third['trade'].update(sales_claim_id='sales-ar-2027',purchase_claim_id='purchase-ap-2027',supplier_payment='170/1')
    third['cash'].update(payroll='60/1',capex_id='capex-2027',capex_service='2028-01-01',dividend='12/1')
    third['opening_settlements']=[{'id':key,'amount':'0/1'} for key in ['opening-ar','opening-ap','purchase-ap','sales-ar']]
    third['opening_settlements'] += [{'id':'purchase-ap-2026','amount':'10/1'},{'id':'sales-ar-2026','amount':'176/5'}]
    for e in third['events']:
        e['at']=e['at'].replace('2026-','2027-')
    long_path=deepcopy(path);long_path['continuations'].append(third)
    long=execute(long_path,source);witnesses['three_year_path']={'path':long_path,'result':long}
    last=long['years'][2]['annual_run']
    check('three_year_chain_complete',long['status']=='complete_conditional' and verify_chain(long_path,long))
    check('extending_path_preserves_existing_year_ids',[y['result_sha256'] for y in long['years'][:2]]==[y['result_sha256'] for y in result['years']])
    check('third_year_independent_income',last['income']['revenue']==408 and last['income']['cost_of_sales']==170 and last['income']['depreciation']==16 and last['income']['tax']==Q(156,5) and last['statements']['profit']==Q(624,5))
    check('third_year_independent_cash',last['statements']['cash_flows']['operating']==Q(626,5) and last['statements']['cash']==cash2+Q(516,5))
    check('third_year_claims_and_inventory',last['closing_balances']['receivables']==Q(204,5) and last['closing_balances']['payables']==-10 and last['inventory_units']==12)
    check('third_year_lifetime_claims',long['years'][2]['closing_memory']['claims']['sales-ar']['recognised']==300 and long['years'][2]['closing_memory']['claims']['sales-ar']['settled']==300)
    unknown=deepcopy(long_path);unknown['continuations'][0]['inventory']['price']='unknown'
    stopped=execute(unknown,source);witnesses['middle_year_unresolved']={'path':unknown,'result':stopped}
    check('unresolved_middle_year_blocks_third',len(stopped['years'])==2 and stopped['unexecuted']==[{'index':2,'period':third['period'],'status':'unresolved','reason':'predecessor_incomplete'}] and verify_chain(unknown,stopped))
    check('unexecuted_third_report_unresolved',report_view(unknown,stopped,'2027-01-01')['status']=='unresolved')
